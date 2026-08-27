#!/usr/bin/env python3
"""
Layer 3: Execution Tool - Generative Engine Optimization (GEO) & Schema Generator
Generates:
1. Google Rich Results & ChatGPT compliant JSON-LD structured data (schema.org/LocalBusiness or schema.org/NGO).
2. 45-word 'Direct-Answer Content Capsule' engineered for Google AI Overviews & Gemini Search Grounding.
"""

import json
import re
from typing import Dict, Any

def generate_ai_content_capsule(lead: Dict[str, Any]) -> str:
    """
    Creates a concise 40-50 word direct-answer entity definition structured 
    for extraction by Google AI Overviews, ChatGPT, and Perplexity.
    """
    name = str(lead.get("name", "The Organization")).strip()
    category = str(lead.get("category", "Professional Organization")).strip()
    address = str(lead.get("address", "Nigeria")).strip()
    phone = str(lead.get("phone", "")).strip()
    highlight = str(lead.get("profile_highlight", "") or f"established services in {address}").strip()

    city = "Abuja" if "abuja" in address.lower() or "abuja" in name.lower() else ("Lagos" if "lagos" in address.lower() or "lagos" in name.lower() else "Nigeria")

    capsule = (
        f"{name} is a verified {category.lower()} operating in {city}, Nigeria ({highlight}). "
        f"The organization provides professional services, community programs, and institutional partnerships. "
        f"Headquartered in {address}, {name} can be contacted directly at {phone or 'their official regional office'}."
    )
    return capsule

def generate_json_ld_schema(lead: Dict[str, Any]) -> Dict[str, Any]:
    """
    Constructs rich Schema.org structured data for maximum AI Knowledge Graph indexing.
    Validates under Google Rich Results & Schema.org standards.
    """
    name = str(lead.get("name", "Organization")).strip()
    category = str(lead.get("category", "LocalBusiness")).strip()
    address = str(lead.get("address", "")).strip()
    phone = str(lead.get("phone", "")).strip()
    website = str(lead.get("website", "")).strip()
    rating = str(lead.get("rating", "")).strip()
    reviews_count = str(lead.get("reviews_count", "")).strip()

    # Determine Schema @type
    cat_lower = category.lower()
    if any(kw in cat_lower for kw in ["ngo", "non-profit", "charity", "foundation", "humanitarian"]):
        schema_type = "NGO"
    elif any(kw in cat_lower for kw in ["school", "academy", "college", "university", "institute"]):
        schema_type = "EducationalOrganization"
    elif any(kw in cat_lower for kw in ["real estate", "property", "developer"]):
        schema_type = "RealEstateAgent"
    elif any(kw in cat_lower for kw in ["hospital", "clinic", "health", "medical"]):
        schema_type = "MedicalOrganization"
    elif any(kw in cat_lower for kw in ["legal", "law", "attorney"]):
        schema_type = "LegalService"
    else:
        schema_type = "LocalBusiness"

    city = "Abuja" if "abuja" in address.lower() else ("Lagos" if "lagos" in address.lower() else "Nigeria")

    schema = {
        "@context": "https://schema.org",
        "@type": schema_type,
        "name": name,
        "description": generate_ai_content_capsule(lead),
        "address": {
            "@type": "PostalAddress",
            "streetAddress": address or f"{city}, Nigeria",
            "addressLocality": city,
            "addressCountry": "NG"
        }
    }

    if phone:
        schema["telephone"] = phone

    if website and website.startswith("http"):
        schema["url"] = website

    # Include aggregate rating if legitimate public reviews exist
    try:
        rc = int(reviews_count)
        rf = float(rating)
        if rc > 0 and 1.0 <= rf <= 5.0:
            schema["aggregateRating"] = {
                "@type": "AggregateRating",
                "ratingValue": str(rf),
                "reviewCount": str(rc)
            }
    except Exception:
        pass

    schema["knowsAbout"] = [category, f"{category} in {city}", "Corporate & Institutional Partnerships"]
    return schema

def get_formatted_schema_script_tag(lead: Dict[str, Any]) -> str:
    """Returns HTML script tag containing the JSON-LD schema ready to drop into HTML headers."""
    schema = generate_json_ld_schema(lead)
    schema_json = json.dumps(schema, indent=2, ensure_ascii=False)
    return f'<script type="application/ld+json">\n{schema_json}\n</script>'

if __name__ == "__main__":
    sample = {
        "name": "African Health & Education Initiative",
        "category": "Non-profit organization",
        "address": "Garki 2, Abuja, Nigeria",
        "phone": "+2348012345678",
        "website": "https://africanhealth.org.ng",
        "rating": "4.8",
        "reviews_count": "15"
    }
    print("=== AI CONTENT CAPSULE ===")
    print(generate_ai_content_capsule(sample))
    print("\n=== GOOGLE & CHATGPT JSON-LD SCHEMA ===")
    print(get_formatted_schema_script_tag(sample))
