"""Builds the house cleaning site. Run: python _src/build.py

All business facts come from _src/site.json. Copy lives in _src/content.py.
The house illustration comes from _src/scene.py.
"""
import datetime
import hashlib
import html
import json
import math
import os
import shutil

import content as C
import scene

SRC = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SRC)
S = json.load(open(os.path.join(SRC, "site.json"), encoding="utf-8"))
P = S["pricing"]
BASE = S["base_url"]
TODAY = datetime.date.today().isoformat()
CITY = S["home_city"]
NAME = S["name"]
BIZ_ID = BASE + "#business"
PAGES = []  # (url path, priority) for the sitemap


def esc(t):
    return html.escape(str(t), quote=True)


def ver(rel):
    with open(os.path.join(ROOT, rel), "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()[:8]


ICONS = {}


def icon(name):
    if name not in ICONS:
        svg = open(os.path.join(ROOT, "assets", "icons", name + ".svg"), encoding="utf-8").read().strip()
        ICONS[name] = svg.replace("<svg ", '<svg class="i" aria-hidden="true" focusable="false" ', 1)
    return ICONS[name]


# ------------------------------------------------------------------ pricing
def rnd(x, step):
    return math.floor(x / step + 0.5) * step


def estimate(kind="standard", beds=3, full=2, half=0, sqft=1800, cond="kept", pets=False, freq="once", addons=()):
    """Same math as assets/quote.js. Keep them in step."""
    sub = P["base"] + beds * P["per_bedroom"] + full * P["per_full_bath"] + half * P["per_half_bath"]
    sub += max(0, sqft - P["sqft_included"]) * P["per_extra_sqft"]
    sub *= P["types"][kind]["mult"] * P["conditions"][cond]["mult"]
    if pets:
        sub += P["pets"]
    add = sum(a["price"] for a in P["addons"] if a["id"] in addons and kind not in a["included"])
    total = sub + add
    disc = P["frequencies"][freq]["discount"] if kind == "standard" else 0
    est = max(P["min_price"], total * (1 - disc))
    hours = est / P["rate_per_cleaner_hour"]
    return {
        "lo": rnd(est * P["range_low"], P["round_to"]),
        "hi": rnd(est * P["range_high"], P["round_to"]),
        "hours": max(1.5, math.floor(hours * 2 + 0.5) / 2),
        "team_hours": max(1, math.floor(hours / P["team_size"] * 2 + 0.5) / 2),
    }


def hrs(h):
    return ("%g" % h)


HOMES = [
    ("1 bed, 1 bath", "about 800 sq ft", 1, 1, 0, 800),
    ("2 beds, 1 bath", "about 1,100 sq ft", 2, 1, 0, 1100),
    ("3 beds, 2 baths", "about 1,800 sq ft", 3, 2, 0, 1800),
    ("4 beds, 2.5 baths", "about 2,600 sq ft", 4, 2, 1, 2600),
    ("5 beds, 3.5 baths", "about 3,600 sq ft", 5, 3, 1, 3600),
]

E3 = {k: estimate(k) for k in P["types"]}
B3 = estimate("standard", freq="biweekly")
ADDON = {a["id"]: a["price"] for a in P["addons"]}

FMT = {
    "city": CITY,
    "lo3": E3["standard"]["lo"], "hi3": E3["standard"]["hi"],
    "dlo3": E3["deep"]["lo"], "dhi3": E3["deep"]["hi"],
    "blo3": B3["lo"], "bhi3": B3["hi"],
    "team_hours3": hrs(E3["deep"]["team_hours"]),
    "team_hours_std3": hrs(E3["standard"]["team_hours"]),
    "oven": ADDON["oven"], "fridge": ADDON["fridge"], "basement": ADDON["basement"],
    "keys": S["policies"]["keys"], "payment": S["policies"]["payment"], "cancel": S["policies"]["cancel"],
}


def fill(t, extra=None):
    d = dict(FMT)
    if extra:
        d.update(extra)
    return t.format(**d)


def money(lo, hi):
    return f"${lo:,} to ${hi:,}"


# ------------------------------------------------------------------ schema
def hours_spec():
    return [{"@type": "OpeningHoursSpecification", "dayOfWeek": h["schema"], "opens": h["open"], "closes": h["close"]} for h in S["hours"]]


def business_schema():
    return {
        "@type": "LocalBusiness",
        "@id": BIZ_ID,
        "name": NAME,
        "description": f"House cleaning company based in {CITY}, {S['state_name']}. Standard, deep, move-in/move-out and recurring cleaning with online pricing and booking.",
        "url": BASE,
        "telephone": "+1-" + S["phone"][:3] + "-" + S["phone"][3:6] + "-" + S["phone"][6:],
        "email": S["email"],
        "image": BASE + "assets/img/og.png",
        "logo": BASE + "assets/img/icon-512.png",
        "priceRange": f"${E3['standard']['lo']}-${estimate('move', 5, 3, 1, 3600)['hi']}",
        "currenciesAccepted": "USD",
        "address": {"@type": "PostalAddress", "addressLocality": CITY, "addressRegion": S["state"], "postalCode": S["home_zip"], "addressCountry": "US"},
        "areaServed": [{"@type": "City", "name": f"{t['name']}, {S['state']}"} for t in S["towns"]],
        "openingHoursSpecification": hours_spec(),
        "knowsAbout": ["House cleaning", "Deep cleaning", "Move-out cleaning", "Recurring house cleaning"],
        "hasOfferCatalog": {
            "@type": "OfferCatalog",
            "name": "House cleaning services",
            "itemListElement": [
                {"@type": "Offer", "itemOffered": {"@type": "Service", "name": s["name"], "url": BASE + "services/" + s["slug"] + "/"},
                 "priceSpecification": {"@type": "PriceSpecification", "price": estimate(s["type"], freq="biweekly" if s.get("recurring") else "once")["lo"], "priceCurrency": "USD",
                                        "description": "Starting price for a 3-bedroom, 2-bath home of about 1,800 sq ft"}}
                for s in C.SERVICES
            ],
        },
        **({"sameAs": S["same_as"]} if S["same_as"] else {}),
    }


def crumbs_schema(crumbs):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": BASE + u} for i, (n, u) in enumerate(crumbs)]}


def faq_schema(faqs):
    return {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}


# ------------------------------------------------------------------ shell
NAV = [("Services", "services/"), ("Pricing", "pricing/"), ("Checklist", "checklist/"), ("Areas", "areas/"), ("FAQ", "faq/")]


def header(pre, current):
    links = "".join(
        f'<a href="{pre}{u}"{" aria-current=\"page\"" if current == u else ""}>{n}</a>' for n, u in NAV)
    return f"""<header class="head" id="top">
  <div class="wrap head-in">
    <a class="brand" href="{pre or './'}" aria-label="{esc(NAME)} home">{icon('house')}<span>{esc(NAME)}</span></a>
    <nav class="nav" id="nav" aria-label="Main">{links}<a class="nav-tel" href="tel:+1{S['phone']}">{icon('phone')}{S['phone_show']}</a></nav>
    <a class="head-tel" href="tel:+1{S['phone']}" aria-label="Call {S['phone_show']}">{icon('phone')}<span>{S['phone_show']}</span></a>
    <a class="btn btn-go btn-sm head-cta" href="{pre}quote/">Get my price</a>
    <button class="menu-btn" type="button" aria-expanded="false" aria-controls="nav"><span class="menu-open">{icon('list')}</span><span class="menu-close">{icon('x')}</span><span class="sr">Menu</span></button>
  </div>
</header>"""


def footer(pre):
    hours = "".join(f"<li>{esc(h['days'])}: {esc(h['show'])}</li>" for h in S["hours"])
    svc = "".join(f'<li><a href="{pre}services/{s["slug"]}/">{esc(s["name"])}</a></li>' for s in C.SERVICES)
    towns = "".join(f'<li><a href="{pre}areas/{t["slug"]}/">{esc(t["name"])}</a></li>' for t in S["towns"])
    note = ('<p class="foot-note">Preview build. The business name, phone, email, prices and service area are placeholders.</p>'
            if S["preview"] else "")
    return f"""<footer class="foot">
  <div class="wrap foot-grid">
    <div class="foot-biz">
      <a class="brand" href="{pre or './'}">{icon('house')}<span>{esc(NAME)}</span></a>
      <p>House cleaning in {esc(CITY)}, {esc(S['state'])} and nearby suburbs.</p>
      <p><a href="tel:+1{S['phone']}">{S['phone_show']}</a><br><a href="mailto:{S['email']}">{esc(S['email'])}</a></p>
      <ul class="plain">{hours}</ul>
    </div>
    <div><h2>Services</h2><ul class="plain">{svc}<li><a href="{pre}pricing/">Pricing</a></li><li><a href="{pre}checklist/">Cleaning checklist</a></li></ul></div>
    <div><h2>Areas</h2><ul class="plain cols2">{towns}</ul></div>
    <div><h2>Company</h2><ul class="plain"><li><a href="{pre}about/">About us</a></li><li><a href="{pre}faq/">FAQ</a></li><li><a href="{pre}contact/">Contact</a></li><li><a href="{pre}quote/">Get my price</a></li><li><a href="{pre}privacy/">Privacy</a></li></ul></div>
  </div>
  <div class="wrap foot-base"><p>&copy; {datetime.date.today().year} {esc(NAME)}. {esc(CITY)}, {esc(S['state_name'])}.</p>{note}</div>
</footer>"""


def page(path, title, desc, main, current="", crumbs=None, schema=None, scripts=(), body_class="", priority="0.7", head_extra=""):
    depth = path.count("/")
    pre = "../" * depth
    url = BASE + path.replace("index.html", "")
    graph = [business_schema(), {"@type": "WebSite", "@id": BASE + "#site", "url": BASE, "name": NAME, "publisher": {"@id": BIZ_ID}}]
    if crumbs:
        graph.append(crumbs_schema([("Home", "")] + crumbs))
    graph += schema or []
    ld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":"))
    robots = '<meta name="robots" content="noindex">' if S["preview"] else '<meta name="robots" content="index, follow, max-image-preview:large">'
    full_title = title if NAME in title else f"{title} | {NAME}"
    crumb_html = ""
    if crumbs:
        items = [f'<a href="{pre or "./"}">Home</a>'] + [
            (f'<a href="{pre}{u}">{esc(n)}</a>' if i < len(crumbs) - 1 else f'<span aria-current="page">{esc(n)}</span>')
            for i, (n, u) in enumerate(crumbs)]
        crumb_html = f'<nav class="crumbs wrap" aria-label="Breadcrumb">{" <span aria-hidden=\"true\">/</span> ".join(items)}</nav>'
    js = "".join(f'<script src="{pre}assets/{s}?v={ver("assets/" + s)}" defer></script>' for s in scripts)
    doc = f"""<!doctype html>
<html lang="en-US">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(desc)}">
{robots}
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{esc(NAME)}">
<meta property="og:title" content="{esc(full_title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}assets/img/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#f6f8f7" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0f1a1d" media="(prefers-color-scheme: dark)">
<link rel="icon" href="{pre}assets/img/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{pre}assets/img/icon-180.png">
<link rel="manifest" href="{pre}site.webmanifest">
<link rel="preload" href="{pre}assets/fonts/bricolage.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{pre}assets/fonts/figtree.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{pre}assets/site.css?v={ver('assets/site.css')}">
<script>document.documentElement.classList.add('js');if(!matchMedia('(prefers-reduced-motion: reduce)').matches)document.documentElement.classList.add('motion')</script>
<script type="application/ld+json">{ld}</script>
{head_extra}</head>
<body class="{body_class}">
<a class="skip" href="#main">Skip to content</a>
{header(pre, current)}
{crumb_html}
<main id="main">
{main.replace("{pre}", pre)}
</main>
{footer(pre)}
<script src="{pre}assets/site.js?v={ver('assets/site.js')}" defer></script>
{js}
</body>
</html>
"""
    out = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(doc)
    if path != "404.html":
        PAGES.append((path.replace("index.html", ""), priority))


