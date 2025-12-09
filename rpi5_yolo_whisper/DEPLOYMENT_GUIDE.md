# 🚀 Complete Deployment Guide - Raspberry Pi 5

## 📋 Prerequisites
- Raspberry Pi 5 (4GB or 8GB RAM)
- MicroSD card (32GB+ recommended)
- Raspberry Pi OS (64-bit) installed
- Internet connection
- SSH access or monitor/keyboard

---

## 🎯 Quick Deployment (5 Steps)

### Step 1: Push Code to GitHub

On your Windows PC:

```powershell
cd "C:\Users\NITIN NAYN\Offline_Module_For_IRIS"

# Add all changes
git add .

# Commit with message
git commit -m "Add NCNN YOLO and Fast Whisper optimizations"

# Push to GitHub
git push origin main
```

### Step 2: Clone on Raspberry Pi

SSH into your Raspberry Pi or open terminal:

```bash
# SSH into Pi (from Windows)
ssh pi@raspberrypi.local
# Default password: raspberry (change it!)

# OR use Pi's terminal directly
```

Clone the repository:

```bash
cd ~
git clone https://github.com/thekaushal01/Offline_Module_For_IRIS.git
cd Offline_Module_For_IRIS/rpi5_yolo_whisper
```

### Step 3: Run Deployment Script

```bash
chmod +x deploy_rpi5.sh
./deploy_rpi5.sh
```

**This script will:**
- ✅ Update system packages
- ✅ Install all dependencies (Python, NCNN, OpenCV, etc.)
- ✅ Create Python virtual environment
- ✅ Install Python packages
- ✅ Build NCNN tools
- ✅ Convert YOLO model to NCNN
- ✅ Download Whisper models
- ✅ Configure hardware (I2C, Camera)
- ✅ Test all components

**Time required**: 20-30 minutes

### Step 4: Reboot (if prompted)

```bash
sudo reboot
```

### Step 5: Run the System

After reboot:

```bash
cd ~/Offline_Module_For_IRIS/rpi5_yolo_whisper
source venv/bin/activate

# Run the GUI application
python gui_mobile_detector.py
```

---

## 📝 Detailed Step-by-Step Guide

### 1. Prepare Raspberry Pi

#### Initial Setup
```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Change default password
passwd

# Set hostname (optional)
sudo raspi-config
# Navigate to: System Options → Hostname

# Enable SSH (if not already)
sudo raspi-config
# Navigate to: Interface Options → SSH → Enable
```

### 2. Clone Repository

```bash
# Install git if not present
sudo apt-get install git -y

# Clone your repository
cd ~
git clone https://github.com/thekaushal01/Offline_Module_For_IRIS.git

# Navigate to project
cd Offline_Module_For_IRIS/rpi5_yolo_whisper
```

### 3. Run Automated Deployment

```bash
# Make script executable
chmod +x deploy_rpi5.sh

# Run deployment (takes 20-30 minutes)
./deploy_rpi5.sh
```

**What happens during deployment:**

```
[STEP] Updating system packages...
[STEP] Installing system dependencies...
[STEP] Enabling I2C and Camera interfaces...
[STEP] Creating Python virtual environment...
[STEP] Installing Python packages (10-15 minutes)...
[STEP] Installing NCNN for optimized YOLO inference...
[STEP] Building NCNN conversion tools...
[STEP] Converting YOLO model to NCNN format...
[STEP] Pre-downloading Whisper models...
[STEP] Configuring system...
[STEP] Testing hardware components...
[STEP] Creating systemd service for auto-start...
✅ INSTALLATION COMPLETE!
```

### 4. Manual Installation (Alternative)

If you prefer manual installation:

```bash
cd ~/Offline_Module_For_IRIS/rpi5_yolo_whisper

# System dependencies
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv ffmpeg espeak portaudio19-dev

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r requirements_rpi5.txt

# Install NCNN
chmod +x install_ncnn.sh
./install_ncnn.sh

# Convert YOLO model
python convert_yolo_ncnn.py models/yolo11n.pt
```

