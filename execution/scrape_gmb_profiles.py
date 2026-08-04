#!/usr/bin/env python3
"""
Layer 3: Execution Tool - Google My Business (GMB) Profile Scraper
Scrapes GMB / Google Maps business listings for target search queries.
Extracts Name, Rating, Reviews Count, Category, Address, Phone, Website, and Emails (crawled from target website).
Saves output deliverables to .tmp/ directory in CSV and JSON formats.
"""

import argparse
import asyncio
import os
import re
import sys
import json
import urllib.parse
from pathlib import Path
import pandas as pd
from bs4 import BeautifulSoup
import requests
from playwright.async_api import async_playwright

# Ensure execution directory is in python module search path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from export_to_google_sheets import export_df_to_google_sheet
    from qualify_and_pitch_leads import process_and_qualify_dataframe
except ImportError:
    from execution.export_to_google_sheets import export_df_to_google_sheet
    from execution.qualify_and_pitch_leads import process_and_qualify_dataframe




TMP_DIR = Path(__file__).parent.parent / ".tmp"
TMP_DIR.mkdir(parents=True, exist_ok=True)

# Common regex pattern to find email addresses
EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

# Ignore common junk / image / placeholder matches
IGNORED_EMAIL_DOMAINS_AND_EXTS = [
    "example.com", "domain.com", "email.com", "yourdomain.com",
    "png", "jpg", "jpeg", "gif", "svg", "webp", "sentry.io",
    "wixpress.com", "schema.org", "w3.org"
]

def clean_email(email_str: str) -> bool:
    email_lower = email_str.lower()
    for ignored in IGNORED_EMAIL_DOMAINS_AND_EXTS:
        if ignored in email_lower:
            return False
    # Avoid extensions in email host part
    if re.search(r"\.(png|jpg|jpeg|gif|svg|webp|css|js)$", email_lower):
        return False
    return True

def find_emails_in_text(text: str) -> list:
    found = re.findall(EMAIL_REGEX, text)
    valid_emails = set()
    for e in found:
        e_clean = e.strip(".,;:()")
        if clean_email(e_clean):
            valid_emails.add(e_clean)
    return list(valid_emails)

def scrape_emails_from_website(website_url: str) -> str:
    """Visits the business website to scrape contact email addresses."""
    if not website_url or not website_url.startswith("http"):
        return ""
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    emails = set()
    urls_to_check = [website_url]
    
    # Try fetching homepage
    try:
        resp = requests.get(website_url, headers=headers, timeout=8, allow_redirects=True)
        if resp.status_code == 200:
            found_hp = find_emails_in_text(resp.text)
            emails.update(found_hp)
            
            # Look for contact / about page links if no email found on homepage
            if not emails:
                soup = BeautifulSoup(resp.text, 'html.parser')
                for a in soup.find_all('a', href=True):
                    href = a['href'].lower()
                    if 'contact' in href or 'about' in href:
                        full_url = urllib.parse.urljoin(website_url, a['href'])
                        if full_url not in urls_to_check:
                            urls_to_check.append(full_url)
                            if len(urls_to_check) >= 3:
                                break
    except Exception as err:
        print(f"   [!] Note: Could not fetch website {website_url}: {err}")

    # Check contact/about subpages if needed
    for sub_url in urls_to_check[1:]:
        if emails:
            break
        try:
            resp = requests.get(sub_url, headers=headers, timeout=6, allow_redirects=True)
            if resp.status_code == 200:
                found_sub = find_emails_in_text(resp.text)
                emails.update(found_sub)
        except Exception:
            pass

    return ", ".join(list(emails))

