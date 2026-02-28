#!/bin/bash
# Church Community Tracker — Linux / macOS installer
# Run once: bash install.sh

set -e

echo ""
echo " Church Community Tracker — Installer"
echo " ======================================"
echo ""

# Find python3
if command -v python3 &>/dev/null; then
    PYTHON=python3
elif command -v python &>/dev/null; then
    PYTHON=python
else
    echo " ERROR: Python not found."
    echo " Install Python 3.8+ first:"
    echo "   Ubuntu/Debian : sudo apt install python3"
    echo "   macOS         : brew install python3"
    exit 1
fi

echo " Using: $PYTHON ($($PYTHON --version))"
echo ""

# Run the main installer script
$PYTHON "$(dirname "$0")/install.py"

echo ""
echo " To run the app:  bash run.sh"
echo "              or: $PYTHON main.py"
echo ""
