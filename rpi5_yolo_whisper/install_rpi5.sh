#!/bin/bash
# Installation script for Raspberry Pi 5
# YOLO + Whisper Voice-Activated Object Detector

echo "=========================================="
echo "Raspberry Pi 5 Setup"
echo "YOLO + Whisper Object Detector"
echo "=========================================="

# Check if running on Raspberry Pi
if [ ! -f /proc/device-tree/model ]; then
    echo "⚠️  Warning: This script is designed for Raspberry Pi"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update system
echo ""
echo "📦 Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install system dependencies
echo ""
echo "📦 Installing system dependencies..."
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    libportaudio2 \
    libportaudiocpp0 \
    portaudio19-dev \
    espeak \
    espeak-data \
    libespeak-dev \
    libopenblas-dev \
    libopencv-dev \
    python3-opencv \
    ffmpeg \
    git

# Install camera support (if Pi Camera)
echo ""
read -p "Do you have Raspberry Pi Camera Module? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📷 Installing Raspberry Pi Camera support..."
    sudo apt-get install -y python3-picamera2
    echo "✅ Camera support installed"
    echo "Note: Enable camera interface in raspi-config if not already enabled"
fi

# Create virtual environment
echo ""
echo "🔧 Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "📦 Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Install Python dependencies
echo ""
echo "📦 Installing Python packages..."
echo "This may take 10-15 minutes on Raspberry Pi..."
pip install -r requirements_rpi5.txt

# Download models
echo ""
echo "📥 Downloading AI models..."

# Download YOLO model
echo "Downloading YOLO11n model..."
python3 << EOF
from ultralytics import YOLO
import os
os.makedirs('models', exist_ok=True)
if not os.path.exists('models/yolo11n.pt'):
    model = YOLO('yolo11n.pt')
    os.rename('yolo11n.pt', 'models/yolo11n.pt')
    print("✅ YOLO11n model downloaded")
else:
    print("✅ YOLO model already exists")
EOF

# Download Whisper models
echo ""
echo "Downloading Whisper models (tiny + small)..."
python3 << EOF
from faster_whisper import WhisperModel
print("Downloading Whisper tiny model...")
WhisperModel('tiny', device='cpu', compute_type='int8')
print("✅ Whisper tiny model downloaded")
print("Downloading Whisper small model...")
WhisperModel('small', device='cpu', compute_type='int8')
print("✅ Whisper small model downloaded")
EOF

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "📝 Creating configuration file (.env)..."
    cat > .env << EOF
# Wake Word
WAKE_WORD=iris
WAKE_WORD_THRESHOLD=0.6

# Whisper Settings
WHISPER_MODEL=small
WHISPER_DEVICE=cpu
WHISPER_LANGUAGE=en

# YOLO Settings
YOLO_MODEL=models/yolo11n.pt
YOLO_CONFIDENCE=0.5

# Camera Settings (picamera or usb)
CAMERA_TYPE=picamera
CAMERA_INDEX=0
CAMERA_WIDTH=640
CAMERA_HEIGHT=480

# TTS Settings
TTS_ENGINE=pyttsx3
TTS_RATE=150
TTS_VOLUME=1.0

# Audio Settings
SAMPLE_RATE=16000
EOF
    echo "✅ Configuration file created"
else
    echo "✅ Configuration file already exists"
fi

# Test components
echo ""
echo "=========================================="
echo "🧪 Testing Components"
echo "=========================================="

echo ""
echo "Testing imports..."
python3 << EOF
print("Testing imports...")
try:
    import cv2
    print("✅ OpenCV")
    import numpy
    print("✅ NumPy")
    from ultralytics import YOLO
    print("✅ YOLO")
    from faster_whisper import WhisperModel
    print("✅ Whisper")
    import pyttsx3
    print("✅ pyttsx3")
    import sounddevice
    print("✅ sounddevice")
    print("\n✅ All imports successful!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    exit(1)
EOF

# Final instructions
echo ""
echo "=========================================="
echo "✅ Installation Complete!"
echo "=========================================="
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Activate virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Configure settings (optional):"
echo "   nano .env"
echo ""
echo "3. Run the app:"
echo "   python main_rpi5.py"
echo ""
echo "4. Say 'IRIS' to activate, then:"
echo "   'What do you see?'"
echo "   'Detect objects'"
echo ""
echo "=========================================="
echo "🎉 Ready to use!"
echo "=========================================="
