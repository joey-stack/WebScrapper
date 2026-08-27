#!/usr/bin/env python3
"""
Layer 3: Execution Tool - Automated Multi-Touch Smart Follow-Up Engine
Implements Jordan Platten's & High-Ticket Agency Follow-Up Framework:
- Touch 1 (Day 0): Initial Pitch (Competitor name + Review audit + GEO Angle)
- Touch 2 (Day 3 / 72h): Value & Competitor Gap Bump (Cites #1 Competitor & Lost Calls)
- Touch 3 (Day 7 / 168h): 'Permission to Close File' Soft Takeaway (Statistically 48% Response Spike)
- Touch 4 (Day 14 / 336h): Free AI Knowledge Graph Schema Gift (Pure Value Drop)

Features:
1. Threaded Replies (Maintains email conversation history with Re: Subject).
2. Anti-Ban Throttling & Spam Trigger Scanning.
3. Multi-Account SMTP Inbox Rotation.
4. Auto-Exclusion for Replied or Unsubscribed Leads.
5. Real-Time Google Sheets CRM Synchronization.
"""

import argparse
import datetime
import os
import random
import re
import smtplib
import sys
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# Ensure utf-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Ensure execution path is accessible
sys.path.insert(0, str(Path(__file__).parent))
try:
    from export_to_google_sheets import export_df_to_google_sheet
except ImportError:
    from execution.export_to_google_sheets import export_df_to_google_sheet

try:
    from send_outreach_emails import parse_sender_accounts, connect_smtp_account, scan_and_sanitize_spam
except ImportError:
    from execution.send_outreach_emails import parse_sender_accounts, connect_smtp_account, scan_and_sanitize_spam

TMP_CSV = Path(__file__).parent.parent / ".tmp" / "gmb_leads_combined.csv"
DEFAULT_SHEET_URL = "https://docs.google.com/spreadsheets/d/1wGuXHelu2SqOUG2IQNMWG8gF08KqO_OcTb5rU1cziiU"

def get_clean_org_name(raw_name: str) -> str:
    clean = raw_name.split("|")[0].split("-")[0].strip()
    return clean or raw_name

def generate_touch2_competitor_gap_pitch(row: dict) -> str:
    """Touch 2 (Day 3): Value & Competitor Gap Bump."""
    name = get_clean_org_name(str(row.get("name", "Organization")))
    location = "Abuja" if "abuja" in str(row.get("address", "")).lower() else ("Lagos" if "lagos" in str(row.get("address", "")).lower() else "Nigeria")
    category = str(row.get("category", "") or "local").lower()
    
    top_comp = str(row.get("top_competitor_name", "") or "").strip()
    if not top_comp or top_comp.lower() == name.lower() or "top 3" in top_comp.lower():
        top_comp = f"competing {category} organizations in {location}"

    whatsapp_num = os.getenv("MY_WHATSAPP_NUMBER", "2348183292909")
    calendar_url = os.getenv("CALENDAR_BOOKING_URL", "").strip()
    cal_text = f" or grab 5 minutes on my calendar ({calendar_url})" if calendar_url else ""

    body = (
        f"Hi {name} Team,\n\n"
        f"I wanted to follow up quickly on my note from a few days ago regarding {name}'s Google Maps search rank in {location}.\n\n"
        f"Inbound search interest for {category} services in {location} is high, but right now {top_comp} is capturing over 80% of local phone calls and inquiries because {name} is currently sitting outside the primary Top 3 Map Pack.\n\n"
        f"Have you had 3 minutes to review the tailored digital roadmap we put together to move {name} ahead of {top_comp}?\n\n"
        f"Let me know if you'd like me to send the 1-page PDF over, or we can connect briefly on WhatsApp (+{whatsapp_num}){cal_text}.\n\n"
        f"Best regards,\n"
        f"{os.getenv('SENDER_NAME', 'Joel Adawah')}\n\n"
        f"---\n"
        f"P.S. If you prefer not to receive further updates, simply reply 'unsubscribe' and we will remove your email immediately."
    )
    clean_body, _ = scan_and_sanitize_spam(body)
    return clean_body

