#!/bin/bash
# Git deployment commands for Raspberry Pi
# Run these commands on your Raspberry Pi 5

echo "🚀 IRIS Deployment on Raspberry Pi 5"
echo "======================================"
echo ""

# 1. Clone repository
echo "📦 Step 1: Cloning repository..."
cd ~
git clone https://github.com/thekaushal01/Offline_Module_For_IRIS.git
cd Offline_Module_For_IRIS/rpi5_yolo_whisper

# 2. Make scripts executable
echo ""
echo "🔧 Step 2: Setting up permissions..."
chmod +x install_rpi5.sh install_ncnn.sh quick_deploy.sh

# 3. Run quick deployment
echo ""
echo "⚡ Step 3: Running automated deployment..."
echo "This will take 20-30 minutes..."
echo ""
./quick_deploy.sh

echo ""
echo "✅ Deployment Complete!"
echo ""
echo "🎯 To run the application:"
echo "  cd ~/Offline_Module_For_IRIS/rpi5_yolo_whisper"
echo "  source venv/bin/activate"
echo "  python gui_mobile_detector.py"
echo ""
echo "🎤 Voice Commands:"
echo "  - Say 'IRIS' to activate"
echo "  - Say 'detect objects' or 'what do you see'"
echo ""
echo "📊 Expected Performance:"
echo "  - Response time: 3-4 seconds"
echo "  - YOLO FPS: 45-60"
echo "  - Memory: ~500MB"
echo ""
