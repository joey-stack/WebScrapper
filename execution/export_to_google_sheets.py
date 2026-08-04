#!/usr/bin/env python3
"""
Layer 3: Execution Tool - Google Sheets Exporter
Creates a fresh Google Sheet for scraped deliverables and populates it with extracted data.
Uses gspread and google-auth. Looks for credentials.json, token.json, or SERVICE_ACCOUNT_FILE in .env.
"""

import os
import sys
import json
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# Synchronize time with Google HTTP server to handle system clock skew
def patch_google_auth_time_skew():
    try:
        import time, datetime, email.utils, requests, google.auth._helpers
        resp = requests.head('https://www.google.com', timeout=5)
        date_str = resp.headers.get('Date')
        if date_str:
            server_ts = email.utils.mktime_tz(email.utils.parsedate_tz(date_str))
            google.auth._helpers.utcnow = lambda: datetime.datetime.fromtimestamp(server_ts, datetime.timezone.utc).replace(tzinfo=None)
    except Exception:
        pass

patch_google_auth_time_skew()


def get_gspread_client():
    import gspread
    from google.oauth2 import service_account
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")
    token_path = os.getenv("GOOGLE_TOKEN_FILE", "token.json")

    # Method 1: Service Account JSON
    if os.path.exists(credentials_path):
        try:
            with open(credentials_path, "r") as f:
                cred_data = json.load(f)
            if cred_data.get("type") == "service_account":
                scopes = [
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive"
                ]
                creds = service_account.Credentials.from_service_account_file(credentials_path, scopes=scopes)
                client = gspread.authorize(creds)
                return client, "service_account"
        except Exception as e:
            print(f"   [-] Service account auth attempt error: {e}")

    # Method 2: OAuth Token JSON
    if os.path.exists(token_path):
        try:
            scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
            creds = Credentials.from_authorized_user_file(token_path, scopes=scopes)
            client = gspread.authorize(creds)
            return client, "oauth_token"
        except Exception as e:
            print(f"   [-] OAuth token auth attempt error: {e}")

    return None, None

def export_df_to_google_sheet(df: pd.DataFrame, title_or_url: str, share_email: str = None) -> str:
    client, auth_type = get_gspread_client()
    
    if not client:
        print("\n[!] Google Credentials Not Configured:")
        print("    To automatically export to Google Sheets, place your 'credentials.json' (Service Account or OAuth)")
        print("    in the project root directory: /Users/jdesign/Downloads/WebScrapper/credentials.json")
        print("    The CSV file in .tmp/ remains available as a local deliverable.")
        return ""

    try:
        sheet = None
        if title_or_url.startswith("http") or "docs.google.com" in title_or_url:
            print(f"\n[*] Opening existing Google Sheet URL: '{title_or_url}'...")
            sheet = client.open_by_url(title_or_url)
        else:
            try:
                print(f"\n[*] Creating fresh Google Sheet: '{title_or_url}'...")
                sheet = client.create(title_or_url)
            except Exception as create_err:
                if "quota" in str(create_err).lower() or "storage" in str(create_err).lower():
                    print("\n[!] Note: Google Service Accounts do not have personal Drive storage quota.")
                    print("    To publish to your Google Sheet:")
                    print("    1. Create a blank Google Sheet in your personal Google Account.")
                    print("    2. Share it with your Service Account email:")
                    print(f"       👉 webscrapper@leadgen-488818.iam.gserviceaccount.com")
                    print("    3. Run: python3 execution/export_to_google_sheets.py .tmp/gmb_leads_combined.csv \"<YOUR_SHEET_URL>\"")
                    return ""
                else:
                    raise create_err

        worksheet = sheet.get_worksheet(0)
        
        # Prepare header and data
        data_to_write = [df.columns.values.tolist()] + df.fillna("").astype(str).values.tolist()
        worksheet.clear()
        
        # In gspread v6, worksheet.update(data) updates the entire grid cleanly
        worksheet.update(data_to_write)


        sheet_url = sheet.url
        try:
            sheet.share(None, perm_type='anyone', role='reader')
            print(f"[+] Google Sheet permissions updated: Anyone with link can view.")
        except Exception:
            pass

        if share_email:
            try:
                sheet.share(share_email, perm_type='user', role='writer')
                print(f"[+] Shared Google Sheet with {share_email}")
            except Exception as se:
                print(f"[-] Could not share with {share_email}: {se}")

        print(f"\n[==================================================]")
        print(f"[+] SUCCESS! Dataset published to live Google Sheet:")
        print(f"    URL: {sheet_url}")
        print(f"[==================================================]")
        return sheet_url

    except Exception as err:
        err_msg = str(err)
        if "Google Drive API has not been used" in err_msg or "disabled" in err_msg:
            print("\n[!] Google Drive API is not enabled in your Google Cloud Project:")
            print("    Click this link to enable it with 1-click:")
            print("    👉 https://console.developers.google.com/apis/api/drive.googleapis.com/overview?project=227356734148")
        else:
            print(f"[-] Error updating Google Sheet: {err}")
        return ""

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 export_to_google_sheets.py <csv_file_path> <sheet_title_or_url>")
        sys.exit(1)
        
    csv_file = sys.argv[1]
    sheet_title_or_url = sys.argv[2]
    
    if os.path.exists(csv_file):
        df_input = pd.read_csv(csv_file)
        export_df_to_google_sheet(df_input, sheet_title_or_url)
    else:
        print(f"[-] File not found: {csv_file}")

