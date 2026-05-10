#!/bin/bash
# Startup script für Render - installiert Playwright Browser, dann startet Flask

# Geh zum Script-Verzeichnis (backend/)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "Working directory: $(pwd)"
echo "Installing Playwright browsers..."
python -m playwright install chromium

echo "Starting Flask app..."
python app.py
