#!/usr/bin/env python3
"""
Downloads MinGit using high-speed CDN mirror with range resuming and extracts to .bin/git.
"""

import os
import sys
import time
import zipfile
import requests
from pathlib import Path

MIRROR_URL = "https://npmmirror.com/mirrors/git-for-windows/v2.47.1.windows.1/MinGit-2.47.1-64-bit.zip"
TARGET_DIR = Path(__file__).parent.parent / ".bin" / "git"
ZIP_PATH = Path(__file__).parent / "mingit_fast.zip"

def download_fast_resumable():
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    git_exe = TARGET_DIR / "cmd" / "git.exe"

    if git_exe.exists():
        print(f"[+] MinGit already exists at {git_exe}")
        return str(git_exe)

    for attempt in range(1, 20):
        downloaded = ZIP_PATH.stat().st_size if ZIP_PATH.exists() else 0
        headers = {"User-Agent": "Mozilla/5.0"}
        if downloaded > 0:
            headers["Range"] = f"bytes={downloaded}-"
            print(f"[*] Resuming download from {downloaded // (1024*1024)}MB...")

        try:
            r = requests.get(MIRROR_URL, headers=headers, stream=True, allow_redirects=True, timeout=20)
            if r.status_code == 416:
                print("[+] File completely downloaded.")
                break
            if r.status_code not in (200, 206):
                raise ConnectionError(f"HTTP Status {r.status_code}")

            mode = "ab" if r.status_code == 206 else "wb"
            total = int(r.headers.get("content-length", 0)) + (downloaded if r.status_code == 206 else 0)

            with open(ZIP_PATH, mode) as f:
                for chunk in r.iter_content(chunk_size=1024 * 512):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total > 0:
                            pct = int((downloaded / total) * 100)
                            print(f"    Downloaded {downloaded // (1024*1024)}MB / {total // (1024*1024)}MB ({pct}%)...", end="\r", flush=True)

            print(f"\n[+] MinGit archive downloaded successfully ({ZIP_PATH.stat().st_size} bytes).")
            break
        except Exception as e:
            print(f"\n[-] Attempt {attempt} dropped ({e}), resuming in 2s...")
            time.sleep(2)

    print(f"[*] Extracting archive to {TARGET_DIR}...")
    with zipfile.ZipFile(ZIP_PATH, "r") as zf:
        zf.extractall(TARGET_DIR)

    print(f"[+] MinGit successfully installed and ready at: {git_exe}")
    return str(git_exe)

if __name__ == "__main__":
    download_fast_resumable()
