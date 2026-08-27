@echo off
REM ============================================================================
REM Windows Task Scheduler Setup for Autonomous Lead Acquisition Engine
REM Registers 3 daily scheduled runs at peak B2B decision-maker hours (WAT):
REM 1. Morning Outbound Batch:  08:30 AM
REM 2. Midday Follow-up Sweep:  01:15 PM
REM 3. End-of-Day Recap & Brief: 04:45 PM
REM ============================================================================

echo [*] Registering Windows Scheduled Tasks for Lead Acquisition Engine...

set PYTHON_EXE=python.exe
set SCRIPT_PATH=%~dp0run_continuous_autopilot.py

REM Task 1: 08:30 AM Morning Batch
schtasks /create /tn "CRM_Autopilot_Morning_0830" /tr "\"%PYTHON_EXE%\" \"%SCRIPT_PATH%\" --once --limit 15" /sc daily /st 08:30 /f

REM Task 2: 01:15 PM Midday Sweep
schtasks /create /tn "CRM_Autopilot_Midday_1315" /tr "\"%PYTHON_EXE%\" \"%SCRIPT_PATH%\" --once --limit 15" /sc daily /st 13:15 /f

REM Task 3: 04:45 PM End-of-Day Recap
schtasks /create /tn "CRM_Autopilot_Evening_1645" /tr "\"%PYTHON_EXE%\" \"%SCRIPT_PATH%\" --once --limit 15" /sc daily /st 16:45 /f

echo.
echo [+] SUCCESS! 3 Daily Scheduled Tasks Registered with Windows Task Scheduler:
echo     1. CRM_Autopilot_Morning_0830 (08:30 AM WAT)
echo     2. CRM_Autopilot_Midday_1315  (01:15 PM WAT)
echo     3. CRM_Autopilot_Evening_1645 (04:45 PM WAT)
echo.
pause
