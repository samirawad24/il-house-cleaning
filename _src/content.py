"""Copy and structured content. Business facts come from site.json; this file holds the words."""

# Room-by-room checklist. Flags: S standard, D deep, M move-in/move-out.
CHECKLIST = [
    ("kitchen", "Kitchen", [
        ("Wipe counters and backsplash", "SDM"),
        ("Clean the stovetop and drip pans", "SDM"),
        ("Clean the outside of the fridge, oven, dishwasher and microwave", "SDM"),
        ("Clean the microwave inside", "SDM"),
        ("Scrub and shine the sink and faucet", "SDM"),
        ("Wipe cabinet fronts and handles", "SDM"),
        ("Empty the trash and put in a new liner", "SDM"),
        ("Vacuum and mop the floor", "SDM"),
        ("Degrease the range hood and its filter", "DM"),
        ("Hand-wipe baseboards", "DM"),
        ("Clean inside the oven", "M"),
        ("Clean inside the fridge and freezer", "M"),
        ("Wipe inside cabinets and drawers", "M"),
    ]),
    ("bathrooms", "Bathrooms", [
        ("Scrub the toilet inside, outside and around the base", "SDM"),
        ("Clean the tub, shower walls and glass", "SDM"),
        ("Clean the sink, counter and faucet", "SDM"),
        ("Clean mirrors", "SDM"),
        ("Wipe cabinet fronts", "SDM"),
        ("Empty the trash", "SDM"),
        ("Vacuum and mop the floor", "SDM"),
        ("Scrub grout and remove soap scum buildup", "DM"),
        ("Wipe vents and light fixtures", "DM"),
        ("Hand-wipe baseboards", "DM"),
        ("Wipe inside vanity drawers and cabinets", "M"),
    ]),
    ("bedrooms", "Bedrooms", [
        ("Dust nightstands, dressers and shelves", "SDM"),
        ("Make the beds, and change sheets if you leave clean ones out", "SD"),
        ("Vacuum carpet and mop hard floors", "SDM"),
        ("Empty the trash", "SDM"),
        ("Dust ceiling fans and light fixtures", "DM"),
        ("Wipe doors, frames and light switches", "DM"),
        ("Vacuum under the beds where we can reach", "DM"),
        ("Hand-wipe baseboards", "DM"),
        ("Wipe closet shelves and vacuum closet floors", "M"),
    ]),
    ("living", "Living areas", [
        ("Dust shelves, decor and TV stands", "SDM"),
        ("Clean glass tables and mirrors", "SDM"),
        ("Wipe door handles and light switches", "SDM"),
        ("Clean salt and mud marks at the entry", "SDM"),
        ("Vacuum and mop floors and stairs", "SDM"),
        ("Vacuum the couch and under the cushions", "DM"),
        ("Wipe window sills and tracks", "DM"),
        ("Spot-clean walls", "DM"),
        ("Hand-wipe baseboards", "DM"),
    ]),
]

NOT_INCLUDED = [
    "Outside windows and anything that needs a ladder taller than a step stool",
    "Moving heavy furniture or appliances",
    "Mold remediation, pest droppings or bodily fluids",
    "Carpet shampooing and upholstery steam cleaning",
    "Pet waste, litter boxes and cages",
]