async def extract_gmb_listing_details(page, index: int, card_element) -> dict:
    """Extracts detailed info from a Google Maps listing element / detail pane."""
    data = {
        "name": "",
        "rating": "",
        "reviews_count": "",
        "category": "",
        "address": "",
        "phone": "",
        "website": "",
        "email": "",
        "google_maps_url": ""
    }

    try:
        # First check card text directly
        card_text = await card_element.inner_text()
        
        # Click the link inside the card to open details pane
        link_el = await card_element.query_selector("a[href*='/maps/place/'], a.hfA2B")
        if link_el:
            await link_el.click()
        else:
            await card_element.click()
        await asyncio.sleep(2.5)
    except Exception as e:
        print(f"   [-] Warning: could not click card #{index+1}: {e}")

    # Extract details from card and side panel
    try:
        # Title / Name: First try directly from card element (most accurate per card)
        aria_name = await card_element.get_attribute("aria-label")
        card_title_el = await card_element.query_selector("div.fontHeadlineSmall, div.qBF1Pd, span.OSrA2b, a.hfA2B")
        
        if aria_name and aria_name.strip():
            data["name"] = aria_name.strip()
        elif card_title_el:
            data["name"] = (await card_title_el.inner_text()).strip()
        else:
            # Fallback to detail pane title
            title_el = await page.query_selector("h1.DUwif, h1.fontHeadlineLarge, div.fontHeadlineSmall")
            if title_el:
                data["name"] = (await title_el.inner_text()).strip()

        # Google Maps URL
        data["google_maps_url"] = page.url


        # Rating & Reviews
        rating_el = await page.query_selector("div.F7v2d span.MW4etd, span.MW4etd, div.fontBodyMedium span[role='img']")
        if rating_el:
            data["rating"] = (await rating_el.inner_text()).strip()

        reviews_el = await page.query_selector("button:has-text('reviews'), span.UY7F9, button[aria-label*='reviews']")
        if reviews_el:
            rev_txt = await reviews_el.inner_text()
            data["reviews_count"] = re.sub(r"[^\d]", "", rev_txt)

        # Category
        cat_el = await page.query_selector("button.DkEaL, button[jsaction*='category']")
        if cat_el:
            data["category"] = (await cat_el.inner_text()).strip()

        # Address: Try button attribute, then inner_text, then card text fallback
        addr_el = await page.query_selector("button[data-item-id='address'], button[aria-label*='Address:']")
        if addr_el:
            aria_label = await addr_el.get_attribute("aria-label")
            if aria_label:
                data["address"] = re.sub(r"^Address:\s*", "", aria_label, flags=re.IGNORECASE).strip()
            else:
                data["address"] = (await addr_el.inner_text()).replace("Address:", "").strip()

        # Phone: Try button attribute, then inner_text
        phone_el = await page.query_selector("button[data-item-id*='phone'], button[aria-label*='Phone:']")
        if phone_el:
            aria_label = await phone_el.get_attribute("aria-label")
            if aria_label:
                data["phone"] = re.sub(r"^Phone:\s*", "", aria_label, flags=re.IGNORECASE).strip()
            else:
                data["phone"] = (await phone_el.inner_text()).replace("Phone:", "").strip()

        # Website: Try href on authority element or card website button
        web_el = await page.query_selector("a[data-item-id='authority'], a[aria-label*='Website:']")
        if web_el:
            href = await web_el.get_attribute("href")
            if href:
                data["website"] = href.strip()
        else:
            # Fallback to card website link
            card_web_el = await card_element.query_selector("a[data-value='Website'], a[aria-label*='website']")
            if card_web_el:
                href = await card_web_el.get_attribute("href")
                if href:
                    data["website"] = href.strip()

    except Exception as err:
        print(f"   [-] Error extracting card details #{index+1}: {err}")


    # Crawl website for email if website exists
    if data["website"]:
        print(f"   [+] Crawling website for email: {data['website']}")
        data["email"] = scrape_emails_from_website(data["website"])

    return data

