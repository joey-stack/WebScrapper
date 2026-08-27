# Directive: Autonomous AI Appointment Setter, Reply Intent Classification & Proposal Dispatch

## Purpose
Monitors the agency inbox via IMAP for incoming email responses from outreach leads. When a lead replies:
1. Performs semantic intent classification:
   - `MEETING_REQUEST`: Auto-dispatches calendar booking invitation with `CALENDAR_BOOKING_URL` and direct WhatsApp call invite.
   - `PROPOSAL_REQUEST` / `PRICING_QUESTION` / `HIGH_INTENT_CLOSE`: Auto-generates branded 1-page PDF proposal and dispatches to directed or sender address.
   - `UNSUBSCRIBE`: Immediately halts all communications and cancels sequences.
2. Extracts any alternative email addresses the client directed the proposal/information to (e.g. "please send the proposal to director@ngo.org").
3. Updates `email_sent_status` to `CLIENT_REPLIED`, logs `response_intent`, and records `directed_proposal_email`.
4. Cancels automated follow-up sequences (`CANCELLED_CLIENT_REPLIED`).
5. Promotes the lead to `2_Active_Deals` with intent-tagged deal stages (`📅 MEETING_REQUESTED`, `🔥 HIGH_INTENT_CLOSE`, `📄 PROPOSAL_AUTO_SENT`).
6. Syncs the live response data directly to the Google Sheet.

---

## Inputs
- `.env` credentials (`SENDER_EMAIL`, `SENDER_PASSWORD`, `IMAP_SERVER`, `CALENDAR_BOOKING_URL`, `MY_WHATSAPP_NUMBER`)
- Local leads CSV: `.tmp/gmb_leads_combined.csv`
- Google Sheet URL: `https://docs.google.com/spreadsheets/d/1wGuXHelu2SqOUG2IQNMWG8gF08KqO_OcTb5rU1cziiU`

---

## Tools
- `execution/track_email_responses.py`
- `execution/generate_pdf_proposal.py`
- `execution/manage_crm_engine.py`

---

## Execution Command
```bash
python execution/track_email_responses.py --limit 50
```

---

## Output Fields Added to Tracking Sheet
- `client_replied`: `YES` / `NO` / `UNSUBSCRIBED`
- `response_intent`: `MEETING_REQUEST` / `PROPOSAL_REQUEST` / `PRICING_QUESTION` / `HIGH_INTENT_CLOSE` / `UNSUBSCRIBE`
- `client_replied_at`: Timestamp of detected response (e.g. `2026-08-26 16:30`)
- `latest_client_reply_snippet`: Clean text snippet of the client's email response
- `directed_proposal_email`: Target email address specified by client if redirected
- `reply_status_notes`: Meeting invite dispatch confirmation, proposal delivery log, and status notes
