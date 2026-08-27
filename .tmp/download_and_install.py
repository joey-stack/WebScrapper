import os
import sys
import subprocess
from pathlib import Path
import requests

WHEELS_DIR = Path(__file__).parent / "wheels"
WHEELS_DIR.mkdir(parents=True, exist_ok=True)

def download_file(url: str, dest_path: Path):
    if dest_path.exists() and dest_path.stat().st_size > 1000:
        print(f"[+] Already downloaded: {dest_path.name} ({dest_path.stat().st_size} bytes)")
        return
    print(f"[*] Downloading {url} -> {dest_path.name}...")
    headers = {"User-Agent": "pip/25.0.1"}
    r = requests.get(url, stream=True, headers=headers, timeout=30)
    r.raise_for_status()
    total_downloaded = 0
    with open(dest_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024 * 512):
            if chunk:
                f.write(chunk)
                total_downloaded += len(chunk)
                print(f"    Downloaded {total_downloaded // 1024} KB...", end="\r", flush=True)
    print(f"\n[+] Finished: {dest_path.name} ({dest_path.stat().st_size} bytes)")

def get_pypi_wheel_url(pkg_name: str, version_filter: str = None) -> tuple:
    api_url = f"https://pypi.org/pypi/{pkg_name}/json"
    res = requests.get(api_url, timeout=15).json()
    urls = res["urls"]
    # Look for cp312 win_amd64 wheel or py3-none-any wheel
    best_url = None
    best_filename = None
    for u in urls:
        fn = u["filename"]
        if "cp312" in fn and "win_amd64" in fn and fn.endswith(".whl"):
            return u["url"], fn
        elif "py3-none-any" in fn and fn.endswith(".whl") and not best_url:
            best_url = u["url"]
            best_filename = fn
        elif "py2.py3-none-any" in fn and fn.endswith(".whl"):
            best_url = u["url"]
            best_filename = fn
    if best_url:
        return best_url, best_filename
    raise Exception(f"No suitable wheel found for {pkg_name}")

def main():
    packages = [
        "numpy",
        "pandas",
        "gspread",
        "google-auth",
        "google-auth-oauthlib",
        "google-api-python-client",
        "reportlab",
        "lxml"
    ]
    
    wheel_paths = []
    for pkg in packages:
        try:
            url, filename = get_pypi_wheel_url(pkg)
            dest = WHEELS_DIR / filename
            download_file(url, dest)
            wheel_paths.append(dest)
        except Exception as e:
            print(f"[-] Error fetching {pkg}: {e}")

    print("\n[*] Installing downloaded wheels...")
    for whl in wheel_paths:
        print(f"[*] Installing {whl.name}...")
        res = subprocess.run([sys.executable, "-m", "pip", "install", "--no-deps", str(whl)], capture_output=True, text=True)
        print(res.stdout)
        if res.returncode != 0:
            print(f"[-] Error: {res.stderr}")

if __name__ == "__main__":
    main()