SERVICES = [
    {
        "slug": "standard-cleaning",
        "type": "standard",
        "name": "Standard cleaning",
        "h1": "Standard house cleaning",
        "crop": "kitchen",
        "card": "Kitchen, bathrooms, bedrooms and living areas, top to bottom. For homes that get cleaned regularly.",
        "title": "Standard House Cleaning in {city}, IL",
        "desc": "Standard house cleaning in {city} and nearby suburbs. What's included, prices from ${from3} for a 3-bed, 2-bath home, and online booking.",
        "lede": "We dust and wipe the kitchen, bathrooms, bedrooms and living areas, vacuum and mop the floors, and take out the trash. A standard clean of a 3-bedroom, 2-bath home in the {city} area costs ${lo3} to ${hi3}.",
        "flag": "S",
        "body": [
            ("Who it's for", "Homes that get cleaned every few weeks, or homes in decent shape that need a reset. If nobody has cleaned in a couple of months, book a deep clean first. The standard clean keeps up after that."),
        ],
        "faq": [
            ("How often should I book a standard clean?", "Most families with kids or pets book every two weeks. Couples and people living alone often book every four weeks. Weekly visits cost 20% less per visit and keep the house close to spotless."),
            ("Do I need a deep clean first?", "Only if the home hasn't had a professional clean in the last couple of months. Pick \"It's been a while\" in the price calculator and we price the extra time in."),
            ("Do you bring supplies?", "Yes. The team brings vacuums, mops, cloths and products. If you want us to use your own products, leave them out and tell us in the booking notes."),
        ],
    },
    {
        "slug": "deep-cleaning",
        "type": "deep",
        "name": "Deep cleaning",
        "h1": "Deep house cleaning",
        "crop": "bath",
        "card": "Everything in a standard clean plus baseboards, grout, vents, the range hood and the buildup in corners.",
        "title": "Deep House Cleaning in {city}, IL",
        "desc": "Deep house cleaning in {city}: baseboards, grout, vents, range hood and more. Prices from ${from3} for a 3-bed, 2-bath home. Book online.",
        "lede": "A deep clean covers everything in a standard clean, then adds the slow work: hand-wiped baseboards, door frames and switches, scrubbed grout, the range hood and the dust on fans and vents. A deep clean of a 3-bedroom, 2-bath home in the {city} area costs ${lo3} to ${hi3}.",
        "flag": "D",
        "body": [
            ("When to book one", "Book a deep clean for your first visit with us, before hosting family for the holidays, at the end of winter when salt and grit have tracked through the house, or once or twice a year between standard cleans."),
        ],
        "faq": [
            ("What's the difference between a standard and a deep clean?", "A standard clean keeps a home in good shape. A deep clean adds baseboards, door frames, light switches, vents, fans, grout and the range hood, and spends longer on buildup in the kitchen and bathrooms. It takes about 1.6 times as long."),
            ("How long does a deep clean take?", "For a 3-bedroom, 2-bath home, a team of two spends about {team_hours3} hours. Bigger homes and homes that need extra work take longer."),
            ("Is the inside of the oven and fridge included?", "Not in a deep clean. Add them in the price calculator for ${oven} and ${fridge}. Both come included with a move-in or move-out clean."),
        ],
    },
    {
        "slug": "move-out-cleaning",
        "type": "move",
        "name": "Move-in and move-out cleaning",
        "h1": "Move-in and move-out cleaning",
        "crop": "living",
        "card": "For empty homes. Inside cabinets, closets, the oven and the fridge, plus everything in a deep clean.",
        "title": "Move-Out Cleaning in {city}, IL",
        "desc": "Move-in and move-out cleaning in {city}: inside cabinets, oven, fridge and closets included. From ${from3} for a 3-bed, 2-bath home. Book online.",
        "lede": "A move clean is for an empty home. We clean inside the cabinets, drawers, closets, oven and fridge, along with everything in a deep clean. A move clean of a 3-bedroom, 2-bath home in the {city} area costs ${lo3} to ${hi3}.",
        "flag": "M",
        "body": [
            ("Who books it", "Tenants who want the home ready for the final walkthrough, buyers who want a clean start before the furniture arrives, and landlords and realtors turning a home between people. You don't need to be there. Leave a lockbox code and we'll text you when we're done."),
        ],
        "faq": [
            ("Does the home need to be empty?", "Mostly. We can work around a few boxes, but we can't clean inside cabinets or closets that are still full, and we don't move furniture."),
            ("Will a move-out clean get my deposit back?", "We clean to the standard most Illinois leases ask for, and we come back within 24 hours if your walkthrough turns up something we missed. Your landlord still makes the call on the deposit."),
            ("Can you clean on closing day?", "Often, yes. Book the earliest arrival window and tell us your closing time in the booking notes."),
        ],
    },
    {
        "slug": "recurring-cleaning",
        "type": "standard",
        "name": "Weekly and biweekly cleaning",
        "h1": "Weekly, biweekly and monthly house cleaning",
        "crop": "bed",
        "card": "A standard clean on a schedule. Weekly saves 20%, every two weeks 15%, every four weeks 10%.",
        "title": "Recurring House Cleaning in {city}, IL",
        "desc": "Recurring house cleaning in {city}. Weekly, every 2 weeks or every 4 weeks, with up to 20% off each visit. See your price and book online.",
        "lede": "Book a standard clean every week, every two weeks or every four weeks and pay less per visit: 20%, 15% or 10% off. Every two weeks, a 3-bedroom, 2-bath home in the {city} area costs ${blo3} to ${bhi3} per visit.",
        "flag": "S",
        "recurring": True,
        "body": [
            ("How it works", "Your first visit is often a deep clean, so the regular visits start from a clean baseline. After that we come on the same weekday and in the same arrival window. We send the same team whenever we can, so they learn your home and how you like it."),
        ],
        "faq": [
            ("Can I skip or move a visit?", "Yes. Tell us 48 hours before your arrival window and we'll move it or skip it at no charge."),
            ("Do I have to sign a contract?", "No. You can stop any time with 48 hours notice."),
            ("What does the first visit cost?", "If the home hasn't had a professional clean in a while, we start with a deep clean at the deep clean price. The discounted recurring price starts with the second visit."),
        ],
    },
]

