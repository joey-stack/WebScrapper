#!/usr/bin/env python3
"""
Layer 3: Execution Tool - Branded 1-Page PDF Client Proposal Generator
Generates clean, executive 1-page PDF proposals containing:
- Agency Header & Client Name
- Selected Price Class Tier & Package Fees (Setup + Retainer)
- 5-Star ELI5 Conversion Strategy & Problem Statement
- Itemized Deliverables Scope (1-5)
- Payment Terms & 50% Deposit Schedule
"""

import argparse
import datetime
import os
import re
import sys
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

TMP_CSV = Path(__file__).parent.parent / ".tmp" / "gmb_leads_combined.csv"
OUTPUT_DIR = Path(__file__).parent.parent / ".tmp" / "proposals"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def clean_currency_str(val: str) -> str:
    """Replaces unicode Naira symbol with clean NGN label for standard Helvetica PDF fonts."""
    if not val:
        return ""
    val = str(val).replace("₦", "NGN ")
    val = re.sub(r"\s+", " ", val).strip()
    return val

def generate_pdf_proposal_for_lead(lead_name: str, csv_path: Path = TMP_CSV) -> Path:
    if not csv_path.exists():
        print(f"[-] Error: Leads CSV not found at {csv_path}")
        return None

    df = pd.read_csv(csv_path)

    # Find matching lead
    matched = df[df["name"].astype(str).str.lower().str.contains(lead_name.lower())]
    if matched.empty:
        print(f"[-] Error: No lead matching '{lead_name}' found in dataset.")
        return None

    row = matched.iloc[0]
    org_name = str(row.get("name", "Organization"))
    service_needed = str(row.get("service_needed", "Website & Local Search Optimization"))
    price_class = str(row.get("price_class", "Tier 3: Enterprise Full-Stack"))
    setup_fee = clean_currency_str(str(row.get("one_time_setup_fee", "NGN 450,000")))
    monthly_fee = clean_currency_str(str(row.get("monthly_maintenance_fee", "NGN 35,000/mo")))
    package_summary = clean_currency_str(str(row.get("recommended_price_ngn", "NGN 450,000")))
    scope = clean_currency_str(str(row.get("service_scope_breakdown", "")))
    strategy = clean_currency_str(str(row.get("conversion_strategy", "")))

    sanitized_filename = re.sub(r"[^\w]+", "_", org_name.lower()).strip("_") + "_proposal.pdf"
    output_pdf_path = OUTPUT_DIR / sanitized_filename

    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
    except ImportError:
        print("[!] reportlab package not installed. Installing reportlab...")
        os.system("pip install reportlab")
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors

    doc = SimpleDocTemplate(
        str(output_pdf_path),
        pagesize=letter,
        rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        "SubTitleStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        textColor=colors.HexColor("#475569"),
        spaceAfter=12
    )

    h2_style = ParagraphStyle(
        "H2Style",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=8,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        "BodyStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#334155")
    )

    elements = []

    # Header Banner
    today_str = datetime.datetime.now().strftime("%B %d, %Y")
    elements.append(Paragraph("DIGITAL ELEVATION & GROWTH PROPOSAL", title_style))
    elements.append(Paragraph(f"Prepared for: <b>{org_name}</b> | Date: {today_str} | Prepared by: <b>Joel Adawah & Team</b>", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563eb"), spaceAfter=10))

    # Executive Overview Box
    elements.append(Paragraph("1. Executive Summary & Recommended Tier", h2_style))
    summary_text = (
        f"<b>Selected Package:</b> {price_class}<br/>"
        f"<b>Service Focus:</b> {service_needed}<br/>"
        f"<b>One-Time Investment (Setup):</b> {setup_fee}<br/>"
        f"<b>Ongoing Retainer (Maintenance):</b> {monthly_fee}"
    )
    elements.append(Paragraph(summary_text, body_style))
    elements.append(Spacer(1, 8))

    # Strategy & Analogy Section
    elements.append(Paragraph("2. Executive Conversion Strategy & Roadmap", h2_style))
    
    raw_strat = strategy.replace("★", " Stars").replace("•", "").strip()
    raw_strat = re.sub(r"^5-STAR EXECUTIVE CONVERSION STRATEGY FOR.*?\n?", "", raw_strat, flags=re.IGNORECASE)
    raw_strat = re.sub(r"5-STAR EXECUTIVE CONVERSION STRATEGY FOR [^\n•]+", "", raw_strat, flags=re.IGNORECASE)
    raw_strat = re.sub(r"-{5,}", "", raw_strat)

    # Insert linebreaks before numbered sections and steps
    formatted_strat = raw_strat
    for marker in [
        "1. THE REAL-WORLD ANALOGY", "2. OUR ACTIONABLE SOLUTION & TECHNICAL APPROACH",
        "3. EXPECTED OUTCOME & TIMELINE", "Step 1", "Step 2", "Step 3", "Step 4"
    ]:
        formatted_strat = formatted_strat.replace(marker, f"\n{marker}")

    strat_lines = [l.strip() for l in formatted_strat.split("\n") if l.strip()]
    for line in strat_lines:
        # Strip organization name prefix if present at start of line
        line = re.sub(rf"^{re.escape(org_name)}\s*", "", line, flags=re.IGNORECASE).strip()

        if "Core Strength Identified:" in line or line.startswith("Core Strength:"):
            content = line.split(":", 1)[-1].strip()
            elements.append(Paragraph(f"• <b>Core Strength:</b> {content}", body_style))
            elements.append(Spacer(1, 2))
        elif "Primary Problem Identified:" in line or "Identified Growth Gap:" in line:
            content = line.split(":", 1)[-1].strip()
            elements.append(Paragraph(f"• <b>Identified Growth Gap:</b> {content}", body_style))
            elements.append(Spacer(1, 4))
        elif re.match(r"^\d+\.\s+", line) or line.startswith("Step "):
            if ":" in line:
                label_part, body_part = line.split(":", 1)
                formatted_para = f"<b>{label_part.strip()}:</b> {body_part.strip()}"
            else:
                formatted_para = f"<b>{line}</b>"

            if line.startswith("Step "):
                elements.append(Paragraph(f"• {formatted_para}", ParagraphStyle("StepBullet", parent=body_style, leftIndent=10, spaceAfter=3)))
            else:
                elements.append(Paragraph(formatted_para, ParagraphStyle("SubH", parent=body_style, spaceBefore=4, spaceAfter=3)))
        else:
            elements.append(Paragraph(line, body_style))
            elements.append(Spacer(1, 3))
            
    elements.append(Spacer(1, 6))

    # Itemized Scope Table
    elements.append(Paragraph("3. Itemized Scope of Deliverables", h2_style))
    
    bullet_style = ParagraphStyle(
        "BulletStyle",
        parent=body_style,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=4
    )

    clean_scope = scope.replace("•", "").strip()
    
    # Split by DELIVERABLE if flattened
    for d_num in range(1, 6):
        clean_scope = clean_scope.replace(f"DELIVERABLE {d_num}:", f"\nDELIVERABLE {d_num}:")

    scope_items = [item.strip() for item in clean_scope.split("\n") if item.strip()]

    for item in scope_items:
        if "DELIVERABLE" in item:
            parts = item.split(":", 1)
            if len(parts) == 2:
                formatted_item = f"<b>{parts[0].strip()}:</b> {parts[1].strip()}"
            else:
                formatted_item = f"<b>{item}</b>"
        else:
            formatted_item = item

        elements.append(Paragraph(f"• {formatted_item}", bullet_style))

    elements.append(Spacer(1, 8))

    # Investment & Terms Table
    elements.append(Paragraph("4. Investment Summary & Payment Terms", h2_style))
    
    th_style = ParagraphStyle(
        "THStyle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        textColor=colors.whitesmoke
    )
    td_style = ParagraphStyle(
        "TDStyle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#1e293b")
    )

    table_raw = [
        ["Fee Description", "Amount (NGN & USD)", "Payment Milestone"],
        ["Initial Onboarding & Build Setup", setup_fee, "50% Upon Acceptance"],
        ["Final Sign-Off & Launch Handover", package_summary, "50% Prior to Final Deployment"],
        ["Monthly Maintenance & Map Retainer", monthly_fee, "Monthly Starting Month 2"]
    ]

    table_data = []
    for r_idx, row_cells in enumerate(table_raw):
        row_para = []
        for cell in row_cells:
            st = th_style if r_idx == 0 else td_style
            row_para.append(Paragraph(str(cell), st))
        table_data.append(row_para)

    t = Table(table_data, colWidths=[150, 230, 160])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 12))

    # Acceptance Signature Line
    elements.append(Paragraph("<b>Acceptance & Authorization:</b> Sign below to accept this proposal and initiate Phase 1 Onboarding.", body_style))
    elements.append(Spacer(1, 15))
    sig_data = [["Authorized Signature: _______________________", "Date: ___________________"]]
    sig_table = Table(sig_data, colWidths=[350, 190])
    sig_table.setStyle(TableStyle([('FONTSIZE', (0, 0), (-1, -1), 9)]))
    elements.append(sig_table)

    doc.build(elements)
    print(f"\n[+] SUCCESS! Branded 1-Page PDF Proposal Generated:")
    print(f"    Path: {output_pdf_path}")
    return output_pdf_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PDF Client Proposal Generator")
    parser.add_argument("--lead-name", type=str, required=True, help="Organization Name (e.g. 'Project 1000')")
    args = parser.parse_args()

    generate_pdf_proposal_for_lead(lead_name=args.lead_name)