# ------------------------------------------------------------------ blocks
def faq_block(faqs, heading="Questions people ask", hid="faq-h", more=""):
    items = "".join(
        f'<details class="qa"><summary><span>{esc(q)}</span>{icon("caret-down")}</summary><p>{esc(a)}</p></details>' for q, a in faqs)
    return f'<section class="sec faq" aria-labelledby="{hid}"><div class="wrap narrow"><h2 id="{hid}">{heading}</h2><div class="qa-list">{items}</div>{more}</div></section>'


def price_table(kinds=("standard", "deep", "move"), freq=None, caption=""):
    heads = "".join(f'<th scope="col">{esc(P["types"][k]["label"])}</th>' for k in kinds) if not freq else "".join(
        f'<th scope="col">{esc(P["frequencies"][fq]["label"])}</th>' for fq in freq)
    rows = ""
    for label, size, b, fb, hb, sq in HOMES:
        if freq:
            cells = "".join(f"<td>{money(**{k: v for k, v in estimate('standard', b, fb, hb, sq, freq=fq).items() if k in ('lo', 'hi')})}</td>" for fq in freq)
        else:
            cells = "".join(f"<td>{money(**{k: v for k, v in estimate(k2, b, fb, hb, sq).items() if k in ('lo', 'hi')})}</td>" for k2 in kinds)
        rows += f'<tr><th scope="row">{label}<small>{size}</small></th>{cells}</tr>'
    cap = f"<caption>{esc(caption)}</caption>" if caption else ""
    return f'<div class="tbl-wrap"><table class="tbl">{cap}<thead><tr><th scope="col">Home</th>{heads}</tr></thead><tbody>{rows}</tbody></table></div>'


def crop_img(name, pre="{pre}", cls="crop", lazy=True):
    alt = scene.CROPS[name][1]
    vb = scene.CROPS[name][0]
    return f'<img class="{cls}" src="{pre}assets/img/room-{name}.svg" width="{vb[2]}" height="{vb[3]}" alt="{esc(alt)}"{" loading=\"lazy\"" if lazy else ""} decoding="async">'


