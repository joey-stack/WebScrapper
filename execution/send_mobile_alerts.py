#!/usr/bin/env python3
"""
Layer 3: Execution Tool - Instant Mobile Push Alerts & Daily Briefing Engine
Dispatches real-time mobile notifications via:
1. Direct High-Priority Admin Email Push (rings your phone via Gmail app)
2. Free ntfy.sh Instant Mobile Push (zero account setup, instant notification banner & sound)
3. CallMeBot WhatsApp Gateway (when API key is present)
"""

import argparse
import datetime
import os
import re
import smtplib
import sys
import urllib.parse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
import requests
from dotenv import load_dotenv

load_dotenv()

# Ensure utf-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# User WhatsApp & Notification Configuration
DEFAULT_PHONE = os.getenv("MY_WHATSAPP_NUMBER", "2348183292909")
CALLMEBOT_API_KEY = os.getenv("CALLMEBOT_API_KEY", "")
ADMIN_EMAIL = os.getenv("SENDER_EMAIL", "joeladawah2@gmail.com")
NTFY_TOPIC = os.getenv("NTFY_TOPIC", "joel_adawah_leads_alert")

def format_clean_phone(raw_phone: str) -> str:
    """Formats phone number into international digits without leading '+' or dashes."""
    cleaned = re.sub(r"[^\d]", "", str(raw_phone or ""))
    if cleaned.startswith("0") and len(cleaned) == 11:
        cleaned = "234" + cleaned[1:]
    return cleaned

def send_ntfy_push(title: str, message: str, click_url: str = None, priority: str = "high") -> bool:
    """
    Sends an instant push notification to your phone via ntfy.sh.
    Zero account setup required - just subscribe to topic on phone.
    """
    try:
        topic = os.getenv("NTFY_TOPIC", NTFY_TOPIC).strip()
        clean_title = re.sub(r"[^\x00-\x7F]+", " ", title).strip()
        headers = {
            "Title": clean_title if clean_title else "CRM Notification",
            "Priority": priority,
            "Tags": "rotating_light,fire" if priority == "urgent" else "bar_chart,briefcase"
        }
        if click_url:
            headers["Click"] = click_url

        url = f"https://ntfy.sh/{topic}"
        res = requests.post(url, data=message.encode("utf-8"), headers=headers, timeout=10)
        if res.status_code == 200:
            print(f"[+] Instant ntfy mobile push sent to topic '{topic}'!")
            return True
    except Exception as e:
        print(f"[-] ntfy push notice: {e}")
    return False

def send_admin_email_alert(subject: str, body: str) -> bool:
    """
    Sends a high-priority push notification email directly to your Gmail account.
    Triggers your phone's native Gmail notification chime immediately.
    """
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    sender_email = os.getenv("SENDER_EMAIL", "joeladawah2@gmail.com")
    sender_password = os.getenv("SENDER_PASSWORD", "")

    if not sender_email or not sender_password:
        return False

    try:
        msg = MIMEMultipart()
        msg["From"] = f"🚨 CRM Autopilot <{sender_email}>"
        msg["To"] = ADMIN_EMAIL
        msg["Subject"] = f"🚨 {subject}"
        msg["X-Priority"] = "1"  # High Priority header
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP(smtp_server, 587, timeout=15)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print(f"[+] High-priority alert emailed to {ADMIN_EMAIL} (Gmail push triggered)!")
        return True
    except Exception as e:
        print(f"[-] Admin email alert error: {e}")
        return False

def send_whatsapp_alert(message_text: str, phone: str = None) -> bool:
    """
    Sends an instant WhatsApp message to the user's phone via CallMeBot.
    """
    target_phone = format_clean_phone(phone or DEFAULT_PHONE)
    api_key = os.getenv("CALLMEBOT_API_KEY", CALLMEBOT_API_KEY).strip()

    if not api_key:
        return False

    try:
        encoded_text = urllib.parse.quote(message_text)
        url = f"https://api.callmebot.com/whatsapp.php?phone={target_phone}&text={encoded_text}&apikey={api_key}"
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            print(f"[+] WhatsApp message successfully delivered to +{target_phone}!")
            return True
    except Exception:
        pass
    return False

