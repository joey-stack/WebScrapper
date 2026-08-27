#!/usr/bin/env python3
"""
Test Suite: Self-Learning AI Pitch Optimization & Multi-Armed Bandit A/B Engine
Verifies:
1. Performance ledger data integrity
2. Impression and reply attribution
3. Epsilon-greedy multi-armed bandit traffic routing
4. Diagnostic weakness detection
5. Evolutionary copy mutation
6. Automated pruning of underperformers (<3% reply rate after 15 sends)
"""

import os
import sys
import json
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "execution"))

from optimize_pitch_performance import (
    load_ledger,
    save_ledger,
    record_send_event,
    record_reply_event,
    select_optimal_variant_id,
    diagnose_variant_weakness,
    mutate_variant,
    evaluate_and_evolve_pitches,
    LEDGER_FILE,
    BASE_VARIANTS
)

def test_self_learning_loop():
    print("\n==================================================")
    print("[*] RUNNING TEST SUITE: SELF-LEARNING OPTIMIZATION ENGINE")
    print("==================================================")

    # 1. Test Ledger Initialization
    print("\n--- TEST 1: Performance Ledger Initialization ---")
    backup_path = LEDGER_FILE.with_suffix(".bak")
    if LEDGER_FILE.exists():
        shutil.copy(LEDGER_FILE, backup_path)

    ledger = load_ledger()
    assert "variants" in ledger, "Ledger missing 'variants' key!"
    assert "AUTHORITY_V1" in ledger["variants"], "Missing AUTHORITY_V1 in ledger!"
    assert "EXEC_SHORT_V1" in ledger["variants"], "Missing EXEC_SHORT_V1 in ledger!"
    print("[+] Ledger successfully initialized with 4 baseline psychological angles.")

    # 2. Test Send & Reply Attribution
    print("\n--- TEST 2: Send & Reply Event Attribution ---")
    record_send_event("EXEC_SHORT_V1")
    record_send_event("EXEC_SHORT_V1")
    record_reply_event("EXEC_SHORT_V1", intent="MEETING_REQUEST")

    ledger_after = load_ledger()
    exec_short = ledger_after["variants"]["EXEC_SHORT_V1"]
    assert exec_short["impressions_sent"] >= 2, f"Expected >=2 sends, got {exec_short['impressions_sent']}"
    assert exec_short["replies_received"] >= 1, f"Expected >=1 reply, got {exec_short['replies_received']}"
    assert exec_short["positive_replies"] >= 1, f"Expected >=1 positive reply, got {exec_short['positive_replies']}"
    assert exec_short["reply_rate"] == 50.0, f"Expected 50.0% reply rate, got {exec_short['reply_rate']}"
    print(f"[+] Attribution verified: EXEC_SHORT_V1 sent={exec_short['impressions_sent']}, replies={exec_short['replies_received']}, rate={exec_short['reply_rate']}%")

    # 3. Test Multi-Armed Bandit Selection
    print("\n--- TEST 3: Multi-Armed Bandit Traffic Allocation ---")
    # Set EXEC_SHORT_V1 as dominant champion (50% reply rate)
    champion = select_optimal_variant_id(epsilon=0.0)
    assert champion == "EXEC_SHORT_V1", f"Expected EXEC_SHORT_V1 to be selected as champion, got {champion}"
    print(f"[+] Exploitation confirmed: Highest converting variant '{champion}' receives priority routing.")

    # 4. Test Copy Weakness Diagnostic
    print("\n--- TEST 4: Copy Weakness Diagnostics ---")
    long_variant_data = {
        "pitch_template": " ".join(["word"] * 125) + " Hope you are well? What do you think? Can we talk? Are you available?",
    }
    flaws = diagnose_variant_weakness(long_variant_data)
    assert any("Excessive length" in f for f in flaws), "Failed to detect excessive length"
    assert any("Generic greeting" in f for f in flaws), "Failed to detect generic greeting"
    assert any("Multiple competing questions" in f for f in flaws), "Failed to detect competing questions"
    print(f"[+] Diagnostics detected {len(flaws)} copy flaws: {flaws}")

    # 5. Test Copy Mutation & Evolution
    print("\n--- TEST 5: Evolutionary Copy Mutation ---")
    old_variant = {
        "angle_name": "Competitor Map Gap",
        "pitch_template": "Old long template...",
        "generation": 1
    }
    new_id, new_data = mutate_variant("COMPETITOR_V1", old_variant)
    assert new_id == "COMPETITOR_V2", f"Expected COMPETITOR_V2, got {new_id}"
    assert new_data["generation"] == 2, f"Expected generation 2, got {new_data['generation']}"
    assert new_data["status"] == "ACTIVE", "New mutated variant must be active"
    print(f"[+] Evolutionary mutation succeeded: Generated '{new_id}' (Gen {new_data['generation']}).")

    # 6. Test Automated Pruning & Evolution on Underperformance
    print("\n--- TEST 6: Automated Self-Annealing Evolution Cycle ---")
    # Simulate an underperforming variant (20 sends, 0 replies)
    ledger_test = load_ledger()
    ledger_test["variants"]["GLASS_HQ_V1"]["impressions_sent"] = 20
    ledger_test["variants"]["GLASS_HQ_V1"]["replies_received"] = 0
    ledger_test["variants"]["GLASS_HQ_V1"]["reply_rate"] = 0.0
    save_ledger(ledger_test)

    evaluate_and_evolve_pitches()

    ledger_evolved = load_ledger()
    assert ledger_evolved["variants"]["GLASS_HQ_V1"]["status"] == "RETIRED_UNDERPERFORMING", "GLASS_HQ_V1 should be retired"
    assert "GLASS_HQ_V2" in ledger_evolved["variants"], "GLASS_HQ_V2 should have been bred into active rotation"
    print("[+] Full self-annealing loop verified: GLASS_HQ_V1 retired and evolved into GLASS_HQ_V2.")

    # Clean up test modifications by restoring clean initial state
    fresh_ledger = {
        "created_at": "2026-08-27 18:00",
        "total_dispatches": 0,
        "total_replies": 0,
        "overall_reply_rate": 0.0,
        "last_evolution_at": "2026-08-27 18:00",
        "variants": BASE_VARIANTS
    }
    save_ledger(fresh_ledger)
    if backup_path.exists():
        backup_path.unlink()

    print("\n==================================================")
    print("[+] ALL 6 SELF-LEARNING ENGINE TESTS PASSED!")
    print("==================================================")

if __name__ == "__main__":
    test_self_learning_loop()
