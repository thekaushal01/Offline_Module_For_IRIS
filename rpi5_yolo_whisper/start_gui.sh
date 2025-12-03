#!/bin/bash
# Quick start script for GUI application
# Run with: ./start_gui.sh

echo "=========================================="
echo "Voice-Activated Object Detection GUI"
echo "=========================================="
echo ""

# Set display for VNC
export DISPLAY=:1

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

# Run GUI application
echo "Starting GUI application..."
echo ""
echo "Controls:"
echo "  - Say 'IRIS' to activate voice commands"
echo "  - Press 'Q' to quit"
echo "  - Press 'D' to detect objects manually"
echo "  - Press 'S' to save screenshot"
echo ""
echo "=========================================="
echo ""

python main_gui.py
