# Directive: Automated Outreach Email Sending, Deliverability Guard & ICP Priority Dispatch

## Goal
Automate sending value-first personalized pitch emails to qualified leads extracted from Google My Business scraping, prioritize high-converting Tier A leads, enforce strict anti-spam pre-flight sanitization, track delivery status in CSV and Google Sheets, and schedule automated follow-ups for un-responded leads.

## Prerequisites & Environment Configuration
Store email credentials and settings in `.env`:
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password
SENDER_NAME=Joel Adawah
CALENDAR_BOOKING_URL=https://calendly.com/your-strategy-call
MY_WHATSAPP_NUMBER=2348183292909
```

> **Note for Gmail users**: Use a Google Account [App Password](https://myaccount.google.com/apppasswords) rather than your main account password.

## Workflow & Features (5-Part Engine Architecture)
1. **ICP Priority Sorting & Tiering**:
   - Reads `.tmp/gmb_leads_combined.csv` or live Google Sheet.
   - Automatically prioritizes `Tier A: High-Intent Hot Lead` (ICP score 80–100) first in daily dispatch queues.
2. **Pre-Flight Anti-Spam Scanner**:
   - Scans subjects and email bodies against 120+ known spam trigger words and replaces aggressive phrases with safe, professional business terminology.
3. **Multi-Account Inbox Rotation & Safe Throttling**:
   - Rotates sender accounts across active inboxes with humanized 15–35s randomized delays.
4. **4-Touch Sequence Orchestration**:
   - Touch 1 (Day 0): Initial Value Pitch (`SENT_INITIAL`)
   - Touch 2 (Day 2): WhatsApp 1-Click Conversational Touch (via `whatsapp_outreach_copy`)
   - Touch 3 (Day 4): Strategic Follow-up with mini-audit scope (`SENT_FOLLOWUP_1`)
   - Touch 4 (Day 7): Soft Breakup / Last Chance inquiry (`SEQUENCE_COMPLETE_DAY_7`)

## Execution Command Examples
- Dry run (preview dispatches without sending):
  `python execution/send_outreach_emails.py --dry-run`
- Send initial outreach pitches (priority sorted):
  `python execution/send_outreach_emails.py --send-initial --limit 25`
- Check and send due follow-ups:
  `python execution/send_outreach_emails.py --send-followups`
