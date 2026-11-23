# Wild Aster Boutique pitch: guards + asserts + send + read-back + registry append + lane.db event (abort-on-any-gate)
# Adapted from the proven copa-cafe send_pitch.py (2026-11-22). Resume-safe: existing registry pitch row = skip.
# Intended to run inside the recipient-local send window (Indianapolis EST 07:00-17:00). DRY=1 = guards+asserts only.
import json, re, subprocess, sys, os, time, datetime, imaplib

DRAFT = '/Users/rleon/sites/wild-aster-indianapolis/PITCH-DRAFT.md'
REG = '/Users/rleon/.hermes/projects/websites/pitch_registry.jsonl'
LANEDB = '/Users/rleon/.hermes/projects/websites/lane.db'
ENVOUT = '/Users/rleon/sites/wild-aster-indianapolis/send-envelope.json'
TO = 'hello@shopsaltandash.com'
SUBJ = 'Website demo for Wild Aster Boutique'
TOKEN = 'wild-aster-indianapolis-t1'
SLUG = 'wild-aster-indianapolis'
CARD = 't_f44ac4fb'
body = open(DRAFT, encoding='utf-8').read()
assert '\u2026' not in body, 'U+2026 mangled token in draft'

def norm(s): return re.sub(r'[^a-z0-9]', '', (s or '').lower())
rows = [json.loads(l) for l in open(REG) if l.strip()]
nto = norm(TO)

# 0) resume predicate
if any(r.get('type') == 'pitch' and r.get('slug') == SLUG for r in rows):
    sys.exit('SKIP: registry already has a pitch row for this slug — never re-send')

# 1) never-pitch-twice guards
email_hits = [r for r in rows if norm(r.get('email', '')) == nto]
nameq = norm('wild aster boutique')
name_hits = [r for r in rows if any(nameq == norm(a) or nameq in norm(a) or norm(a) in nameq
              for a in ([r.get('business', '')] + list(r.get('name_aliases', []) or [])) if norm(a))]
print('GUARD email rows:', [(r.get('type'), r.get('slug'), r.get('email')) for r in email_hits])
print('GUARD name rows:', [(r.get('type'), r.get('slug'), r.get('business')) for r in name_hits])
pitched_emails = {norm(r['email']) for r in rows if r.get('type') == 'pitch' and r.get('email')}
blocking_names = [r for r in name_hits if r.get('type') in ('pitch', 'no', 'optout', 'has_site', 'sent')]
if any(norm(r.get('email', '')) in pitched_emails for r in email_hits) or blocking_names:
    sys.exit('ABORT: already pitched/known on this email-or-name key')

# 2) inbox cap (2 businesses max per inbox)
inbox_alias = 'hello@shopsaltandash.com'
n_same_inbox = sum(1 for r in rows if r.get('type') == 'pitch' and (r.get('alias') == inbox_alias or norm(r.get('email', '')) == nto))
print(f'inbox cap check ({inbox_alias}):', n_same_inbox, '(cap 2)')
assert n_same_inbox < 2, 'ABORT: inbox cap'

# 3) optout suppression (email is globally suppressed)
opt_emails = {norm(r.get('email', '')) for r in rows if r.get('type') == 'optout'}
assert nto not in opt_emails, 'ABORT: opted-out address'
try:
    sup = open('/Users/rleon/.hermes/projects/websites/optout_list.txt').read()
    assert nto not in norm(sup), 'ABORT: optout_list.txt'
except FileNotFoundError:
    pass

# 4) copy form asserts (proven formula; ABORT before send) — URLs derived from the draft itself
assert body.count('](http') == 2, f'links {body.count("](http")}'
assert body.count('<img') == 1, 'img count'
demo = re.search(r'\]\((https://wild-aster-indianapolis-demo[^)]+)\)', body).group(1)
pay = re.search(r'\]\((https://buy\.stripe[^)]+)\)', body).group(1)
pixel = re.search(r'<img src="([^"]+)"', body)
for need in ('utm_medium=email', 'utm_campaign=websites', f'utm_content={TOKEN}'):
    assert need in demo, 'demo missing ' + need
    assert need in pay, 'pay missing ' + need
