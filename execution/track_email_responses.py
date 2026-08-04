#!/usr/bin/env python3
"""
Layer 3: Execution Tool - Incoming Email Reply Tracker & Lead Conversion Monitor
Scans Gmail inbox via IMAP for incoming responses from outreach leads, records reply text/timestamps,
stops automated follow-up dispatches for replied leads, and syncs live tracking data to Google Sheets.
"""

import argparse
import datetime
import email
from email.header import decode_header
import imaplib
import os
import re
import sys
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# Ensure execution path is accessible
sys.path.insert(0, str(Path(__file__).parent))
try:
    from export_to_google_sheets import export_df_to_google_sheet
except ImportError:
    from execution.export_to_google_sheets import export_df_to_google_sheet

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

def extract_email_body(msg) -> str:
    """Extracts plain text content from an email message object."""
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
    else:
        try:
            payload = msg.get_payload(decode=True)
            if payload:
                body = payload.decode("utf-8", errors="ignore")
        except Exception:
            pass
            
    # Clean snippet (first 300 characters, remove newlines)
    clean_body = re.sub(r"\s+", " ", body).strip()
    return clean_body[:300]

def connect_imap():
    """Connects to Gmail IMAP server using environment credentials."""
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
        "client_replied_at": "",
        "latest_client_reply_snippet": "",
        "reply_status_notes": ""
    }
    for col, default_val in reply_cols.items():
        if col not in df.columns:
            df[col] = default_val

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
    print(f"[*] Incoming Email Response Tracker")
    print(f"[*] Monitoring Leads: {len(email_to_idx)} active lead email(s)")
    print(f"==================================================")

    try:
        mail = connect_imap()
        print("[+] IMAP Connected to Gmail inbox.")
    except Exception as e:
        print(f"[-] Failed to connect to IMAP: {e}")
        return

    # Search for messages
    status, messages = mail.search(None, "ALL")
    if status != "OK" or not messages[0]:
        print("[!] No messages found in INBOX.")
        mail.logout()
        return

    msg_ids = messages[0].split()
    recent_ids = msg_ids[-search_limit:]  # Inspect the last N messages
    print(f"[*] Scanning recent {len(recent_ids)} inbox messages for client replies...")

    new_replies_count = 0
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    for msg_id in reversed(recent_ids):
        status, data = mail.fetch(msg_id, "(RFC822)")
        if status != "OK":
            continue

        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)

        from_header = decode_mime_header(msg.get("From", ""))
        subject_header = decode_mime_header(msg.get("Subject", ""))

        # Extract email address from From header
        sender_match = re.search(r"[\w\.-]+@[\w\.-]+", from_header)
        if not sender_match:
            continue

        sender_email = sender_match.group(0).lower()

        # Check if sender matches any lead email in dataset
        if sender_email in email_to_idx:
            idx = email_to_idx[sender_email]
            lead_name = df.at[idx, "name"]
            snippet = extract_email_body(msg)

            # Keyword Analysis: Unsubscribe vs High Intent
            low_snippet = (subject_header + " " + snippet).lower()
            unsub_keywords = ["unsubscribe", "remove", "stop", "not interested", "do not contact", "take me off", "opt out", "dont contact", "don't contact"]
            high_intent_keywords = ["proceed", "invoice", "account detail", "bank detail", "payment", "agreed", "let's do", "send proposal", "interested", "yes", "call"]

            is_unsub = any(kw in low_snippet for kw in unsub_keywords)
            is_ready_to_close = any(kw in low_snippet for kw in high_intent_keywords)

            if is_unsub:
                stage_tag = "🛑 UNSUBSCRIBED"
                print(f"\n[🛑 UNSUBSCRIBE REQUEST DETECTED!]")
                print(f"     Lead:     {lead_name}")
                print(f"     From:     {from_header}")
                print(f"     Subject:  {subject_header}")

                df.at[idx, "client_replied"] = "UNSUBSCRIBED"
                df.at[idx, "email_sent_status"] = "UNSUBSCRIBED"
                df.at[idx, "followup_status"] = "CANCELLED_UNSUBSCRIBED"
                df.at[idx, "client_replied_at"] = now_str
                df.at[idx, "latest_client_reply_snippet"] = snippet
                df.at[idx, "reply_status_notes"] = f"[UNSUBSCRIBED] Requested removal on {now_str}"
                new_replies_count += 1
            else:
                stage_tag = "🔥 HIGH INTENT / READY TO CLOSE" if is_ready_to_close else "CLIENT_REPLIED"
                print(f"\n[🎯 REPLY DETECTED!]")
                print(f"     Lead:     {lead_name}")
                print(f"     From:     {from_header}")
                print(f"     Subject:  {subject_header}")
                print(f"     Stage:    {stage_tag}")
                print(f"     Snippet:  {snippet[:120]}...")

                df.at[idx, "client_replied"] = "YES"
                df.at[idx, "email_sent_status"] = "CLIENT_REPLIED"
                df.at[idx, "followup_status"] = "CANCELLED_CLIENT_REPLIED"
                df.at[idx, "client_replied_at"] = now_str
                df.at[idx, "latest_client_reply_snippet"] = snippet
                df.at[idx, "reply_status_notes"] = f"[{stage_tag}] Replied on {now_str}: {subject_header}"
                new_replies_count += 1

    mail.logout()

    print(f"\n==================================================")
    print(f"[+] Response Scan Complete. New Replies Detected: {new_replies_count}")
    print(f"==================================================")

    # Save updated CSV
    df.to_csv(csv_path, index=False, encoding="utf-8")
    print(f"[+] Updated dataset saved to local CSV: {csv_path}")

    # Sync to live Google Sheet
    if sheet_url:
        try:
            export_df_to_google_sheet(df, sheet_url)
        except Exception as e:
            print(f"[-] Note: Google Sheet sync skipped ({e}). Local CSV updated.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Incoming Email Reply Tracker for Outreach Leads")
    parser.add_argument("--limit", type=int, default=50, help="Number of recent inbox emails to scan (default: 50)")
    parser.add_argument("--sheet-url", type=str, default="https://docs.google.com/spreadsheets/d/1wGuXHelu2SqOUG2IQNMWG8gF08KqO_OcTb5rU1cziiU", help="Google Sheet URL")

    args = parser.parse_args()

    track_incoming_replies(
        csv_path=TMP_CSV,
        sheet_url=args.sheet_url,
        search_limit=args.limit
    )
