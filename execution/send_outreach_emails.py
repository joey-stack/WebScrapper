#!/usr/bin/env python3
"""
Layer 3: Execution Tool - Enterprise Anti-Ban Email Outreach & Follow-up Scheduler
Features:
- Multi-Inbox Rotation (rotates sender accounts to bypass single-account daily limits)
- Humanized Spintax Variation (varies email bodies so spam filters don't detect identical blasts)
- Compliant Opt-Out Headers
- Randomized Throttle Delays (15-35s)
- Automatic Status Tracking & Live Google Sheet Sync
"""

import argparse
import datetime
import os
import random
import smtplib
import sys
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
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

def parse_sender_accounts():
    """Parses sender accounts from .env. Supports multi-account rotation."""
    raw_accounts = os.getenv("SENDER_ACCOUNTS", "").strip()
    accounts = []
    
    if raw_accounts:
        # Format: email1:pass1|email2:pass2
        for item in raw_accounts.split("|"):
            if ":" in item:
                e, p = item.split(":", 1)
                accounts.append({"email": e.strip(), "password": p.strip()})
    
    if not accounts:
        # Fallback to single account variables
        single_e = os.getenv("SENDER_EMAIL", "").strip()
        single_p = os.getenv("SENDER_PASSWORD", "").strip()
        if single_e and single_p:
            accounts.append({"email": single_e, "password": single_p})
            
    return accounts

def connect_smtp_account(account: dict):
    """Establishes an authenticated SMTP connection for a specific sender account."""
    server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    port = int(os.getenv("SMTP_PORT", "587"))

    smtp = smtplib.SMTP(server, port)
    smtp.ehlo()
    smtp.starttls()
    smtp.login(account["email"], account["password"])
    return smtp

def spin_text(text: str) -> str:
    """Varies greeting & closing words so spam filters do not hash identical content."""
    greetings = ["Hello Team", "Hi Team", "Good day Team", "Greetings Team"]
    selected_greeting = random.choice(greetings)
    
    # Replace standard greeting if present
    for g in ["Hello Team", "Hi Team", "Good day Team"]:
        if text.startswith(g):
            text = text.replace(g, selected_greeting, 1)
            break

    # Add anti-spam opt-out footer
    opt_out = "\n\n---\nP.S. If you prefer not to receive further updates from us, simply reply 'unsubscribe' and we will remove your email immediately."
    return text + opt_out

def generate_email_subject(lead_name: str, service_needed: str) -> str:
    clean_name = lead_name.split("|")[0].split("-")[0].strip()
    subjects = [
        f"Quick question regarding {clean_name}'s web presence",
        f"Improving {clean_name}'s local Google Search visibility",
        f"Strategic digital roadmap for {clean_name}"
    ]
    if "Website" in service_needed:
        return subjects[0]
    else:
        return subjects[1]

def generate_followup_pitch(lead_name: str, service_needed: str, original_pitch: str) -> str:
    clean_name = lead_name.split("|")[0].split("-")[0].strip()
    followup = (
        f"Hi Team {clean_name},\n\n"
        f"I wanted to follow up on my previous note regarding {clean_name}'s digital presence.\n\n"
        f"Have you had 5 minutes to review the strategic digital roadmap we prepared for your team?\n\n"
        f"I would be glad to share a quick 5-minute overview whenever suits your schedule this week.\n\n"
        f"Best regards,\n"
        f"{os.getenv('SENDER_NAME', 'Joel Adawah')}\n\n"
        f"--- Original Message ---\n\n"
        f"{original_pitch}"
    )
    return followup

def generate_breakup_pitch(lead_name: str, service_needed: str) -> str:
    clean_name = lead_name.split("|")[0].split("-")[0].strip()
    breakup = (
        f"Hi Team {clean_name},\n\n"
        f"I know how busy managing an organization can be, so I won't continue clogging your inbox!\n\n"
        f"If improving {clean_name}'s Google search rank or web portal becomes a priority down the road, please feel free to reach back out anytime.\n\n"
        f"Wishing {clean_name} continued growth and success!\n\n"
        f"Warm regards,\n"
        f"{os.getenv('SENDER_NAME', 'Joel Adawah')}"
    )
    return breakup

