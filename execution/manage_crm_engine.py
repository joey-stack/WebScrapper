#!/usr/bin/env python3
"""
Layer 3: Execution Tool - Multi-Tab Google Sheets CRM Engine & Project Tracker
Part of Jordan Platten's 5-Part Client Acquisition Engine:
Initializes, formats, and syncs 4 CRM tabs in Google Sheets:
1. 1_Outreach_Pipeline (ICP Scored & Sorted leads with WhatsApp copy)
2. 2_Active_Deals (Intent-tagged deal stages, contact routing, and action notes)
3. 3_Project_Milestones (50% Deposit & 4-Phase deliverable tracking)
4. 4_Financial_Dashboard (Automated formulas for Pipeline, Closed Won, MRR, & Sector Performance)
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
try:
    from export_to_google_sheets import get_gspread_client
except ImportError:
    from execution.export_to_google_sheets import get_gspread_client

DEFAULT_SHEET_URL = "https://docs.google.com/spreadsheets/d/1wGuXHelu2SqOUG2IQNMWG8gF08KqO_OcTb5rU1cziiU"
TMP_CSV = Path(__file__).parent.parent / ".tmp" / "gmb_leads_combined.csv"

def init_crm_worksheets(sheet_url: str):
    print(f"[*] Connecting to Google Sheet: {sheet_url}")
    client, _ = get_gspread_client()
    if not client:
        print("[!] Failed to authorize gspread client.")
        return
    spreadsheet = client.open_by_url(sheet_url)

    tab_names = ["1_Outreach_Pipeline", "2_Active_Deals", "3_Project_Milestones", "4_Financial_Dashboard"]
    for t_name in tab_names:
        try:
            spreadsheet.worksheet(t_name)
            print(f"[+] Worksheet '{t_name}' already exists.")
        except Exception:
            spreadsheet.add_worksheet(title=t_name, rows=100, cols=30)
            print(f"[+] Created worksheet '{t_name}'.")

    # Sync Tab 1 (Outreach Pipeline) from CSV if data exists
    if TMP_CSV.exists():
        df_pipeline = pd.read_csv(TMP_CSV)
        ws_p = spreadsheet.worksheet("1_Outreach_Pipeline")
        ws_p.clear()
        ws_p.update([df_pipeline.columns.values.tolist()] + df_pipeline.fillna("").values.tolist())
        print("[+] Synced 1_Outreach_Pipeline with latest ICP-scored leads.")

    # Initialize Tab 2 (Active Deals) headers if empty
    ws_deals = spreadsheet.worksheet("2_Active_Deals")
    if not ws_deals.get_all_values():
        headers_deals = [
            "Organization Name", "Contact Email", "Deal Stage", "Response Intent", "Price Class", 
            "One-Time Setup Fee", "Monthly Maintenance Retainer", "Total Deal Value (NGN)", 
            "Latest Client Reply Snippet", "Last Response Timestamp", "Next Action Notes"
        ]
        ws_deals.update([headers_deals])
        print("[+] Formatted 2_Active_Deals headers.")

    # Initialize Tab 3 (Project Milestones) headers if empty
    ws_milestones = spreadsheet.worksheet("3_Project_Milestones")
    if not ws_milestones.get_all_values():
        headers_milestones = [
            "Client Name", "Price Class", "Project Status", 
            "Phase 1: 50% Deposit Paid", "Phase 1: GMB Access Granted", "Phase 1: Domain Credentials Granted",
            "Phase 2: Web Portal Launched", "Phase 2: 30+ Directory Citations", "Phase 2: Geotagged Media Uploaded",
            "Phase 3: Review System Active", "Phase 3: GEO Schema Deployed", 
            "Phase 4: 50% Final Balance Paid", "Phase 4: Monthly Retainer Active",
            "Project Start Date", "Target Completion Date"
        ]
        ws_milestones.update([headers_milestones])
        print("[+] Formatted 3_Project_Milestones headers.")

    # Format Tab 4 (Financial Dashboard) formulas
    ws_dash = spreadsheet.worksheet("4_Financial_Dashboard")
    ws_dash.clear()
    dash_data = [
        ["AGENCY FINANCIAL & CLIENT ACQUISITION METRICS DASHBOARD"],
        [""],
        ["Metric Description", "Formula / Calculated Value", "Notes & Insights"],
        ["Total Pipeline Opportunities", "=COUNTA('1_Outreach_Pipeline'!A2:A100)", "Total leads evaluated in pipeline"],
        ["Tier A Hot Leads (ICP 80-100)", "=COUNTIF('1_Outreach_Pipeline'!C2:C100, \"*Tier A*\")", "Highest-converting high-ticket prospects"],
        ["Total Active Deals In Discussion", "=COUNTA('2_Active_Deals'!A2:A100)", "Prospects currently in sales conversation"],
        ["Strategy Calls / Meetings Booked", "=COUNTIF('2_Active_Deals'!C2:C100, \"*MEETING*\")", "Calendar discovery meetings scheduled"],
        ["Total Closed Revenue (NGN)", "=SUMIF('2_Active_Deals'!C2:C100, \"CLOSED_WON\", '2_Active_Deals'!H2:H100)", "Realized revenue from Closed Won deals"],
        ["Monthly Recurring Revenue (MRR - NGN)", "=SUMIF('3_Project_Milestones'!C2:C100, \"COMPLETED_RETAINER_ACTIVE\", '2_Active_Deals'!G2:G100)", "Active ongoing monthly retainers"],
        ["Outreach Conversion Rate %", "=IFERROR((COUNTIF('2_Active_Deals'!C2:C100, \"CLOSED_WON\") / COUNTA('1_Outreach_Pipeline'!A2:A100)) * 100, 0)", "Percentage of pipeline leads converted to Closed Won"]
    ]
    ws_dash.update(dash_data)
    print("[+] Formatted 4_Financial_Dashboard formula metrics.")

def sync_replies_to_active_deals(sheet_url: str):
    print(f"[*] Syncing email replies to 2_Active_Deals...")
    client, _ = get_gspread_client()
    if not client:
        print("[!] Failed to authorize gspread client.")
        return
    spreadsheet = client.open_by_url(sheet_url)
    ws_pipeline = spreadsheet.worksheet("1_Outreach_Pipeline")
    ws_deals = spreadsheet.worksheet("2_Active_Deals")

    records = ws_pipeline.get_all_records()
    if not records:
        print("[!] No records found in 1_Outreach_Pipeline.")
        return

    df = pd.DataFrame(records)
    if "email_sent_status" not in df.columns:
        print("[!] Column 'email_sent_status' missing in 1_Outreach_Pipeline.")
        return

    replied = df[df["email_sent_status"] == "CLIENT_REPLIED"]
    if replied.empty:
        print("[*] No CLIENT_REPLIED leads found in 1_Outreach_Pipeline.")
        return

    deals_rows = []
    headers = [
        "Organization Name", "Contact Email", "Deal Stage", "Response Intent", "Price Class", 
        "One-Time Setup Fee", "Monthly Maintenance Retainer", "Total Deal Value (NGN)", 
        "Latest Client Reply Snippet", "Last Response Timestamp", "Next Action Notes"
    ]

    for _, row in replied.iterrows():
        directed_e = str(row.get("directed_proposal_email", "")).strip()
        orig_e = str(row.get("email", "")).strip()
        intent = str(row.get("response_intent", "GENERAL_INQUIRY")).strip().upper()

        if intent == "MEETING_REQUEST":
            stage = "📅 MEETING_REQUESTED (Calendar Invite Sent)"
            action_notes = "Calendar booking invite sent. Monitor calendar booking / WhatsApp response."
        elif intent == "HIGH_INTENT_CLOSE":
            stage = "🔥 HIGH_INTENT_CLOSE (Proposal & Invoice Pending)"
            action_notes = "High-intent closing signal! Deliver invoice / banking details for Phase 1 onboarding."
        elif intent == "PRICING_QUESTION":
            stage = "💬 PRICING_INQUIRY (Proposal Auto-Sent)"
            action_notes = "Package tier breakdown & PDF proposal sent. Follow-up within 24 hours."
        elif intent == "PROPOSAL_REQUEST":
            stage = "📄 PROPOSAL_AUTO_SENT"
            action_notes = "PDF Proposal delivered to client. Follow-up on review."
        else:
            stage = "💬 ACTIVE_INQUIRY"
            action_notes = "Engage in consultative conversation."

        if directed_e and "@" in directed_e and directed_e.lower() != orig_e.lower():
            contact_email = f"{directed_e} (orig: {orig_e})"
            action_notes += f" [Routed to requested address: {directed_e}]"
        else:
            contact_email = directed_e if (directed_e and "@" in directed_e) else orig_e

        deals_rows.append([
            row.get("name", ""),
            contact_email,
            stage,
            intent,
            row.get("price_class", ""),
            row.get("one_time_setup_fee", ""),
            row.get("monthly_maintenance_fee", ""),
            row.get("recommended_price_ngn", ""),
            row.get("latest_client_reply_snippet", ""),
            row.get("client_replied_at", datetime.datetime.now().strftime("%Y-%m-%d %H:%M")),
            action_notes
        ])

    ws_deals.clear()
    ws_deals.update([headers] + deals_rows)
    print(f"[+] Promoted {len(deals_rows)} replied leads to 2_Active_Deals with intent tags.")

def onboard_closed_won_projects(sheet_url: str):
    print(f"[*] Scanning 2_Active_Deals for CLOSED_WON projects...")
    client, _ = get_gspread_client()
    if not client:
        print("[!] Failed to authorize gspread client.")
        return
    spreadsheet = client.open_by_url(sheet_url)
    ws_deals = spreadsheet.worksheet("2_Active_Deals")
    ws_milestones = spreadsheet.worksheet("3_Project_Milestones")

    records = ws_deals.get_all_records()
    if not records:
        print("[!] No deals found in 2_Active_Deals.")
        return

    df = pd.DataFrame(records)
    if "Deal Stage" not in df.columns:
        print("[!] Column 'Deal Stage' missing in 2_Active_Deals.")
        return

    closed = df[df["Deal Stage"].astype(str).str.contains("CLOSED_WON", case=False)]
    if closed.empty:
        print("[*] No CLOSED_WON deals found in 2_Active_Deals.")
        return

    milestone_rows = []
    headers = [
        "Client Name", "Price Class", "Project Status", 
        "Phase 1: 50% Deposit Paid", "Phase 1: GMB Access Granted", "Phase 1: Domain Credentials Granted",
        "Phase 2: Web Portal Launched", "Phase 2: 30+ Directory Citations", "Phase 2: Geotagged Media Uploaded",
        "Phase 3: Review System Active", "Phase 3: GEO Schema Deployed", 
        "Phase 4: 50% Final Balance Paid", "Phase 4: Monthly Retainer Active",
        "Project Start Date", "Target Completion Date"
    ]

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

    ws_milestones.clear()
    ws_milestones.update([headers] + milestone_rows)
    print(f"[+] Created deliverable tracking for {len(milestone_rows)} CLOSED_WON projects in 3_Project_Milestones.")

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
    if args.onboard_closed_won:
        onboard_closed_won_projects(args.sheet_url)
