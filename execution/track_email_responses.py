#!/usr/bin/env python3
"""
Layer 3: Execution Tool - Autonomous AI Appointment Setter, Reply Intent Classifier & Proposal Dispatcher
Part 5 of Jordan Platten's 5-Part Client Acquisition Engine:
- Semantic Reply Intent Classification (Meeting Request, Proposal Request, Pricing Question, High Intent Close, Unsubscribe)
- Autonomous Calendar Booking Setter (dispatches Calendly/Calendar invite for meeting requests)
- Directed Proposal Email Routing (dispatches PDF proposal to requested address)
- Multi-channel WhatsApp callback reference integration
- Live Google Sheets CRM Synchronization & Deal Stage Promotion
"""

import argparse
import datetime
import email
from email.header import decode_header
import imaplib
import os
import re
import smtplib
import sys
from pathlib import Path
from bs4 import BeautifulSoup
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# Ensure execution path is accessible
sys.path.insert(0, str(Path(__file__).parent))
try:
    from export_to_google_sheets import export_df_to_google_sheet
except ImportError:
    from execution.export_to_google_sheets import export_df_to_google_sheet

try:
    from optimize_pitch_performance import record_reply_event
except ImportError:
    from execution.optimize_pitch_performance import record_reply_event

TMP_CSV = Path(__file__).parent.parent / ".tmp" / "gmb_leads_combined.csv"

def decode_mime_header(header_val: str) -> str:
    """Decodes MIME encoded headers safely."""
    if not header_val:
        return ""
    decoded_parts = []
    for text, encoding in decode_header(header_val):
        if isinstance(text, bytes):
            try:
                decoded_parts.append(text.decode(encoding or "utf-8", errors="ignore"))
            except Exception:
                decoded_parts.append(text.decode("latin1", errors="ignore"))
        else:
            decoded_parts.append(str(text))
    return " ".join(decoded_parts)

def extract_email_body_full(msg) -> tuple:
    """Extracts both full body text and a clean short snippet from an email message object."""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            if content_type == "text/plain" and "attachment" not in content_disposition:
                try:
                    payload = part.get_payload(decode=True)
                    if payload:
                        body = payload.decode("utf-8", errors="ignore")
                        break
                except Exception:
                    pass
            elif content_type == "text/html" and not body and "attachment" not in content_disposition:
                try:
                    payload = part.get_payload(decode=True)
                    if payload:
                        html_text = payload.decode("utf-8", errors="ignore")
                        soup = BeautifulSoup(html_text, "html.parser")
                        body = soup.get_text(separator=" ")
                except Exception:
                    pass
    else:
        try:
            payload = msg.get_payload(decode=True)
            if payload:
                body = payload.decode("utf-8", errors="ignore")
        except Exception:
            pass
            
    clean_snippet = re.sub(r"\s+", " ", body).strip()[:300]
    return body, clean_snippet

def extract_email_body(msg) -> str:
    _, snippet = extract_email_body_full(msg)
    return snippet

def strip_quoted_reply_text(body: str) -> str:
    """Strips out quoted reply history to isolate the client's new message."""
    lines = body.splitlines()
    clean_lines = []
    for line in lines:
        stripped = line.strip()
        if re.match(r"^On\s+.*,\s+.*wrote\s*:", stripped, flags=re.IGNORECASE):
            break
        if re.match(r"^-+\s*Original Message\s*-+", stripped, flags=re.IGNORECASE):
            break
        if re.match(r"^From:\s+.*", stripped, flags=re.IGNORECASE):
            break
        if stripped.startswith(">"):
            continue
        clean_lines.append(line)
    return "\n".join(clean_lines).strip()

def get_agency_emails() -> set:
    """Collects agency sender emails from environment to avoid false positive directed email matching."""
    emails = set()
    single_e = os.getenv("SENDER_EMAIL", "").strip().lower()
    if single_e:
        emails.add(single_e)
    raw_accounts = os.getenv("SENDER_ACCOUNTS", "").strip()
    if raw_accounts:
        for item in raw_accounts.split("|"):
            if ":" in item:
                emails.add(item.split(":", 1)[0].strip().lower())
    for i in range(1, 6):
        e_var = os.getenv(f"SENDER_EMAIL_{i}", "").strip().lower()
        if e_var:
            emails.add(e_var)
    return emails

