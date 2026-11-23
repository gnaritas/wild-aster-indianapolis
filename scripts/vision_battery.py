#!/usr/bin/env python3
"""OpenRouter vision battery (lane-sanctioned fallback when the lane vision router
timeouts): threaded image defect-hunt, one call per shot, VERDICT line enforced.
t_f44ac4fb render sweep, 2026-11-22."""
import base64, json, os, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor

KEY = None
for line in open(os.path.expanduser('~/.hermes/.env')):
    if line.startswith('OPENROUTER_API_KEY='):
        KEY = line.split('=', 1)[1].strip().strip('"').strip("'")
        break
if not KEY:
    sys.exit('no OPENROUTER_API_KEY')

GUARD = ("Do NOT flag: faint decorative flower-stamp art or circles in backgrounds; dashed "
         "decorative rings near the brand lockup or on info cards; italic gold 'Boutique' "
         "serif styling; normal narrow-screen line wrapping (including header links wrapping "
         "to a second line on mobile); 1-2px nits; the right-edge scrollbar gutter.")
PROMPTS = {
    'vision-sheet-mobile900.png': "Contact sheet of MOBILE 390px full-page captures of a boutique site (pages labeled home, clothing, local-brands, visit, about, contact, privacy, 404, thanks). Coarse thumbnails: report only GROSS defects certain at this scale — horizontal cut-off at the right edge, overlapping blocks, text outside the narrow column, sections missing where content is expected, broken footer stacking. " + GUARD + " Label each claim with its page name. End with exactly one line: VERDICT: CLEAN or VERDICT: DEFECTS",
    's1-home-desktop.png': "Full-page 1280px desktop capture of a size-inclusive clothing boutique homepage. List every visual/layout defect: section, exact problem (misaligned grids, overflow/clipping, uneven margins, overlaps, broken nav/footer, contrast failure). " + GUARD + " End with exactly one line: VERDICT: CLEAN or VERDICT: DEFECTS",
    's1-home-mobile.png': "Full-page 390px mobile capture of a boutique homepage. List every visual/layout defect: anything cut off at the left/right edge, overlapping blocks, grids that failed to stack to one column, broken header or footer stacking. " + GUARD + " End with exactly one line: VERDICT: CLEAN or VERDICT: DEFECTS",
    's1-contact-desktop.png': "Full-page 1280px desktop capture of the boutique contact page (form left, opening info card right). List every visual/layout defect. " + GUARD + " End with exactly one line: VERDICT: CLEAN or VERDICT: DEFECTS",
    's1-contact-mobile.png': "Full-page 390px mobile capture of the boutique contact page (form and info card stack). List every visual/layout defect. " + GUARD + " End with exactly one line: VERDICT: CLEAN or VERDICT: DEFECTS",
}
OUT = {}


def ask(name):
    img = base64.b64encode(open(name, 'rb').read()).decode()
    body = json.dumps({
        'model': 'google/gemini-2.5-flash',
        'messages': [{'role': 'user', 'content': [
            {'type': 'text', 'text': PROMPTS[name]},
            {'type': 'image_url', 'image_url': {'url': 'data:image/png;base64,' + img}}]}],
        'max_tokens': 900,
    }).encode()
    req = urllib.request.Request('https://openrouter.ai/api/v1/chat/completions', data=body, headers={
        'Authorization': 'Bearer ' + KEY, 'content-type': 'application/json'})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                j = json.load(r)
            txt = j['choices'][0]['message']['content']
            verdict = 'DEFECTS' if 'VERDICT: DEFECTS' in txt else ('CLEAN' if 'VERDICT: CLEAN' in txt else 'NO-VERDICT')
            return name, {'verdict': verdict, 'text': txt}
        except Exception as e:
            if attempt == 2:
                return name, {'verdict': 'ERROR', 'text': str(e)}


with ThreadPoolExecutor(max_workers=4) as pool:
    for name, res in pool.map(ask, PROMPTS):
        OUT[name] = res
        print('====', name, res['verdict'])
        print(res['text'][-1400:])
json.dump(OUT, open('vision-results.json', 'w'), indent=1)
print('saved vision-results.json')