def generate_touch3_breakup_pitch(row: dict) -> str:
    """Touch 3 (Day 7): Soft 'Permission to Close File' Takeaway."""
    name = get_clean_org_name(str(row.get("name", "Organization")))
    location = "Abuja" if "abuja" in str(row.get("address", "")).lower() else ("Lagos" if "lagos" in str(row.get("address", "")).lower() else "Nigeria")
    
    body = (
        f"Hi {name} Team,\n\n"
        f"I haven't heard back, so I assume improving {name}'s web presence and Google search visibility in {location} isn't a priority for your leadership team right now.\n\n"
        f"Should I close out this file, or would you still like to review the complimentary 1-page digital roadmap before we archive it?\n\n"
        f"Either way, wishing {name} continued growth and success!\n\n"
        f"Warm regards,\n"
        f"{os.getenv('SENDER_NAME', 'Joel Adawah')}\n\n"
        f"---\n"
        f"P.S. Reply 'unsubscribe' to stop all future messages."
    )
    clean_body, _ = scan_and_sanitize_spam(body)
    return clean_body

def generate_touch4_geo_schema_gift_pitch(row: dict) -> str:
    """Touch 4 (Day 14): Free AI Knowledge Graph & GEO Schema Gift Drop."""
    name = get_clean_org_name(str(row.get("name", "Organization")))
    location = "Abuja" if "abuja" in str(row.get("address", "")).lower() else ("Lagos" if "lagos" in str(row.get("address", "")).lower() else "Nigeria")
    
    body = (
        f"Hi {name} Team,\n\n"
        f"Even if we don't work together right now, I wanted to leave your team with something valuable.\n\n"
        f"We generated a verified Google & ChatGPT JSON-LD Knowledge Graph Schema tag specifically for {name} to help your organization get cited by Google Gemini AI Overviews and Perplexity search in {location}.\n\n"
        f"If you'd like me to send the code block over to your IT or web manager to install (100% complimentary), just reply 'send schema' and I'll deliver it immediately.\n\n"
        f"All the best with your programs!\n\n"
        f"{os.getenv('SENDER_NAME', 'Joel Adawah')}"
    )
    clean_body, _ = scan_and_sanitize_spam(body)
    return clean_body

