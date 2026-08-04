# Directive: Autonomous Master CRM Orchestration & Auto-Pilot Engine

## Purpose
Runs a 100% hands-off, zero-click autonomous cycle that coordinates lead qualification, outreach email dispatches, incoming reply tracking via IMAP, lead pipeline promotion, project deliverable onboarding, and real-time financial dashboard sync.

---

## What Is Needed Before Execution? (Pre-flight Requirements)

1. **Environment Credentials (`.env`)**:
   - `SENDER_EMAIL=joeladawah2@gmail.com`
   - `SENDER_PASSWORD=gmocguuimyufqbzi`
   - `SMTP_SERVER=smtp.gmail.com`
   - `IMAP_SERVER=imap.gmail.com`

2. **Google OAuth Token / Service Credentials (`credentials.json` / `token.json`)**:
   - Authorized to edit your Google Sheet: `https://docs.google.com/spreadsheets/d/1wGuXHelu2SqOUG2IQNMWG8gF08KqO_OcTb5rU1cziiU`

3. **Lead Dataset (`.tmp/gmb_leads_combined.csv`)**:
   - Scraped lead records with business details, email addresses, and search ranks #11 to #50+.

---

## How Everything Is Automated (6-Step Cycle)

```
[1. Verify Credentials & CRM Structure]
                  │
                  ▼
[2. Dispatch Safe Daily Email Batches]
                  │
                  ▼
[3. Scan IMAP Inbox for Client Replies]
                  │
                  ▼
[4. Promote Replied Leads to 2_Active_Deals]
                  │
                  ▼
[5. Onboard CLOSED_WON Deals to 3_Project_Milestones]
                  │
                  ▼
[6. Recalculate 4_Financial_Dashboard Revenue Metrics]
```

---

## Execution Command

```bash
python3 execution/run_autonomous_crm_cycle.py --limit 20
```

---

## Background Auto-Pilot Scheduling Options

### Option A: Schedule Tool (Background Timer)
Run automatically every 4 hours or daily in the background.

### Option B: macOS `cron` / `launchd`
Runs automatically in the background even if the terminal is closed.