assert f'client_reference_id={TOKEN}' in pay, 'pay missing client_reference_id'
assert pixel and pixel.group(1) == f'https://wild-aster-indianapolis-demo.up.railway.app/open?t={TOKEN}', 'pixel token'
t = re.sub(r'\*\*', '', body)
t = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', t)
t = re.sub(r'<img[^>]*>', '', t)
lines = [l for l in t.splitlines() if l.strip()]
lines = [l for l in lines if not l.startswith('Hi ') and not l.startswith('— Jarvis')
         and not l.startswith('OnSmalltalk Media ·') and not l.startswith('<img')]
n = len(re.findall(r'\S+', ' '.join(lines)))
print(f'ASSERT core words: {n} (limit 110); links 2; utm+pixel token {TOKEN} OK')
assert n <= 110, f'ABORT words {n}'

if os.environ.get('DRY'):
    sys.exit(f'GUARDS+ASSERTS PASS (dry, not sent); words={n}')

# 4b) recipient-local send window (Indianapolis = EST/EDT; owner mail 07:00-17:00 local only)
import datetime as _dt
try:
    from zoneinfo import ZoneInfo
    local_now = _dt.datetime.now(ZoneInfo('America/Indiana/Indianapolis'))
except Exception:
    local_now = _dt.datetime.utcnow() - _dt.timedelta(hours=5)  # EST fallback Nov-Mar
print('recipient-local now:', local_now.strftime('%Y-%m-%d %H:%M %Z'))
if not (7 <= local_now.hour < 17):
    sys.exit(f'ABORT WINDOW: {local_now.strftime("%H:%M")} local outside 07:00-17:00 — park, never night-send')

# 4c) envelope-reuse guard (session-house-boston 2026-11-23): if a crashed earlier attempt
# already sent, send-envelope.json carries ok=true — reuse its mid, NEVER re-send, fall through
# to read-back + registry append.
prev_env = None
if os.path.exists(ENVOUT):
    try:
        pe = json.load(open(ENVOUT))
        pd = (pe.get('env') or {}).get('data') or {}
        if pe.get('ok') and (pd.get('message_id') or pd.get('msg_id')):
            prev_env = pe.get('env')
            print('RESUME-SEND: envelope ok=true on disk — reusing msg id, NOT re-sending')
    except Exception:
        pass

# 5) send (body on stdin, --json envelope; message_id from the envelope JSON)
if prev_env is None:
    res = subprocess.run(['email', 'send', '--account', 'jarvis', '--as', 'websites',
                          '--to', TO, '--subject', SUBJ, '--json'],
                         input=body.encode(), capture_output=True, timeout=120)
    try:
        env = json.loads(res.stdout.decode())
    except Exception:
        open(ENVOUT, 'w').write(res.stdout.decode() + '\n---STDERR---\n' + res.stderr.decode())
        sys.exit('ABORT: unparseable send envelope — do NOT resend, read back Sent Mail first')
    json.dump({'ok': env.get('ok'), 'env': env}, open(ENVOUT, 'w'))
else:
    env = prev_env
ok = env.get('ok')
mid = (env.get('data') or {}).get('message_id') or (env.get('data') or {}).get('msg_id')
print('SEND ok=', ok, 'msg:', mid if ok else env)
if not ok or not mid:
    sys.exit('ABORT send — read back [Gmail]/Sent Mail before any retry')

# 6) sent read-back (raw imaplib): Message-ID equality + identity header pair
conf = {}
for l in open(os.path.expanduser('~/.hermes/config/jarvis-email.conf')):
    if '=' in l: k, v = l.split('=', 1); conf[k.strip()] = v.strip()
    elif ':' in l: k, v = l.split(':', 1); conf[k.strip()] = v.strip()