### 5. Hardware Configuration

#### Enable Camera
```bash
sudo raspi-config
# Interface Options → Camera → Enable
```

#### Enable I2C (for sensors)
```bash
sudo raspi-config
# Interface Options → I2C → Enable

# Add user to i2c group
sudo usermod -a -G i2c $USER
```

#### Test I2C Devices
```bash
sudo apt-get install i2c-tools
i2cdetect -y 1
# Should show device at 0x68 (MPU9250)
```

### 6. Configuration

Edit `.env` file for your setup:

```bash
nano .env
```

**Recommended settings:**

```env
# Optimized for Raspberry Pi 5
WHISPER_MODEL=tiny              # Fastest (1-2s)
WHISPER_FAST_MODE=true          # Speed optimization
YOLO_MODEL=models/yolo11n.pt    # NCNN auto-detected
YOLO_CONFIDENCE=0.5

CAMERA_TYPE=picamera            # or 'usb'
CAMERA_WIDTH=640
CAMERA_HEIGHT=480
```

### 7. Testing

#### Test Individual Components

```bash
cd ~/Offline_Module_For_IRIS/rpi5_yolo_whisper
source venv/bin/activate

# Test camera
python -c "from picamera2 import Picamera2; cam = Picamera2(); cam.start(); print('Camera OK'); cam.stop()"

# Test microphone
python test_voice.py

# Test ultrasonic sensor
python test_ultrasonic_lgpio.py

# Test IMU (fall detection)
python test_mpu9250.py

# Test YOLO performance
python benchmark_yolo.py

# Test Whisper speed
python optimized_whisper_stt.py
```

#### Run Full System Test

```bash
# GUI version (recommended)
python gui_mobile_detector.py

# Console version
python main_rpi5.py
```

### 8. Auto-Start on Boot (Optional)

The deployment script creates a systemd service. To enable:

```bash
# Enable service
sudo systemctl enable iris-detector

# Start service now
sudo systemctl start iris-detector

# Check status
sudo systemctl status iris-detector

# View logs
journalctl -u iris-detector -f

# Disable auto-start
sudo systemctl disable iris-detector
```

### 9. Remote Access via VNC

#### Install TigerVNC
```bash
sudo apt-get install tigervnc-standalone-server

# Set VNC password
vncpasswd

# Start VNC server
vncserver :1 -geometry 1280x720 -depth 24
```

#### Connect from PC/Phone
1. Install VNC Viewer on your device
2. Connect to: `raspberrypi.local:5901`
3. Enter VNC password
4. Run: `python gui_mobile_detector.py`

---

## 🔄 Updating the System

### Pull Latest Changes

```bash
cd ~/Offline_Module_For_IRIS
git pull origin main

cd rpi5_yolo_whisper
source venv/bin/activate

# Reinstall requirements if updated
pip install -r requirements_rpi5.txt
```

### Update Models

```bash
# Re-convert YOLO to NCNN
python convert_yolo_ncnn.py models/yolo11n.pt

# Re-download Whisper models
python -c "from faster_whisper import WhisperModel; WhisperModel('tiny', device='cpu', compute_type='int8')"
```

---

## 🐛 Troubleshooting

### Deployment Script Fails

**Check logs:**
```bash
./deploy_rpi5.sh 2>&1 | tee deployment.log
```

**Common issues:**

1. **Insufficient space**
   ```bash
   df -h
   # Need at least 8GB free
   ```

2. **Permission errors**
   ```bash
   sudo chown -R $USER:$USER ~/Offline_Module_For_IRIS
   ```

3. **Network issues**
   ```bash
   ping google.com
   # Check internet connection
   ```

### Camera Not Working

```bash
# Enable camera
sudo raspi-config
# Interface Options → Camera → Enable

# Check camera
vcgencmd get_camera
# Should show: supported=1 detected=1

# Test with libcamera
libcamera-hello -t 5000
```

