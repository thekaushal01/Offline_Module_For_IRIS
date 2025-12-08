# 🚀 Git Deployment Guide - Raspberry Pi 5 Setup

## 📦 Quick Deployment (Recommended)

### On Your Development PC (Windows)

```powershell
# 1. Navigate to project directory
cd "C:\Users\NITIN NAYN\Offline_Module_For_IRIS"

# 2. Initialize Git (if not already done)
git init

# 3. Add all files
git add .

# 4. Commit changes
git commit -m "Initial commit: IRIS offline module with NCNN and optimized Whisper"

# 5. Push to GitHub (if you have a repo)
git remote add origin https://github.com/YOUR_USERNAME/Offline_Module_For_IRIS.git
git branch -M main
git push -u origin main
```

### On Raspberry Pi 5

```bash
# 1. Install Git (if not installed)
sudo apt-get update
sudo apt-get install -y git

# 2. Clone the repository
cd ~
git clone https://github.com/YOUR_USERNAME/Offline_Module_For_IRIS.git
cd Offline_Module_For_IRIS

# 3. Run automated setup
cd rpi5_yolo_whisper
chmod +x install_rpi5.sh install_ncnn.sh
./install_rpi5.sh

# 4. Install NCNN for optimized YOLO
./install_ncnn.sh

# 5. Download and convert YOLO model
python convert_yolo_ncnn.py models/yolo11n.pt

# 6. Test the system
python benchmark_yolo.py
python optimized_whisper_stt.py

# 7. Run the application
python gui_mobile_detector.py
```

---

## 📋 Step-by-Step Deployment

### Step 1: Push to Git Repository

#### Option A: Using Existing GitHub Repo

```powershell
# On Windows PC
cd "C:\Users\NITIN NAYN\Offline_Module_For_IRIS"

# Check Git status
git status

# Add all changes
git add .

# Commit with descriptive message
git commit -m "Add NCNN optimization and fast Whisper for Raspberry Pi 5"

# Push to GitHub
git push origin main
```

#### Option B: Create New GitHub Repository

1. Go to https://github.com/new
2. Repository name: `Offline_Module_For_IRIS`
3. Description: "Voice-activated object detection with YOLO and Whisper for Raspberry Pi 5"
4. Choose Public or Private
5. Click "Create repository"

Then on Windows:
```powershell
cd "C:\Users\NITIN NAYN\Offline_Module_For_IRIS"
git init
git add .
git commit -m "Initial commit: IRIS offline module"
git remote add origin https://github.com/YOUR_USERNAME/Offline_Module_For_IRIS.git
git branch -M main
git push -u origin main
```

### Step 2: Clone on Raspberry Pi

```bash
# SSH into your Raspberry Pi
ssh pi@raspberrypi.local

# Clone the repository
cd ~
git clone https://github.com/YOUR_USERNAME/Offline_Module_For_IRIS.git

# Navigate to project
cd Offline_Module_For_IRIS/rpi5_yolo_whisper
```

### Step 3: Automated Installation

```bash
# Make scripts executable
chmod +x install_rpi5.sh install_ncnn.sh

# Run main installation (15-20 minutes)
./install_rpi5.sh
```

This installs:
- ✅ System dependencies (Python, OpenCV, audio libraries)
- ✅ Python virtual environment
- ✅ Python packages (YOLO, Whisper, etc.)
- ✅ Audio/camera setup
- ✅ Whisper models (tiny by default)

### Step 4: Install NCNN (Optional but Recommended)

```bash
# Install NCNN for 3x faster YOLO inference
./install_ncnn.sh
```

This installs:
- ✅ NCNN library and tools
- ✅ Model conversion tools (onnx2ncnn)
- ✅ Optimization tools

### Step 5: Convert YOLO Model to NCNN

```bash
# Activate virtual environment
source venv/bin/activate

# Convert model (this creates optimized INT8 version)
python convert_yolo_ncnn.py models/yolo11n.pt
```

Creates:
- `models/yolo11n_ncnn.param` - NCNN model structure
- `models/yolo11n_ncnn.bin` - NCNN weights
- `models/yolo11n_ncnn_int8.param` - Quantized model
- `models/yolo11n_ncnn_int8.bin` - Quantized weights

### Step 6: Test Performance

```bash
# Benchmark YOLO performance
python benchmark_yolo.py --runs 20

# Test Whisper speed
python optimized_whisper_stt.py
```

Expected results:
- YOLO: 45-60 FPS (NCNN) vs 15-20 FPS (PyTorch)
- Whisper: 1-2s (tiny/fast) vs 10-15s (medium/standard)

### Step 7: Configure Settings

```bash
# Edit configuration
nano .env
```

Key settings:
```env
# YOLO (auto-detects NCNN if available)
YOLO_MODEL=models/yolo11n.pt
YOLO_CONFIDENCE=0.5

# Whisper (optimized for speed)
WHISPER_MODEL=tiny
WHISPER_FAST_MODE=true

# Camera
CAMERA_TYPE=picamera  # or 'usb'
CAMERA_WIDTH=640
CAMERA_HEIGHT=480

# Sensors (if using)
ULTRASONIC_ENABLED=true
FALL_DETECTION_ENABLED=true
```