def cta_band(text="Get your price in about a minute"):
    return f"""<section class="band" aria-labelledby="band-h"><div class="wrap band-in">
<h2 id="band-h">{esc(text)}</h2>
<div class="band-act"><a class="btn btn-dark" href="{{pre}}quote/">Get my price</a><a class="band-tel" href="tel:+1{S['phone']}">or call {S['phone_show']}</a></div>
</div></section>"""


def checks_for(flag):
    out = ""
    for key, room, tasks in C.CHECKLIST:
        li = "".join(f"<li>{icon('check')}{esc(t)}</li>" for t, fl in tasks if flag in fl)
        out += f'<div class="inc-room"><h3>{esc(room)}</h3><ul class="ticks">{li}</ul></div>'
    return f'<div class="inc-grid">{out}</div>'


def not_included():
    return '<ul class="nots">' + "".join(f"<li>{icon('x')}{esc(t)}</li>" for t in C.NOT_INCLUDED) + "</ul>"


def promise_strip():
    items = "".join(
        f'<li>{icon(p["icon"])}<div><h3>{esc(p["title"])}</h3><p>{esc(p["text"])}</p></div></li>' for p in S["promises"])
    return f'<section class="promises" aria-label="What you can count on"><ul class="wrap promise-list">{items}</ul></section>'


def town_list(pre="{pre}"):
    return '<ul class="towns">' + "".join(
        f'<li><a href="{pre}areas/{t["slug"]}/"><span>{esc(t["name"])}</span><small>{esc(", ".join(t["zips"]))}</small></a></li>' for t in S["towns"]) + "</ul>"


def map_frame(q):
    return (f'<iframe class="map" title="Map of {esc(q)}" loading="lazy" referrerpolicy="no-referrer-when-downgrade" '
            f'src="https://www.google.com/maps?q={esc(q.replace(" ", "+"))}&amp;z=10&amp;output=embed"></iframe>')


# ------------------------------------------------------------------ home
def build_home():
    e3 = E3["standard"]
    steps = [
        ("hero", f"""<h1>House cleaning in {esc(CITY)} and nearby suburbs</h1>
<p class="lede">See your price in about a minute, then book a time that suits you. We bring the supplies.</p>
<div class="acts"><a class="btn btn-go" href="quote/">Get my price</a><a class="btn btn-line" href="tel:+1{S['phone']}">{icon('phone')}Call {S['phone_show']}</a></div>"""),
        ("kitchen", '<h2>Kitchen</h2><p>We degrease the stovetop and backsplash, scrub the sink, wipe the counters and appliance fronts, then mop the floor.</p>'),
        ("bath", '<h2>Bathrooms</h2><p>We scrub the tub, shower and toilet inside and out, clean the mirror and mop the floor on the way out.</p>'),
        ("bed", '<h2>Bedrooms</h2><p>We dust nightstands, dressers and fan blades, make the beds, and vacuum along the edges where dust collects.</p>'),
        ("living", '<h2>Living room and floors</h2><p>Winter brings road salt and slush through the front door. We clean the entry, vacuum the couch, dust the shelves and mop the hard floors.</p>'),
        ("done", f"""<h2>That was a standard clean</h2>
<p>For a 3-bedroom, 2-bath home of about 1,800 square feet, it costs {money(e3['lo'], e3['hi'])}. A team of two finishes in about {hrs(e3['team_hours'])} hours.</p>
<div class="acts"><a class="btn btn-go" href="quote/">Get my price</a></div>"""),
    ]
    step_html = "".join(f'<div class="step" data-step="{i}" id="step-{k}">{h}</div>' for i, (k, h) in enumerate(steps))
    story = f"""<section class="story" id="story" aria-label="A house getting cleaned room by room">
<div class="stage">
  <div class="wrap stage-in">
    <div class="steps">{step_html}</div>
    <div class="scene" id="scene">{scene.scene(True)}</div>
  </div>
</div>
</section>"""

    price_rows = ""
    for label, size, b, fb, hb, sq in HOMES[1:4]:
        s_, d_ = estimate("standard", b, fb, hb, sq), estimate("deep", b, fb, hb, sq)
        price_rows += f'<tr><th scope="row">{label}<small>{size}</small></th><td>{money(s_["lo"], s_["hi"])}</td><td>{money(d_["lo"], d_["hi"])}</td></tr>'
    prices = f"""<section class="sec prices" aria-labelledby="prices-h"><div class="wrap prices-in">
<div class="prices-copy">
  <h2 id="prices-h">What house cleaning costs here</h2>
  <p>These are our prices for {esc(CITY)} and the towns around it, before add-ons. Booking every two weeks takes 15% off a standard clean.</p>
  <div class="acts"><a class="btn btn-go" href="quote/">Get my price</a><a class="txt-link" href="pricing/">How we set prices {icon('arrow-right')}</a></div>
</div>
<div class="tbl-wrap"><table class="tbl"><thead><tr><th scope="col">Home</th><th scope="col">Standard</th><th scope="col">Deep</th></tr></thead><tbody>{price_rows}</tbody></table></div>
</div></section>"""

    cells = ""
    for i, s in enumerate(C.SERVICES):
        e = estimate(s["type"], freq="biweekly" if s.get("recurring") else "once")
        cells += f"""<a class="svc svc-{i}" href="services/{s['slug']}/">
{crop_img(s['crop'], '')}
<div class="svc-txt"><h3>{esc(s['name'])}</h3><p>{esc(s['card'])}</p><span class="from">From ${e['lo']:,} for a 3-bed, 2-bath home{' per visit' if s.get('recurring') else ''}</span></div></a>"""
    services = f'<section class="sec" aria-labelledby="svc-h"><div class="wrap"><h2 id="svc-h">Cleaning services</h2><div class="svc-grid">{cells}</div></div></section>'

    how = f"""<section class="sec how" aria-labelledby="how-h"><div class="wrap">
<h2 id="how-h" class="big">Price it, book it, come home to a clean house.</h2>
<ol class="how-list">
<li><h3>{icon('calculator')}Price it</h3><p>Tell us about your home. The price updates as you answer.</p></li>
<li><h3>{icon('calendar-blank')}Book it</h3><p>Pick a day and an arrival window. We confirm and text you the day before.</p></li>
<li><h3>{icon('broom')}We clean</h3><p>The team shows up in your window with everything they need. You don't have to be home.</p></li>
</ol></div></section>"""

    tabs = ""
    panels = ""
    for i, (key, room, tasks) in enumerate(C.CHECKLIST):
        sel = "true" if i == 0 else "false"
        tabs += f'<button type="button" role="tab" id="tab-{key}" aria-controls="panel-{key}" aria-selected="{sel}"{"" if i == 0 else " tabindex=\"-1\""}>{esc(room)}</button>'
        std = "".join(f"<li>{icon('check')}{esc(t)}</li>" for t, fl in tasks if "S" in fl)
        deep = [t for t, fl in tasks if fl.startswith("D")]
        deep_txt = f'<p class="adds"><strong>A deep clean adds:</strong> {esc("; ".join(t[0].lower() + t[1:] for t in deep))}.</p>' if deep else ""
        panels += f'<div class="tab-panel" role="tabpanel" id="panel-{key}" aria-labelledby="tab-{key}"{"" if i == 0 else " hidden"}><ul class="ticks">{std}</ul>{deep_txt}</div>'
    checklist = f"""<section class="sec rooms" aria-labelledby="rooms-h"><div class="wrap rooms-in">
<div><h2 id="rooms-h">What we clean in each room</h2><p>Here's what a standard clean covers in each room. The full checklist compares standard, deep and move cleans side by side.</p><a class="txt-link" href="checklist/">See the full checklist {icon('arrow-right')}</a></div>
<div class="tabs" data-tabs><div class="tab-row" role="tablist" aria-label="Rooms">{tabs}</div>{panels}</div>
</div></section>"""

    area = f"""<section class="sec area" aria-labelledby="area-h"><div class="wrap area-in">
{map_frame(CITY + ', ' + S['state'])}
<div><h2 id="area-h">Where we clean</h2><p>We're based in {esc(CITY)} and clean homes in these towns. Enter your ZIP code in the price calculator to check yours.</p>{town_list('')}</div>
</div></section>"""

    faqs = [(fill(q), fill(a)) for q, a in C.GENERAL_FAQ[:6]]
    more = '<p class="more-faq"><a class="txt-link" href="faq/">All questions and answers ' + icon('arrow-right') + "</a></p>"
    main = story + promise_strip() + prices + services + how + checklist + area + faq_block(faqs, more=more) + cta_band()
    page("index.html", f"House Cleaning in {CITY}, IL | {NAME}",
         f"House cleaning in {CITY}, Aurora, Wheaton and nearby suburbs. See your price in a minute and book online. Standard cleans from ${E3['standard']['lo']} for a 3-bed, 2-bath home.",
         main, "", None, [faq_schema(faqs)], ["vendor/gsap.min.js", "vendor/ScrollTrigger.min.js", "story.js"], "home", "1.0")


