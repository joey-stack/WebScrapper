#!/usr/bin/env python3
"""
Layer 3: Execution Tool - Autonomous Scheduled Background Autopilot Daemon
Runs continuously in the background to execute the master acquisition cycle:
1. Scheduled B2B Slots: 08:30 AM (Morning Outbound), 01:15 PM (Midday Follow-ups), 04:45 PM (End-of-Day Scan & Recap).
2. Interval Polling: Monitors IMAP inbox continuously for real-time response capture.
3. WhatsApp Dispatch: Pushes instant alerts on lead response & daily pipeline briefing.
"""

import argparse
import datetime
import os
import sys
import time
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
from run_autonomous_crm_cycle import run_full_autonomous_cycle, DEFAULT_SHEET_URL, TMP_CSV
from send_mobile_alerts import send_daily_summary_whatsapp_alert
from optimize_pitch_performance import load_ledger, select_optimal_variant_id

def compute_daily_stats() -> dict:
    """Computes daily pipeline metrics from CSV and ledger."""
    stats = {
        "leads_scraped_today": 0,
        "total_leads_database": 0,
        "emails_dispatched_today": 0,
        "replies_received_today": 0,
        "active_deals_count": 0,
        "champion_angle": select_optimal_variant_id(epsilon=0.0)
    }

    if TMP_CSV.exists():
        try:
            df = pd.read_csv(TMP_CSV)
            stats["total_leads_database"] = len(df)
            
            today_str = datetime.datetime.now().strftime("%Y-%m-%d")
            
            if "initial_email_sent_at" in df.columns:
                sent_today = df[df["initial_email_sent_at"].astype(str).str.startswith(today_str)]
                stats["emails_dispatched_today"] = len(sent_today)

            if "client_replied" in df.columns:
                replied = df[df["client_replied"].astype(str).isin(["YES", "REPLIED"])]
                stats["active_deals_count"] = len(replied)
                
            if "client_replied_at" in df.columns:
                replied_today = df[df["client_replied_at"].astype(str).str.startswith(today_str)]
                stats["replies_received_today"] = len(replied_today)
        except Exception:
            pass

    return stats

def run_autopilot_daemon(
    sheet_url: str = DEFAULT_SHEET_URL,
    email_limit: int = 15,
    interval_minutes: int = 60,
    business_hours_mode: bool = True,
    dry_run: bool = False,
    run_once: bool = False
):
    print("\n==================================================")
    print("🤖 AUTONOMOUS CLIENT ACQUISITION AUTOPILOT DAEMON")
    print(f"[*] Started At: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"[*] Mode: {'SINGLE PASS' if run_once else ('BUSINESS HOURS SCHEDULE' if business_hours_mode else f'INTERVAL ({interval_minutes}m)')}")
    print(f"[*] Live Dry-Run: {dry_run}")
    print("==================================================")

    if run_once:
        print("[*] Executing single autonomous acquisition cycle...")
        run_full_autonomous_cycle(sheet_url=sheet_url, email_limit=email_limit, dry_run=dry_run)
        daily_stats = compute_daily_stats()
        send_daily_summary_whatsapp_alert(daily_stats)
        print("[+] Single pass complete. Exiting.")
        return

    last_run_hour = -1
    last_daily_summary_date = ""

    while True:
        try:
            now = datetime.datetime.now()
            current_hour = now.hour
            current_minute = now.minute
            today_str = now.strftime("%Y-%m-%d")

            should_run_cycle = False
            is_end_of_day = False

            if business_hours_mode:
                # Slot 1: Morning Outbound (08:30 - 09:30 WAT)
                if current_hour == 8 and 30 <= current_minute <= 59 and last_run_hour != 8:
                    print(f"\n[⏰ SCHEDULED TRIGGER]: Slot 1 - Morning Outbound Batch ({now.strftime('%I:%M %p')})")
                    should_run_cycle = True
                    last_run_hour = 8

                # Slot 2: Midday Follow-up & Inbox Scan (13:15 - 14:00 WAT)
                elif current_hour == 13 and 15 <= current_minute <= 45 and last_run_hour != 13:
                    print(f"\n[⏰ SCHEDULED TRIGGER]: Slot 2 - Midday Outreach & Reply Scan ({now.strftime('%I:%M %p')})")
                    should_run_cycle = True
                    last_run_hour = 13

                # Slot 3: End of Day Sweep & Summary (16:45 - 17:30 WAT)
                elif current_hour == 16 and 45 <= current_minute <= 59 and last_run_hour != 16:
                    print(f"\n[⏰ SCHEDULED TRIGGER]: Slot 3 - End-of-Day Pipeline Wrap ({now.strftime('%I:%M %p')})")
                    should_run_cycle = True
                    is_end_of_day = True
                    last_run_hour = 16

            else:
                # Interval mode (runs every N minutes)
                should_run_cycle = True

            if should_run_cycle:
                print(f"\n[*] Executing autonomous CRM cycle at {now.strftime('%Y-%m-%d %H:%M:%S')}...")
                run_full_autonomous_cycle(sheet_url=sheet_url, email_limit=email_limit, dry_run=dry_run)

                if is_end_of_day and last_daily_summary_date != today_str:
                    print("[*] Sending Daily WhatsApp Briefing...")
                    daily_stats = compute_daily_stats()
                    send_daily_summary_whatsapp_alert(daily_stats)
                    last_daily_summary_date = today_str

            # Heartbeat sleep
            sleep_duration = 60 if business_hours_mode else (interval_minutes * 60)
            time.sleep(sleep_duration)

        except KeyboardInterrupt:
            print("\n[!] Autopilot Daemon stopped by user.")
            break
        except Exception as e:
            print(f"[-] Autopilot Loop Exception: {e}")
            time.sleep(60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Autonomous Lead Acquisition Autopilot Daemon")
    parser.add_argument("--sheet-url", default=DEFAULT_SHEET_URL, help="Target Google Sheet URL")
    parser.add_argument("--limit", type=int, default=15, help="Outreach dispatch limit per pass")
    parser.add_argument("--interval-minutes", type=int, default=60, help="Interval for continuous mode")
    parser.add_argument("--business-hours", action="store_true", default=True, help="Run on peak business hour slots")
    parser.add_argument("--dry-run", action="store_true", help="Run without physically sending emails")
    parser.add_argument("--once", action="store_true", help="Run one full cycle pass and exit")
    args = parser.parse_args()

    run_autopilot_daemon(
        sheet_url=args.sheet_url,
        email_limit=args.limit,
        interval_minutes=args.interval_minutes,
        business_hours_mode=args.business_hours,
        dry_run=args.dry_run,
        run_once=args.once
    )
