#!/usr/bin/env python3
"""Wild Aster Boutique — template v2 site generator (websites lane, t_f44ac4fb, 2026-11-22).
Facts ONLY from the card / Mirror Indy source article (Nov 2026). No invented claims.
7 content pages + 404 + thanks. Single local stylesheet, zero JS, inline SVG art only.
Design identity: prairie-aster boutique — Georgia serif display, system-sans body,
cream paper + deep plum ink + aster-violet/goldenrod accents. No sibling look-alike."""
import os, json, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
PUBLIC = os.path.join(HERE, "public")
BUILT = "2026-11-22"
SLUG = "wild-aster-indianapolis"
ORIGIN = "https://" + SLUG + "-demo.up.railway.app"
NAME = "Wild Aster Boutique"
SHORT = "Wild Aster"
EMAIL = "hello@shopsaltandash.com"
MI = "https://mirrorindy.org/new-clothing-store-in-irvington-small-business-indianapolis/"
SALT = "https://shopsaltandash.com"

def U(path):
    return ORIGIN + ("/" if path == "/" else path)

# ---------------- shared assets ----------------
# aster mark: 12-petal daisy, gold center (currentColor petals so header/footer recolor).
# Rotated path copies instead of <use> — the stamp appears 3x per page; <defs id> would duplicate ids.
PETAL_D = "M12 1.8c1.5 1.9 1.5 4.4 0 6.3-1.5-1.9-1.5-4.4 0-6.3z"
PETALS = "".join(f'<path d="{PETAL_D}" transform="rotate({d} 12 12)"/>' for d in range(0, 360, 30))
STAMP = ('<svg class="stamp" viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
         '<g fill="currentColor" opacity=".92">' + PETALS + '</g>'
         '<circle cx="12" cy="12" r="2.7" fill="var(--gold)"/></svg>')

def NAV():
    return ('<nav aria-label="Site"><ul>'
            '<li><a href="/clothing">Clothing</a></li>'
            '<li><a href="/local-brands">Local brands</a></li>'
            '<li><a href="/visit">Visit</a></li>'
            '<li><a href="/about">About</a></li>'
            '<li><a class="btn pill" href="/contact">Contact</a></li>'
            '</ul></nav>')

FOOTER = (
 '<footer class="site"><div class="wrap foottop"><div><p class="fbrand">' + STAMP +
 '<span>Wild Aster <em>Boutique</em></span></p>'
 '<p class="ftag">Size-inclusive clothing &middot; S&ndash;3XL &middot; under $100</p>'
 '<div class="fnaps"><p class="ftown">Find us</p>'
 '<address class="addr">Downtown Irvington<br>Indianapolis, Indiana</address>'
 '<p class="fhrs">Wed&ndash;Sun 11&nbsp;a.m.&ndash;6&nbsp;p.m. &middot; Mon &amp; Tue closed</p>'
 '<p>Questions: <a href="mailto:' + EMAIL + '">' + EMAIL + '</a> &middot; <a href="/contact">contact form</a></p>'
 '</div></div>'
 '<nav aria-label="Footer"><ul>'
 '<li><a href="/clothing">Clothing</a></li>'
 '<li><a href="/local-brands">Local brands</a></li>'
 '<li><a href="/visit">Visit</a></li>'
 '<li><a href="/about">About</a></li>'
 '<li><a href="/contact">Contact</a></li>'
 '<li><a href="/privacy">Privacy</a></li></ul></nav>'
 '<p class="fpress">In the news:<br><a href="' + MI + '" rel="noopener">Mirror Indy: New Irvington boutique will sell size-inclusive clothes</a></p>'
 '</div><div class="wrap"><p class="footline">&copy; 2026 Wild Aster Boutique &middot; Size-inclusive boutique &middot; Downtown Irvington, Indianapolis, Indiana</p></div></footer>'
)

def HEAD(title, desc, path, util=False):
    t = title.replace("&", "&amp;")
    s = ['<!DOCTYPE html>\n<html lang="en">\n<head>\n<!-- BUILT-' + BUILT + ' -->',
         '<meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width, initial-scale=1">',
         '<title>' + t + '</title>',
         '<meta name="description" content="' + desc + '">',
         '<meta name="robots" content="noindex, nofollow">',
         '<link rel="canonical" href="' + U(path) + '">',
         '<link rel="icon" type="image/svg+xml" href="/favicon.svg">']
    if not util:
        s += ['<meta property="og:type" content="website">',
              '<meta property="og:site_name" content="Wild Aster Boutique">',
              '<meta property="og:title" content="' + t + '">',
              '<meta property="og:description" content="' + desc + '">',
              '<meta property="og:url" content="' + U(path) + '">',
              '<meta property="og:image" content="' + ORIGIN + '/og.png">',
              '<meta name="twitter:card" content="summary_large_image">',
              '<meta name="twitter:title" content="' + t + '">',
              '<meta name="twitter:description" content="' + desc + '">']
    s += ['<link rel="stylesheet" href="/style.css">', '</head>', '<body>',
          '<a class="skip" href="#main">Skip to content</a>',
          '<header class="site"><div class="wrap hdr"><a class="wm" href="/">' + STAMP +
          '<span>Wild Aster <em>Boutique</em></span></a>' + NAV() + '</div></header>']
    return "\n".join(s)

def LD(blocks):
    return '<script type="application/ld+json">\n' + json.dumps(
        {"@graph": blocks} if len(blocks) > 1 else blocks[0],
        indent=1, ensure_ascii=False) + '\n</script>'