M = imaplib.IMAP4_SSL(conf.get('IMAP_SERVER', 'imap.gmail.com'))
M.login(conf['EMAIL'], conf['APP_PASSWORD'])
M.select('"[Gmail]/Sent Mail"')
typ, m = M.uid('search', None, 'SUBJECT', '"Website demo for Wild Aster Boutique"')
ids = [i.decode() for i in m[0].split()]
hit = None
for uid in ids[-3:]:
    typ, d = M.uid('fetch', uid, '(BODY.PEEK[HEADER])')
    hdr = d[0][1].decode(errors='replace')
    if mid in hdr:
        orp = bool(re.search(r'X-Google-Original-From:[^>]*jarvis\+websites', hdr, re.I))
        rto = bool(re.search(r'Reply-To:\s*\S*jarvis\+websites', hdr, re.I))
        hit = {'uid': uid, 'ogf': orp, 'reply_to': rto}
        break
M.logout()
print('READBACK:', hit)
assert hit and hit['ogf'] and hit['reply_to'], 'ABORT READBACK — mail out but unproven; append registry only after proof, never re-send'

# 7) registry append AT SEND (type IN the dict), then recount-verify
row = {
    'type': 'pitch', 'date': '2026-11-23',
    'ts': datetime.datetime.now().astimezone().isoformat(timespec='seconds'),
    'slug': SLUG, 'business': 'Wild Aster Boutique (Indianapolis IN - Irvington)',
    'name_aliases': ['Wild Aster Boutique', 'Wild Aster', 'wild-aster', 'Wild Aster Indianapolis', 'wildasterboutique'],
    'email': TO, 'alias': inbox_alias, 'card': CARD,
    'msg_id': mid, 'preview': 'https://wild-aster-indianapolis-demo.up.railway.app',
    'subject': SUBJ, 'subject_arm': 'v7', 'cohort': 'A',
    'shot': False, 'pixel': True, 'utm_content': TOKEN,
    'followup_due': '2026-12-02',
    'ladder': 't2 2026-12-02 / t3 2026-12-09 / t4 2026-12-16 (weekday ladder, US-holiday shift); teardown recheck >= 2026-12-22',
    'feed_id': 'press-mirrorindy', 'shop_id': 'wild-aster-indianapolis',
    'note': ('owner email PUBLISHED in Mirror Indy new-opening article (hiring contact, owner\'s sister-brand inbox; '
             'press-quoted named owner Ashton Boehman = cross-business tie to Salt & Ash Market, shopsaltandash.com live; '
             'same inbox as Salt & Ash allowed, cap 1); no-site evidence: variant matrix DRY + RDAP unregistered, '
             ' GBP no listing, shopsaltandash.com carries zero Wild Aster mentions, brand-SERP clean of own domain; '
             'opens 2026-11-28 Small Business Saturday; founder bundle T1 $249+$39/mo 31d trial; v7 subject arm; 9-page site'),
}
with open(REG, 'a') as f:
    f.write(json.dumps(row, ensure_ascii=False) + '\n')
pitches = 0; mine = 0; line_no = 0
for i, l in enumerate(open(REG), 1):
    try: d = json.loads(l)
    except Exception: continue
    if d.get('type') == 'pitch':
        pitches += 1
        if d.get('slug') == SLUG: mine += 1; line_no = i  # physical registry line (events.line PK), not pitch ordinal — sokoya 2026-11-23 pitfall
assert mine == 1, f'wild-aster pitch rows={mine}'
print(f'REGISTRY_OK total_pitch_rows={pitches} mine=1 line={line_no}')

# 8) lane.db events mirror row
import sqlite3
db = sqlite3.connect(LANEDB)
db.execute("""INSERT INTO events (line,type,slug,business,email,msg_id,followup_due,date_txt,ts,note)
VALUES (?,?,?,?,?,?,?,?,?,?)""",
 (line_no, 'pitch', SLUG, 'Wild Aster Boutique (Indianapolis IN - Irvington)', TO, mid,
  '2026-12-02', '2026-11-23', int(time.time()),
  'pitched via websites desk; demo wild-aster-indianapolis-demo.up.railway.app; founder bundle T1 $249+$39/mo 31d trial; v7 subject arm; read-back proof uid=' + hit['uid']))
db.commit()
print('EVENT_ROW_OK', db.execute("SELECT line,type,slug,msg_id FROM events WHERE slug=?", (SLUG,)).fetchall())
print('ALL_DONE', mid)
