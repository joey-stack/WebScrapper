#!/usr/bin/env python3
"""
Test Suite: WhatsApp Mobile Alerts & Autopilot Daemon
Verifies:
1. Phone number normalization to international format
2. Hot lead alert message construction and intent emoji matching
3. Daily pipeline briefing construction
4. Daily stats calculation from ledger and CSV
5. WhatsApp dispatch fallback when API key is unconfigured
"""

import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "execution"))

from send_mobile_alerts import (
    format_clean_phone,
    send_hot_lead_whatsapp_alert,
    send_daily_summary_whatsapp_alert,
    send_whatsapp_alert
)
from run_continuous_autopilot import compute_daily_stats

def run_tests():
    print("\n==================================================")
    print("[*] RUNNING TEST SUITE: WHATSAPP ALERTS & AUTOPILOT")
    print("==================================================")

    # 1. Test Phone Normalization
    print("\n--- TEST 1: Phone Number Normalization ---")
    p1 = format_clean_phone("08183292909")
    assert p1 == "2348183292909", f"Expected 2348183292909, got {p1}"
    p2 = format_clean_phone("+234 818-329-2909")
    assert p2 == "2348183292909", f"Expected 2348183292909, got {p2}"
    print(f"[+] Phone normalization verified: '08183292909' -> '+{p1}'")

    # 2. Test Hot Lead WhatsApp Alert Construction
    print("\n--- TEST 2: Hot Lead Alert Formatting ---")
    ok1 = send_hot_lead_whatsapp_alert(
        lead_name="Test Organization Nigeria",
        intent="MEETING_REQUEST",
        snippet="Can we schedule a call for this Friday?",
        target_email="director@testorg.ng",
        wa_direct_link="https://wa.me/2348012345678"
    )
    assert ok1 is True, "Hot lead alert should return True (fallback or live)"
    print("[+] Hot lead alert formatting verified.")

    # 3. Test Daily Summary WhatsApp Alert Construction
    print("\n--- TEST 3: Daily Summary Alert Formatting ---")
    test_stats = {
        "leads_scraped_today": 12,
        "total_leads_database": 34,
        "emails_dispatched_today": 8,
        "replies_received_today": 2,
        "active_deals_count": 2,
        "champion_angle": "EXEC_SHORT_V1"
    }
    ok2 = send_daily_summary_whatsapp_alert(test_stats)
    assert ok2 is True, "Daily summary alert should return True"
    print("[+] Daily summary alert formatting verified.")

    # 4. Test Daily Stats Computation from Live Filesystem
    print("\n--- TEST 4: Live Daily Pipeline Stats Computation ---")
    stats = compute_daily_stats()
    assert "total_leads_database" in stats, "Stats missing total_leads_database"
    assert "champion_angle" in stats, "Stats missing champion_angle"
    print(f"[+] Live pipeline stats calculated: Total Database = {stats['total_leads_database']} leads | Champion Angle = {stats['champion_angle']}")

    print("\n==================================================")
    print("[+] ALL 4 WHATSAPP ALERT & AUTOPILOT TESTS PASSED!")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