GENERAL_FAQ = [
    ("How much does house cleaning cost in {city}?", "A standard clean of a 3-bedroom, 2-bath home of about 1,800 square feet costs ${lo3} to ${hi3}. A deep clean of the same home costs ${dlo3} to ${dhi3}. Recurring visits cost 10% to 20% less. The price calculator gives you an exact figure for your home."),
    ("Do I need to be home?", "{keys}"),
    ("Do you bring your own supplies?", "Yes. We bring vacuums, mops, cloths and products. Leave your own out if you'd rather we use them."),
    ("How long does a cleaning take?", "A team of two spends about {team_hours_std3} hours on a standard clean of a 3-bedroom, 2-bath home, and about {team_hours3} hours on a deep clean. The price calculator shows the time for your home."),
    ("Do you clean homes with pets?", "Yes. Tell us about your pets in the calculator so we bring extra time for pet hair. Please keep pets that don't like visitors in a closed room."),
    ("What if I'm not happy with the cleaning?", "Tell us within 24 hours and we come back to fix it at no charge."),
    ("How do I pay?", "{payment}"),
    ("What is your cancellation policy?", "{cancel}"),
    ("Do you clean finished basements?", "Yes. Add a finished basement in the calculator for ${basement}. It covers a family room, a bathroom and the stairs."),
    ("What do you do about winter salt and slush?", "We clean the salt lines and mud off entry floors and mats on every visit from November to March. If a snowstorm closes the roads, we call you to reschedule at no charge."),
    ("Are your cleaners insured?", "Yes. We carry liability insurance and our team is bonded."),
    ("Do you clean apartments and condos?", "Yes. Use the same price calculator and enter your square footage."),
]

PRIVACY = [
    ("What we collect", "When you use the price calculator or send a booking or contact request, we collect what you type: your name, phone number, email, address and details about your home. The price calculator itself runs in your browser and sends nothing until you submit a request."),
    ("How we use it", "We use your details to give you a price, schedule and confirm your cleaning, send reminders and answer your questions. We don't sell your information or share it with advertisers."),
    ("Booking tools", "Our online calendar runs on Cal.com, which stores your booking and sends confirmation emails. Our service area map loads from Google Maps. Each service has its own privacy policy."),
    ("Keeping or deleting your information", "We keep customer records for as long as you book with us and for tax purposes after that. Call or email us and we'll delete your information or send you a copy."),
]