# ------------------------------------------------------------------ services
def build_services():
    cells = ""
    for i, s in enumerate(C.SERVICES):
        e = estimate(s["type"], freq="biweekly" if s.get("recurring") else "once")
        cells += f"""<a class="svc svc-{i}" href="{s['slug']}/">{crop_img(s['crop'], '{pre}')}
<div class="svc-txt"><h2>{esc(s['name'])}</h2><p>{esc(s['card'])}</p><span class="from">From ${e['lo']:,} for a 3-bed, 2-bath home{' per visit' if s.get('recurring') else ''}</span></div></a>"""
    main = f"""<section class="sec page-top"><div class="wrap">
<h1>House cleaning services</h1>
<p class="lede">We offer four kinds of house cleaning in {esc(CITY)} and nearby towns. Each one has a fixed price you can see before you book.</p>
<div class="svc-grid">{cells}</div></div></section>
<section class="sec"><div class="wrap narrow"><h2>Add-ons</h2><p>Add any of these to a cleaning in the price calculator.</p>{addon_table()}</div></section>{cta_band()}"""
    page("services/index.html", f"House Cleaning Services in {CITY}, IL",
         f"Standard, deep, move-in/move-out and recurring house cleaning in {CITY} and nearby suburbs, with prices for each.",
         main, "services/", [("Services", "services/")], [], (), "", "0.8")

    for s in C.SERVICES:
        kind = s["type"]
        e3 = estimate(kind, freq="biweekly" if s.get("recurring") else "once")
        ex = {"from3": e3["lo"], "lo3": E3[kind]["lo"], "hi3": E3[kind]["hi"]}
        faqs = [(fill(q, ex), fill(a, ex)) for q, a in s["faq"]]
        body = "".join(f"<h2>{esc(h)}</h2><p>{esc(fill(t, ex))}</p>" for h, t in s["body"])
        if s.get("recurring"):
            table = price_table(freq=("once", "monthly", "biweekly", "weekly"), caption="Standard clean price per visit")
        else:
            table = price_table((kind,), caption=f"{s['name']} prices")
        e = E3[kind]
        others = "".join(f'<li><a href="../{o["slug"]}/">{esc(o["name"])}</a></li>' for o in C.SERVICES if o is not s)
        main = f"""<section class="sec page-top"><div class="wrap svc-head">
<div><h1>{esc(s['h1'])}</h1><p class="lede">{esc(fill(s['lede'], ex))}</p>
<div class="acts"><a class="btn btn-go" href="{{pre}}quote/?type={kind}{'&amp;freq=biweekly' if s.get('recurring') else ''}">Get my price</a><a class="btn btn-line" href="tel:+1{S['phone']}">{icon('phone')}Call {S['phone_show']}</a></div></div>
{crop_img(s['crop'], '{pre}', 'crop crop-lg', False)}
</div></section>
<section class="sec"><div class="wrap prose-grid">
<div class="prose">{body}
<h2>Prices</h2><p>The price depends on bedrooms, bathrooms and square footage. A team of two spends about {hrs(e['team_hours'])} hours on a 3-bedroom, 2-bath home.</p>{table}
<p class="small">Prices for homes in good shape. Homes that need extra work cost 15% to 30% more. See <a href="{{pre}}pricing/">how we set prices</a>.</p></div>
<aside class="side"><h2>Other services</h2><ul class="plain">{others}</ul><h2>Areas we serve</h2><ul class="plain">{"".join(f'<li><a href="{{pre}}areas/{t["slug"]}/">{esc(t["name"])}</a></li>' for t in S["towns"])}</ul></aside>
</div></section>
<section class="sec tint"><div class="wrap"><h2>What's included</h2>{checks_for(s['flag'])}<h3 class="nots-h">Not included in any cleaning</h3>{not_included()}</div></section>
{faq_block(faqs)}{cta_band()}"""
        svc_schema = {
            "@type": "Service", "name": s["name"], "serviceType": s["name"], "url": BASE + "services/" + s["slug"] + "/",
            "description": fill(s["lede"], ex), "provider": {"@id": BIZ_ID},
            "areaServed": [{"@type": "City", "name": f"{t['name']}, {S['state']}"} for t in S["towns"]],
            "offers": {"@type": "Offer", "priceCurrency": "USD", "price": e3["lo"], "url": BASE + "quote/",
                       "description": "Starting price for a 3-bedroom, 2-bath home of about 1,800 sq ft"},
        }
        page(f"services/{s['slug']}/index.html", fill(s["title"], ex), fill(s["desc"], ex), main, "services/",
             [("Services", "services/"), (s["name"], f"services/{s['slug']}/")], [svc_schema, faq_schema(faqs)], (), "", "0.9")


def addon_table():
    rows = ""
    for a in P["addons"]:
        inc = a["included"]
        note = "Included in " + " and ".join({"deep": "deep", "move": "move"}[k] for k in inc) + " cleans" if inc else ""
        rows += f'<tr><th scope="row">{esc(a["label"])}</th><td>${a["price"]}</td><td>{esc(note)}</td></tr>'
    return f'<div class="tbl-wrap"><table class="tbl"><thead><tr><th scope="col">Add-on</th><th scope="col">Price</th><th scope="col"><span class="sr">Notes</span></th></tr></thead><tbody>{rows}</tbody></table></div>'


