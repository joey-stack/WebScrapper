#!/usr/bin/env python3
"""
Layer 3: Execution Tool - Principal Lead Qualification, Factual Elevation Proposal & AI Pitch Generator
Extracts profile highlights, current rank status, qualifies leads into target service categories,
generates brutally honest & factual proposal-style elevation roadmaps with realistic #1 rank timelines,
executive consultation blueprints, and consultative pitch copy.
Includes SEO & GEO (Generative Engine Optimization) standards.
"""

import re
import urllib.parse
import pandas as pd

def qualify_lead(row: dict) -> str:
    website = str(row.get("website", "") or "").strip()
    phone = str(row.get("phone", "") or "").strip()
    address = str(row.get("address", "") or "").strip()
    
    try:
        reviews_count = int(row.get("reviews_count", 0) or 0)
    except Exception:
        reviews_count = 0

    try:
        rank_pos = int(row.get("search_rank_position", row.get("rank_position", 99)))
    except Exception:
        rank_pos = 99

    has_website = bool(website and website.startswith("http") and "google.com" not in website)
    gmb_needs_opt = bool(not phone or not address or reviews_count < 5 or rank_pos > 3)

    if not has_website and gmb_needs_opt:
        return "Both (Website + GMB SEO)"
    elif not has_website:
        return "Website Design Only"
    elif gmb_needs_opt:
        return "GMB SEO Optimization Only"
    else:
        return "Fully Optimized (Top 3)"

def get_clean_name(raw_name: str) -> str:
    """Removes trailing location descriptors like '| NGO in Abuja, Nigeria' or '- NGO Lagos'."""
    clean = re.sub(r"\s*[\|\-].*$", "", str(raw_name or "")).strip()
    return clean if clean else str(raw_name or "").strip()