def process_email_outreach(csv_path: Path, mode: str, sheet_url: str = None, limit: int = 25, dry_run: bool = False):
    if not csv_path.exists():
        print(f"[-] Error: Leads file not found at {csv_path}")
        return

    accounts = parse_sender_accounts()
    if not accounts and not dry_run:
        print("[!] Error: No valid sender accounts found in .env!")
        return

    df = pd.read_csv(csv_path)

    # Initialize tracking columns if missing
    tracking_cols = {
        "email_sent_status": "PENDING",
        "sender_account_used": "",
        "initial_email_sent_at": "",
        "followup_due_at": "",
        "followup_sent_at": "",
        "followup_status": "NOT_DUE"
    }
    for col, default_val in tracking_cols.items():
        if col not in df.columns:
            df[col] = default_val

    now = datetime.datetime.now()
    sent_count = 0
    account_idx = 0

    print(f"\n==================================================")
    print(f"[*] Enterprise Anti-Ban Email Outreach Scheduler")
    print(f"[*] Senders Available: {len(accounts)} account(s)")
    print(f"[*] Mode: {mode.upper()} | Leads with emails: {len(df[df['email'].notna()])}/{len(df)}")
    print(f"==================================================")

    for idx, row in df.iterrows():
        email_str = str(row.get("email", "") or "").strip()
        if not email_str or "@" not in email_str:
            continue

        # Strict Unsubscribe & Reply Guardrail
        curr_sent_status = str(row.get("email_sent_status", "")).upper()
        curr_followup_status = str(row.get("followup_status", "")).upper()
        if "UNSUBSCRIBED" in curr_sent_status or "UNSUBSCRIBED" in curr_followup_status or "REPLIED" in curr_sent_status:
            continue

        if sent_count >= limit:
            print(f"\n[+] Reached safe daily batch limit of {limit} dispatches.")
            break

        recipient_email = [e.strip() for e in email_str.split(",") if "@" in e][0]
        lead_name = str(row.get("name", "Organization")).strip()
        service_needed = str(row.get("service_needed", ""))
        raw_pitch = str(row.get("personalized_pitch", ""))

        if mode == "initial" and str(row.get("email_sent_status")) in ["PENDING", "", "nan", "None"]:
            subject = generate_email_subject(lead_name, service_needed)
            body = spin_text(raw_pitch)
            due_date = (now + datetime.timedelta(days=3)).strftime("%Y-%m-%d %H:%M")
            sent_time = now.strftime("%Y-%m-%d %H:%M")

            current_account = accounts[account_idx % len(accounts)] if accounts else {"email": "dryrun@domain.com"}
            account_idx += 1

            print(f"\n---> [{sent_count+1}/{limit}] Dispatching Initial Pitch:")
            print(f"     From:     {current_account['email']}")
            print(f"     To:       {lead_name} <{recipient_email}>")
            print(f"     Subject:  {subject}")

            if dry_run:
                print("     [DRY RUN - Email not physically sent]")
            else:
                try:
                    smtp_conn = connect_smtp_account(current_account)
                    msg = MIMEMultipart()
                    msg["From"] = f"{os.getenv('SENDER_NAME', 'Joel Adawah')} <{current_account['email']}>"
                    msg["To"] = recipient_email
                    msg["Subject"] = subject
                    msg.attach(MIMEText(body, "plain"))
                    smtp_conn.send_message(msg)
                    smtp_conn.quit()

                    delay = random.randint(15, 35)
                    print(f"     [+] Success! Pausing {delay}s for humanized rate limiting...")
                    time.sleep(delay)
                except Exception as send_err:
                    print(f"     [-] Failed to send via {current_account['email']}: {send_err}")
                    continue

            df.at[idx, "email_sent_status"] = "SENT_INITIAL" if not dry_run else "DRY_RUN_INITIAL"
            df.at[idx, "sender_account_used"] = current_account["email"]
            df.at[idx, "initial_email_sent_at"] = sent_time
            df.at[idx, "followup_due_at"] = due_date
            df.at[idx, "followup_status"] = "SCHEDULED_DAY_3"
            sent_count += 1

        elif mode == "followup" and str(row.get("email_sent_status")) in ["SENT_INITIAL", "DRY_RUN_INITIAL"]:
            due_str = str(row.get("followup_due_at", ""))
            f_status = str(row.get("followup_status", ""))

            is_due = False
            if due_str:
                try:
                    due_dt = datetime.datetime.strptime(due_str, "%Y-%m-%d %H:%M")
                    if now >= due_dt:
                        is_due = True
                except Exception:
                    is_due = True

            if is_due:
                # Follow-Up #1 (Day 3)
                if f_status in ["SCHEDULED_DAY_3", "NOT_DUE", ""]:
                    subject = f"Re: {generate_email_subject(lead_name, service_needed)}"
                    body = spin_text(generate_followup_pitch(lead_name, service_needed, raw_pitch))
                    sent_time = now.strftime("%Y-%m-%d %H:%M")
                    next_due = (now + datetime.timedelta(days=4)).strftime("%Y-%m-%d %H:%M")

                    current_account = accounts[account_idx % len(accounts)] if accounts else {"email": "dryrun@domain.com"}
                    account_idx += 1

                    print(f"\n---> [{sent_count+1}/{limit}] Dispatching Follow-up #1 (Day 3):")
                    print(f"     From:     {current_account['email']}")
                    print(f"     To:       {lead_name} <{recipient_email}>")
                    print(f"     Subject:  {subject}")

                    if dry_run:
                        print("     [DRY RUN - Follow-up #1 not physically sent]")
                    else:
                        try:
                            smtp_conn = connect_smtp_account(current_account)
                            msg = MIMEMultipart()
                            msg["From"] = f"{os.getenv('SENDER_NAME', 'Joel Adawah')} <{current_account['email']}>"
                            msg["To"] = recipient_email
                            msg["Subject"] = subject
                            msg.attach(MIMEText(body, "plain"))
                            smtp_conn.send_message(msg)
                            smtp_conn.quit()

                            delay = random.randint(15, 35)
                            print(f"     [+] Success! Pausing {delay}s for humanized rate limiting...")
                            time.sleep(delay)
                        except Exception as send_err:
                            print(f"     [-] Failed to send via {current_account['email']}: {send_err}")
                            continue

                    df.at[idx, "followup_status"] = "SENT_FOLLOWUP_1" if not dry_run else "DRY_RUN_FOLLOWUP_1"
                    df.at[idx, "followup_sent_at"] = sent_time
                    df.at[idx, "followup_due_at"] = next_due  # Schedule Day 7 Soft Breakup
                    sent_count += 1

                # Follow-Up #2 (Day 7 Soft Breakup)
                elif f_status in ["SENT_FOLLOWUP_1", "DRY_RUN_FOLLOWUP_1"]:
                    subject = f"Re: {generate_email_subject(lead_name, service_needed)}"
                    body = spin_text(generate_breakup_pitch(lead_name, service_needed))
                    sent_time = now.strftime("%Y-%m-%d %H:%M")

                    current_account = accounts[account_idx % len(accounts)] if accounts else {"email": "dryrun@domain.com"}
                    account_idx += 1

                    print(f"\n---> [{sent_count+1}/{limit}] Dispatching Follow-up #2 (Day 7 Soft Breakup):")
                    print(f"     From:     {current_account['email']}")
                    print(f"     To:       {lead_name} <{recipient_email}>")
                    print(f"     Subject:  {subject}")

                    if dry_run:
                        print("     [DRY RUN - Follow-up #2 Soft Breakup not physically sent]")
                    else:
                        try:
                            smtp_conn = connect_smtp_account(current_account)
                            msg = MIMEMultipart()
                            msg["From"] = f"{os.getenv('SENDER_NAME', 'Joel Adawah')} <{current_account['email']}>"
                            msg["To"] = recipient_email
                            msg["Subject"] = subject
                            msg.attach(MIMEText(body, "plain"))
                            smtp_conn.send_message(msg)
                            smtp_conn.quit()

                            delay = random.randint(15, 35)
                            print(f"     [+] Success! Pausing {delay}s for humanized rate limiting...")
                            time.sleep(delay)
                        except Exception as send_err:
                            print(f"     [-] Failed to send via {current_account['email']}: {send_err}")
                            continue

                    df.at[idx, "followup_status"] = "SEQUENCE_COMPLETE_DAY_7" if not dry_run else "DRY_RUN_SEQUENCE_COMPLETE"
                    df.at[idx, "followup_sent_at"] = sent_time
                    sent_count += 1

    df.to_csv(csv_path, index=False, encoding="utf-8")
    print(f"\n[+] Updated status tracking saved to local CSV: {csv_path}")

    if sheet_url:
        try:
            export_df_to_google_sheet(df, sheet_url)
        except Exception as e:
            print(f"[-] Note: Sheet sync skipped ({e}). Local CSV is updated.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enterprise Anti-Ban Outreach Sender & Follow-up Scheduler")
    parser.add_argument("--send-initial", action="store_true", help="Send initial personalized pitches")
    parser.add_argument("--send-followups", action="store_true", help="Send scheduled follow-ups")
    parser.add_argument("--dry-run", action="store_true", help="Preview dispatches without sending")
    parser.add_argument("--limit", type=int, default=25, help="Maximum emails per batch (default: 25)")
    parser.add_argument("--sheet-url", type=str, default="https://docs.google.com/spreadsheets/d/1wGuXHelu2SqOUG2IQNMWG8gF08KqO_OcTb5rU1cziiU", help="Google Sheet URL")

    args = parser.parse_args()

    mode = "initial"
    if args.send_followups:
        mode = "followup"

    process_email_outreach(
        csv_path=TMP_CSV,
        mode=mode,
        sheet_url=args.sheet_url,
        limit=args.limit,
        dry_run=args.dry_run or (not args.send_initial and not args.send_followups)
    )
