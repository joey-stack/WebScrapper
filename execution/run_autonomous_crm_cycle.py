#!/usr/bin/env python3
"""
Layer 3: Execution Tool - Single Master Autonomous CRM Orchestrator
Executes the full automated cycle hands-off:
1. Verifies credentials & dataset state
2. Dispatches pending initial outreach emails & due follow-ups (safe Gmail rate limits)
3. Scans Gmail IMAP inbox for incoming client responses
4. Promotes replied leads to 2_Active_Deals on Google Sheet
5. Onboards CLOSED_WON deals to 3_Project_Milestones deliverable checklists
6. Recalculates 4_Financial_Dashboard revenue metrics
"""

import argparse
import datetime
import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Ensure execution path is accessible
sys.path.insert(0, str(Path(__file__).parent))

from send_outreach_emails import process_email_outreach
from follow_up_engine import dispatch_smart_followups
from track_email_responses import track_incoming_replies
from manage_crm_engine import init_crm_worksheets, sync_replies_to_active_deals, onboard_closed_won_projects
from scrape_daily_leads import scrape_and_append_daily_leads
from optimize_pitch_performance import evaluate_and_evolve_pitches

DEFAULT_SHEET_URL = "https://docs.google.com/spreadsheets/d/1wGuXHelu2SqOUG2IQNMWG8gF08KqO_OcTb5rU1cziiU"
TMP_CSV = Path(__file__).parent.parent / ".tmp" / "gmb_leads_combined.csv"

def run_full_autonomous_cycle(sheet_url: str = DEFAULT_SHEET_URL, email_limit: int = 20, dry_run: bool = False):
    print(f"\n==================================================")
    print(f"[*] RUNNING AUTONOMOUS CRM OUTREACH & CONVERSION CYCLE")
    print(f"[*] Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"==================================================")

    # 0. Scrape Fresh Daily Leads
    print("\n--- STEP 0: SCRAPING FRESH DAILY BURIED LEADS (#11-50+) ---")
    try:
        scrape_and_append_daily_leads(limit=10, sheet_url=sheet_url)
    except Exception as e:
        print(f"[-] Step 0 Warning: {e}")

    # 1. Initialize & Ensure Worksheets Exist
    print("\n--- STEP 1: VERIFYING CRM WORKSHEETS & STRUCTURE ---")
    try:
        init_crm_worksheets(sheet_url)
    except Exception as e:
        print(f"[-] Step 1 Warning: {e}")

    # 1.5. Self-Learning Pitch Performance Evaluation & Evolution
    print("\n--- STEP 1.5: EVALUATING & EVOLVING PITCH PERFORMANCE ---")
    try:
        evaluate_and_evolve_pitches()
    except Exception as e:
        print(f"[-] Step 1.5 Warning: {e}")

    # 2. Dispatch Outbound Emails (Initial & Multi-Touch Smart Follow-ups)
    print("\n--- STEP 2: DISPATCHING OUTBOUND OUTREACH & SMART FOLLOW-UPS ---")
    try:
        process_email_outreach(csv_path=TMP_CSV, mode="initial", sheet_url=sheet_url, limit=email_limit, dry_run=dry_run)
        dispatch_smart_followups(csv_path=TMP_CSV, sheet_url=sheet_url, limit=email_limit, dry_run=dry_run)
    except Exception as e:
        print(f"[-] Step 2 Error: {e}")

    # 3. Scan IMAP Inbox for Incoming Client Replies
    print("\n--- STEP 3: SCANNING GMAIL IMAP INBOX FOR CLIENT REPLIES ---")
    try:
        track_incoming_replies(csv_path=TMP_CSV, sheet_url=sheet_url, search_limit=50)
    except Exception as e:
        print(f"[-] Step 3 Error: {e}")

    # 4. Promote Replied Leads to 2_Active_Deals
    print("\n--- STEP 4: PROMOTING REPLIED LEADS TO 2_ACTIVE_DEALS ---")
    try:
        sync_replies_to_active_deals(sheet_url)
    except Exception as e:
        print(f"[-] Step 4 Error: {e}")

    # 5. Onboard CLOSED_WON Deals to 3_Project_Milestones
    print("\n--- STEP 5: ONBOARDING CLOSED_WON DEALS TO 3_PROJECT_MILESTONES ---")
    try:
        onboard_closed_won_projects(sheet_url)
    except Exception as e:
        print(f"[-] Step 5 Error: {e}")

    print(f"\n==================================================")
    print(f"[+] AUTONOMOUS CRM CYCLE COMPLETE!")
    print(f"[+] Live CRM Dashboard: {sheet_url}")
    print(f"==================================================\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Master Autonomous CRM Orchestrator")
    parser.add_argument("--sheet-url", type=str, default=DEFAULT_SHEET_URL, help="Google Sheet URL")
    parser.add_argument("--limit", type=int, default=20, help="Max outbound emails per batch")
    parser.add_argument("--dry-run", action="store_true", help="Run without physically sending emails")

    args = parser.parse_args()

    run_full_autonomous_cycle(
        sheet_url=args.sheet_url,
        email_limit=args.limit,
        dry_run=args.dry_run
    )
