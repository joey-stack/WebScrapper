# Directive: Autonomous Master CRM Orchestration & 5-Part Acquisition Machine

## Purpose
Runs a 100% hands-off, zero-click autonomous cycle based on Jordan Platten's 5-Part Client Acquisition Engine that coordinates lead scraping, ICP scoring, anti-spam sanitized outreach email dispatches, incoming reply tracking & intent classification, autonomous calendar meeting scheduling / directed proposal dispatch, lead pipeline promotion, project deliverable onboarding, and real-time financial dashboard sync.

---

## Pre-flight Requirements

1. **Environment Credentials (`.env`)**:
   - `SENDER_EMAIL=your_email@gmail.com`
   - `SENDER_PASSWORD=your_app_password`
   - `SMTP_SERVER=smtp.gmail.com`
   - `IMAP_SERVER=imap.gmail.com`
   - `CALENDAR_BOOKING_URL=https://calendly.com/your-strategy-call`
   - `MY_WHATSAPP_NUMBER=2348183292909`

2. **Google OAuth Token / Service Credentials (`credentials.json` / `token.json`)**:
   - Authorized to edit your master Google Sheet: `https://docs.google.com/spreadsheets/d/1wGuXHelu2SqOUG2IQNMWG8gF08KqO_OcTb5rU1cziiU`

---

## The 6-Step Autonomous Cycle

```
[0. Scrape Fresh Daily Buried Leads (#11-50+)]
                   │
                   ▼
[1. ICP Scoring (0-100), Priority Tiering & CRM Init]
                   │
                   ▼
[2. Dispatch Safe Daily Email Batches (Anti-Spam Sanitized, Tier A First)]
                   │
                   ▼
[3. Scan IMAP Inbox for Client Replies & Semantic Intent]
   ├── MEETING_REQUEST ➔ Auto-Dispatch Calendar Booking Invite
   ├── PROPOSAL_REQUEST ➔ Auto-Generate & Email PDF Proposal
   └── UNSUBSCRIBE ➔ Cancel Sequences & Halt Outreach
                   │
                   ▼
[4. Promote Replied Leads to 2_Active_Deals with Intent Tags]
                   │
                   ▼
[5. Onboard CLOSED_WON Deals to 3_Project_Milestones Checklist]
                   │
                   ▼
[6. Recalculate 4_Financial_Dashboard Revenue & Conversion Metrics]
```

---

## Execution Command

```bash
python execution/run_autonomous_crm_cycle.py --limit 20
```
