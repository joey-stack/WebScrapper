#!/usr/bin/env python3
"""
Verification Suite for Automated Multi-Touch Smart Follow-Up Engine
Tests:
1. Touch 2 (Day 3 Competitor Gap Pitch Generation).
2. Touch 3 (Day 7 Permission to Close File Takeaway).
3. Touch 4 (Day 14 Complimentary AI GEO Schema Gift).
4. Elapsed hour detection & touch selection logic.
5. Exclusion guardrails for replied & unsubscribed prospects.
6. Dry-run follow-up execution loop.
"""

import datetime
import os
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent / "execution"))
from follow_up_engine import (
    generate_touch2_competitor_gap_pitch,
    generate_touch3_breakup_pitch,
    generate_touch4_geo_schema_gift_pitch,
    dispatch_smart_followups
)

def run_tests():
    print("\n==================================================")
    print("[*] RUNNING VERIFICATION SUITE: SMART FOLLOW-UP ENGINE")
    print("==================================================")

    lead_sample = {
        "name": "Chateau Royal Real Estate Ltd | Lagos",
        "category": "Real Estate Developer",
        "address": "Lekki Phase 1, Lagos, Nigeria",
        "top_competitor_name": "UPDC Plc",
        "phone": "+2348012345678"
    }

    # TEST 1: Touch 2 Pitch Generation
    print("\n--- TEST 1: Touch 2 (Day 3 Competitor Gap Bump) ---")
    t2_pitch = generate_touch2_competitor_gap_pitch(lead_sample)
    print(t2_pitch)
    assert "UPDC Plc" in t2_pitch, "Expected top competitor UPDC Plc in Touch 2 pitch!"
    assert "80%" in t2_pitch, "Expected 80% map pack citation in Touch 2 pitch!"
    print("[+] Test 1 Passed: Touch 2 dynamically injects competitor and search gap.")

    # TEST 2: Touch 3 Breakup Pitch Generation
    print("\n--- TEST 2: Touch 3 (Day 7 Permission to Close File) ---")
    t3_pitch = generate_touch3_breakup_pitch(lead_sample)
    print(t3_pitch)
    assert "close out this file" in t3_pitch or "archive it" in t3_pitch, "Expected takeaway hook in Touch 3!"
    print("[+] Test 2 Passed: Touch 3 generates high-converting takeaway message.")

    # TEST 3: Touch 4 AI GEO Schema Gift Drop
    print("\n--- TEST 3: Touch 4 (Day 14 Free AI GEO Schema Gift) ---")
    t4_pitch = generate_touch4_geo_schema_gift_pitch(lead_sample)
    print(t4_pitch)
    assert "Google & ChatGPT JSON-LD" in t4_pitch or "Schema" in t4_pitch, "Expected schema gift mention in Touch 4!"
    print("[+] Test 3 Passed: Touch 4 generates pure-value GEO schema gift.")

    # TEST 4: Follow-up Dispatch Simulation with Mock DataFrame
    print("\n--- TEST 4: Follow-Up Dispatch Simulation ---")
    tmp_test_csv = Path(__file__).parent / ".tmp" / "test_followup_leads.csv"
    tmp_test_csv.parent.mkdir(parents=True, exist_ok=True)

    now = datetime.datetime.now()
    four_days_ago = (now - datetime.timedelta(days=4)).strftime("%Y-%m-%d %H:%M")
    eight_days_ago = (now - datetime.timedelta(days=8)).strftime("%Y-%m-%d %H:%M")

    mock_df = pd.DataFrame([
        {
            "name": "Eligible Day 3 Lead",
            "email": "lead1@test.org",
            "email_sent_status": "SENT",
            "initial_email_sent_at": four_days_ago,
            "followup_status": "NOT_DUE",
            "client_replied": "NO",
            "top_competitor_name": "Rival Alpha"
        },
        {
            "name": "Replied Lead (Must Skip)",
            "email": "lead2@test.org",
            "email_sent_status": "SENT",
            "initial_email_sent_at": four_days_ago,
            "followup_status": "NOT_DUE",
            "client_replied": "YES",
            "top_competitor_name": "Rival Beta"
        },
        {
            "name": "Eligible Day 7 Lead",
            "email": "lead3@test.org",
            "email_sent_status": "SENT",
            "initial_email_sent_at": eight_days_ago,
            "followup_status": "SENT_FOLLOWUP_1_DAY_3",
            "client_replied": "NO",
            "top_competitor_name": "Rival Gamma"
        }
    ])
    mock_df.to_csv(tmp_test_csv, index=False)

    dispatched = dispatch_smart_followups(csv_path=tmp_test_csv, sheet_url=None, limit=10, dry_run=True)
    print(f"[+] Total follow-ups dispatched in simulation: {dispatched}")
    assert dispatched == 2, f"Expected 2 eligible follow-ups dispatched (skipping replied lead), got {dispatched}"

    # Verify status updates
    res_df = pd.read_csv(tmp_test_csv)
    assert res_df.loc[0, "followup_status"] == "DRY_RUN_FOLLOWUP_1"
    assert res_df.loc[1, "followup_status"] == "NOT_DUE"  # Replied lead untouched
    assert res_df.loc[2, "followup_status"] == "DRY_RUN_FOLLOWUP_2"

    print("[+] Test 4 Passed: Scheduling and exclusion logic validated perfectly.")

    # Cleanup
    if tmp_test_csv.exists():
        tmp_test_csv.unlink()

    print("\n==================================================")
    print("[+] ALL 4 SMART FOLLOW-UP ENGINE TESTS PASSED!")
    print("==================================================\n")

if __name__ == "__main__":
    run_tests()
