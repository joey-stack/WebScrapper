# Directive: Track Incoming Email Responses & Client Reply Monitoring

## Purpose
Monitors `joeladawah2@gmail.com` via IMAP for incoming email responses from outreach leads. When a lead replies:
1. Records the reply timestamp and message snippet.
2. Updates `email_sent_status` to `CLIENT_REPLIED`.
3. Cancels automated follow-up sequences (`CANCELLED_CLIENT_REPLIED`).
4. Syncs the live response data directly to the Google Sheet.

---

## Inputs
- `.env` credentials (`SENDER_EMAIL`, `SENDER_PASSWORD`, `IMAP_SERVER`)
- Local leads CSV: `.tmp/gmb_leads_combined.csv`
- Google Sheet URL: `https://docs.google.com/spreadsheets/d/1wGuXHelu2SqOUG2IQNMWG8gF08KqO_OcTb5rU1cziiU`

---

## Tools
- `execution/track_email_responses.py`

---

## Execution Command
```bash
python3 execution/track_email_responses.py --limit 50
```

---

## Output Fields Added to Tracking Sheet
- `client_replied`: `YES` / `NO`
- `client_replied_at`: Timestamp of detected response (e.g. `2026-08-03 20:35`)
- `latest_client_reply_snippet`: Clean text snippet of the client's email response
- `reply_status_notes`: Subject line and status notes