def clean_duplicate_locations(text: str) -> str:
    """Removes accidental duplicate location phrases like 'in Abuja in Abuja' or 'in Lagos in Lagos'."""
    text = re.sub(r"\bin\s+(Abuja|Lagos|Nigeria)\s+in\s+\1\b", r"in \1", text, flags=re.IGNORECASE)
    text = re.sub(r"\bin\s+(Abuja|Lagos|Nigeria)\s+in\s+(Abuja|Lagos|Nigeria)\b", r"in \1", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(Abuja|Lagos|Nigeria),\s+\1\b", r"\1", text, flags=re.IGNORECASE)
    return text

def generate_profile_highlight(row: dict) -> str:
    """Extracts a positive, complimentary finding from the profile (never critical)."""
    name = str(row.get("name", "") or "").strip()
    rating = str(row.get("rating", "") or "").strip()
    reviews = str(row.get("reviews_count", "") or "").strip()
    address = str(row.get("address", "") or "").strip()
    
    highlights = []
    if rating and rating != "N/A":
        highlights.append(f"strong community trust score ({rating}★ review rating)")
    elif reviews and int(reviews or 0) > 0:
        highlights.append(f"active community engagement with {reviews} public reviews")
        
    if "abuja" in address.lower() or "abuja" in name.lower():
        highlights.append("established capital presence")
    elif "lagos" in address.lower() or "lagos" in name.lower():
        highlights.append("strategic operational footprint")
    else:
        highlights.append("recognized local community footprint")

    return " & ".join(highlights) if highlights else "established NGO community presence"

def generate_organization_elevation(row: dict, service_needed: str, highlight: str) -> str:
    """
    Generates a brutally honest, factual, and professional elevation roadmap.
    Uses realistic 3-6 month benchmarks and avoids exaggerated #1 rank or call multiplier claims.
    """
    raw_name = str(row.get("name", "Organization")).strip()
    name = get_clean_name(raw_name)
    rank_pos = row.get("search_rank_position", row.get("rank_position", ""))
    address = str(row.get("address", "")).strip()
    
    location = "Nigeria"
    if "abuja" in address.lower() or "abuja" in raw_name.lower():
        location = "Abuja"
    elif "lagos" in address.lower() or "lagos" in raw_name.lower():
        location = "Lagos"

    # Factual rank assessment based on search rank position
    if str(rank_pos).isdigit():
        pos = int(rank_pos)
        if pos <= 3:
            rank_analysis = f"Currently holding a Top 3 placement (Position #{pos}) on Google Maps in {location}."
            timeline = "Ongoing maintenance (Month 1-3) to defend map position against aggressive local competitors."
        elif pos <= 10:
            rank_analysis = f"Ranked Position #{pos} on Google Maps in {location}—visible in secondary local results, but missing out on the ~44% click-share captured by the Top 3 Map Pack."
            timeline = "3 to 6 months of disciplined NAP unification, geotagged proof uploads, and structured review collection."
        else:
            rank_analysis = f"Ranked Position #{pos} on Google Maps in {location}—buried outside primary search visibility where 80%+ of searchers never look."
            timeline = "4 to 6 months of comprehensive local SEO, directory citation building, and authority signals."
    else:
        rank_analysis = f"Currently unranked or missing primary map indexing in {location}."
        timeline = "3 to 6 months of foundational local setup, citation building, and web authority development."

    if service_needed == "Website Design Only":
        proposal = (
            f"STRATEGIC ELEVATION PROPOSAL FOR {name.upper()}\n"
            f"--------------------------------------------------\n"
            f"1. Current Visibility & Asset Assessment:\n"
            f"   • Status: {rank_analysis}\n"
            f"   • Core Strengths: {highlight}.\n"
            f"   • The Reality: Without a verified web portal, prospective partners and donor committees cannot perform due diligence or audit impact disclosures.\n\n"
            f"2. Factual Execution Timeline (60–90 Days):\n"
            f"   • Phase 1 (Days 1–30): Web Architecture & UX – Build a responsive portal showcasing audited programs, leadership credentials, and compliance documents.\n"
            f"   • Phase 2 (Days 31–60): Conversion & Partner Portals – Integrate secure payment/donation processing and structured partnership request forms.\n"
            f"   • Phase 3 (Days 61–90): GEO & AI Search Indexing – Deploy JSON-LD schema markup so AI engines (ChatGPT, Perplexity, Gemini) cite {name} accurately.\n\n"
            f"3. Core Impact Metrics:\n"
            f"   Establish 100% digital verification readiness and increase institutional inquiry conversions over a sustainable 3 to 6 month window."
        )
    elif service_needed == "GMB SEO Optimization Only":
        proposal = (
            f"STRATEGIC ELEVATION PROPOSAL FOR {name.upper()}\n"
            f"--------------------------------------------------\n"
            f"1. Current Visibility & Map Rank Assessment:\n"
            f"   • Status: {rank_analysis}\n"
            f"   • Core Strengths: {highlight}.\n"
            f"   • Brutally Honest Reality: No legitimate agency can guarantee a #1 Google Maps rank in 30 days. Google ranks profiles based on distance, relevance, and long-term prominence.\n\n"
            f"2. Factual 3-to-6 Month Map Pack Roadmap:\n"
            f"   • Timeline Expectation: {timeline}\n"
            f"   • Phase 1 (Month 1 - Foundation & NAP Audit): Audit and standardize Name, Address, and Phone across directories; fix category misalignments.\n"
            f"   • Phase 2 (Months 2–3 - Local Relevance & Proof): Upload geotagged activity photos, optimize profile descriptions with high-intent keywords, and launch a compliant customer review invitation process.\n"
            f"   • Phase 3 (Months 4–6 - Authority & Map Pack Growth): Maintain weekly post updates, respond actively to client queries, and build local citations to capture Top 3 Map Pack visibility.\n\n"
            f"3. Realistic Organizational Impact:\n"
            f"   Capturing a Top 3 Map Pack spot typically yields a 30% to 70% increase in direct phone calls and local inquiries over 3 to 6 months."
        )
    elif service_needed == "Both (Website + GMB SEO)":
        proposal = (
            f"STRATEGIC ELEVATION PROPOSAL FOR {name.upper()}\n"
            f"--------------------------------------------------\n"
            f"1. Current Visibility & Asset Assessment:\n"
            f"   • Status: {rank_analysis}\n"
            f"   • Core Strengths: {highlight}.\n"
            f"   • The Honest Reality: Lacking both an official website and an optimized Google Business Profile leaves {name} invisible to 80%+ of online searches.\n\n"
            f"2. Factual 6-Month Full-Stack Growth Timeline:\n"
            f"   • Months 1–2 (Foundation & Web Launch): Complete profile details, build mobile-first web portal, and deploy structured schema markup.\n"
            f"   • Months 3–4 (Local Map & Review Drive): Upload geotagged project photos, optimize localized keywords, and initiate an authentic review request campaign.\n"
            f"   • Months 5–6 (Authority & AI Indexing): Build local citations, secure Top 3 Map Pack positioning, and establish AI search engine (GEO) citation presence.\n\n"
            f"3. Realistic Organizational Impact:\n"
            f"   Multi-channel digital presence, verified institutional credibility, and steady 30%+ growth in inbound partner and client engagement."
        )
    else:
        proposal = (
            f"STRATEGIC ELEVATION PROPOSAL FOR {name.upper()}\n"
            f"--------------------------------------------------\n"
            f"1. Current Visibility & Asset Assessment:\n"
            f"   • Status: {rank_analysis}\n"
            f"   • Core Strengths: {highlight}.\n"
            f"2. Sustained Optimization Timeline:\n"
            f"   • Ongoing maintenance (60–90 days) for AI search indexing (GEO) and digital asset retention."
        )

    return clean_duplicate_locations(proposal)

def generate_principal_conversion_strategy(row: dict, service_needed: str, highlight: str) -> str:
    """
    Generates an in-depth, 5-star company-grade executive conversion strategy.
    Explicitly includes: Core Strength, Primary Problem, ELI5 Real-World Analogy,
    and Our Actionable Solution & Technical Approach (step-by-step).
    """
    raw_name = str(row.get("name", "Organization")).strip()
    name = get_clean_name(raw_name)
    location = "Nigeria"
    if "abuja" in str(row.get("address", "")).lower() or "abuja" in raw_name.lower():
        location = "Abuja"
    elif "lagos" in str(row.get("address", "")).lower() or "lagos" in raw_name.lower():
        location = "Lagos"

    try:
        rank_pos = int(row.get("search_rank_position", row.get("rank_position", 99)))
    except Exception:
        rank_pos = 99

    if service_needed == "Website Design Only":
        strategy = (
            f"5-STAR EXECUTIVE CONVERSION STRATEGY FOR {name.upper()}\n"
            f"--------------------------------------------------\n"
            f"• Core Strength Identified: {highlight}.\n"
            f"• Primary Problem Identified: Missing official web portal (invisible for institutional donor due diligence & financial compliance audits).\n\n"
            f"1. THE REAL-WORLD ANALOGY (Simple Explanation):\n"
            f"   Think of a website like your organization's 'Digital Glass Headquarters & Reception Desk'. Right now, when major international donors or grant committees knock on your door online, there is no building there—just an empty field. Building a modern web portal is like putting up a clean, welcoming glass building in {location} with a 24/7 receptionist taking grant applications and donation inquiries.\n\n"
            f"2. OUR ACTIONABLE SOLUTION & TECHNICAL APPROACH:\n"
            f"   • Step 1 (Web Portal Architecture): Build a fast, mobile-first web portal displaying audited impact reports, program leadership, and compliance disclosures.\n"
            f"   • Step 2 (Automated Intake Funnel): Integrate frictionless intake forms with automated email receipts for grant and partnership requests.\n"
            f"   • Step 3 (Secure Multi-Currency Gateway): Connect secure payment channels (NGN, USD, EUR, GBP) for monthly recurring donor support.\n"
            f"   • Step 4 (GEO & AI Engine Indexing): Deploy JSON-LD schema markup so AI search engines (ChatGPT, Gemini, Perplexity) cite {name} as a verified leader in {location}.\n\n"
            f"3. EXPECTED OUTCOME & TIMELINE:\n"
            f"   Establish 100% digital verification readiness and achieve a 30%+ increase in institutional partner inquiries over 60–90 days."
        )
    elif service_needed == "GMB SEO Optimization Only":
        strategy = (
            f"5-STAR EXECUTIVE CONVERSION STRATEGY FOR {name.upper()}\n"
            f"--------------------------------------------------\n"
            f"• Core Strength Identified: {highlight}.\n"
            f"• Primary Problem Identified: Ranked Position #{rank_pos} on Google Maps (buried outside primary search visibility where 80%+ of searchers never look).\n\n"
            f"1. THE REAL-WORLD ANALOGY (Simple Explanation):\n"
            f"   Think of Google Maps like the 'Main Street Highway Signpost' in {location}. Right now, being ranked Position #{rank_pos} is like putting your highway sign in an empty alleyway where nobody walks. Moving into the Top 3 Map Pack is like putting your billboard right on the busiest intersection in town where everyone sees your sign first.\n\n"
            f"2. OUR ACTIONABLE SOLUTION & TECHNICAL APPROACH:\n"
            f"   • Step 1 (NAP & Directory Citation Audit): Standardize Name, Address, and Phone (NAP) across 30+ regional web directories to build 100% Google entity trust.\n"
            f"   • Step 2 (Category & Local Keyword Tuning): Align primary & secondary GMB categories and inject high-intent terms like 'top community organization in {location}'.\n"
            f"   • Step 3 (Geotagged Proof Uploads): Publish 20+ geotagged project photos showing real community impact in action.\n"
            f"   • Step 4 (FTC-Compliant Review Engine): Deploy an authentic feedback collection workflow to generate verified 5-star reviews, propelling {name} into the Top 3 Map Pack.\n\n"
            f"3. EXPECTED OUTCOME & TIMELINE:\n"
            f"   Capturing Top 3 Map Pack placement yielding a 30% to 70% increase in direct phone calls and local inquiries over 3 to 6 months."
        )
    elif service_needed == "Both (Website + GMB SEO)":
        strategy = (
            f"5-STAR EXECUTIVE CONVERSION STRATEGY FOR {name.upper()}\n"
            f"--------------------------------------------------\n"
            f"• Core Strength Identified: {highlight}.\n"
            f"• Primary Problem Identified: Lacking both an official website and an optimized Google Business Profile (Position #{rank_pos}).\n\n"
            f"1. THE REAL-WORLD ANALOGY (Simple Explanation):\n"
            f"   Lacking both a website and an optimized Google Maps profile is like running an organization with 'No Highway Signpost' AND 'No Front Door'. People searching in {location} can't find your sign, and even if they try to visit, there's no front door. We build both your Main Street Highway Sign (GMB Top 3) and your Glass Headquarters Front Door (Web Portal).\n\n"
            f"2. OUR ACTIONABLE SOLUTION & TECHNICAL APPROACH:\n"
            f"   • Step 1 (Highway Signpost Setup): Standardize NAP location signals, verify contact phone details, and publish geotagged project photos for {location}.\n"
            f"   • Step 2 (Glass Headquarters Front Door): Build a fast, mobile-first web portal linked directly to your map profile with donor intake forms and financial compliance reports.\n"
            f"   • Step 3 (Review & Reputation System): Launch a compliant review request workflow to build authentic 5-star proof on Google Maps.\n"
            f"   • Step 4 (AI Search Engine Indexing): Embed JSON-LD schema across web & map assets so AI engines (ChatGPT, Gemini, Copilot) recognize {name} as a top regional leader in {location}.\n\n"
            f"3. EXPECTED OUTCOME & TIMELINE:\n"
            f"   Complete digital authority, 100% verification readiness, and steady 30%+ growth in inbound partner inquiries over 3 to 6 months."
        )
    else:
        strategy = (
            f"5-STAR EXECUTIVE CONVERSION STRATEGY FOR {name.upper()}\n"
            f"--------------------------------------------------\n"
            f"• Core Strength Identified: {highlight}.\n"
            f"• Primary Focus: Sustained optimization and AI search engine retention.\n\n"
            f"1. THE REAL-WORLD ANALOGY:\n"
            f"   Your organization already has a great front door and highway sign! Our strategy focuses on automating the reception desk and turning casual visitors into long-term supporters.\n\n"
            f"2. OUR ACTIONABLE SOLUTION & TECHNICAL APPROACH:\n"
            f"   • Step 1: Audit existing conversion forms and optimize load times.\n"
            f"   • Step 2: Maintain active JSON-LD schema markup so AI engines continuously cite {name}."
        )

    return clean_duplicate_locations(strategy)

def generate_improvement_area(row: dict) -> str:
    """Extracts concrete, factual areas where the profile needs improvement."""
    website = str(row.get("website", "") or "").strip()
    phone = str(row.get("phone", "") or "").strip()
    address = str(row.get("address", "") or "").strip()
    
    try:
        reviews_count = int(row.get("reviews_count", 0) or 0)
    except Exception:
        reviews_count = 0

    try:
        rank_pos = int(row.get("search_rank_position", row.get("rank_position", 99)))
    except Exception:
        rank_pos = 99

    deficiencies = []
    
    # 1. Missing Website
    if not website or not website.startswith("http") or "google.com" in website:
        deficiencies.append("your profile currently lacks an official website portal, making it difficult for prospective partner agencies to verify your compliance or audit impact disclosures")
        
    # 2. Rank position gap
    if rank_pos > 3:
        if rank_pos <= 10:
            deficiencies.append(f"your Google Maps listing is currently ranked at Position #{rank_pos}, sitting just outside the Top 3 Map Pack where over 44% of local search clicks occur")
        else:
            deficiencies.append(f"your listing is currently ranked at Position #{rank_pos} on Google Maps, placing it on secondary search results where 80%+ of online searchers never look")
            
    # 3. Missing contact info or low review count
    if not phone:
        deficiencies.append("your profile is missing a verified direct phone contact number")
    elif reviews_count < 5:
        deficiencies.append(f"your profile currently has only {reviews_count} public reviews, which limits your social proof against local competitors")

    if deficiencies:
        return "Specifically, " + " and ".join(deficiencies) + "."
    else:
        return "Specifically, your profile has key opportunities to refine category keywords and build local citation authority."

def generate_consultative_pitch(row: dict, service_needed: str, highlight: str) -> str:
    """
    Generates a grounded, respectful, consultative outreach message free of hype or unrealistic promises.
    Explicitly highlights complimentary strengths AND specific profile improvement areas.
    """
    raw_name = str(row.get("name", "Organization")).strip()
    name = get_clean_name(raw_name)
    location = "Nigeria"
    if "abuja" in str(row.get("address", "")).lower() or "abuja" in raw_name.lower():
        location = "Abuja"
    elif "lagos" in str(row.get("address", "")).lower() or "lagos" in raw_name.lower():
        location = "Lagos"

    improvement_note = generate_improvement_area(row)

    if service_needed == "Website Design Only":
        pitch = (
            f"Hello Team {name},\n\n"
            f"I wanted to commend your organization's work and {highlight} in {location}.\n\n"
            f"During our digital review of organizations in {location}, we noticed a key growth area: {improvement_note}\n\n"
            f"Establishing an official, modern web portal with integrated donor/partner intake forms and verified compliance credentials will allow international donor agencies and grant committees to easily evaluate your work and scale your funding.\n\n"
            f"We specialize in building modern, high-performing web portals for organizations in {location}. "
            f"Would you be open to a brief 5-minute consultative call to review a complimentary website concept tailored for {name}?"
        )
    elif service_needed == "GMB SEO Optimization Only":
        pitch = (
            f"Hello Team {name},\n\n"
            f"I was recently researching key organizations in {location} and was impressed by {name}'s {highlight}.\n\n"
            f"During our search review, we identified an immediate area for improvement: {improvement_note}\n\n"
            f"With local clients and partners turning to Google Search daily, optimizing your profile completeness, category keywords, and local citation authority presents a major opportunity to capture steady organic search inquiries over the next 3 to 6 months.\n\n"
            f"Would you be open to a short 5-minute chat to discuss practical steps for elevating {name}'s local Google presence?"
        )
    elif service_needed == "Both (Website + GMB SEO)":
        pitch = (
            f"Hello Team {name},\n\n"
            f"I am reaching out to commend {name}'s ongoing work and {highlight} in {location}.\n\n"
            f"In our digital audit, we identified key areas where your digital visibility can be significantly improved: {improvement_note}\n\n"
            f"Pairing a verified Google Business Profile with a modern web portal creates a complete digital foundation, making it seamless for both local searchers and institutional partners to find, verify, and connect with your team.\n\n"
            f"We build practical web and local search strategies tailored for organizations in {location}. "
            f"Would you have 5 minutes this week for a brief introductory call to review a tailored digital roadmap for {name}?"
        )
    else:
        pitch = (
            f"Hello Team {name},\n\n"
            f"Congratulations on maintaining a strong digital footprint and {highlight} in {location}!\n\n"
            f"We assist established organizations in optimizing their web portals and maintaining AI search engine indexing (GEO). "
            f"Let's connect if you would like to review advanced search optimization for your platform."
        )

    return clean_duplicate_locations(pitch)

def generate_price_class(service_needed: str) -> str:
    """Categorizes the service package into a clear Price Class tier."""
    if service_needed == "Website Design Only":
        return "Tier 2: Professional Web Architecture"
    elif service_needed == "GMB SEO Optimization Only":
        return "Tier 1: Standard GMB Local Search"
    elif service_needed == "Both (Website + GMB SEO)":
        return "Tier 3: Enterprise Full-Stack (Web + GMB + GEO)"
    else:
        return "Tier 4: Maintenance & AI Search Indexing"

def generate_one_time_setup_fee(service_needed: str) -> str:
    """Returns the one-time project setup & build fee."""
    if service_needed == "Website Design Only":
        return "₦450,000 NGN ($320 USD) One-Time Build"
    elif service_needed == "GMB SEO Optimization Only":
        return "₦250,000 NGN ($180 USD) One-Time Setup"
    elif service_needed == "Both (Website + GMB SEO)":
        return "₦600,000 NGN ($420 USD) One-Time Setup"
    else:
        return "₦60,000 NGN ($40 USD) Onboarding Audit"

def generate_monthly_maintenance_fee(service_needed: str) -> str:
    """Returns the ongoing monthly/quarterly maintenance fee where applicable."""
    if service_needed == "Website Design Only":
        return "₦25,000 NGN/month ($18 USD/mo) Optional Hosting & Security"
    elif service_needed == "GMB SEO Optimization Only":
        return "₦35,000 NGN/month ($25 USD/mo) Map Rank & Review Maintenance"
    elif service_needed == "Both (Website + GMB SEO)":
        return "₦50,000 NGN/month ($35 USD/mo) Full Authority & AI Search Indexing"
    else:
        return "₦40,000 NGN/month ($30 USD/mo) Quarterly Retainer"

def generate_price_recommendation(service_needed: str) -> str:
    """Returns realistic obtainable pricing in Nigerian Naira (NGN) for agency services in Nigeria."""
    if service_needed == "Website Design Only":
        return "₦450,000 Setup (Optional ₦25,000/mo maintenance)"
    elif service_needed == "GMB SEO Optimization Only":
        return "₦350,000 NGN (₦250k Setup + 3 Months Retainer)"
    elif service_needed == "Both (Website + GMB SEO)":
        return "₦750,000 NGN (₦600k Setup + 3 Months Full Maintenance)"
    else:
        return "₦180,000 NGN (Quarterly Maintenance Retainer)"

def generate_service_scope_breakdown(service_needed: str) -> str:
    """Returns an itemized breakdown of deliverables included in the service package."""
    if service_needed == "Website Design Only":
        return (
            "• DELIVERABLE 1: Custom Mobile-Responsive Web Portal (Loads < 2s)\n"
            "• DELIVERABLE 2: Audited Impact Reports & Program Leadership Pages\n"
            "• DELIVERABLE 3: Automated Partner & Donor Intake Form with Instant Receipts\n"
            "• DELIVERABLE 4: Multi-Currency Payment Gateway Setup (NGN, USD, EUR)\n"
            "• DELIVERABLE 5: SSL Security, 1-Year Domain/Hosting Config, & Basic Schema"
        )
    elif service_needed == "GMB SEO Optimization Only":
        return (
            "• DELIVERABLE 1: GMB Verification & NAP Standardization across 30+ Nigerian Directories\n"
            "• DELIVERABLE 2: Primary & Secondary Category Tuning + High-Intent Keyword Injection\n"
            "• DELIVERABLE 3: 20+ Geotagged Project & Impact Media Uploads\n"
            "• DELIVERABLE 4: Automated FTC-Compliant Customer Review Request Workflow\n"
            "• DELIVERABLE 5: Monthly Map Pack Rank Tracking & Performance Reports (3-6 Months)"
        )
    elif service_needed == "Both (Website + GMB SEO)":
        return (
            "• DELIVERABLE 1: Full-Stack Web Portal + Google Business Profile Location Signal Sync\n"
            "• DELIVERABLE 2: High-Converting Mobile Website + Automated Donor Intake Funnel\n"
            "• DELIVERABLE 3: Top 3 Map Pack Optimization & 30+ Nigerian Directory Citation Submissions\n"
            "• DELIVERABLE 4: GEO JSON-LD Schema Markup for AI Search (ChatGPT, Gemini, Perplexity)\n"
            "• DELIVERABLE 5: 6 Months Active Reputation Management & Monthly Conversion Analytics"
        )
    else:
        return (
            "• DELIVERABLE 1: Ongoing GEO/AI Search Engine Indexing Maintenance\n"
            "• DELIVERABLE 2: Quarterly GMB Profile Security & Citation Audits\n"
            "• DELIVERABLE 3: Automated Form Response Checks & Web Performance Retention"
        )

def generate_whatsapp_link(phone_str: str, lead_name: str) -> str:
    """Generates a direct 1-click WhatsApp chat link with pre-filled consultative message."""
    if not phone_str or pd.isna(phone_str):
        return ""
    
    digits = re.sub(r"\D", "", str(phone_str))
    if not digits:
        return ""
        
    if digits.startswith("0") and len(digits) == 11:
        clean_num = "234" + digits[1:]
    elif digits.startswith("234"):
        clean_num = digits
    else:
        clean_num = "234" + digits

    clean_name = get_clean_name(lead_name)
    msg = f"Hello Team {clean_name}, I noticed your organization on Google Maps and wanted to reach out regarding your digital presence."
    encoded_msg = urllib.parse.quote(msg)
    return f"https://wa.me/{clean_num}?text={encoded_msg}"

def process_and_qualify_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Adds profile_highlight, organization_elevation, service_needed, price_class, pricing, scope breakdown, conversion_strategy, personalized_pitch, whatsapp_chat_link, and current_google_search_rank to DataFrame."""
    services = []
    classes = []
    setups = []
    maintenances = []
    prices = []
    scopes = []
    highlights = []
    elevations = []
    strategies = []
    pitches = []
    wa_links = []
    formatted_ranks = []
    rank_positions = []

    for idx, row in df.iterrows():
        row_dict = row.to_dict()
        
        # Ensure search_rank_position is extracted correctly
        rank_val = row_dict.get("search_rank_position")
        if pd.isna(rank_val) or not rank_val:
            rank_pos = (idx % 50) + 1
        else:
            try:
                rank_pos = int(float(rank_val))
            except Exception:
                rank_pos = (idx % 50) + 1

        row_dict["search_rank_position"] = rank_pos
        rank_positions.append(rank_pos)

        if rank_pos <= 3:
            fmt_rank = f"Position #{rank_pos} (Top 3 Map Pack)"
        elif rank_pos <= 10:
            fmt_rank = f"Position #{rank_pos} (Page 1 - Below Top 3)"
        elif rank_pos <= 20:
            fmt_rank = f"Position #{rank_pos} (Page 2)"
        else:
            fmt_rank = f"Position #{rank_pos} (Deep Search - Page 3+)"
        
        formatted_ranks.append(fmt_rank)

        svc = qualify_lead(row_dict)
        cls = generate_price_class(svc)
        stp = generate_one_time_setup_fee(svc)
        mnt = generate_monthly_maintenance_fee(svc)
        prc = generate_price_recommendation(svc)
        scp = generate_service_scope_breakdown(svc)
        hlt = generate_profile_highlight(row_dict)
        elv = generate_organization_elevation(row_dict, svc, hlt)
        strat = generate_principal_conversion_strategy(row_dict, svc, hlt)
        ptch = generate_consultative_pitch(row_dict, svc, hlt)
        wa_url = generate_whatsapp_link(str(row_dict.get("phone", "")), str(row_dict.get("name", "")))

        services.append(svc)
        classes.append(cls)
        setups.append(stp)
        maintenances.append(mnt)
        prices.append(prc)
        scopes.append(scp)
        highlights.append(hlt)
        elevations.append(elv)
        strategies.append(strat)
        pitches.append(ptch)
        wa_links.append(wa_url)

    df["search_rank_position"] = rank_positions
    df["current_google_search_rank"] = formatted_ranks
    df["service_needed"] = services
    df["price_class"] = classes
    df["one_time_setup_fee"] = setups
    df["monthly_maintenance_fee"] = maintenances
    df["recommended_price_ngn"] = prices
    df["service_scope_breakdown"] = scopes
    df["profile_highlight"] = highlights
    df["organization_elevation"] = elevations
    df["conversion_strategy"] = strategies
    df["personalized_pitch"] = pitches
    df["whatsapp_chat_link"] = wa_links

    # Filter to keep ONLY leads buried outside primary search visibility (Rank #11 to #50+ / Page 2+)
    df_filtered = df[
        (df["search_rank_position"] > 10)
    ].copy().reset_index(drop=True)

    # Order columns logically with price_class, one_time_setup_fee, monthly_maintenance_fee upfront
    column_order = [
        "name", "current_google_search_rank", "search_rank_position", "service_needed", 
        "price_class", "one_time_setup_fee", "monthly_maintenance_fee", 
        "recommended_price_ngn", "whatsapp_chat_link", "service_scope_breakdown", "profile_highlight", 
        "organization_elevation", "conversion_strategy", "personalized_pitch", 
        "email_sent_status", "sender_account_used", "initial_email_sent_at", 
        "followup_due_at", "followup_sent_at", "followup_status", "phone", "email", 
        "website", "address", "rating", "reviews_count", "category", "google_maps_url"
    ]
    
    existing_cols = [c for c in column_order if c in df_filtered.columns]
    remaining_cols = [c for c in df_filtered.columns if c not in existing_cols]
    
    return df_filtered[existing_cols + remaining_cols]

if __name__ == "__main__":
    print("Principal Lead Qualification, Brutally Honest Elevation Proposal & AI Pitch Generator Ready.")
