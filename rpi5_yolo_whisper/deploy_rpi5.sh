#!/bin/bash
# Complete Deployment Script for Raspberry Pi 5
# Optimized IRIS Visual Assistance System with NCNN + Fast Whisper

set -e  # Exit on error

echo "=================================================="
echo "🚀 IRIS System Deployment - Raspberry Pi 5"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_step() {
    echo -e "${GREEN}[STEP]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ] || ! grep -q "Raspberry Pi" /proc/device-tree/model; then
    print_warning "This script is optimized for Raspberry Pi 5"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# ========================================
# Step 1: System Update
# ========================================
print_step "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# ========================================
# Step 2: Install System Dependencies
# ========================================
print_step "Installing system dependencies..."

sudo apt-get install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    cmake \
    git \
    ffmpeg \
    espeak \
    portaudio19-dev \
    libopencv-dev \
    libatlas-base-dev \
    libhdf5-dev \
    libhdf5-serial-dev \
    libharfbuzz0b \
    libwebp7 \
    libjasper1 \
    libilmbase25 \
    libopenexr25 \
    libgstreamer1.0-0 \
    libavcodec-extra \
    libavformat58 \
    libswscale5 \
    i2c-tools \
    python3-smbus \
    python3-lgpio

# ========================================
# Step 3: Enable Hardware Interfaces
# ========================================
print_step "Enabling I2C and Camera interfaces..."

# Enable I2C
if ! grep -q "^dtparam=i2c_arm=on" /boot/config.txt; then
    echo "dtparam=i2c_arm=on" | sudo tee -a /boot/config.txt
    print_warning "I2C enabled - reboot required after installation"
fi

# Enable Camera
if ! grep -q "^start_x=1" /boot/config.txt; then
    echo "start_x=1" | sudo tee -a /boot/config.txt
    echo "gpu_mem=128" | sudo tee -a /boot/config.txt
    print_warning "Camera enabled - reboot required after installation"
fi

# Add user to i2c group
sudo usermod -a -G i2c $USER

# ========================================
# Step 4: Python Virtual Environment
# ========================================
print_step "Creating Python virtual environment..."

cd ~/rpi5_yolo_whisper

if [ -d "venv" ]; then
    print_warning "Virtual environment exists, removing old one..."
    rm -rf venv
fi

python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# ========================================
# Step 5: Install Python Dependencies
# ========================================
print_step "Installing Python packages (this may take 10-15 minutes)..."

# Install requirements
pip install -r requirements_rpi5.txt

# Install Raspberry Pi specific packages
pip install picamera2
pip install lgpio
pip install smbus2

echo ""
print_step "Python packages installed successfully!"

# ========================================
# Step 6: Install NCNN for Optimized YOLO
# ========================================
print_step "Installing NCNN for optimized YOLO inference..."

# Install NCNN Python bindings
pip install ncnn

# Install ONNX tools for model conversion
pip install onnx onnxruntime onnxsim

# Build NCNN tools from source
print_step "Building NCNN conversion tools..."

cd ~
if [ -d "ncnn" ]; then
    print_warning "NCNN directory exists, updating..."
    cd ncnn
    git pull
else
    git clone https://github.com/Tencent/ncnn.git
    cd ncnn
fi

# Create build directory
mkdir -p build
cd build

# Configure with CMake
cmake -DCMAKE_BUILD_TYPE=Release \
      -DNCNN_BUILD_TOOLS=ON \
      -DNCNN_BUILD_PYTHON=OFF \
      -DNCNN_VULKAN=OFF \
      -DNCNN_BUILD_EXAMPLES=OFF \
      -DNCNN_BUILD_TESTS=OFF \
      ..

# Build with all cores
make -j$(nproc)

# Install
sudo make install
sudo ldconfig

echo ""
print_step "NCNN tools installed successfully!"
print_step "Available tools: onnx2ncnn, ncnnoptimize, ncnn2int8"

# ========================================
# Step 7: Convert YOLO Model to NCNN
# ========================================
cd ~/rpi5_yolo_whisper

print_step "Converting YOLO model to NCNN format..."

if [ -f "models/yolo11n.pt" ]; then
    python convert_yolo_ncnn.py models/yolo11n.pt
    
    if [ -f "models/yolo11n_ncnn_int8.param" ]; then
        print_step "✅ YOLO model converted to NCNN successfully!"
    else
        print_warning "NCNN conversion completed but quantized model not found"
        print_warning "Standard NCNN model will be used"
    fi
else
    print_warning "YOLO model not found at models/yolo11n.pt"
    print_warning "Model will be downloaded on first run"
fi

# ========================================
# Step 8: Download Whisper Models
# ========================================
print_step "Pre-downloading Whisper models..."

python3 << EOF
from faster_whisper import WhisperModel
import logging
logging.basicConfig(level=logging.INFO)

print("Downloading Whisper tiny model (75MB)...")
WhisperModel("tiny", device="cpu", compute_type="int8")
print("✅ Tiny model downloaded")

print("Downloading Whisper base model (145MB)...")
WhisperModel("base", device="cpu", compute_type="int8")
print("✅ Base model downloaded")

print("All Whisper models ready!")
EOF

# ========================================
# Step 9: Install Piper TTS
# ========================================
print_step "Installing Piper TTS for high-quality voice synthesis..."

# Run Piper installation script
if [ -f "install_piper.sh" ]; then
    chmod +x install_piper.sh
    ./install_piper.sh || print_warning "Piper installation failed (optional)"
    
    # Download recommended voice model
    if [ -f "download_piper_voice.sh" ]; then
        chmod +x download_piper_voice.sh
        ./download_piper_voice.sh en_US-lessac-medium || print_warning "Voice download failed (optional)"
    fi
else
    print_warning "Piper installation scripts not found (optional feature)"
fi

# ========================================
# Step 10: Configure System
# ========================================
print_step "Configuring system..."

# Check if .env exists, create from template if not
if [ ! -f ".env" ]; then
    print_warning ".env file not found, creating from defaults..."
    cat > .env << 'EOF'
# Raspberry Pi 5 Configuration - Optimized

# Wake Word
WAKE_WORD=iris
WAKE_WORD_THRESHOLD=0.6

# Whisper Settings (Optimized)
WHISPER_MODEL=tiny
WHISPER_DEVICE=cpu
WHISPER_LANGUAGE=en
WHISPER_FAST_MODE=true

# YOLO Settings (Will use NCNN if available)
YOLO_MODEL=models/yolo11n.pt
YOLO_CONFIDENCE=0.5

# Camera Settings
CAMERA_TYPE=picamera
CAMERA_INDEX=0
CAMERA_WIDTH=640
CAMERA_HEIGHT=480

# TTS Settings
TTS_ENGINE=piper
TTS_RATE=1.0
TTS_VOLUME=1.0
PIPER_VOICE=en_US-lessac-medium

# Sensor Settings
ULTRASONIC_ENABLED=true
ULTRASONIC_TRIG_PIN=23
ULTRASONIC_ECHO_PIN=24
ULTRASONIC_ANNOUNCE_THRESHOLD=6.0

FALL_DETECTION_ENABLED=true
MPU9250_ADDRESS=0x68
FALL_IMPACT_THRESHOLD=2.5
FALL_ROTATION_THRESHOLD=150

# Events
EVENT_FILE=/tmp/iris_events.jsonl
EOF
    print_step ".env file created with optimized settings"
fi

# Make scripts executable
chmod +x *.sh

# ========================================
# Step 10: Test Hardware
# ========================================
print_step "Testing hardware components..."

# Test camera
print_step "Testing camera..."
if python3 -c "from picamera2 import Picamera2; cam = Picamera2(); cam.start(); cam.stop(); print('✅ Camera OK')" 2>/dev/null; then
    echo "✅ Camera working"
else
    print_warning "❌ Camera test failed - check connections"
fi

# Test I2C devices
print_step "Scanning I2C devices..."
i2cdetect -y 1
if i2cdetect -y 1 | grep -q "68"; then
    echo "✅ MPU9250 detected at 0x68"
else
    print_warning "⚠️  MPU9250 not detected - check connections"
fi

# Test microphone
print_step "Testing microphone..."
if python3 -c "import sounddevice as sd; print('✅ Audio OK')" 2>/dev/null; then
    echo "✅ Microphone accessible"
else
    print_warning "❌ Microphone test failed"
fi

# ========================================
# Step 11: Create Systemd Service (Optional)
# ========================================
print_step "Creating systemd service for auto-start..."

sudo tee /etc/systemd/system/iris-detector.service > /dev/null << EOF
[Unit]
Description=IRIS Visual Assistance System
After=network.target sound.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$HOME/rpi5_yolo_whisper
Environment="DISPLAY=:0"
ExecStart=$HOME/rpi5_yolo_whisper/venv/bin/python gui_mobile_detector.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload

echo ""
print_step "Systemd service created (not enabled by default)"
echo "To enable auto-start: sudo systemctl enable iris-detector"
echo "To start now: sudo systemctl start iris-detector"

# ========================================
# Final Summary
# ========================================
echo ""
echo "=================================================="
echo "✅ INSTALLATION COMPLETE!"
echo "=================================================="
echo ""
echo "📊 System Status:"
echo "  - Python environment: $(which python)"
echo "  - NCNN tools: $(which onnx2ncnn 2>/dev/null && echo 'Installed' || echo 'Not found')"
echo "  - Whisper models: Downloaded (tiny, base)"
echo "  - YOLO model: $([ -f models/yolo11n_ncnn_int8.param ] && echo 'NCNN optimized' || echo 'PyTorch')"
echo ""
echo "🚀 Quick Start Commands:"
echo ""
echo "  # Activate environment"
echo "  cd ~/rpi5_yolo_whisper"
echo "  source venv/bin/activate"
echo ""
echo "  # Test voice recognition"
echo "  python optimized_whisper_stt.py"
echo ""
echo "  # Test YOLO performance"
echo "  python benchmark_yolo.py"
echo ""
echo "  # Run main GUI application"
echo "  python gui_mobile_detector.py"
echo ""
echo "  # Run voice-activated console app"
echo "  python main_rpi5.py"
echo ""
echo "📖 Documentation:"
echo "  - NCNN optimization: NCNN_OPTIMIZATION_README.md"
echo "  - Whisper optimization: WHISPER_OPTIMIZATION_README.md"
echo "  - Hardware setup: HARDWARE_SETUP_GUIDE.md"
echo "  - Integration guide: INTEGRATION_COMPLETE.md"
echo ""

# Check if reboot needed
if grep -q "dtparam=i2c_arm=on" /boot/config.txt || grep -q "start_x=1" /boot/config.txt; then
    echo "⚠️  REBOOT REQUIRED to enable hardware interfaces"
    echo ""
    read -p "Reboot now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo reboot
    else
        echo "Please reboot manually: sudo reboot"
    fi
fi

echo ""
echo "🎉 Happy detecting!"
echo "=================================================="
