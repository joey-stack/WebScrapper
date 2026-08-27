# Daily Automated Lead Scraper Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `execution/scrape_daily_leads.py` to automatically extract 10–15 fresh buried leads (ranked #11–50+) daily, deduplicate against existing leads, run qualification & pitch generation, and integrate into `run_autonomous_crm_cycle.py`.

**Architecture:** Layer 3 Python script (`execution/scrape_daily_leads.py`) combining `scrape_gmb_leads.py` and `qualify_and_pitch_leads.py` with deduplication filtering and CRM sync.

**Tech Stack:** Python 3, `pandas`, `requests`, `gspread`, `dotenv`.

## Global Constraints
- Target Google Sheet: `https://docs.google.com/spreadsheets/d/1wGuXHelu2SqOUG2IQNMWG8gF08KqO_OcTb5rU1cziiU`
- Max Fresh Daily Leads: 10–15 unique leads per run
- Rank Window: Position #11 to #50+

---

### Task 1: Create Daily Lead Scraper Tool (`execution/scrape_daily_leads.py`)

**Files:**
- Create: `execution/scrape_daily_leads.py`

**Interfaces:**
- Consumes: `.tmp/gmb_leads_combined.csv`, `execution/scrape_gmb_leads.py`, `execution/qualify_and_pitch_leads.py`
- Produces: `scrape_and_append_daily_leads()` function

- [x] **Step 1: Write `execution/scrape_daily_leads.py` with category rotation, rank filtering, deduplication, and auto-qualification**
- [x] **Step 2: Hook `scrape_and_append_daily_leads()` into `execution/run_autonomous_crm_cycle.py`**
- [x] **Step 3: Test `execution/scrape_daily_leads.py`**