# ------------------------------------------------------------------ pricing
def build_pricing():
    t = P["types"]
    c = P["conditions"]
    fq = P["frequencies"]
    main = f"""<section class="sec page-top"><div class="wrap narrow">
<h1>House cleaning prices in {esc(CITY)}</h1>
<p class="lede">A standard clean of a 3-bedroom, 2-bath home of about 1,800 square feet costs {money(E3['standard']['lo'], E3['standard']['hi'])}. A deep clean of the same home costs {money(E3['deep']['lo'], E3['deep']['hi'])}, and a move-out clean costs {money(E3['move']['lo'], E3['move']['hi'])}.</p>
<p class="small">Updated <time datetime="{TODAY}">{datetime.date.today().strftime('%B %-d, %Y') if os.name != 'nt' else datetime.date.today().strftime('%B %#d, %Y')}</time>. Same prices in every town we serve.</p>
<div class="acts"><a class="btn btn-go" href="{{pre}}quote/">Get my price</a></div>
</div></section>
<section class="sec"><div class="wrap narrow prose">
<h2>Prices by home size</h2>{price_table(caption='One-time cleaning')}
<h2>How we figure your price</h2>
<p>Every price starts from the same formula, so two homes of the same size pay the same.</p>
<ul class="facts">
<li>${P['base']} to start, plus ${P['per_bedroom']} per bedroom, ${P['per_full_bath']} per full bathroom and ${P['per_half_bath']} per half bathroom.</li>
<li>{round(P['per_extra_sqft'] * 100, 1):g} cents for each square foot over {P['sqft_included']:,}.</li>
<li>A deep clean costs {t['deep']['mult']:g} times a standard clean. A move-in or move-out clean costs {t['move']['mult']:g} times.</li>
<li>Homes that are {esc(c['behind']['label'].lower())} cost {round((c['behind']['mult'] - 1) * 100):g}% more. Homes where {esc(c['while']['label'][0].lower() + c['while']['label'][1:])} cost {round((c['while']['mult'] - 1) * 100):g}% more.</li>
<li>Pets add ${P['pets']} for the extra time on hair.</li>
<li>The smallest cleaning we book is ${P['min_price']}.</li>
</ul>
<h2>Recurring cleaning discounts</h2>
<p>Standard cleans on a schedule cost less per visit: {round(fq['weekly']['discount'] * 100):g}% off weekly, {round(fq['biweekly']['discount'] * 100):g}% off every two weeks and {round(fq['monthly']['discount'] * 100):g}% off every four weeks.</p>
{price_table(freq=('once', 'monthly', 'biweekly', 'weekly'), caption='Standard clean price per visit')}
<h2>Add-ons</h2>{addon_table()}
<h2>Paying and cancelling</h2>
<p>{esc(S['policies']['payment'])}</p><p>{esc(S['policies']['cancel'])}</p>
<h2>What no cleaning includes</h2>{not_included()}
</div></section>{cta_band()}"""
    page("pricing/index.html", f"House Cleaning Prices in {CITY}, IL ({datetime.date.today().year})",
         f"House cleaning prices in {CITY}: standard cleans from {money(E3['standard']['lo'], E3['standard']['hi'])} for a 3-bed, 2-bath home. Full price table, add-ons and recurring discounts.",
         main, "pricing/", [("Pricing", "pricing/")], [], (), "", "0.9")


# ------------------------------------------------------------------ checklist
def build_checklist():
    tables = ""
    for key, room, tasks in C.CHECKLIST:
        rows = ""
        for task, fl in tasks:
            cells = "".join(f'<td>{icon("check") + "<span class=sr>Included</span>" if k in fl else "<span class=dash aria-label=\"Not included\"></span>"}</td>' for k in "SDM")
            rows += f'<tr><th scope="row">{esc(task)}</th>{cells}</tr>'
        tables += f'<h2 id="{key}">{esc(room)}</h2><div class="tbl-wrap"><table class="tbl tbl-check"><thead><tr><th scope="col">Task</th><th scope="col">Standard</th><th scope="col">Deep</th><th scope="col">Move</th></tr></thead><tbody>{rows}</tbody></table></div>'
    jump = " ".join(f'<a href="#{k}">{esc(r)}</a>' for k, r, _ in C.CHECKLIST)
    main = f"""<section class="sec page-top"><div class="wrap narrow">
<h1>House cleaning checklist, room by room</h1>
<p class="lede">This is the list our team works from in every home. A standard clean covers the basics in each room. A deep clean adds baseboards, grout, vents and the range hood. A move clean adds the inside of cabinets, closets, the oven and the fridge.</p>
<p class="jump">Jump to: {jump}</p>
</div></section>
<section class="sec"><div class="wrap narrow prose">{tables}
<h2>Not included in any cleaning</h2>{not_included()}</div></section>{cta_band()}"""
    hp = {"@type": "HowTo", "name": "House cleaning checklist", "step": [
        {"@type": "HowToSection", "name": room, "itemListElement": [{"@type": "HowToStep", "text": t} for t, fl in tasks if "S" in fl]}
        for _, room, tasks in C.CHECKLIST]}
    page("checklist/index.html", "House Cleaning Checklist by Room",
         "Room-by-room house cleaning checklist comparing standard, deep and move-out cleaning in the kitchen, bathrooms, bedrooms and living areas.",
         main, "checklist/", [("Checklist", "checklist/")], [hp], (), "", "0.8")


