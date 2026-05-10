#!/bin/bash
# Startup script für Render - installiert Playwright Browser, dann startet Flask

echo "Installing Playwright browsers..."
python -m playwright install chromium

echo "Starting Flask app..."
python app.py