def is_valid_directed_email(candidate: str, sender_email: str, agency_emails: set) -> bool:
    if not candidate or "@" not in candidate:
        return False
    candidate_clean = candidate.lower().strip(".,;:<>()'\"")
    if re.search(r"\.(png|jpg|jpeg|gif|svg|webp|css|js)$", candidate_clean, flags=re.IGNORECASE):
        return False
    if candidate_clean in {e.lower() for e in agency_emails if e}:
        return False
    dummy_domains = {"example.com", "domain.com", "yourdomain.com", "email.com", "sentry.io", "wixpress.com", "schema.org", "w3.org"}
    domain = candidate_clean.split("@")[-1].lower()
    if domain in dummy_domains:
        return False
    return True

def extract_directed_email(raw_body: str, sender_email: str, agency_emails: set = None) -> str:
    """Detects if the client requested sending or forwarding the proposal to an alternative email."""
    if not raw_body:
        return ""
    if agency_emails is None:
        agency_emails = set()

    clean_new_text = strip_quoted_reply_text(raw_body)
    if not clean_new_text:
        clean_new_text = raw_body

    directional_patterns = [
        r"(?:send|forward|direct|mail|reach|contact|email|share|cc|copy|submit|write|deliver|route|dispatch)(?:\s+[\w\'-]+){0,8}\s+(?:to|at|via|on|through|address)?\s*[:\s]*<?([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})>?",
        r"(?:new|alternative|alternate|personal|official|director\'?s?|colleague\'?s?|team\'?s?|assistant\'?s?|boss\'?s?|manager\'?s?|secretary\'?s?|head\'?s?|md\'?s?|ceo\'?s?)\s+(?:email|contact|address)?\s*(?:is|:|\-)?\s*<?([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})>?",
        r"(?:my\s+email\s+is|our\s+email\s+is|reach\s+(?:me|us)\s+at|contact\s+(?:me|us)\s+at|email\s+(?:me|us)\s+at)\s*[:\s]*<?([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})>?",
        r"(?:to|cc)\s*:\s*<?([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})>?"
    ]

    for pat in directional_patterns:
        matches = re.finditer(pat, clean_new_text, flags=re.IGNORECASE)
        for match in matches:
            candidate = match.group(1).lower().strip(".,;:<>()'\"")
            if is_valid_directed_email(candidate, sender_email, agency_emails):
                return candidate

    all_emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", clean_new_text)
    for e in all_emails:
        clean_e = e.lower().strip(".,;:<>()'\"")
        if is_valid_directed_email(clean_e, sender_email, agency_emails) and clean_e != sender_email.lower():
            return clean_e

    return ""

def classify_reply_intent(reply_text: str, subject: str) -> str:
    """Classifies client reply into discrete intent categories for autonomous handling."""
    combined = (subject + " " + reply_text).lower()
    body_lower = reply_text.lower()

    unsub_keywords = ["unsubscribe", "remove", "stop", "not interested", "do not contact", "take me off", "opt out", "dont contact", "don't contact", "leave me alone"]
    if any(kw in combined for kw in unsub_keywords):
        return "UNSUBSCRIBE"

    high_intent_keywords = ["proceed", "invoice", "account detail", "bank detail", "payment", "agreed", "let's do it", "lets do it", "ready to start", "send agreement"]
    if any(kw in combined for kw in high_intent_keywords):
        return "HIGH_INTENT_CLOSE"

    meeting_keywords = ["call me", "hop on a call", "schedule", "calendar", "meeting", "when are you free", "zoom", "google meet", "phone call", "let's talk", "lets talk", "book a time", "discuss on call"]
    if any(kw in combined for kw in meeting_keywords):
        return "MEETING_REQUEST"

    # Specific direct pricing questions in the body take precedence
    if any(kw in body_lower for kw in ["how much", "what is the cost", "package cost", "cost of", "what do you charge", "what is the fee", "what are the fees", "what are your rates"]):
        return "PRICING_QUESTION"

    proposal_keywords = ["proposal", "quote", "send info", "send details", "send deck", "send scope", "scope breakdown", "send it", "forward to", "forward all", "forward details", "forward", "details", "reach out to"]
    if any(kw in combined for kw in proposal_keywords):
        return "PROPOSAL_REQUEST"

    pricing_keywords = ["how much", "cost", "rate", "rates", "fee", "fees", "price", "pricing", "budget", "what do you charge"]
    if any(kw in combined for kw in pricing_keywords):
        return "PRICING_QUESTION"

    return "GENERAL_INQUIRY"