# ------------------------------------------------------------------ areas
def build_areas():
    counties = sorted({c.strip() for t in S["towns"] for c in t["county"].replace(" and ", ",").split(",")})
    main = f"""<section class="sec page-top"><div class="wrap area-in">
<div><h1>Areas we serve</h1>
<p class="lede">We clean homes in {len(S['towns'])} towns across {esc(', '.join(counties[:-1]) + ' and ' + counties[-1])} counties, all within about 20 minutes of {esc(CITY)}. Prices are the same in every town.</p>
{town_list()}
<p class="small">Don't see your town? Call {S['phone_show']}. We sometimes take homes just outside this list.</p></div>
{map_frame(CITY + ', ' + S['state'])}
</div></section>{cta_band()}"""
    page("areas/index.html", f"Areas We Serve Near {CITY}, IL",
         f"House cleaning in {', '.join(t['name'] for t in S['towns'][:-1])} and {S['towns'][-1]['name']}, Illinois. Same prices in every town.",
         main, "areas/", [("Areas", "areas/")], [], (), "", "0.8")

    for t in S["towns"]:
        nm = t["name"]
        zips = t["zips"]
        ztxt = (", ".join(zips[:-1]) + " and " + zips[-1]) if len(zips) > 1 else zips[0]
        e = E3["standard"]
        faqs = [
            (f"Do you clean homes in {nm}?", f"Yes. We clean houses, townhomes and condos in {nm}, including ZIP code{'s' if len(zips) > 1 else ''} {ztxt}."),
            (f"How much does house cleaning cost in {nm}?", f"A standard clean of a 3-bedroom, 2-bath home in {nm} costs {money(e['lo'], e['hi'])}. A deep clean costs {money(E3['deep']['lo'], E3['deep']['hi'])}. We charge the same prices in every town we serve, with no travel fee."),
            (f"How soon can you clean in {nm}?", "The booking calendar shows the next open day and arrival window. You can book up to 30 days ahead."),
        ]
        svc = "".join(f'<li><a href="{{pre}}services/{s["slug"]}/">{esc(s["name"])}</a></li>' for s in C.SERVICES)
        near = "".join(f'<li><a href="../{o["slug"]}/">{esc(o["name"])}</a></li>' for o in S["towns"] if o is not t)
        note = f"<p>{esc(t['note'])}</p>" if t["note"] else ""
        windows = ", ".join(S["arrival_windows"][:-1]) + " or " + S["arrival_windows"][-1]
        main = f"""<section class="sec page-top"><div class="wrap area-in">
<div><h1>House cleaning in {esc(nm)}, IL</h1>
<p class="lede">We clean houses, townhomes and condos across {esc(nm)}, ZIP code{'s' if len(zips) > 1 else ''} {esc(ztxt)}. A standard clean of a 3-bedroom, 2-bath home in {esc(nm)} costs {money(e['lo'], e['hi'])}.</p>{note}
<div class="acts"><a class="btn btn-go" href="{{pre}}quote/">Get my price</a><a class="btn btn-line" href="tel:+1{S['phone']}">{icon('phone')}Call {S['phone_show']}</a></div></div>
{map_frame(nm + ', ' + S['state'])}
</div></section>
<section class="sec"><div class="wrap prose-grid"><div class="prose">
<h2>{esc(nm)} house cleaning prices</h2>{price_table(caption=f'One-time cleaning in {nm}')}
<h2>Booking a cleaning in {esc(nm)}</h2>
<p>Pick an arrival window of {esc(windows)}, {esc(S['hours'][0]['days'])}. {esc(S['policies']['keys'])}</p>
<p>{esc(nm)} sits in {esc(t['county'])} {'County' if ' and ' not in t['county'] and ',' not in t['county'] else 'counties'}. Our team comes from {esc(CITY)}{', so we are close by' if nm == CITY else ''}.</p>
</div>
<aside class="side"><h2>Services in {esc(nm)}</h2><ul class="plain">{svc}</ul><h2>Nearby towns</h2><ul class="plain">{near}</ul></aside>
</div></section>
{faq_block(faqs, f'House cleaning in {esc(nm)}: questions')}{cta_band()}"""
        page(f"areas/{t['slug']}/index.html", f"House Cleaning in {nm}, IL",
             f"House cleaning in {nm}, IL ({ztxt}). Standard cleans from {money(e['lo'], e['hi'])} for a 3-bed, 2-bath home. See your price and book online.",
             main, "areas/", [("Areas", "areas/"), (nm, f"areas/{t['slug']}/")], [faq_schema(faqs)], (), "", "0.7")


# ------------------------------------------------------------------ faq, about, contact, privacy, 404
def build_faq():
    faqs = [(fill(q), fill(a)) for q, a in C.GENERAL_FAQ]
    for s in C.SERVICES:
        ex = {"from3": 0, "lo3": E3[s["type"]]["lo"], "hi3": E3[s["type"]]["hi"]}
        faqs += [(fill(q, ex), fill(a, ex)) for q, a in s["faq"]]
    seen, uniq = set(), []
    for q, a in faqs:
        if q not in seen:
            seen.add(q)
            uniq.append((q, a))
    main = f"""<section class="sec page-top"><div class="wrap narrow"><h1>House cleaning questions and answers</h1>
<p class="lede">Prices, booking, what's included and what happens on cleaning day. Call {S['phone_show']} if your question isn't here.</p></div></section>
{faq_block(uniq, 'All questions', 'faq-all')}{cta_band()}"""
    page("faq/index.html", "House Cleaning FAQ", f"Answers about house cleaning prices, booking, supplies, pets, cancellations and what's included, from {NAME} in {CITY}, IL.",
         main, "faq/", [("FAQ", "faq/")], [faq_schema(uniq)], (), "", "0.7")


def build_about():
    promises = "".join(f'<li>{icon(p["icon"])}<div><h3>{esc(p["title"])}</h3><p>{esc(p["text"])}</p></div></li>' for p in S["promises"])
    main = f"""<section class="sec page-top"><div class="wrap svc-head">
<div><h1>About {esc(NAME)}</h1>
<p class="lede">We're a house cleaning company based in {esc(CITY)}, {esc(S['state_name'])}. We clean homes in {esc(CITY)} and {len(S['towns']) - 1} towns around it, and we publish our prices so you know the cost before anyone walks through your door.</p></div>
{crop_img('living', '{pre}', 'crop crop-lg', False)}
</div></section>
<section class="sec"><div class="wrap narrow prose">
<h2>How we work</h2>
<p>You see the price before you book, and that's the price you pay unless you add something on the day. The team arrives in your arrival window, works from the same checklist in every home, and texts you when they're done.</p>
<ul class="promise-list stacked">{promises}</ul>
<h2>Our policies</h2><p>{esc(S['policies']['payment'])}</p><p>{esc(S['policies']['cancel'])}</p><p>{esc(S['policies']['keys'])}</p>
</div></section>{cta_band()}"""
    page("about/index.html", f"About Us: House Cleaners in {CITY}, IL", f"{NAME} is a house cleaning company in {CITY}, IL with published prices, online booking and a 24-hour re-clean promise.",
         main, "", [("About", "about/")], [{"@type": "AboutPage", "url": BASE + "about/", "about": {"@id": BIZ_ID}}], (), "", "0.6")


def request_form(kind):
    """kind: 'book' (with date + window) or 'contact'."""
    win = "".join(f"<option>{esc(w)}</option>" for w in S["arrival_windows"])
    book_fields = f"""
<div class="fld"><label for="{kind}-date">Preferred day</label><input id="{kind}-date" name="date" type="date" required><p class="err" id="{kind}-date-err"></p></div>
<div class="fld"><label for="{kind}-win">Arrival window</label><select id="{kind}-win" name="window">{win}</select></div>
<div class="fld"><label for="{kind}-alt">Second choice day <span class="opt">optional</span></label><input id="{kind}-alt" name="alt_date" type="date"></div>
<div class="fld"><label for="{kind}-addr">Street address</label><input id="{kind}-addr" name="address" autocomplete="street-address" required><p class="err" id="{kind}-addr-err"></p></div>""" if kind == "book" else ""
    msg_label = "Anything we should know? <span class=\"opt\">optional</span>" if kind == "book" else "How can we help?"
    return f"""<form class="req" id="{kind}-form" data-kind="{kind}" novalidate>
<div class="fld-grid">
<div class="fld"><label for="{kind}-name">Your name</label><input id="{kind}-name" name="name" autocomplete="name" required><p class="err" id="{kind}-name-err"></p></div>
<div class="fld"><label for="{kind}-phone">Mobile phone</label><input id="{kind}-phone" name="phone" type="tel" autocomplete="tel" inputmode="tel" required><p class="err" id="{kind}-phone-err"></p></div>
<div class="fld"><label for="{kind}-email">Email</label><input id="{kind}-email" name="email" type="email" autocomplete="email" required><p class="err" id="{kind}-email-err"></p></div>{book_fields}
</div>
<div class="fld"><label for="{kind}-msg">{msg_label}</label><textarea id="{kind}-msg" name="message" rows="4"{'' if kind == 'book' else ' required'}></textarea><p class="err" id="{kind}-msg-err"></p></div>
<input type="hidden" name="quote" value="">
<button class="btn btn-go" type="submit">{'Send booking request' if kind == 'book' else 'Send message'}</button>
<p class="form-note" role="status" aria-live="polite"></p>
</form>"""


