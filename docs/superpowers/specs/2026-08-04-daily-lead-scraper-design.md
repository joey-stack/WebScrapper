# Daily Automated Lead Scraper & Deduplication Engine Spec

## 1. Goal & Architecture
Build an enterprise daily lead scraper (`execution/scrape_daily_leads.py`) that extracts 10–15 fresh buried leads (ranked #11–50+) daily across rotating high-value business sectors and cities in Nigeria, deduplicates them against existing dataset records, automatically qualifies them with 5-Star ELI5 strategies, and appends them to `1_Outreach_Pipeline` on the live Google Sheet.

Target Google Sheet: `https://docs.google.com/spreadsheets/d/1wGuXHelu2SqOUG2IQNMWG8gF08KqO_OcTb5rU1cziiU`

---

## 2. Category & Location Matrix
The scraper rotates daily across target queries:
1. `NGOs in Abuja`, `Foundations in Abuja`
2. `Tech companies in Lagos`, `Innovation hubs in Yaba`
3. `Private schools in Lekki`, `Colleges in Port Harcourt`
4. `Real estate agencies in Abuja`, `Property developers in Lagos`
5. `Private hospitals in Ikeja`, `Specialist clinics in Ibadan`

---

## 3. Deduplication & Qualification Flow
1. **Extraction**: Scrapes businesses ranked position #11 to #50+.
2. **Deduplication**: Matches `google_maps_url`, `name`, and `email` against `.tmp/gmb_leads_combined.csv`. Discards matching records.
3. **Qualification**: Passes new unique leads to `execution/qualify_and_pitch_leads.py` to assign Price Class (Tier 1–4), 1-Time Setup Fee, Monthly Maintenance Fee, 5-Star ELI5 Conversion Strategy, and Consultative Pitch.
4. **CRM Sync**: Appends new leads to `.tmp/gmb_leads_combined.csv` and updates `1_Outreach_Pipeline` on live Google Sheet.
5. **Orchestrator Hook**: Called automatically inside `execution/run_autonomous_crm_cycle.py`.
