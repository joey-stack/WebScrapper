import sys
import subprocess
from pathlib import Path
import requests
from bs4 import BeautifulSoup

WHEELS_DIR = Path(__file__).parent / "wheels"
WHEELS_DIR.mkdir(parents=True, exist_ok=True)

def download_file(url: str, dest_path: Path):
    if dest_path.exists() and dest_path.stat().st_size > 1000:
        print(f"[+] Already downloaded: {dest_path.name}")
        return
    print(f"[*] Downloading {dest_path.name}...")
    headers = {"User-Agent": "pip/25.0.1"}
    r = requests.get(url, stream=True, headers=headers, timeout=60)
    r.raise_for_status()
    with open(dest_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024 * 256):
            if chunk:
                f.write(chunk)
    print(f"[+] Finished: {dest_path.name}")

def find_wheel_link(pkg_name: str):
    simple_url = f"https://pypi.org/simple/{pkg_name}/"
    resp = requests.get(simple_url, headers={"User-Agent": "pip/25.0.1"}, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    links = soup.find_all("a")
    best_link = None
    for a in reversed(links):
        href = a.get("href")
        text = a.text
        if "cp312" in text and "win_amd64" in text and text.endswith(".whl"):
            return href.split("#")[0], text
        if "py3-none-any.whl" in text and not best_link:
            best_link = (href.split("#")[0], text)
        elif "py2.py3-none-any.whl" in text and not best_link:
            best_link = (href.split("#")[0], text)
    return best_link

packages = ["greenlet", "pyee", "playwright"]
downloaded = []
for p in packages:
    try:
        url, fn = find_wheel_link(p)
        dest = WHEELS_DIR / fn
        download_file(url, dest)
        downloaded.append(dest)
    except Exception as e:
        print(f"[-] Error: {e}")

for whl in downloaded:
    print(f"[*] Installing {whl.name}...")
    subprocess.run([sys.executable, "-m", "pip", "install", "--no-deps", str(whl)])

print("[+] Playwright install complete.")
