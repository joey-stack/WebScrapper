# Agency Power-Ups Architecture Spec

## 1. Goal & Architecture
Build 3 enterprise agency power-ups to maximize conversion rates, client proposal delivery, and outbound capacity:
1. **WhatsApp Direct 1-Click Chat Links**: Pre-formatted `https://wa.me/234...` URLs added to `1_Outreach_Pipeline` on Google Sheets.
2. **Automated PDF Proposal Generator (`execution/generate_pdf_proposal.py`)**: Sleek, branded 1-page PDF proposals generated automatically for any lead.
3. **Multi-Account Sender Rotation**: Round-robin dispatching across multiple Gmail sender accounts (`SENDER_EMAIL`, `SENDER_EMAIL_2`, etc.) in `.env`.

Live Google Sheet: `https://docs.google.com/spreadsheets/d/1wGuXHelu2SqOUG2IQNMWG8gF08KqO_OcTb5rU1cziiU`

---

## 2. Power-Up 1: WhatsApp 1-Click Chat Link
Converts local Nigerian numbers (e.g. `08098445566`) to international format (`+2348098445566`) and builds pre-filled encoded text links:
- Formula / URL: `https://wa.me/2348098445566?text=Hello%20Team%20[Name],%20I%20wanted%20to%20reach%20out%20regarding%20[Name]'s%20digital%20presence...`
- Added to `1_Outreach_Pipeline` as `whatsapp_chat_link`.

---

## 3. Power-Up 2: Automated PDF Proposal Generator (`execution/generate_pdf_proposal.py`)
Uses `reportlab` to build 1-page PDF proposals containing:
- Branded Agency Header
- Client Organization Name & Date
- Selected Service Package (Tier 1–4)
- 5-Star ELI5 Strategy & Problem Statement
- Itemized Deliverables Scope (1-5)
- One-Time Setup Fee & Monthly Maintenance Retainer
- Terms & 50% Deposit Details

CLI: `python3 execution/generate_pdf_proposal.py --lead-name "Project 1000 Innovation Hub"`
Saved output: `.tmp/proposals/<sanitized_name>_proposal.pdf`

---

## 4. Power-Up 3: Multi-Account Sender Rotation
Updates `send_outreach_emails.py` to parse indexed env variables:
- `SENDER_EMAIL`, `SENDER_PASSWORD`
- `SENDER_EMAIL_2`, `SENDER_PASSWORD_2`
- `SENDER_EMAIL_3`, `SENDER_PASSWORD_3`
Rotates sender accounts evenly across batch dispatches to preserve inbox health.
