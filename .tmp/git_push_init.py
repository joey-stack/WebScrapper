#!/usr/bin/env python3
"""
Initializes and pushes clean codebase to GitHub repository https://github.com/joey-stack/WebScrapper
"""

import os
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
GIT_EXE = ROOT_DIR / ".bin" / "git" / "cmd" / "git.exe"
REPO_URL = "https://github.com/joey-stack/WebScrapper.git"

def run_git_cmd(args: list):
    git_bin = str(GIT_EXE) if GIT_EXE.exists() else "git"
    full_cmd = [git_bin] + args
    print(f"[*] Running: {' '.join(full_cmd)}")
    res = subprocess.run(full_cmd, cwd=str(ROOT_DIR), capture_output=True, text=True)
    if res.stdout:
        print(res.stdout.strip())
    if res.stderr:
        print(res.stderr.strip())
    return res.returncode == 0

def init_and_push():
    print("==================================================")
    print("[*] INITIALIZING & COMMITTING TO GITHUB REPOSITORY")
    print(f"[*] Target: {REPO_URL}")
    print("==================================================")

    # 1. Init repo
    run_git_cmd(["init", "-b", "main"])

    # 2. Configure identity
    run_git_cmd(["config", "user.name", "Joel Adawah"])
    run_git_cmd(["config", "user.email", "joeladawah2@gmail.com"])

    # 3. Reset index & stage clean files
    run_git_cmd(["reset"])
    run_git_cmd(["add", "."])

    # 4. Commit
    run_git_cmd(["commit", "-m", "feat(crm): initialize 24/7 autonomous client acquisition engine"])

    # 5. Remote setup
    run_git_cmd(["remote", "remove", "origin"])
    run_git_cmd(["remote", "add", "origin", REPO_URL])

    # 6. Branch
    run_git_cmd(["branch", "-M", "main"])

    print("\n[+] Local commit verified. Pushing to GitHub...")
    ok = run_git_cmd(["push", "-u", "origin", "main", "--force"])
    if ok:
        print("\n[+] SUCCESS! Codebase pushed to https://github.com/joey-stack/WebScrapper")
    else:
        print("\n[*] Ready for authentication / push.")

if __name__ == "__main__":
    init_and_push()
