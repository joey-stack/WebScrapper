# Directive: Automated Outreach Email Sending & Follow-up Scheduling

## Goal
Automate sending value-first personalized pitch emails to qualified leads extracted from Google My Business scraping, track delivery status in CSV and Google Sheets, and schedule automated follow-ups for un-responded leads.

## Prerequisites & Environment Configuration
Store email credentials in `.env`:
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password
SENDER_NAME=Your Name / Agency Name
```

> **Note for Gmail users**: Use a Google Account [App Password](https://myaccount.google.com/apppasswords) rather than your main account password.

## Workflow & Features
1. **Initial Pitch Dispatch**:
   - Reads `.tmp/gmb_leads_combined.csv` or live Google Sheet.
   - Filters leads with valid email addresses.
   - Sends personalized outreach pitch (`personalized_pitch`).
   - Marks status as `SENT_INITIAL` and records timestamp in `initial_email_sent_at`.
   - Schedules Follow-up #1 due date (+3 days) in `followup_due_at`.

2. **Automated Follow-up Scheduling**:
   - When run with `--followup`, checks leads where `followup_due_at` is past due and `response_received` is False.
   - Dispatches soft follow-up email citing initial message and strategic proposal.
   - Marks status as `SENT_FOLLOWUP_1` and records timestamp in `followup_sent_at`.

3. **Deliverable & Status Tracking**:
   - Updates local CSV `.tmp/gmb_leads_combined.csv`.
   - Syncs live Google Sheet with updated delivery statuses (`email_sent_status`, `initial_email_sent_at`, `followup_due_at`).

## Execution Command Examples
- Dry run (preview emails without sending):
  `python3 execution/send_outreach_emails.py --dry-run`
- Send initial outreach pitch:
  `python3 execution/send_outreach_emails.py --send-initial`
- Check and send due follow-ups:
  `python3 execution/send_outreach_emails.py --send-followups`
