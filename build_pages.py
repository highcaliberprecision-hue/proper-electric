#!/usr/bin/env python3
"""Generates the /services/*.html, service-areas.html and faq.html pages.
index.html is hand-maintained separately and NOT touched by this script.
Run: python3 build_pages.py
"""
import os
import json

SITE = "https://theproperelectric.com"
PHONE_DISPLAY = "(847) 744-4625"
PHONE_TEL = "8477444625"
EMAIL = "properelectric@gmail.com"

SUBURBS = ["Chicago","Evanston","Oak Park","Naperville","Skokie","Schaumburg",
           "Arlington Heights","Wilmette","Hinsdale","Glenview","Lincolnwood","Northbrook"]

HEAD_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{title}</title>
<meta name="description" content="{description}" />
<meta name="robots" content="index, follow" />
<link rel="canonical" href="{canonical}" />
<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 24 24%22><text y=%2220%22 font-size=%2220%22>⚡</text></svg>" />
<meta name="theme-color" content="#0a0a0a" />

<meta property="og:type" content="website" />
<meta property="og:site_name" content="Proper Electric" />
<meta property="og:title" content="{title}" />
<meta property="og:description" content="{description}" />
<meta property="og:url" content="{canonical}" />
<meta property="og:image" content="{site}/assets/og-image.png" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta property="og:locale" content="en_US" />

<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="{title}" />
<meta name="twitter:description" content="{description}" />
<meta name="twitter:image" content="{site}/assets/og-image.png" />

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{css_path}style.css" />
{jsonld}
</head>
<body>
<div class="grain"></div>
<div class="cursor-glow" id="cursorGlow"></div>
"""

def nav(css_path):
    return f"""<header class="nav" id="nav">
  <div class="nav-inner">
    <a href="{css_path}index.html#top" class="logo">
      <span class="logo-mark">⚡</span>
      <span class="logo-text">proper<em>electric</em></span>
    </a>
    <nav class="nav-links">
      <a href="{css_path}index.html#services">services</a>
      <a href="{css_path}index.html#work">work</a>
      <a href="{css_path}index.html#about">about</a>
      <a href="{css_path}faq.html">faq</a>
      <a href="{css_path}service-areas.html">areas</a>
    </nav>
    <div class="nav-actions">
      <a href="tel:{PHONE_TEL}" class="btn-ghost"><span class="ico">☎</span> call</a>
      <a href="{css_path}index.html#contact" class="btn-solid">get quote</a>
    </div>
    <button class="nav-burger" id="navBurger" aria-label="Menu"><span></span><span></span><span></span></button>
  </div>
  <div class="nav-mobile" id="navMobile">
    <a href="{css_path}index.html#services">services</a>
    <a href="{css_path}index.html#work">work</a>
    <a href="{css_path}index.html#about">about</a>
    <a href="{css_path}faq.html">faq</a>
    <a href="{css_path}service-areas.html">areas</a>
    <a href="{css_path}index.html#contact" class="btn-solid">get quote</a>
  </div>
</header>
"""

def footer(css_path):
    return f"""<footer class="footer">
  <div class="footer-top">
    <div class="footer-brand">
      <span class="logo-mark">⚡</span>
      <span class="logo-text">proper<em>electric</em></span>
    </div>
    <div class="footer-col">
      <h5>contact</h5>
      <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a>
      <a href="mailto:{EMAIL}">{EMAIL}</a>
    </div>
    <div class="footer-col">
      <h5>visit</h5>
      <span>Chicago, IL</span>
      <span>Lic. # IL-EC-00000</span>
    </div>
    <div class="footer-col">
      <h5>legal</h5>
      <a href="{css_path}index.html">Privacy</a>
      <a href="{css_path}index.html">Terms</a>
      <a href="{css_path}index.html">Accessibility</a>
    </div>
  </div>
  <div class="footer-bottom">
    <span>© 2026 Proper Electric. All rights reserved.</span>
    <span>Licensed · Bonded · Insured · IL-EC-00000 · Chicago, IL</span>
  </div>
