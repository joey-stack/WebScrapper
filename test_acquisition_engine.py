#!/usr/bin/env python3
"""
Verification Test Script for 5-Part Autonomous Client Acquisition Engine
"""

import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent / "execution"))

from qualify_and_pitch_leads import (
    qualify_lead, 
    calculate_icp_score, 
    generate_industry_proof_point,
    generate_profile_highlight,
    generate_improvement_area,
    generate_consultative_pitch,
    generate_whatsapp_outreach_copy,
    process_and_qualify_dataframe
)
from send_outreach_emails import scan_and_sanitize_spam
from track_email_responses import classify_reply_intent, extract_directed_email

def run_tests():
    print("==================================================")
    print("[*] RUNNING VERIFICATION SUITE FOR 5-PART ENGINE")
    print("==================================================")

    # Test 1: ICP Scoring & Priority Tiering
    print("\n--- TEST 1: ICP Scoring & Priority Tiering ---")
    lead_hot = {
        "name": "African Health & Education Initiative | Abuja",
        "category": "Non-profit organization",
        "address": "Garki 2, Abuja, Nigeria",
        "website": "",
        "phone": "08012345678",
        "rating": "",
        "reviews_count": 0,
        "search_rank_position": 14
    }
    score, tier = calculate_icp_score(lead_hot)
    print(f"Hot Lead -> Score: {score}/100 | Tier: {tier}")
    assert score >= 80, f"Expected Score >= 80, got {score}"
    assert "Tier A" in tier, f"Expected Tier A, got {tier}"

    lead_warm = {
        "name": "Lagos Property Developers Ltd",
        "category": "Real estate agency",
        "address": "Lekki Phase 1, Lagos, Nigeria",
        "website": "https://lagosproperty.ng",
        "phone": "08098765432",
        "rating": "4.6",
        "reviews_count": 3,
        "search_rank_position": 18
    }
    score_warm, tier_warm = calculate_icp_score(lead_warm)
    print(f"Warm Lead -> Score: {score_warm}/100 | Tier: {tier_warm}")
    assert 50 <= score_warm <= 85, f"Expected Warm Score, got {score_warm}"

    # Test 2: Profile Highlight & Zero-Review Consistency (No Phantom Rating)
    print("\n--- TEST 2: Highlight & Zero-Review Consistency ---")
    highlight_zero = generate_profile_highlight(lead_hot)
    print(f"Zero Reviews Highlight: '{highlight_zero}'")
    assert "★" not in highlight_zero, "Error: Phantom star rating found in zero-review highlight!"
    assert "reviews" not in highlight_zero, "Error: Reviews praised when reviews_count is 0!"

    improvement_zero = generate_improvement_area(lead_hot)
    print(f"Zero Reviews Improvement: '{improvement_zero}'")
    assert "0 public customer reviews" in improvement_zero

    # Test 3: Industry Case Study Proof Injection
    print("\n--- TEST 3: Industry Proof Point Injection ---")
    proof_ngo = generate_industry_proof_point("Non-profit organization", "Abuja")
    print(f"NGO Proof Point: '{proof_ngo}'")
    assert "grant" in proof_ngo.lower()

    proof_tech = generate_industry_proof_point("Software company", "Lagos")
    print(f"Tech Proof Point: '{proof_tech}'")
    assert "demo" in proof_tech.lower()

    # Test 4: WhatsApp Conversational Copy
    print("\n--- TEST 4: WhatsApp Conversational Copy Generation ---")
    wa_copy = generate_whatsapp_outreach_copy(lead_hot, "Both (Website + GMB SEO)", highlight_zero)
    print(f"WhatsApp Copy:\n{wa_copy}")
    assert "Hi Team" in wa_copy
    assert "WhatsApp" in wa_copy

    # Test 5: Anti-Spam Scanner & Sanitizer
    print("\n--- TEST 5: Anti-Spam Pre-Flight Scanner ---")
    spammy_text = "We offer a 100% free audit with guaranteed #1 rank and risk-free instant results!"
    clean_text, triggers = scan_and_sanitize_spam(spammy_text)
    print(f"Original Text: '{spammy_text}'")
    print(f"Clean Text:    '{clean_text}'")
    print(f"Triggers Found: {triggers}")
    assert "100% free" not in clean_text
    assert "guaranteed #1" not in clean_text
    assert len(triggers) >= 3

    # Test 6: Semantic Reply Intent Classification & Directed Email Extraction
    print("\n--- TEST 6: Reply Intent Classification & Directed Email ---")
    test_cases = [
        ("Hi Joel, let's hop on a call this Thursday to discuss your proposal.", "Re: Digital Roadmap", "MEETING_REQUEST"),
        ("Please send your pricing and proposal deck.", "Re: Web presence", "PROPOSAL_REQUEST"),
        ("How much does the Tier 2 website package cost?", "Re: Scope", "PRICING_QUESTION"),
        ("Thanks for reaching out, please forward all details to our executive director at director@careng.org", "Re: Info", "PROPOSAL_REQUEST"),
        ("Please unsubscribe and remove our email from your list.", "Re: Stop", "UNSUBSCRIBE")
    ]

    for body, subj, expected_intent in test_cases:
        classified = classify_reply_intent(body, subj)
        print(f"Text: '{body[:50]}...' -> Intent: {classified} (Expected: {expected_intent})")
        assert classified == expected_intent, f"Expected {expected_intent}, got {classified}"

    directed_email = extract_directed_email("Please forward all details to our executive director at director@careng.org", "info@careng.org")
    print(f"Directed Email Extracted: '{directed_email}'")
    assert directed_email == "director@careng.org"

    # Test 7: Full DataFrame Pipeline Integration
    print("\n--- TEST 7: DataFrame Processing & Sorting ---")
    test_df = pd.DataFrame([lead_warm, lead_hot])
    processed_df = process_and_qualify_dataframe(test_df)
    print(f"Processed Rows: {len(processed_df)}")
    print(f"Columns: {list(processed_df.columns[:8])}")
    # Verify Tier A is sorted to row 0
    assert processed_df.iloc[0]["icp_score"] >= processed_df.iloc[1]["icp_score"]
    print(f"Row 0 Lead: {processed_df.iloc[0]['name']} (Score: {processed_df.iloc[0]['icp_score']})")

    print("\n==================================================")
    print("[+] ALL 7 ENGINE VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