### Step 8: Run Application

```bash
# Activate environment
source venv/bin/activate

# Run GUI application (recommended)
python gui_mobile_detector.py

# Or run voice-only application
python main_rpi5.py
```

---

## 🔄 Updating from Git

When you make changes on your PC and want to update Raspberry Pi:

### On Windows PC:
```powershell
cd "C:\Users\NITIN NAYN\Offline_Module_For_IRIS"
git add .
git commit -m "Description of changes"
git push origin main
```

### On Raspberry Pi:
```bash
cd ~/Offline_Module_For_IRIS
git pull origin main

# If dependencies changed, reinstall
cd rpi5_yolo_whisper
source venv/bin/activate
pip install -r requirements_rpi5.txt

# Restart application
python gui_mobile_detector.py
```

---

## 🐛 Troubleshooting

### Git Clone Fails

```bash
# Check internet connection
ping github.com

# Use SSH instead of HTTPS (if you have SSH keys)
git clone git@github.com:YOUR_USERNAME/Offline_Module_For_IRIS.git
```

### Installation Script Fails

```bash
# Check logs
./install_rpi5.sh 2>&1 | tee install.log

# Manual installation
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements_rpi5.txt
```

### NCNN Installation Issues

```bash
# Check if NCNN tools are available
which onnx2ncnn

# If not found, rebuild NCNN
cd ~/ncnn/build
cmake -DCMAKE_BUILD_TYPE=Release ..
make -j4
sudo make install
```

### Model Conversion Fails

```bash
# Install ONNX manually
pip install onnx onnxruntime

# Try conversion with verbose output
python convert_yolo_ncnn.py models/yolo11n.pt 2>&1
```

### Application Won't Start

```bash
# Check virtual environment
source venv/bin/activate
which python  # Should show venv path

# Check dependencies
pip list | grep -E "ultralytics|faster-whisper|ncnn"

# Check camera
libcamera-hello  # Test Pi Camera
v4l2-ctl --list-devices  # List USB cameras
```

---

## 📁 Repository Structure

```
Offline_Module_For_IRIS/
├── .gitignore                    # Git ignore rules
├── README.md                     # Main documentation
└── rpi5_yolo_whisper/
    ├── .env                      # Configuration (template)
    ├── install_rpi5.sh          # Main installation script
    ├── install_ncnn.sh          # NCNN installation
    ├── requirements_rpi5.txt    # Python dependencies
    │
    ├── main_rpi5.py             # Voice-only application
    ├── gui_mobile_detector.py   # GUI application (recommended)
    │
    ├── yolo_detector.py         # PyTorch YOLO
    ├── ncnn_yolo_detector.py    # NCNN YOLO (optimized)
    ├── smart_yolo_detector.py   # Auto-selection wrapper
    ├── convert_yolo_ncnn.py     # Model conversion tool
    ├── benchmark_yolo.py        # Performance testing
    │
    ├── whisper_stt.py           # Whisper speech recognition
    ├── optimized_whisper_stt.py # Fast Whisper (optimized)
    ├── offline_tts.py           # Text-to-speech
    ├── offline_wake_word.py     # Wake word detection
    │
    ├── ultrasonic_sensor_lgpio.py   # Distance sensor
    ├── fall_detector.py             # Fall detection (IMU)
    │
    ├── test_*.py                # Test scripts
    ├── NCNN_OPTIMIZATION_README.md
    ├── WHISPER_OPTIMIZATION_README.md
    ├── GIT_DEPLOYMENT_GUIDE.md  # This file
    └── models/
        └── (models download here)
```

---

## 🎯 Quick Commands Reference

### Git Commands
```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/Offline_Module_For_IRIS.git

# Update from remote
git pull origin main

# Check status
git status

# View changes
git diff
```

### Setup Commands
```bash
# Install everything
./install_rpi5.sh && ./install_ncnn.sh

# Convert YOLO model
python convert_yolo_ncnn.py models/yolo11n.pt

# Test performance
python benchmark_yolo.py
```

### Run Commands
```bash
# Activate environment
source venv/bin/activate

# Run GUI app
python gui_mobile_detector.py

# Run voice-only app
python main_rpi5.py
```

---

## 🎉 Expected Performance

After deployment with all optimizations:

| Component | Performance |
|-----------|-------------|
| **YOLO Inference** | 45-60 FPS (NCNN) |
| **Whisper Recognition** | 1-2 seconds (tiny/fast) |
| **Total Response Time** | 3-4 seconds |
| **Memory Usage** | ~500MB |
| **CPU Usage** | 40-50% |

---

## 📞 Support

If you encounter issues:

1. Check the README files in the project
2. Review troubleshooting section above
3. Check logs: `./install_rpi5.sh 2>&1 | tee install.log`
4. Test components individually using test scripts

---

**🚀 Enjoy your optimized IRIS system on Raspberry Pi 5!**