def dispatch_smart_followups(
    csv_path: Path = TMP_CSV,
    sheet_url: str = DEFAULT_SHEET_URL,
    limit: int = 15,
    dry_run: bool = False
) -> int:
    """
    Scans for leads due for smart follow-ups and dispatches them sequentially.
    """
    if not csv_path.exists():
        print(f"[-] Error: Leads CSV not found at {csv_path}")
        return 0

    accounts = parse_sender_accounts()
    if not accounts and not dry_run:
        print("[!] Error: No valid sender accounts found in .env!")
        return 0

    df = pd.read_csv(csv_path)

    # Initialize tracking columns
    for col in ["followup_status", "followup_due_at", "followup_sent_at", "email_sent_status", "client_replied"]:
        if col not in df.columns:
            df[col] = ""
        else:
            df[col] = df[col].astype(object)

    now = datetime.datetime.now()
    sent_count = 0
    account_idx = 0

    print("\n==================================================")
    print("🔁 AUTOMATED SMART MULTI-TOUCH FOLLOW-UP ENGINE")
    print(f"[*] Current Time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"[*] Senders Available: {len(accounts)} account(s)")
    print(f"[*] Total Database: {len(df)} leads")
    print("==================================================")

    for idx, row in df.iterrows():
        if sent_count >= limit:
            print(f"\n[+] Reached safe batch limit of {limit} follow-ups.")
            break

        email_str = str(row.get("email", "") or "").strip()
        if not email_str or "@" not in email_str:
            continue

        # Exclusion guardrails
        sent_status = str(row.get("email_sent_status", "")).upper()
        f_status = str(row.get("followup_status", "")).upper()
        replied_status = str(row.get("client_replied", "")).upper()

        if "UNSUBSCRIBE" in sent_status or "UNSUBSCRIBE" in f_status:
            continue
        if "YES" in replied_status or "REPLIED" in replied_status:
            continue
        if sent_status not in ["SENT", "DRY_RUN_SENT"]:
            continue  # Initial email hasn't been sent yet

        initial_sent_str = str(row.get("initial_email_sent_at", "") or "").strip()
        if not initial_sent_str:
            continue

        try:
            initial_dt = datetime.datetime.strptime(initial_sent_str, "%Y-%m-%d %H:%M")
        except Exception:
            try:
                initial_dt = datetime.datetime.strptime(initial_sent_str.split("T")[0], "%Y-%m-%d")
            except Exception:
                continue

        elapsed_hours = (now - initial_dt).total_seconds() / 3600.0
        lead_name = str(row.get("name", "Organization")).strip()
        clean_name = get_clean_org_name(lead_name)
        recipient_email = [e.strip() for e in email_str.split(",") if "@" in e][0]
        initial_subject = str(row.get("email_subject", "") or f"Strategic roadmap for {clean_name}").strip()
        reply_subject = f"Re: {initial_subject}"

        # Determine which touch is due:
        body = ""
        new_status = ""
        touch_label = ""

        # Touch 2: Day 3 (72h+)
        if elapsed_hours >= 72 and f_status in ["", "NOT_DUE", "SCHEDULED_DAY_3", "PENDING"]:
            touch_label = "Touch 2 (Day 3: Competitor Gap & Value Bump)"
            body = generate_touch2_competitor_gap_pitch(row.to_dict())
            new_status = "SENT_FOLLOWUP_1_DAY_3" if not dry_run else "DRY_RUN_FOLLOWUP_1"

        # Touch 3: Day 7 (168h+)
        elif elapsed_hours >= 168 and f_status in ["SENT_FOLLOWUP_1_DAY_3", "DRY_RUN_FOLLOWUP_1"]:
            touch_label = "Touch 3 (Day 7: Soft Takeaway & Permission to Close File)"
            body = generate_touch3_breakup_pitch(row.to_dict())
            new_status = "SENT_FOLLOWUP_2_DAY_7" if not dry_run else "DRY_RUN_FOLLOWUP_2"

        # Touch 4: Day 14 (336h+) - Pure Value GEO Schema Drop
        elif elapsed_hours >= 336 and f_status in ["SENT_FOLLOWUP_2_DAY_7", "DRY_RUN_FOLLOWUP_2"]:
            touch_label = "Touch 4 (Day 14: Complimentary AI GEO Schema Drop)"
            body = generate_touch4_geo_schema_gift_pitch(row.to_dict())
            new_status = "SEQUENCE_COMPLETED" if not dry_run else "DRY_RUN_SEQUENCE_COMPLETE"

        if not body:
            continue

        current_account = accounts[account_idx % len(accounts)] if accounts else {"email": "dryrun@domain.com"}
        account_idx += 1

        print(f"\n---> [{sent_count+1}/{limit}] Dispatching {touch_label}:")
        print(f"     Lead:     {clean_name} (Initial sent {elapsed_hours:.1f}h ago)")
        print(f"     From:     {current_account['email']}")
        print(f"     To:       {recipient_email}")
        print(f"     Subject:  {reply_subject}")

        if dry_run:
            print("     [DRY RUN - Follow-up not physically sent]")
        else:
            try:
                smtp_conn = connect_smtp_account(current_account)
                msg = MIMEMultipart()
                msg["From"] = f"{os.getenv('SENDER_NAME', 'Joel Adawah')} <{current_account['email']}>"
                msg["To"] = recipient_email
                msg["Subject"] = reply_subject
                msg.attach(MIMEText(body, "plain"))
                smtp_conn.send_message(msg)
                smtp_conn.quit()

                delay = random.randint(15, 30)
                print(f"     [+] Success! Humanized delay {delay}s...")
                time.sleep(delay)
            except Exception as send_err:
                print(f"     [-] Error sending follow-up: {send_err}")
                continue

        df.at[idx, "followup_status"] = new_status
        df.at[idx, "followup_sent_at"] = now.strftime("%Y-%m-%d %H:%M")
        sent_count += 1

    df.to_csv(csv_path, index=False, encoding="utf-8")
    print(f"\n[+] Follow-Up Engine Finished. Dispatched: {sent_count} follow-up(s).")
    print(f"[+] Updated CSV saved to: {csv_path}")

    if sheet_url:
        try:
            export_df_to_google_sheet(df, sheet_url)
        except Exception as e:
            print(f"[-] Sheet sync note: {e}")

    return sent_count

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated Smart Multi-Touch Follow-Up Engine")
    parser.add_argument("--limit", type=int, default=15, help="Max follow-ups to dispatch")
    parser.add_argument("--dry-run", action="store_true", help="Preview dispatches without sending")
    parser.add_argument("--sheet-url", type=str, default=DEFAULT_SHEET_URL, help="Google Sheet CRM URL")

    args = parser.parse_args()
    dispatch_smart_followups(limit=args.limit, dry_run=args.dry_run, sheet_url=args.sheet_url)
