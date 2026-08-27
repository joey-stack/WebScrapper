#!/usr/bin/env python3
"""
Registers Windows Task Scheduler tasks for the Autonomous Lead Acquisition Engine.
"""

import os
import subprocess
import sys
from pathlib import Path

def register_windows_tasks():
    python_exe = sys.executable
    script_path = str(Path(__file__).parent / "run_continuous_autopilot.py").replace("/", "\\")
    cwd = str(Path(__file__).parent.parent).replace("/", "\\")

    tasks = [
        ("CRM_Autopilot_Morning_0830", "08:30"),
        ("CRM_Autopilot_Midday_1315", "13:15"),
        ("CRM_Autopilot_Evening_1645", "16:45")
    ]

    print("==================================================")
    print("[*] REGISTERING NATIVE WINDOWS TASK SCHEDULER JOBS")
    print(f"[*] Python Executable: {python_exe}")
    print(f"[*] Script Path:       {script_path}")
    print("==================================================")

    for task_name, start_time in tasks:
        # Construct cmd line
        cmd = f'schtasks /create /tn "{task_name}" /tr "\"{python_exe}\" \"{script_path}\" --once --limit 15" /sc daily /st {start_time} /f'
        print(f"\n[*] Creating Task: {task_name} at {start_time}...")
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if res.returncode == 0:
            print(f"    [+] Successfully registered {task_name} (Runs daily at {start_time} WAT)!")
        else:
            print(f"    [-] Output: {res.stdout.strip()} {res.stderr.strip()}")

    print("\n==================================================")
    print("[+] VERIFYING REGISTERED TASKS:")
    print("==================================================")
    for task_name, _ in tasks:
        query_cmd = f'schtasks /query /tn "{task_name}"'
        q_res = subprocess.run(query_cmd, shell=True, capture_output=True, text=True)
        if q_res.returncode == 0:
            lines = [l for l in q_res.stdout.splitlines() if task_name in l]
            for line in lines:
                print(f"  • {line.strip()}")

if __name__ == "__main__":
    register_windows_tasks()
