#!/usr/bin/env python3
"""
Layer 3: Execution Tool - Daily Automated Lead Scraper & Deduplication Engine
Extracts 10-15 fresh buried leads (ranked #11-50+) daily across rotating sectors,
deduplicates against existing dataset, qualifies, and syncs to Google Sheets CRM.
"""

import argparse
import asyncio
import datetime
import os
import random
import sys
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
try:
    from playwright.async_api import async_playwright
except ImportError:
    async_playwright = None

load_dotenv()
sys.path.insert(0, str(Path(__file__).parent))

try:
    from scrape_gmb_profiles import scrape_gmb_query
    from qualify_and_pitch_leads import process_and_qualify_dataframe
    from export_to_google_sheets import export_df_to_google_sheet
except ImportError:
    from execution.scrape_gmb_profiles import scrape_gmb_query
    from execution.qualify_and_pitch_leads import process_and_qualify_dataframe
    from execution.export_to_google_sheets import export_df_to_google_sheet

TMP_CSV = Path(__file__).parent.parent / ".tmp" / "gmb_leads_combined.csv"
DEFAULT_SHEET_URL = "https://docs.google.com/spreadsheets/d/1wGuXHelu2SqOUG2IQNMWG8gF08KqO_OcTb5rU1cziiU"

ROTATING_QUERIES = [
    "NGOs in Abuja, Nigeria",
    "Foundations in Abuja, Nigeria",
    "Tech Hubs in Yaba Lagos, Nigeria",
    "Software Companies in Lagos, Nigeria",
    "Private Schools in Lekki Lagos, Nigeria",
    "Colleges in Port Harcourt, Nigeria",
    "Real Estate Agencies in Abuja, Nigeria",
    "Property Developers in Victoria Island Lagos, Nigeria",
    "Private Hospitals in Ikeja Lagos, Nigeria",
    "Specialist Clinics in Ibadan, Nigeria"
]

async def _scrape_query_async(query: str, max_results: int = 30):
    if async_playwright is None:
        print("[!] Warning: Playwright is not installed. Skipping live web scraping.")
        return []
    async with async_playwright() as p:
        return await scrape_gmb_query(p, query=query, max_results=max_results, headless=True)

def scrape_and_append_daily_leads(limit: int = 15, sheet_url: str = DEFAULT_SHEET_URL):
    print(f"\n==================================================")
    print(f"[*] DAILY AUTOMATED LEAD SCRAPER & DEDUPLICATION ENGINE")
    print(f"==================================================")

    existing_urls = set()
    existing_emails = set()
    existing_names = set()

    if TMP_CSV.exists():
        df_exist = pd.read_csv(TMP_CSV)
        for _, r in df_exist.iterrows():
            if pd.notna(r.get("google_maps_url")):
                existing_urls.add(str(r["google_maps_url"]).strip())
            if pd.notna(r.get("email")):
                existing_emails.add(str(r["email"]).strip().lower())
            if pd.notna(r.get("name")):
                existing_names.add(str(r["name"]).strip().lower())

    print(f"[*] Loaded {len(existing_names)} existing leads for deduplication.")

    query = random.choice(ROTATING_QUERIES)
    print(f"[*] Today's Target Query: '{query}'")

    raw_results = asyncio.run(_scrape_query_async(query=query, max_results=30))
    if not raw_results:
        print("[!] No results returned for query.")
        return

    fresh_leads = []
    for item in raw_results:
        rank = item.get("search_rank_position", 99)
        if rank < 11:
            continue  # Focus on buried leads position #11-50+

        name = str(item.get("name", "")).strip()
        g_url = str(item.get("google_maps_url", "")).strip()
        email_addr = str(item.get("email", "")).strip().lower()

        if name.lower() in existing_names or (g_url and g_url in existing_urls):
            continue  # Deduplicate

        if email_addr and email_addr in existing_emails:
            continue  # Deduplicate by email

        fresh_leads.append(item)
        existing_names.add(name.lower())
        if g_url: existing_urls.add(g_url)
        if email_addr: existing_emails.add(email_addr)

        if len(fresh_leads) >= limit:
            break

    print(f"[+] Successfully extracted {len(fresh_leads)} fresh unique buried leads.")
    if not fresh_leads:
        return

    df_fresh = pd.DataFrame(fresh_leads)
    df_qualified = process_and_qualify_dataframe(df_fresh)

    if TMP_CSV.exists():
        df_combined = pd.concat([pd.read_csv(TMP_CSV), df_qualified], ignore_index=True)
    else:
        df_combined = df_qualified

    df_combined.to_csv(TMP_CSV, index=False, encoding="utf-8")
    print(f"[+] Saved updated dataset ({len(df_combined)} total leads) to {TMP_CSV}")

    if sheet_url:
        export_df_to_google_sheet(df_combined, sheet_url)
        print(f"[+] Published updated dataset to Google Sheet: {sheet_url}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Daily Lead Scraper")
    parser.add_argument("--limit", type=int, default=15, help="Number of fresh leads")
    parser.add_argument("--sheet-url", type=str, default=DEFAULT_SHEET_URL, help="Google Sheet URL")

    args = parser.parse_args()
    scrape_and_append_daily_leads(limit=args.limit, sheet_url=args.sheet_url)
