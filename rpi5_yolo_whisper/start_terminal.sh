#!/bin/bash
# Quick start script for terminal version (no GUI)
# Run with: ./start_terminal.sh

echo "=========================================="
echo "Voice-Activated Object Detection"
echo "Terminal Version (No GUI)"
echo "=========================================="
echo ""

# Navigate to directory
cd "$(dirname "$0")"

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if models exist
if [ ! -f "models/yolo11n.pt" ]; then
    echo "⚠️  Warning: YOLO model not found!"
    echo "Please run ./install_rpi5.sh first"
    exit 1
fi

# Run terminal application
echo "Starting application..."
echo ""
echo "Say 'IRIS' to activate, then give voice commands"
echo "Press Ctrl+C to exit"
echo ""
echo "=========================================="
echo ""

python main_rpi5.py
