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

- [x] **Step 1: Write CLI script skeleton and worksheet initializer**
- [x] **Step 2: Add `--sync-replies` to promote replied leads to `2_Active_Deals`**
- [x] **Step 3: Add `--onboard-closed-won` to generate project deliverable checklists in `3_Project_Milestones`**
- [x] **Step 4: Execute `--init-crm` to initialize all 4 CRM tabs on the live Google Sheet**