def send_meeting_invite_email(recipient_email: str, org_name: str, requester_email: str = None, cc_email: str = None) -> bool:
    """Dispatches an autonomous meeting scheduling invitation with Calendar Booking URL and WhatsApp option."""
    sender_email = os.getenv("SENDER_EMAIL", "").strip()
    sender_password = os.getenv("SENDER_PASSWORD", "").strip()
    sender_name = os.getenv("SENDER_NAME", "Joel Adawah").strip()
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    calendar_url = os.getenv("CALENDAR_BOOKING_URL", "https://calendly.com/your-strategy-call").strip()
    my_wa = os.getenv("MY_WHATSAPP_NUMBER", "2348183292909").strip()

    if not sender_email or not sender_password:
        print("[-] Error: SENDER_EMAIL or SENDER_PASSWORD missing in .env")
        return False

    msg = MIMEMultipart()
    msg["From"] = f"{sender_name} <{sender_email}>"
    msg["To"] = recipient_email
    recipients = [recipient_email]

    if cc_email and cc_email.lower() != recipient_email.lower():
        msg["Cc"] = cc_email
        recipients.append(cc_email)

    msg["Subject"] = f"Strategy Call Scheduling - {org_name}"

    greeting_ref = f"As requested by {requester_email}, " if (requester_email and requester_email.lower() != recipient_email.lower()) else ""

    body_text = f"""Hi Team {org_name},

Thank you for your response! {greeting_ref}I would be delighted to connect for a quick 10-minute strategy call to walk you through our tailored digital roadmap for {org_name}.

To pick a date and time that works best for your schedule, please select a slot on my direct calendar here:
👉 {calendar_url}

Alternatively, if you prefer a quick phone or WhatsApp conversation, you can connect directly with my line at:
👉 WhatsApp: https://wa.me/{my_wa} (+{my_wa})

Looking forward to speaking with you!

Warm regards,

{sender_name}
Digital Strategy & Growth Director
"""
    msg.attach(MIMEText(body_text, "plain"))

    try:
        smtp = smtplib.SMTP(smtp_server, smtp_port)
        smtp.ehlo()
        smtp.starttls()
        smtp.login(sender_email, sender_password)
        smtp.sendmail(sender_email, recipients, msg.as_string())
        smtp.quit()
        print(f"[+] SUCCESS! AI Appointment Setter dispatched calendar invite to {recipient_email}")
        return True
    except Exception as e:
        print(f"[-] Failed to send meeting invite: {e}")
        return False

def connect_imap():
    user = os.getenv("SENDER_EMAIL", "").strip()
    password = os.getenv("SENDER_PASSWORD", "").strip()
    imap_server = os.getenv("IMAP_SERVER", "imap.gmail.com")

    if not user or not password:
        raise ValueError("SENDER_EMAIL and SENDER_PASSWORD must be configured in .env!")

    mail = imaplib.IMAP4_SSL(imap_server, 993)
    mail.login(user, password)
    mail.select("inbox")
    return mail