def build_contact():
    hours = "".join(f"<li>{esc(h['days'])}: {esc(h['show'])}</li>" for h in S["hours"])
    main = f"""<section class="sec page-top"><div class="wrap contact-in">
<div><h1>Contact us</h1>
<p class="lede">Call or text {S['phone_show']}, or send a message below. We answer during business hours.</p>
<ul class="contact-list">
<li>{icon('phone')}<a href="tel:+1{S['phone']}">{S['phone_show']}</a></li>
<li>{icon('chat-text')}<a href="sms:+1{S['sms']}">Text {S['phone_show']}</a></li>
<li>{icon('envelope-simple')}<a href="mailto:{S['email']}">{esc(S['email'])}</a></li>
<li>{icon('clock')}<ul class="plain">{hours}</ul></li>
<li>{icon('map-pin')}<span>Based in {esc(CITY)}, {esc(S['state'])}. <a href="{{pre}}areas/">See the towns we serve</a>.</span></li>
</ul></div>
<div class="panel"><h2>Send a message</h2>{request_form('contact')}</div>
</div></section>"""
    page("contact/index.html", f"Contact {NAME}", f"Call, text or email {NAME} in {CITY}, IL. {S['phone_show']}.",
         main, "", [("Contact", "contact/")], [{"@type": "ContactPage", "url": BASE + "contact/", "about": {"@id": BIZ_ID}}],
         ["quote.js"], "", "0.6", f'<script type="application/json" id="site-data">{json.dumps(site_data())}</script>')


def site_data():
    return {"name": NAME, "email": S["email"], "phone_show": S["phone_show"], "cal_link": S["cal_link"],
            "form_endpoint": S["form_endpoint"], "zips": {z: t["name"] for t in S["towns"] for z in t["zips"]}, "pricing": P}


def build_quote():
    p = P
    types = "".join(
        f'<label class="opt-card"><input type="radio" name="type" value="{k}"{" checked" if k == "standard" else ""}><span><strong>{esc(v["label"])}</strong><small>{esc(d)}</small></span></label>'
        for (k, v), d in zip(p["types"].items(), ["Regular upkeep", "Baseboards, grout, buildup", "Empty home, inside everything"]))
    conds = "".join(f'<label class="chip"><input type="radio" name="cond" value="{k}"{" checked" if k == "kept" else ""}><span>{esc(v["label"])}</span></label>' for k, v in p["conditions"].items())
    freqs = "".join(f'<label class="chip"><input type="radio" name="freq" value="{k}"{" checked" if k == "once" else ""}><span>{esc(v["label"])}{f" <em>{round(v["discount"] * 100):g}% off</em>" if v["discount"] else ""}</span></label>' for k, v in p["frequencies"].items())
    addons = "".join(
        f'<label class="check" data-included="{" ".join(a["included"])}"><input type="checkbox" name="addon" value="{a["id"]}"><span class="check-txt">{esc(a["label"])}</span><span class="check-price">+${a["price"]}</span><span class="check-inc">Included</span></label>'
        for a in p["addons"])

    def sel(name, label, opts, val):
        o = "".join(f'<option value="{v}"{" selected" if v == val else ""}>{t}</option>' for v, t in opts)
        return f'<div class="fld"><label for="q-{name}">{label}</label><select id="q-{name}" name="{name}">{o}</select></div>'

    cal_or_form = (f'<div id="cal-inline" class="cal-box"><p class="cal-wait">Loading the calendar...</p></div>'
                   if S["cal_link"] else
                   f'<p>Pick a day and an arrival window. We confirm by text within business hours, usually the same day.</p>{request_form("book")}')
    main = f"""<section class="sec page-top quote-top"><div class="wrap narrow-l">
<h1>Get your house cleaning price</h1>
<p class="lede">Answer a few questions about your home. The price updates as you go, and you can book as soon as it looks right.</p>
</div></section>
<section class="sec quote-sec"><div class="wrap quote-in">
<form class="calc" id="calc" novalidate>
<fieldset><legend>Type of cleaning</legend><div class="opt-cards">{types}</div>
<p class="small"><a href="{{pre}}checklist/">Compare what each one includes</a></p></fieldset>
<fieldset><legend>Your home</legend><div class="fld-grid four">
{sel('beds', 'Bedrooms', [(0, 'Studio')] + [(i, str(i)) for i in range(1, 7)], 3)}
{sel('full', 'Full baths', [(i, str(i)) for i in range(1, 6)], 2)}
{sel('half', 'Half baths', [(i, str(i)) for i in range(0, 4)], 0)}
<div class="fld"><label for="q-sqft">Square feet</label><input id="q-sqft" name="sqft" type="number" inputmode="numeric" min="300" max="8000" step="50" value="1800"><p class="hint">A rough guess is fine.</p></div>
</div>
<div class="fld zip-fld"><label for="q-zip">ZIP code</label><input id="q-zip" name="zip" inputmode="numeric" maxlength="5" pattern="[0-9]{{5}}" autocomplete="postal-code"><p class="hint" id="zip-msg" aria-live="polite"></p></div>
</fieldset>
<fieldset><legend>How does it look right now?</legend><div class="chips">{conds}</div></fieldset>
<fieldset id="freq-set"><legend>How often?</legend><div class="chips">{freqs}</div><p class="hint" id="freq-msg">Discounts apply to standard cleans.</p></fieldset>
<fieldset><legend>Pets</legend><label class="check solo"><input type="checkbox" name="pets" value="1"><span class="check-txt">Cats or dogs live here</span><span class="check-price">+${p['pets']}</span></label></fieldset>
<fieldset><legend>Add-ons</legend><div class="checks">{addons}</div></fieldset>
</form>
<aside class="result" id="result" aria-live="polite">
<div class="result-in">
<p class="result-label">Your price</p>
<p class="result-price"><span id="r-price">$0</span><span class="result-per" id="r-per"></span></p>
<p class="result-time" id="r-time"></p>
<ul class="result-lines" id="r-lines"></ul>
<a class="btn btn-go btn-block" href="#book" id="to-book">Book this cleaning</a>
<p class="small result-fine">Final price stays within this range unless you add something on the day.</p>
</div>
</aside>
</div></section>
<section class="sec book-sec" id="book" aria-labelledby="book-h"><div class="wrap narrow-l">
<h2 id="book-h">Book your cleaning</h2>
<div class="book-sum" id="book-sum"></div>
{cal_or_form}
</div></section>"""
    sd = json.dumps(site_data())
    page("quote/index.html", f"House Cleaning Price Calculator, {CITY} IL",
         f"See your house cleaning price in {CITY} in about a minute, then book a time online. Standard, deep and move-out cleaning.",
         main, "quote/", [("Get my price", "quote/")],
         [{"@type": "WebApplication", "name": "House cleaning price calculator", "url": BASE + "quote/", "applicationCategory": "UtilitiesApplication", "operatingSystem": "Any", "offers": {"@type": "Offer", "price": 0, "priceCurrency": "USD"}, "provider": {"@id": BIZ_ID}}],
         ["quote.js"], "quote", "0.9", f'<script type="application/json" id="site-data">{sd}</script>')


