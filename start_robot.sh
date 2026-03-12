#!/bin/bash
# MAYA Robot Startup Script
# This script ensures the main controller runs with the virtual environment

echo "🤖 Starting MAYA Robot System..."
echo "=================================="

# Navigate to project directory
cd /home/pragyan/Robot

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Run: python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Verify Python environment
echo "🐍 Python: $(which python)"
echo "📦 pip: $(which pip)"

# Start the main controller
echo "🚀 Starting main controller..."
echo "=================================="
python main_controller.py
