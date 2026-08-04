# Multi-Tab Google Sheets CRM Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Multi-Tab Google Sheets CRM Engine (`execution/manage_crm_engine.py`) that initializes 4 tabs on the user's live sheet, auto-promotes replied leads to `2_Active_Deals`, auto-onboards `CLOSED_WON` deals into `3_Project_Milestones`, and updates `4_Financial_Dashboard`.

**Architecture:** Layer 3 Python tool (`execution/manage_crm_engine.py`) using `gspread` and `pandas` to manage worksheet tabs, data validation rules, conditional formatting, and multi-tab sync.

**Tech Stack:** Python 3, `gspread`, `google.oauth2.credentials`, `pandas`, `dotenv`.

## Global Constraints
- Target Google Sheet URL: `https://docs.google.com/spreadsheets/d/1wGuXHelu2SqOUG2IQNMWG8gF08KqO_OcTb5rU1cziiU`
- Currency Formatting: NGN & USD
- Worksheets Managed: `1_Outreach_Pipeline`, `2_Active_Deals`, `3_Project_Milestones`, `4_Financial_Dashboard`

---

### Task 1: Create CRM Engine CLI Tool (`execution/manage_crm_engine.py`)

**Files:**
- Create: `execution/manage_crm_engine.py`

**Interfaces:**
- Consumes: `.tmp/gmb_leads_combined.csv`, Google OAuth Credentials (`token.json`/`credentials.json`), `export_to_google_sheets.py`
- Produces: CLI interface `--init-crm`, `--sync-replies`, `--onboard-closed-won`

- [ ] **Step 1: Write CLI script skeleton and worksheet initializer**

```python
#!/usr/bin/env python3
"""
Layer 3: Execution Tool - Multi-Tab Google Sheets CRM Engine & Project Tracker
Initializes and syncs 4 CRM tabs: 1_Outreach_Pipeline, 2_Active_Deals, 3_Project_Milestones, 4_Financial_Dashboard.
"""

import argparse
import datetime
import os
import sys
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, str(Path(__file__).parent))
from export_to_google_sheets import get_gspread_client

DEFAULT_SHEET_URL = "https://docs.google.com/spreadsheets/d/1wGuXHelu2SqOUG2IQNMWG8gF08KqO_OcTb5rU1cziiU"
TMP_CSV = Path(__file__).parent.parent / ".tmp" / "gmb_leads_combined.csv"

def init_crm_worksheets(sheet_url: str):
    client = get_gspread_client()
    spreadsheet = client.open_by_url(sheet_url)
    
    tab_names = ["1_Outreach_Pipeline", "2_Active_Deals", "3_Project_Milestones", "4_Financial_Dashboard"]
    for t_name in tab_names:
        try:
            spreadsheet.worksheet(t_name)
            print(f"[+] Worksheet '{t_name}' already exists.")
        except Exception:
            spreadsheet.add_worksheet(title=t_name, rows=100, cols=25)
            print(f"[+] Created worksheet '{t_name}'.")

    # Format Tab 1 (Outreach Pipeline) from CSV
    if TMP_CSV.exists():
        df_pipeline = pd.read_csv(TMP_CSV)
        ws_p = spreadsheet.worksheet("1_Outreach_Pipeline")
        ws_p.clear()
        ws_p.update([df_pipeline.columns.values.tolist()] + df_pipeline.fillna("").values.tolist())
        print("[+] Synced 1_Outreach_Pipeline data.")

    # Format Tab 4 (Financial Dashboard) formulas
    ws_dash = spreadsheet.worksheet("4_Financial_Dashboard")
    ws_dash.clear()
    dash_data = [
        ["AGENCY FINANCIAL & PIPELINE METRICS DASHBOARD"],
        ["Metric", "Value (NGN)", "Notes"],
        ["Total Pipeline Value", "=SUM('1_Outreach_Pipeline'!F2:F100)", "Total potential setup fees"],
        ["Total Closed Revenue", "=SUMIF('2_Active_Deals'!C2:C100, \"CLOSED_WON\", '2_Active_Deals'!G2:G100)", "Realized revenue from Closed Won deals"],
        ["Monthly Recurring Revenue (MRR)", "=SUMIF('3_Project_Milestones'!D2:D100, \"COMPLETED_RETAINER_ACTIVE\", '2_Active_Deals'!F2:F100)", "Active monthly retainers"],
        ["Outreach Conversion Rate %", "=IFERROR((COUNTIF('2_Active_Deals'!C2:C100, \"CLOSED_WON\") / COUNTA('1_Outreach_Pipeline'!A2:A100)) * 100, 0)", "Closed Won vs Total Leads"]
    ]
    ws_dash.update(dash_data)
    print("[+] Formatted 4_Financial_Dashboard formulas.")
```

- [ ] **Step 2: Add `--sync-replies` to promote replied leads to `2_Active_Deals`**