def build_privacy():
    body = "".join(f"<h2>{esc(h)}</h2><p>{esc(t)}</p>" for h, t in C.PRIVACY)
    main = f"""<section class="sec page-top"><div class="wrap narrow prose"><h1>Privacy policy</h1>
<p class="small">Last updated <time datetime="{TODAY}">{TODAY}</time></p>
<p class="lede">This page explains what {esc(NAME)} does with the information you give us on this website.</p>{body}
<h2>Contact</h2><p>Questions about your information: <a href="mailto:{S['email']}">{esc(S['email'])}</a> or <a href="tel:+1{S['phone']}">{S['phone_show']}</a>.</p></div></section>"""
    page("privacy/index.html", "Privacy Policy", f"How {NAME} handles the information you share through this website.", main, "", [("Privacy", "privacy/")], [], (), "", "0.2")


def build_404():
    main = f"""<section class="sec page-top"><div class="wrap narrow"><h1>We couldn't find that page</h1>
<p class="lede">The link may be old. These pages can help:</p>
<ul class="plain big-links"><li><a href="{BASE}quote/">Get my price</a></li><li><a href="{BASE}services/">Services</a></li><li><a href="{BASE}pricing/">Pricing</a></li><li><a href="{BASE}">Home</a></li></ul></div></section>"""
    page("404.html", "Page not found", "This page doesn't exist.", main)
    # 404 is served from any depth, so its relative links must be absolute
    p404 = os.path.join(ROOT, "404.html")
    txt = open(p404, encoding="utf-8").read().replace('href="assets/', f'href="{BASE}assets/').replace('src="assets/', f'src="{BASE}assets/')
    for _, u in NAV + [("", "quote/"), ("", "about/"), ("", "faq/"), ("", "contact/"), ("", "privacy/"), ("", "pricing/"), ("", "checklist/")]:
        txt = txt.replace(f'href="{u}', f'href="{BASE}{u}')
    for s in C.SERVICES:
        txt = txt.replace(f'href="services/{s["slug"]}', f'href="{BASE}services/{s["slug"]}')
    for t in S["towns"]:
        txt = txt.replace(f'href="areas/{t["slug"]}', f'href="{BASE}areas/{t["slug"]}')
    txt = txt.replace('href="./"', f'href="{BASE}"').replace('href="site.webmanifest"', f'href="{BASE}site.webmanifest"')
    open(p404, "w", encoding="utf-8", newline="\n").write(txt)


# ------------------------------------------------------------------ files
def build_files():
    for name, (vb, alt) in scene.CROPS.items():
        svg = scene.scene(False, vb, alt)
        open(os.path.join(ROOT, "assets", "img", f"room-{name}.svg"), "w", encoding="utf-8").write(svg)
    open(os.path.join(ROOT, "assets", "img", "house-clean.svg"), "w", encoding="utf-8").write(scene.scene(False))

    urls = "".join(f"<url><loc>{BASE}{u}</loc><lastmod>{TODAY}</lastmod><priority>{pr}</priority></url>" for u, pr in PAGES)
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')

    bots = ["Googlebot", "Bingbot", "GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User", "PerplexityBot", "Perplexity-User", "Google-Extended", "Applebot", "Applebot-Extended"]
    robots = "".join(f"User-agent: {b}\nAllow: /\n\n" for b in bots) + "User-agent: *\nAllow: /\n\n" + f"Sitemap: {BASE}sitemap.xml\n"
    open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8").write(robots)

    e = E3
    lines = [f"# {NAME}", "",
             f"> House cleaning company based in {CITY}, {S['state_name']}. Serves {', '.join(t['name'] for t in S['towns'])}. Published prices, online price calculator and online booking.",
             "",
             f"- Phone: {S['phone_show']}",
             f"- Email: {S['email']}",
             "- Hours: " + "; ".join(f"{h['days']} {h['show']}" for h in S["hours"]),
             f"- Prices (3-bed, 2-bath, about 1,800 sq ft): standard ${e['standard']['lo']} to ${e['standard']['hi']}, deep ${e['deep']['lo']} to ${e['deep']['hi']}, move-in/move-out ${e['move']['lo']} to ${e['move']['hi']}.",
             f"- Recurring discounts on standard cleans: weekly {round(P['frequencies']['weekly']['discount'] * 100):g}%, every 2 weeks {round(P['frequencies']['biweekly']['discount'] * 100):g}%, every 4 weeks {round(P['frequencies']['monthly']['discount'] * 100):g}%.",
             f"- Supplies: the team brings all supplies and equipment.",
             f"- Policies: {S['policies']['cancel']} {S['policies']['payment']}",
             "", "## Pages", "",
             f"- [Price calculator and booking]({BASE}quote/): exact price for a home by bedrooms, bathrooms, square feet, condition, frequency and add-ons",
             f"- [Pricing]({BASE}pricing/): full price table, pricing formula, add-ons and discounts",
             f"- [Cleaning checklist]({BASE}checklist/): room-by-room tasks for standard, deep and move cleans"]
    lines += [f"- [{s['name']}]({BASE}services/{s['slug']}/): {s['card']}" for s in C.SERVICES]
    lines += [f"- [Service areas]({BASE}areas/): {', '.join(t['name'] for t in S['towns'])}",
              f"- [FAQ]({BASE}faq/)", f"- [Contact]({BASE}contact/)", ""]
    open(os.path.join(ROOT, "llms.txt"), "w", encoding="utf-8").write("\n".join(lines))

    manifest = {"name": NAME, "short_name": S["short_name"], "start_url": "./", "display": "browser", "background_color": "#f6f8f7", "theme_color": "#f6f8f7",
                "icons": [{"src": "assets/img/icon-180.png", "sizes": "180x180", "type": "image/png"}, {"src": "assets/img/icon-512.png", "sizes": "512x512", "type": "image/png"}]}
    open(os.path.join(ROOT, "site.webmanifest"), "w", encoding="utf-8").write(json.dumps(manifest, indent=1))
    open(os.path.join(ROOT, ".nojekyll"), "w").write("")


if __name__ == "__main__":
    build_home()
    build_services()
    build_pricing()
    build_checklist()
    build_areas()
    build_faq()
    build_about()
    build_contact()
    build_quote()
    build_privacy()
    build_404()
    build_files()
    print(f"Built {len(PAGES) + 1} pages. Standard 3/2: ${E3['standard']['lo']}-{E3['standard']['hi']}, deep ${E3['deep']['lo']}-{E3['deep']['hi']}, move ${E3['move']['lo']}-{E3['move']['hi']}")