async def scrape_gmb_query(playwright, query: str, max_results: int = 50, headless: bool = True) -> list:
    print(f"\n==================================================")
    print(f"[*] Starting GMB Scrape for Query: '{query}'")
    print(f"[*] Target count: {max_results} listings")
    print(f"==================================================")

    browser = await playwright.chromium.launch(
        headless=headless,
        args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage", "--lang=en-US"]
    )
    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        viewport={"width": 1280, "height": 900},
        locale="en-US"
    )
    page = await context.new_page()

    encoded_query = urllib.parse.quote(query)
    url = f"https://www.google.com/maps/search/{encoded_query}"
    
    print(f"[*] Navigating to: {url}")
    await page.goto(url, wait_until="domcontentloaded", timeout=60000)
    await asyncio.sleep(3.0)

    # Handle Google Consent/Cookie modal if present
    try:
        accept_btn = await page.query_selector("button:has-text('Accept all'), button:has-text('I agree'), form button[aria-label*='Accept']")
        if accept_btn:
            print("[*] Dismissing consent dialog...")
            await accept_btn.click()
            await asyncio.sleep(2.0)
    except Exception:
        pass

    # Wait for results panel / feed container
    try:
        await page.wait_for_selector("div[role='feed'], div.m6QEbc", timeout=15000)
    except Exception:
        print("[!] Warning: Feed container selector wait timed out. Attempting to scroll page.")

    # Scroll sidebar feed to load up to max_results items
    print("[*] Scrolling sidebar to load GMB listings...")
    feed_selector = "div[role='feed']"
    
    prev_count = 0
    same_count_retries = 0

    while True:
        cards = await page.query_selector_all("div[role='article'], a.hfA2B, div.Nv251d")
        curr_count = len(cards)
        print(f"    Loaded {curr_count}/{max_results} listings...")

        if curr_count >= max_results:
            print(f"[+] Reached target count of {max_results} listings.")
            break

        if curr_count == prev_count:
            same_count_retries += 1
            if same_count_retries >= 5:
                print(f"[!] No new items found after multiple scroll attempts. Stopping scroll at {curr_count} items.")
                break
        else:
            same_count_retries = 0
            prev_count = curr_count

        # Scroll feed element down
        feed_el = await page.query_selector(feed_selector)
        if feed_el:
            await feed_el.evaluate("el => el.scrollBy(0, 1500)")
        else:
            await page.keyboard.press("PageDown")

        await asyncio.sleep(1.8)

    # Re-fetch card elements up to max_results
    cards = await page.query_selector_all("div[role='article'], a.hfA2B, div.Nv251d")
    cards = cards[:max_results]

    results = []
    print(f"\n[*] Extracting details for {len(cards)} listings...")
    
    for i, card in enumerate(cards):
        print(f"\n---> Processing listing {i+1}/{len(cards)}")
        listing_data = await extract_gmb_listing_details(page, i, card)
        if listing_data["name"]:
            listing_data["search_rank_position"] = i + 1
            results.append(listing_data)

            print(f"     Name:    {listing_data['name']}")
            print(f"     Phone:   {listing_data['phone'] or 'N/A'}")
            print(f"     Address: {listing_data['address'] or 'N/A'}")
            print(f"     Website: {listing_data['website'] or 'N/A'}")
            print(f"     Email:   {listing_data['email'] or 'N/A'}")

    await browser.close()
    return results

def save_output(query: str, results: list) -> tuple:
    sanitized_name = re.sub(r"[^\w]+", "_", query.lower()).strip("_")
    csv_path = TMP_DIR / f"gmb_leads_{sanitized_name}.csv"
    json_path = TMP_DIR / f"gmb_leads_{sanitized_name}.json"

    df = pd.DataFrame(results)
    if not df.empty:
        df = process_and_qualify_dataframe(df)

    df.to_csv(csv_path, index=False, encoding="utf-8")
    
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(df.to_dict(orient="records"), f, indent=2, ensure_ascii=False)

    print(f"\n[+] Qualified & Processed {len(df)} profiles saved to:")
    print(f"    CSV:  {csv_path}")
    print(f"    JSON: {json_path}")

    # Export to fresh Google Sheet
    sheet_title = f"GMB Leads & Pitches - {query}"
    export_df_to_google_sheet(df, sheet_title)

    return csv_path, json_path



async def main():
    parser = argparse.ArgumentParser(description="Google My Business Profile Scraper")
    parser.add_argument("--query", nargs="+", required=True, help="Search query string(s) (e.g. 'NGOs in Abuja, Nigeria')")
    parser.add_argument("--max-results", type=int, default=50, help="Maximum number of listings to scrape per query")
    parser.add_argument("--headful", action="store_true", help="Run browser in visible headful mode (default: headless)")

    args = parser.parse_args()
    headless = not args.headful

    all_results = []
    
    async with async_playwright() as playwright:
        for q in args.query:
            query_results = await scrape_gmb_query(playwright, q, max_results=args.max_results, headless=headless)
            save_output(q, query_results)
            all_results.extend(query_results)

    if len(args.query) > 1 and all_results:
        combined_csv = TMP_DIR / "gmb_leads_combined.csv"
        combined_json = TMP_DIR / "gmb_leads_combined.json"
        
        df_all = pd.DataFrame(all_results)
        df_all = process_and_qualify_dataframe(df_all)
        
        df_all.to_csv(combined_csv, index=False, encoding="utf-8")
        
        with open(combined_json, "w", encoding="utf-8") as f:
            json.dump(df_all.to_dict(orient="records"), f, indent=2, ensure_ascii=False)

        print(f"\n[==================================================]")
        print(f"[+] Combined Output ({len(df_all)} total listings):")
        print(f"    CSV:  {combined_csv}")
        print(f"    JSON: {json_path if 'json_path' in locals() else combined_json}")
        print(f"[==================================================]")

        export_df_to_google_sheet(df_all, "GMB Leads & Pitches - Combined (Abuja & Lagos)")


if __name__ == "__main__":
    asyncio.run(main())
