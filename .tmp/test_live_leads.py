import requests
import json

query = """[out:json][timeout:25];
area["name:en"="Nigeria"]->.searchArea;
(
  node["office"="ngo"](area.searchArea);
  node["amenity"="hospital"](area.searchArea);
  node["amenity"="school"](area.searchArea);
  node["office"="company"](area.searchArea);
);
out body 25;
"""

r = requests.post("https://overpass-api.de/api/interpreter", data={"data": query}, timeout=20)
print("Status:", r.status_code)
print("Response snippet:", r.text[:300])
for i, el in enumerate(elements[:10]):
    tags = el.get("tags", {})
    name = tags.get("name", "Unnamed")
    city = tags.get("addr:city") or tags.get("addr:state") or "Nigeria"
    category = tags.get("office") or tags.get("amenity") or "Organization"
    website = tags.get("website") or tags.get("contact:website") or ""
    phone = tags.get("phone") or tags.get("contact:phone") or ""
    print(f"  {i+1}. {name} ({category.title()}) | {city} | Phone: {phone} | Web: {website}")
