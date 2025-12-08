#!/bin/bash
# Quick deployment script for Raspberry Pi 5
# Run this after cloning the repository

set -e  # Exit on error

echo "🚀 IRIS Offline Module - Quick Deployment"
echo "=========================================="
echo ""

# Check if running on Raspberry Pi
if [[ $(uname -m) != "aarch64" ]] && [[ $(uname -m) != "armv7l" ]]; then
    echo "⚠️  Warning: This script is designed for Raspberry Pi"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "📦 Step 1: Installing system dependencies..."
./install_rpi5.sh

echo ""
echo "🔧 Step 2: Installing NCNN for optimized YOLO..."
./install_ncnn.sh

echo ""
echo "🤖 Step 3: Setting up models..."
source venv/bin/activate

# Download YOLO model if not exists
if [ ! -f "models/yolo11n.pt" ]; then
    echo "Downloading YOLO11n model..."
    python -c "
from ultralytics import YOLO
import os
os.makedirs('models', exist_ok=True)
model = YOLO('yolo11n.pt')
import shutil
shutil.move('yolo11n.pt', 'models/yolo11n.pt')
print('✅ YOLO model downloaded')
"
fi

# Convert to NCNN
if [ -f "models/yolo11n.pt" ]; then
    echo "Converting YOLO to NCNN format..."
    python convert_yolo_ncnn.py models/yolo11n.pt || echo "⚠️  NCNN conversion failed (optional)"
fi

echo ""
echo "🧪 Step 4: Running performance tests..."
python benchmark_yolo.py --runs 10 || echo "⚠️  Benchmark failed (optional)"

echo ""
echo "✅ Deployment Complete!"
echo ""
echo "📋 Next Steps:"
echo "  1. Edit .env to configure settings"
echo "  2. Run: python gui_mobile_detector.py"
echo "  3. Say 'IRIS' to activate voice commands"
echo ""
echo "📖 Documentation:"
echo "  - NCNN_OPTIMIZATION_README.md (YOLO speed)"
echo "  - WHISPER_OPTIMIZATION_README.md (Speech speed)"
echo "  - GIT_DEPLOYMENT_GUIDE.md (This guide)"
echo ""
echo "🎉 Enjoy your optimized IRIS system!"