def track_incoming_replies(csv_path: Path, sheet_url: str = None, search_limit: int = 50):
    if not csv_path.exists():
        print(f"[-] Error: Combined leads CSV not found at {csv_path}")
        return

    df = pd.read_csv(csv_path)

    # Initialize reply tracking columns if missing
    reply_cols = {
        "client_replied": "NO",
        "response_intent": "",
        "client_replied_at": "",
        "latest_client_reply_snippet": "",
        "directed_proposal_email": "",
        "reply_status_notes": ""
    }
    for col, default_val in reply_cols.items():
        if col not in df.columns:
            df[col] = default_val
        else:
            df[col] = df[col].astype(object)

    # Extract all recipient email addresses from dataset
    email_to_idx = {}
    for idx, row in df.iterrows():
        raw_e = str(row.get("email", "")).strip().lower()
        if "@" in raw_e:
            for single_e in raw_e.split(","):
                clean_e = single_e.strip()
                if "@" in clean_e:
                    email_to_idx[clean_e] = idx

    print(f"\n==================================================")
    print(f"[*] Autonomous AI Reply Tracker & Appointment Setter")
    print(f"[*] Monitoring Leads: {len(email_to_idx)} active lead email(s)")
    print(f"==================================================")

    try:
        mail = connect_imap()
        print("[+] IMAP Connected to Gmail inbox.")
    except Exception as e:
        print(f"[-] Failed to connect to IMAP: {e}")
        return

    status, messages = mail.search(None, "ALL")
    if status != "OK" or not messages[0]:
        print("[!] No messages found in INBOX.")
        mail.logout()
        return

    if not email_to_idx:
        print("[*] No active lead emails to monitor for replies.")
        mail.logout()
        return

    msg_ids = messages[0].split()
    recent_ids = msg_ids[-search_limit:]
    print(f"[*] Scanning recent {len(recent_ids)} inbox message headers for client replies...")

    new_replies_count = 0
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    agency_emails = get_agency_emails()

    for msg_id in reversed(recent_ids):
        status, data = mail.fetch(msg_id, "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])")
        if status != "OK" or not data or not data[0] or not isinstance(data[0], tuple):
            continue

        raw_header = data[0][1]
        msg_header = email.message_from_bytes(raw_header)

        from_header = decode_mime_header(msg_header.get("From", ""))
        subject_header = decode_mime_header(msg_header.get("Subject", ""))

        sender_match = re.search(r"[\w\.-]+@[\w\.-]+", from_header)
        if not sender_match:
            continue

        sender_email = sender_match.group(0).lower()

        if sender_email in email_to_idx:
            status_full, data_full = mail.fetch(msg_id, "(RFC822)")
            if status_full != "OK" or not data_full:
                continue
            raw_email = data_full[0][1]
            msg = email.message_from_bytes(raw_email)

            idx = email_to_idx[sender_email]
            lead_name = df.at[idx, "name"]
            body_full, snippet = extract_email_body_full(msg)

            directed_email = extract_directed_email(body_full, sender_email, agency_emails)
            intent = classify_reply_intent(body_full, subject_header)

            low_text = body_full.lower()
            client_asked_no_reply_to_orig = bool(directed_email and any(kw in low_text for kw in ["don't email this", "dont email this", "not this email", "don't reply here", "dont reply here", "use this other", "wrong email"]))
            target_proposal_email = directed_email if directed_email else sender_email
            cc_addr = sender_email if (directed_email and not client_asked_no_reply_to_orig) else None

            print(f"\n[🎯 INCOMING CLIENT REPLY DETECTED!]")
            print(f"     Lead:     {lead_name}")
            print(f"     From:     {from_header}")
            print(f"     Subject:  {subject_header}")
            print(f"     Intent:   {intent}")
            print(f"     Snippet:  {snippet[:120]}...")
            if directed_email:
                print(f"     [💡 Directed Recipient]: {directed_email}")

            variant_id = str(df.at[idx, "pitch_variant_id"] if "pitch_variant_id" in df.columns else "AUTHORITY_V1").strip()
            try:
                record_reply_event(variant_id, intent=intent)
            except Exception:
                pass

            if intent == "UNSUBSCRIBE":
                df.at[idx, "client_replied"] = "UNSUBSCRIBED"
                df.at[idx, "response_intent"] = "UNSUBSCRIBE"
                df.at[idx, "email_sent_status"] = "UNSUBSCRIBED"
                df.at[idx, "followup_status"] = "CANCELLED_UNSUBSCRIBED"
                df.at[idx, "client_replied_at"] = now_str
                df.at[idx, "latest_client_reply_snippet"] = snippet
                df.at[idx, "reply_status_notes"] = f"[UNSUBSCRIBED] Requested removal on {now_str}"
                new_replies_count += 1

            elif intent == "MEETING_REQUEST":
                print(f"[*] AUTO-DISPATCHING STRATEGY CALL CALENDAR INVITE FOR: {lead_name}...")
                send_ok = send_meeting_invite_email(
                    recipient_email=target_proposal_email,
                    org_name=lead_name,
                    requester_email=sender_email if directed_email else None,
                    cc_email=cc_addr
                )
                
                df.at[idx, "client_replied"] = "YES"
                df.at[idx, "response_intent"] = "MEETING_REQUEST"
                df.at[idx, "email_sent_status"] = "CLIENT_REPLIED"
                df.at[idx, "followup_status"] = "CANCELLED_CLIENT_REPLIED"
                df.at[idx, "client_replied_at"] = now_str
                df.at[idx, "latest_client_reply_snippet"] = snippet
                if directed_email:
                    df.at[idx, "directed_proposal_email"] = directed_email
                df.at[idx, "reply_status_notes"] = f"[MEETING_INVITE_AUTO_SENT] Calendar booking invite emailed to {target_proposal_email} on {now_str}"
                new_replies_count += 1

            elif intent in ["PROPOSAL_REQUEST", "PRICING_QUESTION", "HIGH_INTENT_CLOSE", "GENERAL_INQUIRY"]:
                print(f"[*] AUTO-GENERATING & EMAILING PDF PROPOSAL FOR: {lead_name}...")
                try:
                    from generate_pdf_proposal import generate_pdf_proposal_for_lead, send_proposal_email
                    pdf_path = generate_pdf_proposal_for_lead(lead_name)
                    if pdf_path:
                        send_ok = send_proposal_email(
                            recipient_email=target_proposal_email,
                            org_name=lead_name,
                            pdf_path=pdf_path,
                            cc_email=cc_addr,
                            requester_email=sender_email if directed_email else None
                        )
                        if send_ok:
                            if directed_email:
                                df.at[idx, "reply_status_notes"] = f"[PROPOSAL_AUTO_SENT] PDF proposal emailed to directed address '{target_proposal_email}' (requested by {sender_email}) on {now_str}"
                            else:
                                df.at[idx, "reply_status_notes"] = f"[PROPOSAL_AUTO_SENT] PDF proposal emailed to {sender_email} on {now_str}"
                except Exception as pe:
                    print(f"[-] Failed auto-generating PDF proposal: {pe}")

                df.at[idx, "client_replied"] = "YES"
                df.at[idx, "response_intent"] = intent
                df.at[idx, "email_sent_status"] = "CLIENT_REPLIED"
                df.at[idx, "followup_status"] = "CANCELLED_CLIENT_REPLIED"
                df.at[idx, "client_replied_at"] = now_str
                df.at[idx, "latest_client_reply_snippet"] = snippet
                if directed_email:
                    df.at[idx, "directed_proposal_email"] = directed_email
                if not df.at[idx, "reply_status_notes"]:
                    df.at[idx, "reply_status_notes"] = f"[{intent}] Replied on {now_str}: {subject_header}"
                new_replies_count += 1

            # Dispatch Instant WhatsApp Mobile Alert
            if intent in ["MEETING_REQUEST", "PROPOSAL_REQUEST", "PRICING_QUESTION", "HIGH_INTENT_CLOSE", "GENERAL_INQUIRY"]:
                wa_direct = str(df.at[idx, "whatsapp_chat_link"] if "whatsapp_chat_link" in df.columns else "")
                try:
                    from send_mobile_alerts import send_hot_lead_whatsapp_alert
                    send_hot_lead_whatsapp_alert(
                        lead_name=lead_name,
                        intent=intent,
                        snippet=snippet,
                        target_email=target_proposal_email,
                        wa_direct_link=wa_direct,
                        sender_email=sender_email
                    )
                except Exception as we:
                    print(f"[-] WhatsApp alert warning: {we}")

    mail.logout()

    print(f"\n==================================================")
    print(f"[+] Response Scan Complete. Replies Processed: {new_replies_count}")
    print(f"==================================================")

    df.to_csv(csv_path, index=False, encoding="utf-8")
    print(f"[+] Updated dataset saved to local CSV: {csv_path}")

    if sheet_url:
        try:
            export_df_to_google_sheet(df, sheet_url)
        except Exception as e:
            print(f"[-] Note: Google Sheet sync skipped ({e}). Local CSV updated.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Incoming Email Reply Tracker & AI Appointment Setter")
    parser.add_argument("--limit", type=int, default=50, help="Number of recent inbox emails to scan (default: 50)")
    parser.add_argument("--sheet-url", type=str, default="https://docs.google.com/spreadsheets/d/1wGuXHelu2SqOUG2IQNMWG8gF08KqO_OcTb5rU1cziiU", help="Google Sheet URL")

    args = parser.parse_args()

    track_incoming_replies(
        csv_path=TMP_CSV,
        sheet_url=args.sheet_url,
        search_limit=args.limit
    )
