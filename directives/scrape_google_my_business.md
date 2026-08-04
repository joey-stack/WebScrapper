# Directive: Scrape, Qualify & Pitch Google My Business Profiles for Web Design & GMB SEO

## Goal
Scrape Google My Business profiles for targeted queries (e.g. `"NGOs in Abuja, Nigeria"`, `"NGOs in Lagos, Nigeria"`), analyze their digital presence, qualify leads needing Website Design and/or GMB SEO Optimization, generate tailored conversion strategies & personalized pitch copy, and export deliverables to a fresh Google Sheet.

## Extracted & Calculated Fields
1. `name`: Business / NGO Name
2. `category`: Listed category on GMB
3. `address`: Physical location / street address
4. `phone`: Contact phone number
5. `website`: Official website URL
6. `email`: Scraped email address(es)
7. `rating`: Star rating
8. `reviews_count`: Total review count
9. `service_needed`: Lead Qualification (`"Website Design Only"`, `"GMB SEO Optimization Only"`, `"Both (Website + GMB SEO)"`, or `"Fully Optimized"`)
10. `conversion_strategy`: Tactical plan on how a high-converting website & optimized GMB profile will drive donors, volunteers, and grant credibility for this specific NGO.
11. `personalized_pitch`: Ready-to-send outreach message tailored to the NGO's niche explaining their missing digital assets and business impact.
12. `google_maps_url`: Direct Google Maps listing link.

## Qualification Criteria
- **Website Design Candidate**: Missing official website URL.
- **GMB SEO Optimization Candidate**: Missing phone number, missing address, or low review count (< 5 reviews).
- **Both**: Missing website AND missing key GMB profile details.

## Execution Tools
- `execution/scrape_gmb_profiles.py`: Scrapes listings and calls lead qualification & pitch generator.
- `execution/export_to_google_sheets.py`: Publishes qualified leads with strategies & pitches to Google Sheets.

## Output Deliverable
- Live Google Sheet containing formatted tabs and columns for `service_needed`, `conversion_strategy`, and `personalized_pitch`.