def send_hot_lead_whatsapp_alert(
    lead_name: str,
    intent: str,
    snippet: str,
    target_email: str,
    wa_direct_link: str = None,
    sender_email: str = None
) -> bool:
    """Dispatches multi-channel hot lead notifications (ntfy push, Gmail high-priority alert, WhatsApp)."""
    now_str = datetime.datetime.now().strftime("%I:%M %p WAT")
    
    intent_emojis = {
        "MEETING_REQUEST": "📅 MEETING REQUEST",
        "PROPOSAL_REQUEST": "📄 PROPOSAL REQUEST",
        "PRICING_QUESTION": "💰 PRICING QUESTION",
        "HIGH_INTENT_CLOSE": "🔥 HOT CLOSE OPPORTUNITY",
        "GENERAL_INQUIRY": "💬 NEW INBOUND INQUIRY"
    }
    header_intent = intent_emojis.get(intent, f"🔔 {intent}")
    clean_snippet = re.sub(r"\s+", " ", snippet).strip()[:140]

    title = f"HOT LEAD: {lead_name} ({header_intent})"
    
    msg_lines = [
        f"🚨 HOT LEAD ALERT! ({now_str})",
        f"━━━━━━━━━━━━━━━━━━",
        f"🏢 Organization: {lead_name}",
        f"🎯 Intent: {header_intent}",
        f"✉️ Email: {target_email}",
        f"💬 Reply Snippet: \"{clean_snippet}...\"",
        f"━━━━━━━━━━━━━━━━━━",
        f"⚡ Autonomous Action Taken:",
        f"• Auto-replied & generated tailored deliverables.",
    ]

    if wa_direct_link and "wa.me" in wa_direct_link:
        msg_lines.append(f"\n📲 1-Click WhatsApp Direct Chat:\n{wa_direct_link}")

    full_message = "\n".join(msg_lines)

    print("\n==================================================")
    print(f"[*] DISPATCHING INSTANT MULTI-CHANNEL MOBILE ALERTS")
    print(f"[*] Lead: {lead_name} | Intent: {intent}")
    print("==================================================")

    # 1. Direct High-Priority Email Push (Rings Gmail app on phone)
    send_admin_email_alert(title, full_message)

    # 2. Instant ntfy.sh Push Notification
    send_ntfy_push(title, full_message, click_url=wa_direct_link, priority="urgent")

    # 3. WhatsApp Push (if CallMeBot is configured)
    send_whatsapp_alert(full_message)

    return True

def send_daily_summary_whatsapp_alert(stats: dict) -> bool:
    """Dispatches daily 5:00 PM pipeline briefing across all mobile channels."""
    today_str = datetime.datetime.now().strftime("%A, %b %d, %Y")
    
    scraped = stats.get("leads_scraped_today", 0)
    total_db = stats.get("total_leads_database", 0)
    sent_today = stats.get("emails_dispatched_today", 0)
    replies = stats.get("replies_received_today", 0)
    active_deals = stats.get("active_deals_count", 0)
    champion_angle = stats.get("champion_angle", "AUTHORITY_V1")

    title = f"Daily Acquisition Summary ({today_str})"
    msg = (
        f"📊 DAILY ACQUISITION SUMMARY ({today_str})\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🔍 New Leads Scraped: {scraped}\n"
        f"📁 Total Database Pool: {total_db}\n"
        f"🚀 Outreach Dispatched: {sent_today}\n"
        f"💬 Client Replies: {replies}\n"
        f"💼 Active Pipeline Deals: {active_deals}\n"
        f"🏆 Top Converting Angle: {champion_angle}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"✅ System Status: Active & Listening on IMAP"
    )

    print("\n==================================================")
    print(f"[*] DISPATCHING DAILY PIPELINE BRIEFING")
    print("==================================================")

    send_admin_email_alert(title, msg)
    send_ntfy_push(title, msg, priority="default")
    send_whatsapp_alert(msg)
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-Channel Mobile Alert Engine")
    parser.add_argument("--test", action="store_true", help="Send test hot lead alert")
    parser.add_argument("--daily", action="store_true", help="Send test daily summary")
    args = parser.parse_args()

    if args.daily:
        send_daily_summary_whatsapp_alert({
            "leads_scraped_today": 10,
            "total_leads_database": 22,
            "emails_dispatched_today": 5,
            "replies_received_today": 1,
            "active_deals_count": 1,
            "champion_angle": "AUTHORITY_V1"
        })
    else:
        send_hot_lead_whatsapp_alert(
            lead_name="African Health & Education Initiative",
            intent="MEETING_REQUEST",
            snippet="Hi Joel, let's hop on a call this Thursday at 2 PM to discuss your 1-page roadmap.",
            target_email="director@ahei-ng.org",
            wa_direct_link="https://wa.me/2348033527597?text=Hi%20Team%20AHEI"
        )
