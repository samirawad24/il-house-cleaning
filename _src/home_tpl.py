"""Home page template. Imported by build.py (kept separate because it is the biggest page)."""
import json


def build_home(B):
    S, P, C, E3, CITY, NAME = B.S, B.P, B.C, B.E3, B.CITY, B.NAME
    esc, icon, money, hrs, estimate, bz = B.esc, B.icon, B.money, B.hrs, B.estimate, B.bz
    e3 = E3["standard"]
    todo = [
        ("kitchen", "Kitchen", "Kitchen", "Degrease the stovetop, scrub the sink, wipe the counters, mop the floor"),
        ("bath", "Bathrooms", "Baths", "Scrub the tub, shower and toilet, clean the mirror, mop the floor"),
        ("bed", "Bedrooms", "Beds", "Dust dressers and fan blades, make the beds, vacuum the edges"),
        ("living", "Living room", "Living", "Clear the salt and slush at the door, vacuum the couch, mop"),
    ]
    items = "".join(
        f'<li data-room="{k}"><span class="tick">{icon("check-bold")}</span><span class="todo-t"><span class="lg">{t}</span><span class="sm">{sh}</span></span><span class="todo-d">{d}</span></li>'
        for k, t, sh, d in todo)
    done_txt = f"All done. For a 3-bed, 2-bath home that's {money(e3['lo'], e3['hi'])}, about {hrs(e3['team_hours'])} hours for a team of two."
    story = f"""<section class="story" id="story" aria-labelledby="hero-h">
<div class="stage"><div class="wrap stage-in">
  <div class="stage-copy">
    <h1 id="hero-h">{esc(CITY)} house cleaning</h1>
    <p class="lede">See your price in about a minute and book online. We clean homes across {esc(CITY)} and the nearby suburbs.</p>
    <div class="acts"><a class="btn btn-go" href="quote/">Get my price</a><a class="btn btn-line" href="tel:+1{S['phone']}">{icon('phone')}{S['phone_show']}</a></div>
    <div class="todo" id="todo">
      <p class="todo-h">A standard clean, room by room</p>
      <ol class="todo-list">{items}</ol>
      <p class="todo-now" id="todo-now" aria-hidden="true">{todo[0][3]}</p>
      <p class="todo-done">{done_txt}</p>
    </div>
  </div>
  <div class="stage-art">{bz(B.scene.scene(True), 'bz-art')}</div>
</div></div>
</section>"""

    # price picker: every number is computed here at build time, the page only looks them up
    sizes = B.HOMES[:5]
    table = {k: [estimate(k, b, fb, hb, sq) for _, _, b, fb, hb, sq in sizes] for k in P["types"]}
    table["biweekly"] = [estimate("standard", b, fb, hb, sq, freq="biweekly") for _, _, b, fb, hb, sq in sizes]
    homes = [{"label": f"{l}, {z}", "beds": b, "full": fb, "half": hb, "sqft": sq} for l, z, b, fb, hb, sq in sizes]
    pdata = esc(json.dumps({"t": {k: [[e["lo"], e["hi"], e["team_hours"]] for e in v] for k, v in table.items()}, "h": homes}))
    seg = "".join(
        f'<label class="pill"><input type="radio" name="pt-type" value="{k}"{" checked" if k == "standard" else ""}><span>{esc(v["label"].replace("Move-in / move-out", "Move-out"))}</span></label>'
        for k, v in P["types"].items())
    sz = "".join(
        f'<label class="pill"><input type="radio" name="pt-size" value="{i}"{" checked" if i == 2 else ""}><span>{h[2]} bed</span></label>'
        for i, h in enumerate(sizes))
    s3, b3 = table["standard"][2], table["biweekly"][2]
    tool = f"""<form class="pt-tool" id="pt" data-prices="{pdata}" onsubmit="return false">
  <fieldset><legend>Type of cleaning</legend><div class="pills">{seg}</div></fieldset>
  <fieldset><legend>Bedrooms</legend><div class="pills">{sz}</div></fieldset>
  <div class="pt-out">
    <p class="pt-home" id="pt-home">{esc(homes[2]['label'])}</p>
    <p class="pt-price"><output id="pt-price" for="pt">{money(s3['lo'], s3['hi'])}</output></p>
    <p class="pt-note" id="pt-note">Every 2 weeks: {money(b3['lo'], b3['hi'])} per visit. About {hrs(s3['team_hours'])} hours for a team of two.</p>
  </div>
  <a class="btn btn-go" id="pt-go" href="quote/?type=standard&amp;beds=3&amp;full=2&amp;half=0&amp;sqft=1800">Get my price</a>
</form>"""
    prices = f"""<section class="sec pt" aria-labelledby="pt-h"><div class="wrap pt-in">
<div class="pt-copy" data-r>
  <h2 id="pt-h">What a cleaning costs</h2>
  <p>Pick a cleaning and a home size. These are the real prices for {esc(CITY)} and every town we serve, before add-ons.</p>
  <a class="txt-link" href="pricing/">See the full price list {icon('arrow-right')}</a>
</div>
<div data-r>{bz(tool, 'bz-pt')}</div>
</div></section>"""

    promises = "".join(f'<li data-r>{icon(p["icon"])}<h3>{esc(p["title"])}</h3><p>{esc(p["text"])}</p></li>' for p in S["promises"])
    promise = f'<section class="sec promises" aria-label="What you can count on"><ul class="wrap promise-list">{promises}</ul></section>'

    cells = ""
    for i, s in enumerate(C.SERVICES):
        e = estimate(s["type"], freq="biweekly" if s.get("recurring") else "once")
        cells += f"""<a class="bz svc svc-{i}" href="services/{s['slug']}/" data-r><div class="core">
<div class="svc-art">{B.crop_img(s['crop'], '')}</div>
<div class="svc-txt"><h3>{esc(s['name'])}</h3><p>{esc(s['card'])}</p><p class="from"><span>From ${e['lo']:,}{' per visit' if s.get('recurring') else ''}</span><span class="svc-go">{icon('arrow-up-right')}</span></p></div></div></a>"""
    services = f'<section class="sec svcs" aria-labelledby="svc-h"><div class="wrap"><h2 id="svc-h" data-r>Four ways to book a clean</h2><div class="svc-grid">{cells}</div></div></section>'

    how = """<section class="sec how" aria-labelledby="how-h"><div class="wrap">
<h2 id="how-h" data-r>Booking takes a minute</h2>
<ol class="how-list">
<li data-r><p class="how-v">Price it.</p><p>Tell us about your home. The price updates as you answer, and it's the price you pay.</p></li>
<li data-r><p class="how-v">Book it.</p><p>Pick a day and an arrival window. We confirm and text you the day before.</p></li>
<li data-r><p class="how-v">Come home to it.</p><p>The team arrives with every supply and works from the same checklist in every home. You don't have to be there.</p></li>
</ol></div></section>"""

    tabs = ""
    panels = ""
    for i, (key, room, tasks) in enumerate(C.CHECKLIST):
        sel = "true" if i == 0 else "false"
        tab_idx = "" if i == 0 else ' tabindex="-1"'
        hidden = "" if i == 0 else " hidden"
        tabs += f'<button type="button" role="tab" id="tab-{key}" aria-controls="panel-{key}" aria-selected="{sel}"{tab_idx}>{esc(room)}</button>'
        std = "".join(f"<li>{icon('check-bold')}<span>{esc(t)}</span></li>" for t, fl in tasks if "S" in fl)
        deep = [t for t, fl in tasks if fl.startswith("D")]
        deep_txt = f'<p class="adds"><strong>A deep clean adds:</strong> {esc("; ".join(t[0].lower() + t[1:] for t in deep))}.</p>' if deep else ""
        panels += f'<div class="tab-panel" role="tabpanel" id="panel-{key}" aria-labelledby="tab-{key}"{hidden}><ul class="ticks">{std}</ul>{deep_txt}</div>'
    checklist = f"""<section class="sec rooms" aria-labelledby="rooms-h"><div class="wrap">
<div class="rooms-head" data-r><h2 id="rooms-h">What we clean in each room</h2><p>The standard list for every visit. <a href="checklist/">Compare standard, deep and move cleans</a>.</p></div>
<div class="tabs" data-tabs data-r><div class="tab-row" role="tablist" aria-label="Rooms">{tabs}</div>{bz(panels, 'bz-tab')}</div>
</div></section>"""

    towns = "".join(f'<li><a href="areas/{t["slug"]}/">{esc(t["name"])}</a></li>' for t in S["towns"])
    area = f"""<section class="sec area" aria-labelledby="area-h"><div class="wrap area-in">
<div data-r><h2 id="area-h">Where we clean</h2><p>We're based in {esc(CITY)}. These are the towns we cover, all at the same prices.</p><ul class="town-big">{towns}</ul></div>
<div data-r>{bz(B.map_frame(CITY + ', ' + S['state']), 'bz-map')}</div>
</div></section>"""

    faqs = [(B.fill(q), B.fill(a)) for q, a in C.GENERAL_FAQ[:6]]
    more = '<a class="txt-link" href="faq/">All questions ' + icon('arrow-right') + "</a>"
    main = story + prices + promise + services + how + checklist + area + B.faq_block(faqs, more=more) + B.cta_band()
    B.page("index.html", f"House Cleaning in {CITY}, IL | {NAME}",
           f"House cleaning in {CITY}, Aurora, Wheaton and nearby suburbs. See your price in a minute and book online. Standard cleans from ${E3['standard']['lo']} for a 3-bed, 2-bath home.",
           main, "", None, [B.faq_schema(faqs)], ["vendor/gsap.min.js", "vendor/ScrollTrigger.min.js", "story.js"], "home", "1.0")
