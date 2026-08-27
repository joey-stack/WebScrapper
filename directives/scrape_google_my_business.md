# Directive: Scrape, Qualify & Pitch Google My Business Profiles for Web Design & GMB SEO

## Goal
Scrape Google My Business profiles for targeted queries (e.g. `"NGOs in Abuja, Nigeria"`, `"Tech Hubs in Lagos, Nigeria"`, `"Private Schools in Lekki, Lagos"`), analyze their digital presence, ensure 100% data integrity between review counts and ratings (strictly eliminating phantom ratings or contradictory pitch claims), qualify leads needing Website Design and/or GMB SEO Optimization, generate tailored conversion strategies & personalized pitch copy, and export deliverables to a fresh Google Sheet.

## Extracted & Calculated Fields
1. `name`: Business / NGO Name
2. `category`: Exact listed category on GMB (e.g. Non-profit organization, Software company, Real estate agency)
3. `address`: Physical location / street address and city
4. `phone`: Contact phone number
5. `website`: Official website URL
6. `email`: Scraped email address(es) crawled from website
7. `rating`: Verified star rating (strictly empty if `reviews_count == 0`)
8. `reviews_count`: Total review count (0, 1, 5, 20+)
9. `service_needed`: Lead Qualification (`"Website Design Only"`, `"GMB SEO Optimization Only"`, `"Both (Website + GMB SEO)"`, or `"Fully Optimized"`)
10. `conversion_strategy`: In-depth executive strategy with ELI5 analogy tailored to the organization's exact sector, location, and digital gaps.
11. `personalized_pitch`: Ready-to-send outreach message tailored to the organization's sector, mentioning exact strengths and non-contradictory growth areas.
12. `google_maps_url`: Direct Google Maps listing link.

## Qualification & Pitch Consistency Criteria
- **Strict Data Integrity**: If `reviews_count == 0`, `rating` must be empty and the pitch must NOT claim any star rating or community review praise.
- **Genuine Personalization**: Injects the business's actual category (e.g. "software companies", "real estate agencies") and city into the pitch.
- **Website Design Candidate**: Missing official website URL.
- **GMB SEO Optimization Candidate**: Missing phone number, missing address, buried rank (#11-50+), or low review count (< 5 reviews).
- **Both**: Missing website AND missing key GMB profile details.

## Execution Tools
- `execution/scrape_gmb_profiles.py`: Scrapes listings with multi-layer card & side-panel validation and calls lead qualification & pitch generator.
- `execution/scrape_daily_leads.py`: Automated daily buried lead scraper (#11-50+) across rotating industry sectors.
- `execution/qualify_and_pitch_leads.py`: Generates factual, non-contradictory pitches, price tiers, and conversion strategies.
- `execution/export_to_google_sheets.py`: Publishes qualified leads with strategies & pitches to Google Sheets.

## Output Deliverable
- Live Google Sheet containing formatted tabs and columns for `service_needed`, `conversion_strategy`, and `personalized_pitch`.
