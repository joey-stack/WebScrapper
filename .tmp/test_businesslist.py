import requests
from bs4 import BeautifulSoup
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

url = "https://www.businesslist.com.ng/category/non-governmental-organisations/abuja"
try:
    resp = requests.get(url, headers=headers, timeout=12)
    print("Status:", resp.status_code)
    soup = BeautifulSoup(resp.text, "html.parser")
    listings = soup.find_all("div", class_=re.compile(r"company|listing|item|record", re.IGNORECASE))
    print("Found listing elements:", len(listings))
    for item in listings[:5]:
        h4 = item.find(["h4", "h3", "h2", "a"])
        if h4:
            print("Name:", h4.text.strip())
except Exception as e:
    print("Error:", e)