</footer>
<script src="{css_path}script.js"></script>
</body>
</html>
"""

SERVICE_HERO = """
<section class="section" id="top" style="padding-top:180px;">
  <div class="section-head reveal-up">
    <p class="kicker">{kicker}</p>
    <h2>{h1}</h2>
    <p class="section-desc">{intro}</p>
    <div class="hero-cta" style="margin-top:32px;">
      <a href="{home}#contact" class="btn-solid lg">get a quote <span class="arrow">→</span></a>
      <a href="tel:{phone_tel}" class="btn-outline lg"><span class="ico">☎</span> {phone_display}</a>
    </div>
  </div>
</section>
"""

def service_body(includes, process, faqs, related, home):
    includes_html = "\n".join(f'<li style="padding:6px 0;"><span style="color:var(--gold);">✓</span>&nbsp; {i}</li>' for i in includes)
    process_html = "\n".join(
        f'<div class="pillar reveal-up"><span class="pillar-num">{idx:02d}</span><h3>{step["title"]}</h3><p>{step["body"]}</p></div>'
        for idx, step in enumerate(process, 1)
    )
    faq_html = "\n".join(
        f'''<div class="faq-item">
      <button class="faq-q">{q}<span class="faq-plus">+</span></button>
      <div class="faq-a"><p>{a}</p></div>
    </div>'''
        for q, a in faqs
    )
    related_html = "\n".join(
        f'<a href="{slug}.html" class="btn-outline" style="margin-right:12px;margin-bottom:12px;">{name}</a>'
        for slug, name in related
    )
    return f"""
<section class="section">
  <div class="section-head reveal-up">
    <p class="kicker">what's included</p>
    <h2>every install,<br>done right.</h2>
  </div>
  <ul class="area-tags reveal-up" style="display:block; columns:2; max-width:700px;">
    {includes_html}
  </ul>
</section>

<section class="pillars">
  {process_html}
</section>

<section class="section faq" id="faq">
  <div class="section-head reveal-up">
    <p class="kicker">faq</p>
    <h2>questions about<br>this service.</h2>
  </div>
  <div class="faq-list reveal-up">
    {faq_html}
  </div>
</section>

<section class="section">
  <div class="section-head reveal-up">
    <p class="kicker">related services</p>
    <h2>while we're there.</h2>
  </div>
  <div class="reveal-up">
    {related_html}
  </div>
</section>

<section class="final-cta">
  <p class="kicker">ready when you are</p>
  <h2>let&rsquo;s get this<br>installed right.</h2>
  <a href="{home}#contact" class="btn-solid lg">schedule installation <span class="arrow">→</span></a>