def store_node():
    return {
        "@type": "ClothingStore",
        "@id": ORIGIN + "/#store",
        "name": NAME,
        "alternateName": "Wild Aster",
        "description": "Size-inclusive clothing boutique in downtown Irvington, Indianapolis. Sizes S-3XL, items under $100, with locally made accessories and a focus on women-owned brands.",
        "url": ORIGIN + "/",
        "image": ORIGIN + "/og.png",
        "email": EMAIL,
        "address": {"@type": "PostalAddress", "streetAddress": "Downtown Irvington",
                    "addressLocality": "Indianapolis", "addressRegion": "IN", "addressCountry": "US"},
        "openingHoursSpecification": [
            {"@type": "OpeningHoursSpecification", "dayOfWeek": d, "opens": "11:00", "closes": "18:00"}
            for d in ["Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]],
        "funder": {"@type": "Person", "@id": ORIGIN + "/about#ashton", "name": "Ashton Boehman"},
    }

def webpage(name, url_path, desc, about=None):
    n = {"@type": "WebPage", "@id": U(url_path) + "#webpage", "name": name,
         "url": U(url_path), "isPartOf": {"@id": ORIGIN + "/#website"},
         "description": desc}
    if about: n["about"] = about
    return n

def breadcrumb(items, url_path):
    return {"@type": "BreadcrumbList", "@id": U(url_path) + "#crumbs",
            "itemListElement": [{"@type": "ListItem", "position": i + 1,
                                 "name": n, "item": U(p)} for i, (n, p) in enumerate(items)]}

WEBSITE = {"@type": "WebSite", "@id": ORIGIN + "/#website", "name": NAME, "url": ORIGIN + "/"}

# ---------------- HERO art (inline SVG cluster) ----------------
HERO_ART = (
 '<svg class="heroart" viewBox="0 0 420 340" aria-hidden="true" focusable="false">'
 '<defs><path id="pet" d="M0-58C11-41 11-15 0 0-11-15-11-41 0-58Z"/></defs>'
 '<g transform="translate(150 150)">'
 '<circle r="132" fill="none" stroke="var(--aster)" stroke-width="1" stroke-dasharray="3 6" opacity=".55"/>'
 '<g fill="var(--aster)">' + "".join(f'<use href="#pet" transform="rotate({d}) translate(0 -46)"/>' for d in range(0, 360, 24)) + '</g>'
 '<g fill="var(--rose)" transform="rotate(12) scale(.78)">' + "".join(f'<use href="#pet" transform="rotate({d}) translate(0 -46)"/>' for d in range(0, 360, 30)) + '</g>'
 '<circle r="26" fill="var(--gold)"/><circle r="26" fill="none" stroke="var(--ink)" stroke-width="1.4" opacity=".5"/></g>'
 '<g transform="translate(322 92) scale(.5)" opacity=".9">'
 '<g fill="var(--gold)">' + "".join(f'<use href="#pet" transform="rotate({d}) translate(0 -46)"/>' for d in range(0, 360, 28)) + '</g>'
 '<circle r="22" fill="var(--aster)"/></g>'
 '<g transform="translate(84 288) scale(.4)" opacity=".8">'
 '<g fill="var(--sage)">' + "".join(f'<use href="#pet" transform="rotate({d}) translate(0 -46)"/>' for d in range(0, 360, 28)) + '</g>'
 '<circle r="22" fill="var(--gold)"/></g>'
 '<path d="M150 262c-4 40-10 62-26 78M238 168c30 34 46 60 52 96" fill="none" stroke="var(--sage)" stroke-width="3" stroke-linecap="round"/>'
 '</svg>')

def CTAROW(two=True):
    # NOTE: must close the <p> — _verify.py's tag-stack check is strict (browsers auto-close, parser doesn't)
    b = ['<p class="ctarow"><a class="btn" href="/contact">Contact us</a></p>']
    if two: b = ['<p class="ctarow"><a class="btn" href="/clothing">See the clothing</a> '
                 '<a class="btn ghost" href="/contact">Contact us</a></p>']
    return "".join(b)

def PAGE(path, title, desc, body, ld_blocks, util=False):
    doc = HEAD(title, desc, path, util) + "\n<main id=\"main\">\n" + body + "\n</main>\n" + FOOTER
    if not util: doc = HEAD(title, desc, path) + "\n" + LD(ld_blocks) + "\n<main id=\"main\">\n" + body + "\n</main>\n" + FOOTER
    doc += "\n</body>\n</html>\n"
    open(os.path.join(PUBLIC, "index.html" if path == "/" else path.strip("/") + ".html"),
         "w", encoding="utf-8").write(doc)

# ---------------- FAQ (shared copy for home body + schema) ----------------
FAQS = [
 ("What sizes does Wild Aster carry?",
  "Sizes run from small to 3XL. The racks hold casual pieces like sweaters and stretchy pants, plus a few dresses for special occasions."),
 ("How much will things cost?",
  "Items are priced under $100."),
 ("When do you open, and what are your hours?",
  "Wild Aster opens Saturday, November 28, 2026 — Small Business Saturday. Hours are 11 a.m. to 6 p.m., Wednesday through Sunday."),
 ("Are the accessories locally made?",
  "Yes. Locally made accessories from brands like A Knot That Binds and Rose and Frankie Jewelry sit alongside the clothing, and the focus is on sourcing from women-owned brands."),
 ("Where is the boutique?",
  "Downtown Irvington on Indianapolis's east side — the former Josephine's storefront along the East Washington Street corridor."),
]

def faq_html():
    out = ['<section class="band faqwrap"><div class="wrap"><h2>Questions people are already asking</h2>',
           '<div class="faq">']
    for q, a in FAQS:
        out.append(f'<details><summary>{q}</summary><p>{a}</p></details>')
    out.append('</div></div></section>')
    return "\n".join(out)

FAQ_SCHEMA = {"@type": "FAQPage", "@id": ORIGIN + "/#faq",
              "mainEntity": [{"@type": "Question", "name": q,
                              "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQS],
              "isPartOf": {"@id": ORIGIN + "/#webpage"}}

# ---------------- pages ----------------
def home():
    h1 = "Wild Aster Boutique — Size-Inclusive Clothing &amp; Gifts, Irvington Indianapolis"
    d = ("Wild Aster opens November 28, 2026 in downtown Irvington, Indianapolis: size-inclusive clothing in sizes S-3XL, "
         "items under $100, locally made accessories, and a focus on women-owned brands. Open Wed-Sun 11-6.")
    b = ['<section class="hero"><div class="wrap heroinner">',
         '<p class="ribbon">Opens Sat, Nov 28 &middot; Small Business Saturday</p>',
         '<h1>Size-inclusive style lands in <em>downtown Irvington</em>.</h1>',
         '<p class="lede">Casual pieces like sweaters and stretchy pants, a few dresses for the occasions that matter — '
         'sized small to 3XL, priced under $100, with locally made accessories and a real focus on women-owned brands. '
         'Wild Aster opens Small Business Saturday, November 28, in the old Josephine&rsquo;s storefront.</p>',
         CTAROW(),
         '<ul class="chips"><li>Sizes <b>S&ndash;3XL</b></li><li>Under <b>$100</b></li><li>Woman-owned brands</li><li>Local accessories</li></ul>',
         '</div><div class="wrap heroartwrap">' + HERO_ART + '</div></section>']
    b.append('<section class="band"><div class="wrap"><h2>What&rsquo;s coming through the door</h2>'
             '<div class="grid cards">'
             '<div class="card"><h3>Clothing that actually fits</h3><p>Sweaters, stretchy pants, and a few occasion dresses &mdash; '
             'a full rack sized small to 3XL, chosen by a plus-sized owner who got tired of hunting for boutique pieces that fit.</p></div>'
             '<div class="card"><h3>Everything under $100</h3><p>Every item on the racks is priced under $100. Looking good should not require a loan.</p></div>'
             '<div class="card"><h3>Women-owned brands</h3><p>The buying philosophy is simple: Ashton focuses on sourcing from women-owned brands.</p></div>'
             '<div class="card"><h3>Locally made accessories</h3><p>Accessories from local makers &mdash; <a href="https://aknotthatbinds.com/" rel="noopener">A Knot That Binds</a> '
             'and <a href="https://www.instagram.com/rose_and_frankie_jewelry/" rel="noopener">Rose and Frankie Jewelry</a> &mdash; right alongside the clothing.</p></div>'
             '</div></div></section>')
    b.append('<section class="band ink sister"><div class="wrap"><p class="eyebrow">A sister store, not a twin</p>'
             '<blockquote>&ldquo;It&rsquo;s a sister store, not a twin,&rdquo; says owner Ashton Boehman &mdash; '
             'Wild Aster is the clothing companion to <a href="' + SALT + '" rel="noopener">Salt &amp; Ash Market</a>, '
             'her bath-and-body shop in the Factory Arts District. The apparel started in 2024 as a few racks inside Salt &amp; Ash '
             '(back when it was in Fountain Square); customers loved that it was size-inclusive, and it grew into its own leg.</blockquote>'
             '<p class="attrib">— Ashton Boehman, owner &middot; source: <a href="' + MI + '" rel="noopener">Mirror Indy</a></p></div></section>')
    b.append('<section class="band"><div class="wrap half"><div>'
             '<p class="eyebrow">The storefront</p><h2>The old Josephine&rsquo;s space, carried forward</h2>'
             '<p>Wild Aster takes over the former Josephine&rsquo;s — a local clothing store — right in the heart of Irvington. '
             'It is the third women-led chapter for that storefront, and Ashton wants it to stay one: '
             '<em>&ldquo;It was a space for people to go and feel confident, happy and I want to continue that.&rdquo;</em></p>'
             '<p>Expect window displays worth a slow walk — they are where Ashton spends a lot of her creative energy.</p></div>'
             '<div class="infocard"><p class="ftown">Opening</p><p class="big">Saturday, November 28, 2026</p>'
             '<p class="ftown">Hours</p><p class="big">Wed&ndash;Sun &middot; 11 a.m.&ndash;6 p.m.</p>'
             '<p class="ftown">Where</p><p>Downtown Irvington<br>Indianapolis, Indiana</p>'
             '<p class="ctarow"><a class="btn ghost dark" href="/visit">Visit details</a></p></div></div></section>')
    b.append(faq_html())
    b.append('<section class="band cta"><div class="wrap center"><h2>Be there on opening day</h2>'
             '<p>Doors open 11 a.m. Saturday, November 28 — Small Business Saturday in Irvington.</p>' + CTAROW() + '</div></section>')
    ld = [WEBSITE, webpage(h1.replace("&amp;", "&"), "/", d, about={"@id": ORIGIN + "/#store"}),
          store_node(), FAQ_SCHEMA, breadcrumb([("Home", "/")], "/")]
    PAGE("/", h1, d, "\n".join(b), ld)

def clothing():
    h1 = "Size-Inclusive Clothing, Small to 3XL — Wild Aster Boutique, Indianapolis IN"
    d = ("Boutique apparel sized small through 3XL in Irvington, Indianapolis: sweaters, stretchy pants and occasion dresses, all priced under $100. "
         "Chosen by a plus-sized owner. Opens Nov 28, 2026.")
    b = ['<section class="pagehero"><div class="wrap"><p class="eyebrow">Clothing &middot; Irvington, Indianapolis</p>'
         '<h1>Clothing sized <em>small to 3XL</em>, chosen by someone who lives in it</h1>'
         '<p class="lede">Wild Aster stocks casual pieces like sweaters and stretchy pants, plus a few dresses for special occasions — '
         'a true extended range, not a token rack.</p></div></section>',
         '<section class="band"><div class="wrap half"><div>'
         '<blockquote>&ldquo;I&rsquo;m a plus-sized person myself and I don&rsquo;t often find cute, boutique apparel that really fits me.&rdquo;</blockquote>'
         '<p class="attrib">— Ashton Boehman, owner &middot; source: <a href="' + MI + '" rel="noopener">Mirror Indy</a></p></div>'
         '<div class="infocard"><p class="ftown">The size run</p><p class="big">S &middot; M &middot; L &middot; XL &middot; 2XL &middot; 3XL</p>'
         '<p>From small through 3XL across the clothing.</p></div></div></section>',
         '<section class="band soft"><div class="wrap"><h2>What will be on the racks</h2><div class="grid cards">'
         '<div class="card"><h3>Sweaters</h3><p>Casual pieces you reach for daily — the cozy core of the shop.</p></div>'
         '<div class="card"><h3>Stretchy pants</h3><p>Comfy, easy, made to be worn on repeat.</p></div>'
         '<div class="card"><h3>Occasion dresses</h3><p>A few dresses for the moments that call for one.</p></div>'
         '<div class="card"><h3>Trendy, but not trend-chasing</h3><p>&ldquo;Some of the items will be a little trendy but not so trendy that you won&rsquo;t be wearing them for years and years.&rdquo;</p></div>'
         '</div></div></section>',
         '<section class="band"><div class="wrap center"><p class="eyebrow">Price promise</p>'
         '<p class="big">Every item is priced under $100.</p>' + CTAROW() + '</div></section>']
    svc = {"@type": "Service", "@id": ORIGIN + "/clothing#service",
           "name": "Size-Inclusive Boutique Clothing (Sizes S-3XL)",
           "serviceType": "Clothing retail",
           "description": "Casual and occasion apparel sized small through 3XL, priced under $100, sourced with a focus on women-owned brands.",
           "areaServed": [{"@type": "City", "name": "Indianapolis"}, {"@type": "Place", "name": "Irvington"}],
           "provider": {"@id": ORIGIN + "/#store"}}
    ld = [webpage(h1.replace("&amp;", "&"), "/clothing", d, about={"@id": ORIGIN + "/clothing#service"}),
          svc, {"@type": "Organization", "@id": ORIGIN + "/#store", "name": NAME}, breadcrumb([("Home", "/"), ("Clothing", "/clothing")], "/clothing")]
    PAGE("/clothing", h1, d, "\n".join(b), ld)

def brands():
    h1 = "Locally Made Accessories &amp; Women-Owned Brands — Wild Aster Boutique, Irvington Indianapolis"
    d = ("Wild Aster carries locally made accessories from A Knot That Binds and Rose and Frankie Jewelry, with a buying focus on women-owned brands. "
         "Downtown Irvington, Indianapolis. Opens Nov 28, 2026.")
    b = ['<section class="pagehero"><div class="wrap"><p class="eyebrow">Brands &middot; Irvington, Indianapolis</p>'
         '<h1>Local makers and <em>women-owned</em>, on purpose</h1>'
         '<p class="lede">Wild Aster sources with a point of view: locally made accessories from Indianapolis makers, and a buying focus on women-owned brands.</p></div></section>',
         '<section class="band"><div class="wrap grid twocards">'
         '<div class="card tall"><h3><a href="https://aknotthatbinds.com/" rel="noopener">A Knot That Binds</a></h3>'
         '<p>Locally made accessories, stocked right in the boutique.</p><p class="small"><a href="https://aknotthatbinds.com/" rel="noopener">aknotthatbinds.com</a></p></div>'
         '<div class="card tall"><h3><a href="https://www.instagram.com/rose_and_frankie_jewelry/" rel="noopener">Rose and Frankie Jewelry</a></h3>'
         '<p>Locally made jewelry from an Indianapolis maker, joining the accessories wall.</p>'
         '<p class="small"><a href="https://www.instagram.com/rose_and_frankie_jewelry/" rel="noopener">rose_and_frankie_jewelry on Instagram</a></p></div>'
         '</div></section>',
         '<section class="band soft"><div class="wrap half"><div><p class="eyebrow">The feel</p>'
         '<blockquote>&ldquo;It will have the same feeling as her flagship brand: kitschy, whimsical and handmade.&rdquo;</blockquote>'
         '<p class="attrib">Mirror Indy on Wild Aster &middot; <a href="' + MI + '" rel="noopener">read the story</a></p></div>'
         '<div class="infocard"><p class="ftown">Buying philosophy</p><p class="big">Women-owned first</p>'
         '<p>Ashton focuses on sourcing items from women-owned brands, local makers included.</p></div></div></section>',
         # NOTE: half-section wrappers below close with an extra </div> because <div class="wrap half">
         # opens wrap + half as ONE element; keep exactly three closes (infocard, half, section).
         '<section class="band"><div class="wrap center">' + CTAROW() + '</div></section>']
    svc = {"@type": "Service", "@id": ORIGIN + "/local-brands#service",
           "name": "Locally Made Accessories & Women-Owned Brand Sourcing",
           "serviceType": "Accessory and boutique apparel retail",
           "description": "Locally made accessories from A Knot That Binds and Rose and Frankie Jewelry, sourced with a focus on women-owned brands.",
           "areaServed": [{"@type": "City", "name": "Indianapolis"}, {"@type": "Place", "name": "Irvington"}],
           "provider": {"@id": ORIGIN + "/#store"}}
    ld = [webpage(h1.replace("&amp;", "&"), "/local-brands", d, about={"@id": ORIGIN + "/local-brands#service"}),
          svc, {"@type": "Organization", "@id": ORIGIN + "/#store", "name": NAME},
          breadcrumb([("Home", "/"), ("Local brands", "/local-brands")], "/local-brands")]
    PAGE("/local-brands", h1, d, "\n".join(b), ld)

def about():
    h1 = "About Ashton Boehman — Wild Aster Boutique, Irvington Indianapolis"
    d = ("Wild Aster is owned by Ashton Boehman, the printmaker and crafter behind Salt & Ash Market. From St. Meinrad to Herron printmaking to "
         "downtown Irvington — the story of the boutique. Opens Nov 28, 2026.")
    b = ['<section class="pagehero"><div class="wrap"><p class="eyebrow">About</p>'
         '<h1>Ashton Boehman — printmaker, crafter, <em>shop owner</em></h1>'
         '<p class="lede">Wild Aster is named for the purple, star-shaped wildflower. Its owner is the person behind '
         '<a href="' + SALT + '" rel="noopener">Salt &amp; Ash Market</a>, and the boutique is her second storefront.</p></div></section>',
         '<section class="band"><div class="wrap prose">'
         '<p>Ashton grew up in St. Meinrad, Indiana, and moved to Indianapolis in 2014 to study printmaking at the Herron School of Art '
         'and Design at IU Indianapolis. She is a crafter first — the handmade sensibility runs through everything she stocks, '
         'and through the window displays she designs herself.</p>'
         '<p>In 2024, while Salt &amp; Ash Market was located in Fountain Square, she put a few clothing items on its racks. '
         'Customers were surprised there was so much apparel — and that it was size-inclusive. The clothing kept growing until it became its own leg of Salt &amp; Ash. '
         'Wild Aster is where that leg becomes a store of its own: <em>&ldquo;a sister store, not a twin.&rdquo;</em></p>'
         '<p>Why Irvington? A small-town feel inside a big city, walkable neighbors like Hampton &amp; Co. and The Med, and the East Washington Street corridor '
         'where the IndyGo Blue Line is under construction. And a storefront with history: the space Wild Aster takes over used to house Josephine&rsquo;s, a local clothing store. '
         '<em>&ldquo;It was a space for people to go and feel confident, happy and I want to continue that.&rdquo;</em></p>'
         '<blockquote>&ldquo;I want to be that place people go on a walk and always stop in to see what&rsquo;s new. I want people to go back to going to stores and that spirit of discovery.&rdquo;</blockquote>'
         '<p class="attrib">— Ashton Boehman &middot; all quotes: <a href="' + MI + '" rel="noopener">Mirror Indy</a></p>'
         '</div></section>',
         '<section class="band soft"><div class="wrap center"><h2>Wild Aster &amp; Salt &amp; Ash</h2>'
         '<p>Same owner, same handmade heart — different shops. Salt &amp; Ash Market is boutique bath-and-body in the '
         'Factory Arts District; Wild Aster is the clothing sister, opening in downtown Irvington.</p>'
         '<p class="ctarow"><a class="btn ghost dark" href="' + SALT + '" rel="noopener">See Salt &amp; Ash Market</a> '
         '<a class="btn" href="/visit">Visit Wild Aster</a></p></div></section>']
    person = {"@type": "Person", "@id": ORIGIN + "/about#ashton", "name": "Ashton Boehman",
              "jobTitle": "Owner", "worksFor": {"@id": ORIGIN + "/#store"},
              "description": "Indianapolis printmaker and crafter; owner of Wild Aster Boutique in downtown Irvington and Salt & Ash Market in the Factory Arts District."}
    ld = [{"@type": "AboutPage", "@id": U("/about") + "#webpage", "name": h1.replace("&amp;", "&"),
           "url": U("/about"), "isPartOf": {"@id": ORIGIN + "/#website"}, "about": person},
          person, {"@type": "Organization", "@id": ORIGIN + "/#store", "name": NAME},
          breadcrumb([("Home", "/"), ("About", "/about")], "/about")]
    PAGE("/about", h1, d, "\n".join(b), ld)

def visit():
    h1 = "Visit Wild Aster Boutique — Downtown Irvington, Indianapolis (Open Wed–Sun 11–6)"
    d = ("Wild Aster opens Saturday, November 28, 2026 in downtown Irvington, Indianapolis — the former Josephine's storefront on the East Washington Street corridor. "
         "Open Wednesday through Sunday, 11 a.m. to 6 p.m.")
    b = ['<section class="pagehero"><div class="wrap"><p class="eyebrow">Visit</p>'
         '<h1>Opening day: <em>Saturday, November 28</em></h1>'
         '<p class="lede">Doors open 11 a.m. on Small Business Saturday, in downtown Irvington — the old Josephine&rsquo;s storefront, '
         'right on the East Washington Street corridor.</p>' + CTAROW() + '</div></section>',
         '<section class="band"><div class="wrap grid hoursgrid">'
         '<div class="infocard"><p class="ftown">Hours</p>'
         '<table class="hours"><tr><td>Wednesday</td><td>11 a.m.&ndash;6 p.m.</td></tr>'
         '<tr><td>Thursday</td><td>11 a.m.&ndash;6 p.m.</td></tr>'
         '<tr><td>Friday</td><td>11 a.m.&ndash;6 p.m.</td></tr>'
         '<tr><td>Saturday</td><td>11 a.m.&ndash;6 p.m.</td></tr>'
         '<tr><td>Sunday</td><td>11 a.m.&ndash;6 p.m.</td></tr>'
         '<tr class="closed"><td>Monday &amp; Tuesday</td><td>Closed</td></tr></table></div>'
         '<div class="infocard"><p class="ftown">Where</p><p class="big">Downtown Irvington</p>'
         '<p>Indianapolis, Indiana &mdash; the former Josephine&rsquo;s storefront along the East Washington Street corridor.</p>'
         '<p class="ftown">The neighborhood</p><p>A small-town feel inside a big city: walkable neighbors like Hampton &amp; Co. '
         'and The Med, with the IndyGo Blue Line under construction along East Washington.</p></div>'
         '</div></section>',
         '<section class="band soft"><div class="wrap half"><div><p class="eyebrow">We&rsquo;re hiring</p>'
         '<h2>A retail sales associate, ideally someone who loves this neighborhood</h2>'
         '<p>Ashton is hiring a retail sales associate for the opening. To apply, send a resume and a cover letter to '
         '<a href="mailto:' + EMAIL + '">' + EMAIL + '</a>.</p></div>'
         '<div class="infocard"><p class="ftown">Questions before opening?</p>'
         '<p><a class="btn ghost dark" href="/contact">Send a note</a></p>'
         '<p class="small">Replies come while the shop is open, Wed&ndash;Sun.</p></div></div></section>']
    # balance: wrap-half opens ONE div; closes = infocard, half, section = 3 divs + section.

    ld = [webpage(h1.replace("&amp;", "&"), "/visit", d, about={"@id": ORIGIN + "/#store"}),
          {"@type": "Organization", "@id": ORIGIN + "/#store", "name": NAME},
          breadcrumb([("Home", "/"), ("Visit", "/visit")], "/visit")]
    PAGE("/visit", h1, d, "\n".join(b), ld)

def contact():
    h1 = "Contact Wild Aster Boutique — Downtown Irvington, Indianapolis"
    d = ("Contact Wild Aster Boutique, the size-inclusive clothing shop opening Nov 28, 2026 in downtown Irvington, Indianapolis. "
         "Email hello@shopsaltandash.com or use the contact form.")
    b = ['<section class="pagehero"><div class="wrap"><p class="eyebrow">Contact</p>'
         '<h1>Say hello <em>before the doors open</em></h1>'
         '<p class="lede">Questions, brand suggestions, or you want to be first through the door on November 28 — write to us.</p></div></section>',
         '<section class="band"><div class="wrap grid formgrid">'
         '<form class="cform" method="post" action="/contact">'
         '<div class="frow"><label for="fn">Your name<input id="fn" name="name" required maxlength="120"></label></div>'
         '<div class="frow"><label for="fp">Phone (optional)<input id="fp" name="phone" type="tel" maxlength="60"></label></div>'
         '<div class="frow"><label for="fe">Email (optional)<input id="fe" name="email" type="email" maxlength="120"></label></div>'
         '<div class="frow"><label for="fm">Message<textarea id="fm" name="message" required maxlength="4000" rows="6"></textarea></label></div>'
         '<button class="btn big" type="submit">Send message</button>'
         '<p class="small">We read every note. Open Wed&ndash;Sun, 11 a.m.&ndash;6 p.m.</p></form>'
         '<div class="infocard"><p class="ftown">Email</p><p class="big"><a href="mailto:' + EMAIL + '">' + EMAIL + '</a></p>'
         '<p class="small">Wild Aster&rsquo;s hello inbox (shared with Salt &amp; Ash Market).</p>'
         '<p class="ftown">Hiring</p><p>Send a resume and cover letter to the same address — a retail sales associate role is open for the Irvington shop.</p>'
         '<p class="ftown">Hours</p><p>Wed&ndash;Sun &middot; 11 a.m.&ndash;6 p.m.<br>Mon &amp; Tue closed</p></div>'
         '</div></section>']
    ld = [webpage(h1.replace("&amp;", "&"), "/contact", d, about={"@id": ORIGIN + "/#store"}),
          {"@type": "Organization", "@id": ORIGIN + "/#store", "name": NAME},
          breadcrumb([("Home", "/"), ("Contact", "/contact")], "/contact")]
    PAGE("/contact", h1, d, "\n".join(b), ld)

def privacy():
    h1 = "Privacy — Wild Aster Boutique, Irvington Indianapolis"
    d = ("Privacy basics for the Wild Aster Boutique website: the contact form is the only data collector here. No trackers, no cookies, and no third-party scripts.")
    b = ['<section class="pagehero"><div class="wrap"><p class="eyebrow">Privacy</p>'
         '<h1>The short, human version</h1></div></section>',
         '<section class="band"><div class="wrap prose">'
         '<p>The contact form is the only thing on this site that collects information. What you type — your name, and optionally a phone number and an email address, '
         'plus your message — is delivered to Wild Aster so the shop can answer you. It is used for nothing else: no lists, no advertising, no resale.</p>'
         '<p>This site loads no trackers, no cookies, and no third-party scripts. The stylesheet and every graphic on it come from this site itself.</p>'
         '<p>Want your message deleted? Email <a href="mailto:' + EMAIL + '">' + EMAIL + '</a> and ask.</p>'
         '<p class="small">Last updated ' + BUILT + '.</p></div></section>']
    ld = [{"@type": "WebPage", "@id": U("/privacy") + "#webpage", "name": "Privacy — Wild Aster Boutique",
           "url": U("/privacy"), "isPartOf": {"@id": ORIGIN + "/#website"}},
          breadcrumb([("Home", "/"), ("Privacy", "/privacy")], "/privacy")]
    PAGE("/privacy", h1, d, "\n".join(b), ld)

def utility():
    h1 = "Page not found — Wild Aster Boutique, Irvington Indianapolis"
    d = "That page isn't here. Find the clothing, the visit details, or the contact form at Wild Aster Boutique, downtown Irvington, Indianapolis."
    b = ['<section class="pagehero"><div class="wrap"><p class="eyebrow">404</p>'
         '<h1>That page wandered off the rack</h1>'
         '<p class="lede">Nothing here — but the shop is. Try one of these:</p>'
         '<p class="ctarow"><a class="btn" href="/">Home</a> <a class="btn ghost dark" href="/clothing">Clothing</a> '
         '<a class="btn ghost dark" href="/visit">Visit</a> <a class="btn ghost dark" href="/contact">Contact</a></p></div></section>']
    PAGE("/404", h1, d, "\n".join(b), [], util=True)
    h2 = "Thank you — your message is on its way — Wild Aster Boutique"
    d2 = ("Thank you — your message reached Wild Aster Boutique, the size-inclusive boutique opening Nov 28, 2026 in downtown Irvington, Indianapolis.")
    b2 = ['<section class="pagehero"><div class="wrap"><p class="eyebrow">Received</p>'
          '<h1>Your note is on its way</h1>'
          '<p class="lede">Thanks for writing. The shop answers messages while it&rsquo;s open — Wednesdays through Sundays, 11 a.m. to 6 p.m.</p>'
          '<p class="ctarow"><a class="btn" href="/">Back to home</a> <a class="btn ghost dark" href="/clothing">See the clothing</a></p>'
          '<p class="small">Opens Saturday, November 28 &middot; Downtown Irvington, Indianapolis</p></div></section>']
    PAGE("/thanks", h2, d2, "\n".join(b2), [], util=True)

# ---------------- css ----------------
CSS = """/* Wild Aster Boutique — hand-rolled stylesheet (websites lane, t_f44ac4fb, 2026-11-22).
   Identity: prairie-aster boutique — Georgia serif display, system-sans body copy,
   cream paper, deep-plum ink, aster-violet + goldenrod accents, dashed petal rings.
   No frameworks, no webfonts, no JS. */
:root{
  --serif:Georgia,"Times New Roman",serif;
  --sans:ui-sans-serif,system-ui,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
  --ink:#2b1e2e; --ink2:#453148; --paper:#f7f1e4; --paper2:#efe6d3;
  --aster:#7c56a8; --aster-d:#5a3a7d; --gold:#c0862f; --rose:#c28ba0; --sage:#7d8b6a;
  --line:#d9cdb6; --band:#f1e8d6;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);font-size:17px;line-height:1.66;-webkit-text-size-adjust:100%}
img{max-width:100%}
h1,h2,h3,address{font-family:var(--serif);font-weight:700;color:var(--ink);letter-spacing:-.01em}
h1{font-size:clamp(34px,5.4vw,56px);line-height:1.08;margin:0 0 18px}
h1 em{font-style:italic;color:var(--aster-d)}
h2{font-size:clamp(24px,3.4vw,32px);line-height:1.15;margin:0 0 18px}
h3{font-size:20px;margin:0 0 8px}
address{font-style:normal}
p{margin:0 0 16px}
a{color:var(--aster-d)}
::selection{background:var(--aster);color:#fff}
.wrap{max-width:1060px;margin:0 auto;padding:0 22px}
.center{text-align:center}
.small{font-size:14.5px;color:var(--ink2)}
.eyebrow{font-size:12.5px;font-weight:700;letter-spacing:.22em;text-transform:uppercase;color:var(--aster-d);margin:0 0 10px}
.big{font-family:var(--serif);font-size:clamp(22px,3vw,30px);line-height:1.25;color:var(--ink)}

.skip{position:absolute;left:-9999px}
.skip:focus{left:12px;top:12px;background:var(--gold);color:#fff;padding:8px 14px;font-size:12px;letter-spacing:.12em;text-transform:uppercase;z-index:9}

/* ---------- header ---------- */
header.site{background:var(--ink);color:var(--paper)}
.hdr{display:flex;align-items:center;gap:20px;flex-wrap:wrap;padding-top:14px;padding-bottom:14px}
.wm{display:inline-flex;align-items:center;gap:10px;color:var(--paper);text-decoration:none;font-family:var(--serif);font-weight:700;font-size:21px;letter-spacing:.01em}
.wm em{font-style:italic;color:var(--gold)}
.stamp{width:30px;height:30px;color:var(--aster);flex:none}
header.site nav{margin-left:auto}
header.site nav ul{display:flex;align-items:center;gap:20px;list-style:none;margin:0;padding:0;flex-wrap:wrap}
header.site nav a{color:var(--paper);text-decoration:none;font-size:14.5px;font-weight:600;letter-spacing:.04em}
header.site nav a:hover{color:var(--gold)}
.btn{display:inline-block;background:var(--aster-d);color:#fff!important;text-decoration:none;font-weight:700;font-size:15px;letter-spacing:.03em;padding:12px 22px;border-radius:999px;border:0;cursor:pointer}
.btn:hover{background:var(--aster)}
.btn.pill{padding:9px 18px;background:var(--gold)}
.btn.pill:hover{background:#d69c3e}
.btn.ghost{background:transparent;color:var(--aster-d)!important;border:2px solid var(--aster)}
.btn.ghost:hover{background:var(--aster);color:#fff!important}
.btn.ghost.dark{color:var(--ink)!important;border-color:var(--ink)}
.btn.ghost.dark:hover{background:var(--ink);color:#fff!important;border-color:var(--ink)}
.btn.big{font-size:17px;padding:14px 30px}
.btn.big + .small{margin-top:12px}
.ctarow{display:flex;gap:14px;flex-wrap:wrap;align-items:center;margin:22px 0 0}

/* ---------- hero ---------- */
.hero{background:linear-gradient(160deg,var(--paper) 55%,var(--band) 100%);border-bottom:1px solid var(--line);position:relative;overflow:hidden}
.heroinner{padding:44px 22px 8px;max-width:1060px}
.ribbon{display:inline-block;background:var(--ink);color:var(--paper);font-size:13px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;padding:7px 16px;border-radius:999px;margin:0 0 20px}
.lede{font-size:clamp(17px,2.2vw,20px);line-height:1.6;max-width:640px;color:var(--ink2)}
.heroartwrap{position:relative;display:flex;justify-content:flex-end;padding:0 22px 30px;max-width:1060px;margin:0 auto}
.heroart{width:min(420px,100%);height:auto;display:block;margin-top:-6px}
.chips{display:flex;gap:10px;flex-wrap:wrap;list-style:none;margin:26px 0 34px;padding:0}
.chips li{border:1.5px solid var(--aster);border-radius:8px;padding:8px 14px;font-size:13.5px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:var(--ink2)}
.chips b{color:var(--aster-d)}

/* ---------- bands ---------- */
.band{padding:56px 0;border-bottom:1px solid var(--line)}
.band.soft{background:var(--band)}
.band.ink{background:var(--ink);color:var(--paper);border-bottom:0}
.band.ink h2,.band.ink h3,.band.ink blockquote,.band.ink .big{color:var(--paper)}
.band.ink .eyebrow{color:var(--gold)}
.band.ink a{color:var(--gold)}
.band.cta{background:linear-gradient(150deg,var(--aster-d),var(--aster));border-bottom:0}
.band.cta h2,.band.cta p{color:#fff}
.band.cta .btn{background:var(--gold);color:#241826!important}
.band.cta .btn:hover{background:var(--gold);filter:brightness(1.1)}
.band.cta .btn.ghost.dark{color:#fff!important;border-color:#fff}
.band.cta .btn.ghost.dark:hover{background:#fff;color:var(--aster-d)!important}
.grid{display:grid;gap:20px}
.cards{grid-template-columns:repeat(auto-fit,minmax(230px,1fr));margin-top:8px}
.card{background:#fffdf7;border:1px solid var(--line);border-radius:14px;padding:22px}
.band.ink .card{background:rgba(255,255,255,.06);border-color:rgba(247,241,228,.25)}
.card.tall{padding:28px}
.half{display:grid;grid-template-columns:1.25fr .9fr;gap:40px;align-items:start}
.infocard{background:#fffdf7;border:1px dashed var(--aster);border-radius:14px;padding:22px}
.ftown{font-size:12px;font-weight:700;letter-spacing:.18em;text-transform:uppercase;color:var(--aster-d);margin:0 0 6px}
.band.ink .ftown{color:var(--gold)}
.prose{max-width:740px}
.prose p{margin-bottom:18px}
blockquote{font-family:var(--serif);font-size:clamp(20px,2.6vw,26px);line-height:1.45;color:var(--aster-d);border-left:3px solid var(--gold);padding:2px 0 2px 20px;margin:0 0 14px}
.band.ink blockquote{color:var(--paper)}
.attrib{font-size:14px;color:var(--ink2)}
.hoursgrid{grid-template-columns:1fr 1fr}
.hours{width:100%;border-collapse:collapse;font-size:16px}
.hours td{padding:7px 2px;border-bottom:1px dotted var(--line)}
.hours td:last-child{text-align:right;font-weight:700;color:var(--aster-d)}
.hours .closed td{color:var(--ink2);font-weight:400;border-bottom:0}
.twocards{grid-template-columns:1fr 1fr}

/* ---------- faq ---------- */
.faqwrap .faq{max-width:740px;border-top:1px solid var(--line)}
.faq details{border-bottom:1px solid var(--line)}
.faq summary{cursor:pointer;padding:16px 26px 16px 2px;font-family:var(--serif);font-size:19px;font-weight:700;list-style:none;position:relative}
.faq summary::-webkit-details-marker{display:none}
.faq summary:after{content:"+";position:absolute;right:4px;top:14px;color:var(--aster-d);font-size:22px}
.faq details[open] summary:after{content:"–"}
.faq details p{margin:0 0 18px;color:var(--ink2)}

/* ---------- page heroes ---------- */
.pagehero{padding:44px 0 34px;border-bottom:1px solid var(--line);background:linear-gradient(160deg,var(--paper) 60%,var(--band) 100%)}

/* ---------- form ---------- */
.formgrid{grid-template-columns:1.2fr .8fr;align-items:start}
.cform .frow{margin:0 0 14px}
.cform label{display:flex;flex-direction:column;gap:6px;font-weight:700;font-size:14.5px;letter-spacing:.02em;color:var(--ink)}
.cform input,.cform textarea{font:inherit;font-family:var(--sans);font-size:16px;padding:11px 14px;border:1.5px solid var(--line);border-radius:10px;background:#fffdf7;color:var(--ink);width:100%}
.cform input:focus,.cform textarea:focus{outline:2px solid var(--aster);border-color:var(--aster)}
.cform .btn{margin-top:6px}

/* ---------- footer ---------- */
footer.site{background:var(--ink);color:var(--paper);padding:44px 0 26px;font-size:15px}
.foottop{display:grid;grid-template-columns:1.3fr 1fr 1fr;gap:36px}
.fbrand{display:flex;align-items:center;gap:10px;font-family:var(--serif);font-size:20px;font-weight:700;color:var(--paper);margin:0 0 8px}
.fbrand .stamp{color:var(--gold)}
.fbrand em{font-style:italic;color:var(--gold)}
.ftag{color:#cbb7d3;margin:0 0 18px}
.fnaps .ftown{margin-top:2px}
.fnaps p{margin:0 0 8px;color:var(--paper)}
.fnaps address{margin:0 0 8px}
.fnaps a{color:var(--gold)}
footer.site nav ul{list-style:none;margin:0;padding:0;columns:2;gap:0 14px}
footer.site nav a{color:var(--paper);text-decoration:none}
footer.site nav a:hover{color:var(--gold)}
.fpress{margin:0;color:#cbb7d3}
.fpress a{color:var(--gold)}
.footline{border-top:1px solid rgba(247,241,228,.22);margin:34px 0 0;padding-top:18px;font-size:13.5px;color:#bfa8c8;text-align:center}

/* ---------- responsive ---------- */
@media (max-width:880px){
  .half,.formgrid,.hoursgrid,.twocards{grid-template-columns:1fr}
  .foottop{grid-template-columns:1fr 1fr}
  .fpress{grid-column:1/-1}
  .heroartwrap{justify-content:center;padding-top:6px}
  .heroinner{padding-bottom:0}
}
@media (max-width:640px){
  .foottop{grid-template-columns:1fr}
  header.site nav{margin-left:0}
  header.site nav ul{gap:14px}
  .band{padding:40px 0}
  .heroart{width:min(320px,100%)}
}
"""

def main():
    os.makedirs(PUBLIC, exist_ok=True)
    home(); clothing(); brands(); about(); visit(); contact(); privacy(); utility()
    open(os.path.join(PUBLIC, "style.css"), "w", encoding="utf-8").write(CSS)

    pages = ["/", "/clothing", "/local-brands", "/about", "/visit", "/contact", "/privacy"]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for p in pages:
        sm.append(f'<url><loc>{U(p)}</loc><lastmod>{BUILT}</lastmod></url>')
    sm.append("</urlset>\n")
    open(os.path.join(PUBLIC, "sitemap.xml"), "w", encoding="utf-8").write("\n".join(sm))
    open(os.path.join(PUBLIC, "robots.txt"), "w", encoding="utf-8").write(
        "User-agent: *\nDisallow: /thanks\nDisallow: /404\n\nSitemap: " + ORIGIN + "/sitemap.xml\n")

    fav = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
           '<g fill="#7c56a8">' + PETALS + '</g><circle cx="12" cy="12" r="2.7" fill="#c0862f"/></svg>\n')
    open(os.path.join(PUBLIC, "favicon.svg"), "w", encoding="utf-8").write(fav)

    # canonical 1x1 transparent pixel (open-tracking); copy proven bytes if a sibling tree exists
    src = "/Users/rleon/sites/noodle-house-rochester/public/pixel.gif"
    if os.path.exists(src): shutil.copyfile(src, os.path.join(PUBLIC, "pixel.gif"))
    else: open(os.path.join(PUBLIC, "pixel.gif"), "wb").write(bytes.fromhex(
        "4749463839610100010080000000000021f90401000001002c000000000100010000080400"))

    # og share-card art (1200x630) — rendered to og.png via browser capture
    og = ('<!DOCTYPE html>\n<html lang="en"><head><meta charset="utf-8">\n<title>og-src</title>\n<style>\n'
          '  html,body{margin:0;padding:0}\n'
          '  .c{width:1200px;height:630px;background:#2b1e2e;position:relative;overflow:hidden;'
          'font-family:Georgia,"Times New Roman",serif;color:#f7f1e4}\n'
          '  .glow{position:absolute;width:1000px;height:1000px;border-radius:50%;right:-300px;top:-430px;'
          'background:radial-gradient(closest-side,rgba(124,86,168,.55),transparent 70%)}\n'
          '  .glow2{position:absolute;width:700px;height:700px;border-radius:50%;left:-330px;bottom:-430px;'
          'background:radial-gradient(closest-side,rgba(192,134,47,.30),transparent 70%)}\n'
          '  .inner{position:absolute;left:84px;top:118px;right:430px}\n'
          '  .eyebrow{font-family:ui-sans-serif,system-ui,"Segoe UI",Roboto,sans-serif;font-size:17px;font-weight:700;'
          'letter-spacing:.3em;text-transform:uppercase;color:#e4b95f;margin:0 0 22px}\n'
          '  h1{font-size:104px;line-height:1.02;margin:0 0 24px;letter-spacing:-.015em;font-weight:700}\n'
          '  h1 em{font-style:italic;color:#e4b95f}\n'
          '  .chips{display:flex;gap:12px;margin:0 0 26px;font-family:ui-sans-serif,system-ui,sans-serif}\n'
          '  .chip{border:1.5px solid #9c74bd;border-radius:8px;color:#dfcbe9;font-size:17px;font-weight:700;'
          'letter-spacing:.08em;text-transform:uppercase;padding:9px 15px}\n'
          '  .sub{font-size:27px;line-height:1.45;color:#e8d9f0;max-width:640px;margin:0 0 26px}\n'
          '  .facts{font-family:ui-sans-serif,system-ui,sans-serif;font-size:18px;letter-spacing:.14em;'
          'text-transform:uppercase;color:#c9b3d4;margin:0}\n'
          '  .art{position:absolute;right:64px;top:120px;width:380px}\n'
          '</style></head><body><div class="c">\n'
          '  <div class="glow"></div><div class="glow2"></div>\n'
          '  <div class="inner">\n'
          '    <p class="eyebrow">Opens Nov 28 &middot; Small Business Saturday &middot; Irvington</p>\n'
          '    <h1>Wild Aster <em>Boutique</em></h1>\n'
          '    <div class="chips"><span class="chip">Sizes S–3XL</span><span class="chip">Under $100</span><span class="chip">Woman-owned</span></div>\n'
          '    <p class="sub">Size-inclusive clothing &amp; locally made accessories, opening in the old Josephine&rsquo;s storefront, downtown Irvington, Indianapolis.</p>\n'
          '    <p class="facts">Wed–Sun 11–6 &middot; sweaters &middot; occasion dresses &middot; local accessories</p>\n'
          '  </div>\n'
          '  <svg class="art" viewBox="0 0 420 420" aria-hidden="true"><defs><path id="pet" d="M0-58C11-41 11-15 0 0-11-15-11-41 0-58Z"/></defs>\n'
          '    <circle cx="210" cy="210" r="170" fill="none" stroke="#9c74bd" stroke-width="1.6" stroke-dasharray="4 8" opacity=".6"/>\n'
          '    <g transform="translate(210 210)"><g fill="#b48ad6">'
          + "".join(f'<use href="#pet" transform="rotate({d}) translate(0 -64) scale(1.35)"/>' for d in range(0, 360, 24)) +
          '</g><g fill="#d99bc0" transform="rotate(15) scale(.9)">'
          + "".join(f'<use href="#pet" transform="rotate({d}) translate(0 -64) scale(1.1)"/>' for d in range(0, 360, 30)) +
          '</g><circle r="44" fill="#e4b95f"/><circle r="44" fill="none" stroke="#2b1e2e" stroke-width="2" opacity=".5"/></g></svg>\n'
          '</div></body></html>\n')
    open(os.path.join(HERE, "og-src.html"), "w", encoding="utf-8").write(og)
    print("pages:", [f for f in sorted(os.listdir(PUBLIC))])

main()
