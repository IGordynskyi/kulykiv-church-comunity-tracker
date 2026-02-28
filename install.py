#!/usr/bin/env python3
"""
Cross-platform installer for Church Community Tracker.
Run this once before launching the app for the first time.

  Windows : double-click install.bat  (which calls this script)
  Linux   : bash install.sh           (which calls this script)
  macOS   : bash install.sh           (which calls this script)
  Any OS  : python3 install.py
"""

import sys
import os
import platform
import subprocess

APP_DIR = os.path.dirname(os.path.abspath(__file__))
REQUIRED_PYTHON = (3, 8)


def header(text: str):
    print(f"\n{'─' * 50}")
    print(f"  {text}")
    print(f"{'─' * 50}")


def ok(text: str):
    print(f"  [OK]  {text}")


def info(text: str):
    print(f"  [..] {text}")


def warn(text: str):
    print(f"  [!!] {text}")


def fail(text: str):
    print(f"  [XX] {text}")


# ── 1. Python version check ───────────────────────────────────────────────────

header("Step 1 — Checking Python version")
v = sys.version_info
if v >= REQUIRED_PYTHON:
    ok(f"Python {v.major}.{v.minor}.{v.micro} — OK")
else:
    fail(f"Python {v.major}.{v.minor} is too old. Python {REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]}+ is required.")
    sys.exit(1)


# ── 2. tkinter check ─────────────────────────────────────────────────────────

header("Step 2 — Checking tkinter (GUI library)")
try:
    import tkinter
    ok("tkinter is available")
except ModuleNotFoundError:
    fail("tkinter is NOT installed.")
    os_name = platform.system()
    if os_name == "Linux":
        warn("On Ubuntu/Debian, install it with:")
        warn("    sudo apt install python3-tk")
    elif os_name == "Darwin":
        warn("On macOS, reinstall Python from python.org (includes tkinter),")
        warn("or: brew install python-tk")
    else:
        warn("On Windows, reinstall Python from python.org")
        warn("and make sure 'tcl/tk and IDLE' is checked during install.")
    sys.exit(1)


# ── 3. Install pip packages ───────────────────────────────────────────────────

header("Step 3 — Installing required packages (openpyxl)")
info("Running: pip install openpyxl ...")
result = subprocess.run(
    [sys.executable, "-m", "pip", "install", "openpyxl"],
    capture_output=True, text=True
)
if result.returncode == 0:
    ok("openpyxl installed / already up to date")
else:
    fail("pip install failed. Output:")
    print(result.stderr)
    sys.exit(1)


# ── 4. Initialise database ────────────────────────────────────────────────────

header("Step 4 — Initialising database")
sys.path.insert(0, APP_DIR)
try:
    import database as db
    db.init_db()
    ok(f"Database ready: {db.DB_PATH}")
except Exception as e:
    fail(f"Database init failed: {e}")
    sys.exit(1)


# ── Done ──────────────────────────────────────────────────────────────────────

header("Installation complete!")
print()
print("  To start the application:")
os_name = platform.system()
if os_name == "Windows":
    print("    Double-click  run.bat")
    print("    — or —")
    print("    python main.py")
elif os_name == "Darwin":
    print("    bash run.sh")
    print("    — or —")
    print("    python3 main.py")
else:
    print("    bash run.sh")
    print("    — or —")
    print("    python3 main.py")
print()

# Create a run script for convenience
if os_name == "Windows":
    run_script = os.path.join(APP_DIR, "run.bat")
    if not os.path.exists(run_script):
        with open(run_script, "w") as f:
            f.write('@echo off\ncd /d "%~dp0"\npython main.py\n')
        ok("Created run.bat")
else:
    run_script = os.path.join(APP_DIR, "run.sh")
    if not os.path.exists(run_script):
        with open(run_script, "w") as f:
            f.write('#!/bin/bash\nSCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"\ncd "$SCRIPT_DIR"\npython3 main.py\n')
        os.chmod(run_script, 0o755)
        ok("Created run.sh")
