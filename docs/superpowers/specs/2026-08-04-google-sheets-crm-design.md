# Multi-Tab Google Sheets CRM Engine & Project Tracker Spec

## 1. Goal & Architecture
Build an enterprise Multi-Tab Google Sheets CRM Engine connected to Python automation scripts. The system manages cold outreach lead pipelines, automated response promotion, active deal negotiation, 4-phase project deliverable checklists, and real-time agency revenue dashboards.

Live Google Sheet: `https://docs.google.com/spreadsheets/d/1wGuXHelu2SqOUG2IQNMWG8gF08KqO_OcTb5rU1cziiU`

---

## 2. Google Sheets Tab Specifications

### Tab 1: `1_Outreach_Pipeline` (Prospecting & Cold Dispatch)
Holds all qualified leads ranked #11–50+ on Google Maps.
- `name`: Organization Name
- `current_google_search_rank`: Position #11 to #50+ label
- `search_rank_position`: Integer rank
- `service_needed`: "Website Design Only", "GMB SEO Optimization Only", "Both (Website + GMB SEO)", or "Digital Maintenance"
- `price_class`: Tier 1, Tier 2, Tier 3, or Tier 4
- `one_time_setup_fee`: Setup fee in NGN & USD
- `monthly_maintenance_fee`: Monthly maintenance retainer in NGN & USD
- `recommended_price_ngn`: Package summary
- `service_scope_breakdown`: Itemized deliverables 1-5
- `profile_highlight`: Complimentary finding
- `organization_elevation`: 3-6 month roadmap
- `conversion_strategy`: In-depth 5-star ELI5 strategy with actionable solution approach
- `personalized_pitch`: Consultative email body with specific improvement observations
- `email_sent_status`: "PENDING", "SENT_INITIAL", "CLIENT_REPLIED"
- `sender_account_used`: Sender email address
- `initial_email_sent_at`: Sent timestamp
- `followup_due_at`: Scheduled +3 days due date
- `followup_sent_at`: Followup timestamp
- `followup_status`: "SCHEDULED_DAY_3", "SENT_FOLLOWUP_1", "CANCELLED_CLIENT_REPLIED"
- `phone`, `email`, `website`, `address`, `rating`, `reviews_count`, `category`, `google_maps_url`

### Tab 2: `2_Active_Deals` (Negotiation & Conversion)
Auto-populated when `track_email_responses.py` detects an email reply or when promoted by `manage_crm_engine.py`.
- `lead_name`: Organization Name
- `email`: Contact Email
- `deal_stage`: Dropdown ("🔥 HOT LEAD REPLIED", "MEETING_SCHEDULED", "PROPOSAL_SENT", "CLOSED_WON", "CLOSED_LOST")
- `price_class`: Tier tag
- `one_time_setup_fee`: NGN / USD
- `monthly_maintenance_fee`: NGN / USD
- `total_deal_value_ngn`: Full NGN value
- `latest_reply_snippet`: Clean text snippet of client response
- `last_response_at`: Reply timestamp
- `next_action_notes`: Free text notes & meeting date

### Tab 3: `3_Project_Milestones` (Client Delivery & Execution)
Auto-generated when a deal is updated to `CLOSED_WON`.
- `client_name`: Organization Name
- `service_package`: Service Needed
- `price_class`: Tier tag
- `project_status`: "ONBOARDING", "IN_PROGRESS", "REVIEW_PHASE", "COMPLETED_RETAINER_ACTIVE"
- `phase1_deposit_paid`: Checkbox / Status ("DONE" / "PENDING") - 50% Deposit
- `phase1_gmb_access_granted`: Checkbox / Status ("DONE" / "PENDING")
- `phase1_domain_credentials`: Checkbox / Status ("DONE" / "PENDING")
- `phase2_web_portal_launched`: Checkbox / Status ("DONE" / "PENDING")
- `phase2_directory_citations_30`: Checkbox / Status ("DONE" / "PENDING")
- `phase2_geotagged_media`: Checkbox / Status ("DONE" / "PENDING")
- `phase3_review_workflow`: Checkbox / Status ("DONE" / "PENDING")
- `phase3_geo_schema_deployed`: Checkbox / Status ("DONE" / "PENDING")
- `phase4_final_balance_paid`: Checkbox / Status ("DONE" / "PENDING") - 50% Balance
- `phase4_retainer_active`: Checkbox / Status ("ACTIVE" / "PENDING")
- `project_start_date`: Date string
- `target_completion_date`: Date string

### Tab 4: `4_Financial_Dashboard` (Revenue & Agency Metrics)
Automated formula dashboard calculating live revenue:
- `Total Pipeline Value (NGN)`: Sum of all potential deal values
- `Total Closed Revenue (NGN)`: Sum of closed won deals (Deposits + Final Balances)
- `Monthly Recurring Revenue (MRR - NGN)`: Sum of active monthly maintenance retainers
- `Outreach Conversion Rate %`: (Closed Won Deals / Total Dispatched Outreach) * 100

---

## 3. Automation Scripts (`execution/manage_crm_engine.py`)

1. **`--init-crm`**: Initializes all 4 tabs on the user's live Google Sheet with custom headers, formatting, and data validation rules.
2. **`--sync-replies`**: Promotes replied leads from `1_Outreach_Pipeline` to `2_Active_Deals`.
3. **`--onboard-closed-won`**: Scans `2_Active_Deals` for `CLOSED_WON` deals and creates corresponding deliverable tracking rows in `3_Project_Milestones` and updates `4_Financial_Dashboard`.
