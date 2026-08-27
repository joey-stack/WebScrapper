# Agency Power-Ups Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build 3 Agency Power-Ups: WhatsApp 1-click chat links, automated PDF proposal generator (`execution/generate_pdf_proposal.py`), and multi-account sender rotation in `send_outreach_emails.py`.

**Architecture:** 
- `qualify_and_pitch_leads.py`: Adds `whatsapp_chat_link` generator.
- `execution/generate_pdf_proposal.py`: PDF generation script using `reportlab`.
- `execution/send_outreach_emails.py`: Enhanced multi-sender rotation parser.

**Tech Stack:** Python 3, `reportlab`, `pandas`, `gspread`, `dotenv`.

## Global Constraints
- Target Google Sheet: `https://docs.google.com/spreadsheets/d/1wGuXHelu2SqOUG2IQNMWG8gF08KqO_OcTb5rU1cziiU`
- PDF Output Path: `.tmp/proposals/`
- WhatsApp Format: `https://wa.me/234...`

---

### Task 1: Add WhatsApp 1-Click Chat Links to Dataset & Google Sheet

**Files:**
- Modify: `execution/qualify_and_pitch_leads.py`
- Test: `.tmp/gmb_leads_combined.csv`

**Interfaces:**
- Consumes: Lead phone numbers & organization names
- Produces: `whatsapp_chat_link` column in dataset & Google Sheet

- [x] **Step 1: Write `generate_whatsapp_link(phone: str, name: str)` helper**

```python
def generate_whatsapp_link(phone_str: str, lead_name: str) -> str:
    if not phone_str or pd.isna(phone_str):
        return ""
    
    digits = re.sub(r"\D", "", str(phone_str))
    if not digits:
        return ""
        
    if digits.startswith("0") and len(digits) == 11:
        clean_num = "234" + digits[1:]
    elif digits.startswith("234"):
        clean_num = digits
    else:
        clean_num = "234" + digits

    clean_name = get_clean_name(lead_name)
    msg = f"Hello Team {clean_name}, I noticed your organization on Google Maps and wanted to reach out regarding your digital presence."
    encoded_msg = urllib.parse.quote(msg)
    return f"https://wa.me/{clean_num}?text={encoded_msg}"
```

- [x] **Step 2: Add `whatsapp_chat_link` to `process_and_qualify_dataframe`**
- [x] **Step 3: Run dataset re-qualification and sync to Google Sheet**

---

### Task 2: Create PDF Proposal Generator (`execution/generate_pdf_proposal.py`)

**Files:**
- Create: `execution/generate_pdf_proposal.py`

**Interfaces:**
- Consumes: `.tmp/gmb_leads_combined.csv`
- Produces: PDF proposal files in `.tmp/proposals/`

- [x] **Step 1: Write `execution/generate_pdf_proposal.py` script using `reportlab`**
- [x] **Step 2: Test PDF generation for a sample lead**

---

### Task 3: Enable Multi-Account Sender Rotation in `send_outreach_emails.py`

**Files:**
- Modify: `execution/send_outreach_emails.py`

**Interfaces:**
- Consumes: `.env` indexed variables (`SENDER_EMAIL_2`, `SENDER_PASSWORD_2`, etc.)
- Produces: Round-robin sender selection in `parse_sender_accounts()`

- [x] **Step 1: Enhance `parse_sender_accounts()` to scan `SENDER_EMAIL_1..5`**
- [x] **Step 2: Test multi-account parsing and verification**
