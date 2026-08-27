import os
import sys
import subprocess
from pathlib import Path
import requests
import bs4

WHEELS_DIR = Path(__file__).parent / "wheels"
WHEELS_DIR.mkdir(parents=True, exist_ok=True)

def download_with_resume(url: str, dest_path: Path):
    temp_file = dest_path.with_suffix(".tmp_dl")
    initial_bytes = 0
    if temp_file.exists():
        initial_bytes = temp_file.stat().st_size

    headers = {"User-Agent": "pip/25.0.1"}
    r_head = requests.head(url, headers=headers, timeout=15)
    total_size = int(r_head.headers.get("content-length", 0))

    if dest_path.exists() and dest_path.stat().st_size == total_size:
        print(f"[+] Already downloaded completely: {dest_path.name} ({total_size} bytes)")
        return

    print(f"[*] Downloading {dest_path.name} (Total: {total_size} bytes, Resuming from {initial_bytes} bytes)...")

    max_attempts = 15
    for attempt in range(1, max_attempts + 1):
        try:
            cur_bytes = temp_file.stat().st_size if temp_file.exists() else 0
            if total_size and cur_bytes >= total_size:
                break
            req_headers = {"User-Agent": "pip/25.0.1"}
            if cur_bytes > 0:
                req_headers["Range"] = f"bytes={cur_bytes}-"
            
            with requests.get(url, headers=req_headers, stream=True, timeout=20) as r:
                r.raise_for_status()
                with open(temp_file, "ab" if cur_bytes > 0 else "wb") as f:
                    for chunk in r.iter_content(chunk_size=1024 * 256):
                        if chunk:
                            f.write(chunk)
                            cur_bytes += len(chunk)
                            if cur_bytes % (1024 * 1024 * 2) < (1024 * 256):
                                print(f"    Downloaded {cur_bytes // (1024*1024)} MB / {total_size // (1024*1024)} MB...")
            if total_size and temp_file.stat().st_size >= total_size:
                break
        except Exception as e:
            print(f"[-] Attempt {attempt} failed ({e}), resuming in 2s...")

    if temp_file.exists():
        if dest_path.exists():
            dest_path.unlink()
        temp_file.rename(dest_path)
        print(f"[+] Download complete: {dest_path.name} ({dest_path.stat().st_size} bytes)")

def get_playwright_whl_link():
    soup = bs4.BeautifulSoup(requests.get('https://pypi.org/simple/playwright/').text, 'html.parser')
    link = [a for a in soup.find_all('a') if 'win_amd64.whl' in a.text][-1]
    url = link['href'].split('#')[0]
    fn = link.text
    return url, fn

url, fn = get_playwright_whl_link()
dest = WHEELS_DIR / fn
download_with_resume(url, dest)

print(f"[*] Installing {fn}...")
subprocess.run([sys.executable, "-m", "pip", "install", "--no-deps", str(dest)], check=True)
print("[+] Playwright installed successfully.")

print("[*] Installing Chromium browser for Playwright...")
subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
print("[+] Playwright Chromium browser installed.")