```python
def sync_replies_to_active_deals(sheet_url: str):
    client = get_gspread_client()
    spreadsheet = client.open_by_url(sheet_url)
    ws_pipeline = spreadsheet.worksheet("1_Outreach_Pipeline")
    ws_deals = spreadsheet.worksheet("2_Active_Deals")

    data = ws_pipeline.get_all_records()
    df = pd.DataFrame(data)

    replied = df[df["email_sent_status"] == "CLIENT_REPLIED"]
    if replied.empty:
        print("[*] No replied leads to promote to 2_Active_Deals.")
        return

    deals_rows = []
    for _, row in replied.iterrows():
        deals_rows.append([
            row.get("name", ""),
            row.get("email", ""),
            "🔥 HOT LEAD REPLIED",
            row.get("price_class", ""),
            row.get("one_time_setup_fee", ""),
            row.get("monthly_maintenance_fee", ""),
            row.get("recommended_price_ngn", ""),
            row.get("latest_client_reply_snippet", ""),
            row.get("client_replied_at", datetime.datetime.now().strftime("%Y-%m-%d %H:%M")),
            "Follow-up call / Send Proposal"
        ])

    headers = [
        "Organization Name", "Contact Email", "Deal Stage", "Price Class", 
        "One-Time Setup Fee", "Monthly Maintenance Retainer", "Total Deal Value (NGN)", 
        "Latest Client Reply Snippet", "Last Response Timestamp", "Next Action Notes"
    ]
    ws_deals.clear()
    ws_deals.update([headers] + deals_rows)
    print(f"[+] Promoted {len(deals_rows)} replied leads to 2_Active_Deals.")
```

- [ ] **Step 3: Add `--onboard-closed-won` to generate project deliverable checklists in `3_Project_Milestones`**

```python
def onboard_closed_won_projects(sheet_url: str):
    client = get_gspread_client()
    spreadsheet = client.open_by_url(sheet_url)
    ws_deals = spreadsheet.worksheet("2_Active_Deals")
    ws_milestones = spreadsheet.worksheet("3_Project_Milestones")

    data = ws_deals.get_all_records()
    df = pd.DataFrame(data)

    closed = df[df["Deal Stage"] == "CLOSED_WON"]
    if closed.empty:
        print("[*] No CLOSED_WON deals found.")
        return

    milestone_rows = []
    now_str = datetime.datetime.now().strftime("%Y-%m-%d")
    target_str = (datetime.datetime.now() + datetime.timedelta(days=60)).strftime("%Y-%m-%d")

    for _, row in closed.iterrows():
        milestone_rows.append([
            row.get("Organization Name", ""),
            row.get("Price Class", ""),
            "ONBOARDING",
            "PENDING",  # Phase 1 Deposit (50%)
            "PENDING",  # Phase 1 GMB Access
            "PENDING",  # Phase 1 Domain Credentials
            "PENDING",  # Phase 2 Web Portal Launched
            "PENDING",  # Phase 2 Directory Citations (30+)
            "PENDING",  # Phase 2 Geotagged Media
            "PENDING",  # Phase 3 Review System
            "PENDING",  # Phase 3 GEO Schema
            "PENDING",  # Phase 4 Final Balance (50%)
            "PENDING",  # Phase 4 Retainer Active
            now_str,
            target_str
        ])

    headers = [
        "Client Name", "Price Class", "Project Status", 
        "Phase 1: 50% Deposit Paid", "Phase 1: GMB Access Granted", "Phase 1: Domain Credentials Granted",
        "Phase 2: Web Portal Launched", "Phase 2: 30+ Directory Citations", "Phase 2: Geotagged Media Uploaded",
        "Phase 3: Review System Active", "Phase 3: GEO Schema Deployed", 
        "Phase 4: 50% Final Balance Paid", "Phase 4: Monthly Retainer Active",
        "Project Start Date", "Target Completion Date"
    ]
    ws_milestones.clear()
    ws_milestones.update([headers] + milestone_rows)
    print(f"[+] Created deliverable tracking for {len(milestone_rows)} CLOSED_WON projects.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-Tab Google Sheets CRM Engine")
    parser.add_argument("--init-crm", action="store_true", help="Initialize all 4 CRM worksheets")
    parser.add_argument("--sync-replies", action="store_true", help="Promote replied leads to 2_Active_Deals")
    parser.add_argument("--onboard-closed-won", action="store_true", help="Onboard CLOSED_WON deals to 3_Project_Milestones")
    parser.add_argument("--sheet-url", type=str, default=DEFAULT_SHEET_URL, help="Google Sheet URL")

    args = parser.parse_args()

    if args.init_crm:
        init_crm_worksheets(args.sheet_url)
    if args.sync_replies:
        sync_replies_to_active_deals(args.sheet_url)
    if args.onboard-closed-won:
        onboard_closed_won_projects(args.sheet_url)
```

- [ ] **Step 4: Execute `--init-crm` to initialize all 4 CRM tabs on the live Google Sheet**

Run: `python3 execution/manage_crm_engine.py --init-crm`
Expected Output: `SUCCESS! Formatted 4_Financial_Dashboard formulas and initialized 4 CRM worksheets.`
