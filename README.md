# House cleaning site (Illinois client)

Static site. GitHub Pages serves it from the repo root.

## Edit and rebuild

1. Business facts, towns, prices and booking settings: `_src/site.json`
2. Page copy and the room checklist: `_src/content.py`
3. House illustration: `_src/scene.py`
4. Styles and scripts: `assets/site.css`, `assets/story.js` (scroll scene), `assets/quote.js` (calculator + booking)
5. Run `python _src/build.py`, then commit and push.

The calculator math lives in two places on purpose: `estimate()` in `_src/build.py` (price tables, schema, llms.txt) and `estimate()` in `assets/quote.js` (live calculator). Change both together.

`assets/img/og.png` (the link preview image) has the business name baked in. Regenerate it after the name changes.

## Booking

- `cal_link` empty: the quote page shows a booking request form.
- `cal_link` set (for example `prairie-home/cleaning`): the quote page embeds that Cal.com calendar and passes the quote into the booking notes.
- Suggested Cal.com event type: 30 minutes, named "Cleaning arrival", booking questions for phone and address, availability matching the arrival windows.
- `form_endpoint` empty: forms open the visitor's email app. Set it to a Formspree or FormSubmit URL so requests arrive without the email app.

## Before going live (set `preview` to false)

Placeholders to replace with real facts:
- Business name, phone, text number, email, hours, arrival windows
- Home city, ZIP and the towns list (each town can take a `note` with real local detail, which helps those pages rank)
- Prices (market defaults for the west Chicago suburbs right now)
- Promises: insured and bonded, 24-hour re-clean, text before arrival
- Policies: cancellation fee, payment timing, keys
- FAQ claims in `_src/content.py`: no contract on recurring, same team when possible, winter storm rescheduling
- Google Business Profile, Facebook and Yelp URLs go in `same_as`
- Real team and job photos (About page and service pages)
- `base_url` once the custom domain is live

Then submit `sitemap.xml` in Google Search Console and Bing Webmaster Tools.
