#!/bin/bash
# Camera Diagnostics Script for Raspberry Pi
# Run this if you're having camera issues

echo "=========================================="
echo "🔍 Raspberry Pi Camera Diagnostics"
echo "=========================================="
echo ""

# Check Pi model
echo "📋 System Information:"
if [ -f /proc/device-tree/model ]; then
    cat /proc/device-tree/model
    echo ""
else
    echo "⚠️  Not running on Raspberry Pi"
fi
echo ""

# Check camera type in .env
echo "=========================================="
echo "📁 Current Configuration (.env):"
echo "=========================================="
if [ -f .env ]; then
    grep CAMERA .env
else
    echo "⚠️  .env file not found!"
fi
echo ""

# Check Pi Camera
echo "=========================================="
echo "🎥 Pi Camera Detection:"
echo "=========================================="
if command -v vcgencmd &> /dev/null; then
    vcgencmd get_camera
    echo ""
    
    # Check if camera is enabled
    if vcgencmd get_camera | grep -q "detected=1"; then
        echo "✅ Pi Camera is detected!"
    else
        echo "❌ Pi Camera NOT detected!"
        echo "   → Check ribbon cable connection"
        echo "   → Enable camera: sudo raspi-config → Interface Options → Camera"
    fi
else
    echo "⚠️  vcgencmd not available (not on Raspberry Pi)"
fi
echo ""

# Test libcamera
echo "=========================================="
echo "📸 Testing libcamera (Pi Camera):"
echo "=========================================="
if command -v libcamera-hello &> /dev/null; then
    echo "Running 2-second camera test..."
    if timeout 3 libcamera-hello --timeout 2000 2>&1 | grep -q "Preview window"; then
        echo "✅ Pi Camera test successful!"
    else
        echo "⚠️  Camera test may have issues"
    fi
else
    echo "⚠️  libcamera-hello not found"
    echo "   Install: sudo apt-get install libcamera-apps"
fi
echo ""

# Check USB cameras
echo "=========================================="
echo "🔌 USB Camera Detection:"
echo "=========================================="
if ls /dev/video* 2>/dev/null; then
    echo "✅ USB camera(s) found"
    for device in /dev/video*; do
        echo "   → $device"
    done
else
    echo "❌ No USB cameras detected"
fi
echo ""

# Check Python environment
echo "=========================================="
echo "🐍 Python Environment:"
echo "=========================================="
if [ -d "venv" ]; then
    echo "✅ Virtual environment found"
    
    # Activate and check packages
    source venv/bin/activate 2>/dev/null
    
    echo ""
    echo "Checking installed packages..."
    
    # Check picamera2
    if python -c "import picamera2" 2>/dev/null; then
        echo "✅ picamera2 installed"
        python -c "import picamera2; print(f'   Version: {picamera2.__version__}')" 2>/dev/null || echo "   (version unknown)"
    else
        echo "❌ picamera2 NOT installed"
        echo "   Install: sudo apt-get install python3-picamera2"
        echo "   Or: pip install picamera2"
    fi
    
    # Check OpenCV
    if python -c "import cv2" 2>/dev/null; then
        echo "✅ opencv-python installed"
        python -c "import cv2; print(f'   Version: {cv2.__version__}')" 2>/dev/null || echo "   (version unknown)"
    else
        echo "❌ opencv-python NOT installed"
        echo "   Install: pip install opencv-python"
    fi
    
    # Check ultralytics
    if python -c "import ultralytics" 2>/dev/null; then
        echo "✅ ultralytics (YOLO) installed"
    else
        echo "❌ ultralytics NOT installed"
        echo "   Install: pip install ultralytics"
    fi
    
else
    echo "⚠️  Virtual environment not found"
    echo "   Run: ./install_rpi5.sh"
fi
echo ""

# Check camera interface in config
echo "=========================================="
echo "⚙️  Camera Interface Status:"
echo "=========================================="
if command -v raspi-config &> /dev/null; then
    # This is tricky to check without running raspi-config
    echo "Check camera interface with: sudo raspi-config"
    echo "   → Interface Options → Camera → Enable"
else
    echo "⚠️  raspi-config not available"
fi
echo ""

# Recommendations
echo "=========================================="
echo "💡 Recommendations:"
echo "=========================================="
echo ""

# Check .env settings
if [ -f .env ]; then
    camera_type=$(grep "^CAMERA_TYPE=" .env | cut -d'=' -f2)
    
    if [ "$camera_type" = "picamera" ]; then
        echo "✓ .env is set to use Pi Camera"
        if vcgencmd get_camera 2>/dev/null | grep -q "detected=1"; then
            echo "✓ Pi Camera is detected"
            echo ""
            echo "✅ Everything looks good for Pi Camera!"
            echo ""
            echo "To run the detector:"
            echo "  source venv/bin/activate"
            echo "  python gui_detector.py"
        else
            echo "❌ Pi Camera not detected!"
            echo ""
            echo "Fix steps:"
            echo "  1. Check ribbon cable (blue side to camera, pins to black latch)"
            echo "  2. Enable camera: sudo raspi-config"
            echo "  3. Reboot: sudo reboot"
            echo "  4. Test: libcamera-hello --timeout 2000"
        fi
    elif [ "$camera_type" = "usb" ]; then
        echo "✓ .env is set to use USB Camera"
        if ls /dev/video* 2>/dev/null; then
            echo "✓ USB camera is detected"
            echo ""
            echo "✅ Everything looks good for USB Camera!"
        else
            echo "❌ USB camera not detected!"
            echo ""
            echo "Options:"
            echo "  1. Connect a USB webcam"
            echo "  2. Or switch to Pi Camera in .env:"
            echo "     nano .env"
            echo "     Change: CAMERA_TYPE=picamera"
        fi
    fi
else
    echo "⚠️  .env file not found - create it from installation"
fi

echo ""
echo "=========================================="
echo "📚 More Help:"
echo "=========================================="
echo "  RASPBERRY_PI_SETUP.md - Full setup guide"
echo "  GUI_README.md - GUI usage help"
echo ""
echo "Run this script again after making changes!"
echo "=========================================="