### I2C Devices Not Found

```bash
# Enable I2C
sudo raspi-config
# Interface Options → I2C → Enable

# Install tools
sudo apt-get install i2c-tools

# Scan devices
i2cdetect -y 1

# Check permissions
sudo usermod -a -G i2c $USER
# Logout and login
```

### Audio/Microphone Issues

```bash
# List audio devices
arecord -l

# Test recording
arecord -d 5 test.wav
aplay test.wav

# Adjust volume
alsamixer
```

### Slow Performance

1. **Check CPU temperature**
   ```bash
   vcgencmd measure_temp
   # Should be < 70°C
   ```

2. **Enable performance governor**
   ```bash
   echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
   ```

3. **Increase GPU memory**
   ```bash
   sudo nano /boot/config.txt
   # Add: gpu_mem=256
   sudo reboot
   ```

### Model Download Fails

```bash
# Manually download Whisper models
python3 << EOF
from faster_whisper import WhisperModel
WhisperModel("tiny", device="cpu", compute_type="int8")
WhisperModel("base", device="cpu", compute_type="int8")
EOF

# Check YOLO model
ls -lh models/yolo11n.pt
```

---

## 📊 Performance Verification

### Expected Benchmarks

```bash
# Run benchmarks
cd ~/Offline_Module_For_IRIS/rpi5_yolo_whisper
source venv/bin/activate

# YOLO performance
python benchmark_yolo.py
# Expected: 45-60 FPS (NCNN), 15-20 FPS (PyTorch)

# Whisper performance
python optimized_whisper_stt.py
# Expected: 1-2s (tiny), 2-3s (base)
```

### System Resources

```bash
# Check CPU usage
htop

# Check memory
free -h

# Check temperature
watch -n 1 vcgencmd measure_temp
```

---

## 🎯 Usage Examples

### Voice Commands

```bash
python main_rpi5.py
```

1. Say: **"IRIS"**
2. System: "Yes?"
3. Say: **"What do you see?"**
4. System describes detected objects

### GUI Application

```bash
python gui_mobile_detector.py
```

- Click "Start Detection" for live feed
- Say "IRIS detect" for voice activation
- Use controls to adjust settings

### Testing Sensors

```bash
# Ultrasonic distance
python test_ultrasonic_lgpio.py

# Fall detection
python test_mpu9250.py

# Combined system
python gui_mobile_detector.py
```

---

## 📚 Reference Commands

### Common Operations

```bash
# Activate environment
cd ~/Offline_Module_For_IRIS/rpi5_yolo_whisper
source venv/bin/activate

# Run GUI
python gui_mobile_detector.py

# Run console
python main_rpi5.py

# Check status
sudo systemctl status iris-detector

# View logs
journalctl -u iris-detector -f

# Restart system
sudo reboot
```

### Maintenance

```bash
# Update code
cd ~/Offline_Module_For_IRIS
git pull

# Update packages
source rpi5_yolo_whisper/venv/bin/activate
pip install --upgrade -r rpi5_yolo_whisper/requirements_rpi5.txt

# Clean cache
pip cache purge
sudo apt-get autoremove -y
sudo apt-get clean
```

---

## 🎉 Success Checklist

After deployment, verify:

- [ ] System boots without errors
- [ ] Camera captures video
- [ ] Microphone records audio
- [ ] I2C devices detected (if sensors connected)
- [ ] YOLO detects objects (45-60 FPS with NCNN)
- [ ] Whisper recognizes speech (1-2s with tiny model)
- [ ] Voice commands work ("IRIS detect")
- [ ] TTS speaks responses
- [ ] GUI displays live feed
- [ ] All sensors reading data

---

**🚀 Your optimized IRIS system is ready to run on Raspberry Pi 5!**

**Total setup time**: 30-40 minutes
**Expected performance**: 3-4s total response time
**Resource usage**: ~500MB RAM, 40-50% CPU