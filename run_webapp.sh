#!/bin/bash
# Web App Startup Script

echo "🚀 Starting Ambiguity Detection Web App..."
echo ""
echo "Installing dependencies..."
pip install -q Flask Flask-CORS numpy

echo "✓ Dependencies installed"
echo ""
echo "Starting Flask server..."
echo ""
python app.py