</section>
"""

def service_jsonld(name, description, slug):
    return f"""<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Service",
  "serviceType": "{name}",
  "name": "{name}",
  "description": "{description}",
  "provider": {{
    "@type": "Electrician",
    "name": "Proper Electric",
    "telephone": "+1{PHONE_TEL}",
    "url": "{SITE}/"
  }},
  "areaServed": {{ "@type": "City", "name": "Chicago" }},
  "url": "{SITE}/services/{slug}.html"
}}
</script>"""

SERVICES = [
    {
        "slug": "ev-charger-installation",
        "name": "EV Charger Installation",
        "kicker": "ev charging",
        "h1": "ev charger installation<br>in chicago.",
        "intro": "Tesla Wall Connector, ChargePoint, or any universal Level 2 charger — installed, permitted, and inspected in a single visit, with every available rebate applied for you.",
        "description": "Level 2 EV charger installation in Chicago and surrounding suburbs — Tesla, ChargePoint, universal chargers, rebate guidance, same-day quotes.",
        "includes": [
            "Load calculation & panel capacity check",
            "Dedicated circuit run from panel to charger",
            "Charger mounting (garage, driveway, or exterior wall)",
            "Permit filing and village/city inspection",
            "Federal, state & ComEd rebate paperwork",
            "Walkthrough of your charger's app & scheduling",
        ],
        "process": [
            {"title": "free on-site quote", "body": "We check your panel's spare capacity and your charger location — no cost, no obligation."},
            {"title": "install day", "body": "Most Level 2 installs are done in a single visit, typically 2–4 hours depending on the run from your panel."},
            {"title": "permit & inspection", "body": "We file the electrical permit and coordinate the village inspection — you don't have to chase anyone down."},
            {"title": "rebates filed", "body": "We hand you the paperwork for the federal tax credit, Illinois EV rebate, and ComEd incentive, filled out and ready to submit."},
        ],
        "faqs": [
            ("Do I need a panel upgrade for an EV charger?", "Not always — most homes with a 100A+ service and some spare breaker slots can add a Level 2 charger without a panel upgrade. We check this for free during your quote."),
            ("Which chargers do you install?", "Tesla Wall Connector (Gen 3), ChargePoint Home Flex, and any UL-listed universal Level 2 charger — we're comfortable with all major brands, not just one."),
            ("How much does it cost?", "Most Level 2 installs run $600–$1,800 depending on panel capacity and the distance from your panel to the charger location."),
            ("Can I install it myself and just have you inspect it?", "EV charger circuits require a licensed electrician to pull permit in Chicago and most surrounding suburbs — we handle the full install plus the permit and inspection."),
        ],
        "related": [("smart-home-lighting", "Smart Home Lighting"), ("panel-upgrades", "Panel Upgrades")],
    },
    {
        "slug": "smart-home-lighting",
        "name": "Smart Home Lighting",
        "kicker": "smart home",
        "h1": "whole-home smart<br>lighting control.",
        "intro": "Alexa, Google Home, or Lutron — we wire your home for whole-house lighting control, scenes, and scheduling, whether you're retrofitting an existing house or wiring new construction.",
        "description": "Smart home lighting installation in Chicago — Alexa, Google Home, and Lutron whole-home control, scene design, retrofit and new construction.",
        "includes": [
            "Smart switch & dimmer installation (existing wiring)",
            "Lutron Caséta / RA3 whole-home systems",
            "Alexa & Google Home integration and scene setup",
            "Three-way and four-way smart switch wiring",
            "Low-voltage wiring for new construction & remodels",
            "App setup, scheduling, and one-on-one walkthrough",
        ],
        "process": [
            {"title": "walkthrough", "body": "We map every room, switch, and fixture you want on smart control — including 3-way and 4-way runs, which need special handling."},
            {"title": "wiring & install", "body": "Smart switches/dimmers go in, neutral wires get pulled where needed, and Lutron systems get their in-wall hub wired in."},
            {"title": "scene setup", "body": "We build your scenes (movie night, morning, away) and connect everything to Alexa or Google Home before we leave."},
            {"title": "handoff", "body": "A short walkthrough so everyone in the house knows how to use the app, the physical switches, and voice commands."},
        ],
        "faqs": [
            ("Do smart switches work in older homes without a neutral wire?", "Sometimes — some smart switches work without a neutral, but for reliability we usually recommend pulling a neutral where it's missing. We check this during the quote."),
            ("Alexa, Google, or Lutron — which should I pick?", "Lutron Caséta/RA3 is the most reliable for whole-home dimming and doesn't depend on Wi-Fi to function locally. Alexa/Google smart switches are more budget-friendly and great for single rooms. We'll recommend based on your home and budget."),
            ("Can you retrofit this into a house that's already finished?", "Yes — most of our smart lighting work is retrofit. No drywall damage in the vast majority of cases since we work through existing switch boxes."),
            ("How long does a whole-home install take?", "A single-room smart switch swap takes under an hour. A whole-home Lutron system is typically a full day depending on room count."),
        ],
        "related": [("recessed-lighting", "Recessed & Designer Lighting"), ("ev-charger-installation", "EV Charger Installation")],
    },
    {
        "slug": "recessed-lighting",
        "name": "Recessed & Designer Lighting",
        "kicker": "architectural lighting",
        "h1": "recessed & designer<br>lighting.",
        "intro": "Architectural lighting design that actually elevates a room — recessed cans, layered lighting layouts, and dimming, planned before a single hole gets cut.",
        "description": "Recessed and designer lighting installation in Chicago — layout design, LED retrofit, dimming, and architectural lighting for kitchens, living rooms, and additions.",
        "includes": [
            "Lighting layout design (spacing, layering, sightlines)",
            "Recessed can installation (new construction & retrofit)",
            "LED retrofit of existing incandescent fixtures",
            "Dimmer and smart-dimmer wiring",
            "Under-cabinet & accent lighting",
            "Ceiling patch coordination for retrofit installs",
        ],
        "process": [
            {"title": "layout design", "body": "We plan can spacing and layering (ambient, task, accent) against your actual ceiling and furniture layout — not just a generic grid."},
            {"title": "install", "body": "Cans go in, wired to dedicated dimmer circuits where it makes sense, with attention to airtight/insulation-contact rated fixtures where needed."},
            {"title": "dimming", "body": "Every recessed lighting job gets dimmer switches as standard — smart dimmers on request."},
            {"title": "finish", "body": "We coordinate with your drywall/paint contractor if patching is needed, or handle small patches ourselves on most retrofit jobs."},
        ],
        "faqs": [
            ("Can you add recessed lighting without tearing up my ceiling?", "In most retrofit jobs, yes — modern recessed housings install through a cut hole from below with minimal patching, no full ceiling demo required."),
            ("How many recessed lights do I need for a room?", "It depends on ceiling height, room use, and whether you're layering with other fixtures — we spec this during the free design walkthrough, not with a generic formula."),
            ("Do you install dimmers with every recessed lighting job?", "Yes, dimming is standard on our recessed lighting installs unless you tell us otherwise."),
            ("Can this be added to a room with existing smart home lighting?", "Yes — we'll wire it to match whatever system (Lutron, Alexa, Google) is already running your home."),
        ],
        "related": [("smart-home-lighting", "Smart Home Lighting"), ("exterior-landscape-lighting", "Exterior & Landscape Lighting")],
    },
    {
        "slug": "panel-upgrades",
        "name": "Panel Upgrades",
        "kicker": "panel upgrades",
        "h1": "200a+ panel<br>upgrades.",
        "intro": "Old fuse box, breakers that keep tripping, or adding an EV charger, hot tub, or solar — a modern 200A+ panel is the foundation everything else depends on.",
        "description": "Electrical panel upgrades in Chicago — 100A to 200A+ service upgrades, fuse box replacement, code-compliant installs, permitted and inspected.",
        "includes": [
            "Full panel replacement (fuse box or undersized breaker panel)",
            "100A → 200A+ service upgrades",
            "Meter socket and service entrance work (coordinated with ComEd)",
            "Whole-home surge protection",
            "Permit filing and village/city inspection",
            "Grounding and bonding brought up to current code",
        ],
        "process": [
            {"title": "load assessment", "body": "We calculate your home's actual electrical load — current and planned (EV, solar, hot tub) — to size the right panel, not just the biggest one."},
            {"title": "ComEd coordination", "body": "Service upgrades usually require a scheduled outage with ComEd for the meter/service entrance work — we handle that coordination."},
            {"title": "install day", "body": "Old panel comes out, new panel goes in, circuits get labeled and re-terminated, grounding brought up to current code."},
            {"title": "permit & inspection", "body": "Panel upgrades require a permit and inspection in virtually every Chicagoland municipality — we file and coordinate it."},
        ],
        "faqs": [
            ("How do I know if I need a panel upgrade?", "Common signs: breakers that trip under normal use, a fuse box instead of breakers, adding an EV charger/hot tub/solar, or an insurance company flagging an old panel (Federal Pacific, Zinsco). We'll give you a straight answer during the free quote."),
            ("How long does a panel upgrade take?", "Most residential panel upgrades are done in a single day, though the ComEd-coordinated outage means we schedule it in advance rather than same-day."),
            ("Will I be without power during the upgrade?", "Yes, for a portion of the day — typically a few hours during the actual swap. We schedule around your availability."),
            ("Do I need a permit for a panel upgrade?", "Yes, always — we file it and coordinate the inspection as part of every panel upgrade."),
        ],
        "related": [("ev-charger-installation", "EV Charger Installation"), ("commercial-electrical", "Commercial Electrical")],
    },
    {
        "slug": "exterior-landscape-lighting",
        "name": "Exterior & Landscape Lighting",
        "kicker": "outdoor lighting",
        "h1": "exterior & landscape<br>lighting.",
        "intro": "Low-voltage landscape lighting, security lighting, and seasonal/holiday installs — outdoor electrical work that holds up through a Chicago winter.",
        "description": "Exterior and landscape lighting installation in Chicago — low-voltage landscape lighting, security lighting, and seasonal holiday lighting installs.",
        "includes": [
            "Low-voltage landscape lighting (path, uplighting, accent)",
            "Security & motion-activated exterior lighting",
            "Soffit and eave lighting",
            "Permanent holiday/seasonal lighting tracks",
            "Weatherproof exterior outlets and switching",
            "Transformer sizing and low-voltage wire runs",
        ],
        "process": [
            {"title": "site walk", "body": "We walk the property at dusk or after dark when possible — landscape lighting design only makes sense when you can see what it's actually lighting."},
            {"title": "wiring", "body": "Low-voltage runs get buried or routed cleanly, transformers sized to the actual fixture load, weatherproof connections throughout."},
            {"title": "aim & adjust", "body": "Fixtures get aimed and adjusted after dark so uplighting, path lights, and accents actually land where they should."},
            {"title": "seasonal option", "body": "For holiday lighting, we can install a permanent low-profile track so future seasonal lighting is a plug-in job, not a ladder job."},
        ],
        "faqs": [
            ("Is landscape lighting expensive to run?", "Low-voltage LED landscape lighting draws very little power — a typical whole-property system costs a few dollars a month to run on a timer or photocell."),
            ("Can you install permanent holiday lighting?", "Yes — we install a permanent low-profile track along rooflines so you (or we) can plug in seasonal lighting each year without a ladder."),
            ("Do you bury the wiring?", "Yes, low-voltage landscape wiring is buried or routed through conduit — nothing left exposed across the yard."),
            ("Will exterior lighting hold up through winter?", "All our exterior fixtures and connections are rated for Chicago winters — proper weatherproof connectors and sealed fixtures are non-negotiable on outdoor work."),
        ],
        "related": [("recessed-lighting", "Recessed & Designer Lighting"), ("commercial-electrical", "Commercial Electrical")],
    },
    {
        "slug": "commercial-electrical",
        "name": "Commercial Electrical",
        "kicker": "commercial",
        "h1": "commercial<br>electrical.",
        "intro": "Restaurants, retail, and office build-outs — code-compliant electrical work that passes inspection the first time, scheduled around your business hours.",
        "description": "Commercial electrical contractor in Chicago — restaurant and retail build-outs, tenant improvements, signage circuits, code-compliant installs.",
        "includes": [
            "Tenant improvement / build-out electrical",
            "Restaurant & kitchen equipment circuits",
            "Retail and signage electrical (interior & exterior)",
            "Emergency and exit lighting (code-required)",
            "Panel and service sizing for commercial loads",
            "Off-hours scheduling to avoid disrupting business",
        ],
        "process": [
            {"title": "plan review", "body": "We review your build-out plans (or work with your GC/architect directly) to scope the electrical before the permit is filed."},
            {"title": "rough-in", "body": "Circuits, panels, and conduit go in at the rough-in stage, coordinated with drywall, HVAC, and plumbing trades."},
            {"title": "trim & equipment", "body": "Fixtures, outlets, signage circuits, and kitchen/equipment connections get finished and tested."},
            {"title": "inspection & close-out", "body": "We coordinate the final electrical inspection and hand over as-built documentation for your records."},
        ],
        "faqs": [
            ("Can you work around our business hours?", "Yes — most retail and restaurant electrical work we do is scheduled overnight or before/after business hours specifically to avoid disrupting operations."),
            ("Do you handle restaurant kitchen equipment circuits?", "Yes — dedicated circuits for cooking equipment, walk-in coolers, and ventilation systems are a regular part of our commercial work."),
            ("Do you work directly with our general contractor?", "Yes, we regularly coordinate directly with GCs and architects on build-outs rather than needing the owner in the middle of every decision."),
            ("Is emergency/exit lighting required?", "Yes, in virtually every commercial occupancy — we handle code-required emergency and exit lighting as part of every commercial build-out."),
        ],
        "related": [("panel-upgrades", "Panel Upgrades"), ("exterior-landscape-lighting", "Exterior & Landscape Lighting")],
    },
]

def build_service_page(svc):
    css_path = "../"
    home = css_path + "index.html"
    title = f"{svc['name']} Chicago | Proper Electric"
    canonical = f"{SITE}/services/{svc['slug']}.html"
    jsonld = service_jsonld(svc["name"], svc["description"], svc["slug"])
    html = HEAD_TEMPLATE.format(title=title, description=svc["description"], canonical=canonical,
                                 site=SITE, css_path=css_path, jsonld=jsonld)
    html += nav(css_path)
    html += SERVICE_HERO.format(kicker=svc["kicker"], h1=svc["h1"], intro=svc["intro"],
                                 home=home, phone_tel=PHONE_TEL, phone_display=PHONE_DISPLAY)
    html += service_body(svc["includes"], svc["process"], svc["faqs"], svc["related"], home)
    html += footer(css_path)
    return html

FAQ_EXTRA = [
    ("Do you offer financing for larger projects like panel upgrades?", "We don't offer in-house financing, but many panel upgrade and whole-home rewire customers use 0% promotional financing through their utility or a home improvement card — ask during your quote and we'll point you to current options."),
    ("What areas do you NOT cover?", "We focus on Cook, DuPage, and Lake counties. If you're outside that radius, call us anyway — we can usually tell you quickly whether it makes sense."),
    ("Do you pull permits for every job?", "Any job that requires one by code — panel upgrades, EV chargers, new circuits, service changes — gets a permit and inspection. Simple like-for-like repairs (swapping a fixture, replacing a switch) typically don't require one."),
    ("What's your warranty on electrical work?", "All labor is warrantied for one year, and we stand behind it — if something we installed fails, we come back and fix it at no charge."),
    ("Do you offer emergency service?", "Yes — we're available 24/7 for electrical emergencies (no power, sparking, breaker won't reset) in addition to our regular Mon–Sat 7am–7pm hours."),
    ("Can you match an existing fixture or switch style?", "In most cases yes, especially for common brands — bring a photo or model number to your quote and we'll source a match or the closest equivalent."),
]

def build_faq_page():
    css_path = ""
    home = "index.html"
    title = "Electrician FAQ — Proper Electric Chicago"
    description = "Answers to common questions about EV charger installation, panel upgrades, rebates, permits, and electrical service in Chicago."
    canonical = f"{SITE}/faq.html"

    all_faqs = [
        ("How much does EV charger installation cost in Chicago?", "Most Level 2 installs run $600–$1,800 depending on panel capacity and run length — we give you an exact number on-site, free, before any work starts."),
        ("Do I qualify for rebates in Illinois?", "Most homeowners qualify for at least one of the federal, state, or ComEd programs. We check your eligibility as part of every quote."),
        ("How long does installation take?", "A standard EV charger or lighting install is typically done in a single visit. Panel upgrades and whole-home rewires are scheduled and scoped up front."),
        ("Are you licensed and insured?", "Yes — fully licensed, bonded, and insured in Illinois (Lic. # IL-EC-00000), with every job permitted and inspected."),
    ] + FAQ_EXTRA

    faq_items = "\n".join(f'''<div class="faq-item">
      <button class="faq-q">{q}<span class="faq-plus">+</span></button>
      <div class="faq-a"><p>{a}</p></div>
    </div>''' for q, a in all_faqs)

    faq_schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in all_faqs
        ],
    }
    jsonld = f'<script type="application/ld+json">\n{json.dumps(faq_schema, indent=2)}\n</script>'

    html = HEAD_TEMPLATE.format(title=title, description=description, canonical=canonical,
                                 site=SITE, css_path=css_path, jsonld=jsonld)
    html += nav(css_path)
    html += f'''
<section class="section faq" id="faq" style="padding-top:180px;">
  <div class="section-head reveal-up">
    <p class="kicker">faq</p>
    <h2>straight answers.<br>no upsells.</h2>
    <p class="section-desc">Everything customers ask us most, from EV rebates to permits and emergency service. Don't see your question — just call.</p>
  </div>
  <div class="faq-list reveal-up">
    {faq_items}
  </div>
</section>

<section class="final-cta">
  <p class="kicker">still have questions?</p>
  <h2>call and ask<br>us directly.</h2>
  <a href="tel:{PHONE_TEL}" class="btn-solid lg"><span class="ico">☎</span> {PHONE_DISPLAY}</a>
</section>
'''
    html += footer(css_path)
    return html

def build_service_areas_page():
    css_path = ""
    title = "Service Areas — Chicago Electrician | Proper Electric"
    description = "Proper Electric serves Chicago, Evanston, Oak Park, Naperville, and Cook, DuPage & Lake county suburbs — same-day estimates, licensed & insured."
    canonical = f"{SITE}/service-areas.html"
    jsonld = ""

    area_notes = [
        ("Chicago", "City installs run the full range — vintage two-flats needing panel upgrades and rewires, high-rise condo association work, and new-construction EV readiness in newer developments."),
        ("Evanston & Oak Park", "Older housing stock (pre-1960s) is common here — a lot of our panel upgrade and knob-and-tube rewire work happens in these two suburbs specifically."),
        ("Naperville & Schaumburg", "Newer construction with higher electrical capacity already in place — most calls here are EV charger installs and smart home retrofits rather than panel work."),
        ("Wilmette, Glenview & Northbrook", "Larger single-family homes, frequent whole-home smart lighting (Lutron) installs and landscape/exterior lighting projects."),
        ("Skokie & Lincolnwood", "A mix of older bungalows and newer builds — common jobs are recessed lighting upgrades and EV charger installs."),
        ("Arlington Heights & Hinsdale", "Higher rate of panel upgrades tied to additions, hot tubs, and detached garage sub-panels."),
    ]
    notes_html = "\n".join(
        f'<div class="service-card reveal-up"><h3 style="text-transform:none;font-size:20px;margin-bottom:10px;">{name}</h3><p style="color:var(--muted);font-size:14.5px;line-height:1.6;">{note}</p></div>'
        for name, note in area_notes
    )
    tags_html = "\n".join(f"<span>{s}</span>" for s in SUBURBS)

    html = HEAD_TEMPLATE.format(title=title, description=description, canonical=canonical,
                                 site=SITE, css_path=css_path, jsonld=jsonld)
    html += nav(css_path)
    html += f'''
<section class="section" id="top" style="padding-top:180px;">
  <div class="section-head reveal-up">
    <p class="kicker">service area</p>
    <h2>serving chicago<br>&amp; surrounding areas.</h2>
    <p class="section-desc">Same-day estimates across Cook, DuPage and Lake counties. If you're not sure we cover your zip — just call.</p>
  </div>
  <div class="area-tags reveal-up">
    {tags_html}
  </div>
</section>

<section class="section">
  <div class="section-head reveal-up">
    <p class="kicker">what we see locally</p>
    <h2>every suburb's<br>a little different.</h2>
  </div>
  <div class="services-grid">
    {notes_html}
  </div>
</section>

<section class="final-cta">
  <p class="kicker">not sure we cover your area?</p>
  <h2>just give us<br>a call.</h2>
  <a href="tel:{PHONE_TEL}" class="btn-solid lg"><span class="ico">☎</span> {PHONE_DISPLAY}</a>
</section>
'''
    html += footer(css_path)
    return html

if __name__ == "__main__":
    root = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(os.path.join(root, "services"), exist_ok=True)

    for svc in SERVICES:
        path = os.path.join(root, "services", f"{svc['slug']}.html")
        with open(path, "w") as f:
            f.write(build_service_page(svc))
        print(f"wrote {path}")

    with open(os.path.join(root, "faq.html"), "w") as f:
        f.write(build_faq_page())
    print("wrote faq.html")

    with open(os.path.join(root, "service-areas.html"), "w") as f:
        f.write(build_service_areas_page())
    print("wrote service-areas.html")
