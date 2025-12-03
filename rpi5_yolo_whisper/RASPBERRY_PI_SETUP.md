# 🚀 Complete Raspberry Pi Setup Instructions

**Voice-Activated Object Detection with GUI**  
Repository: https://github.com/Aniket-1149/rasp-object-detection

---

## 📋 What You'll Get

A complete voice-activated object detection system with:
- ✅ Live video GUI accessible via TigerVNC (PC/Phone)
- ✅ Voice activation ("Say IRIS")
- ✅ Real-time object detection with bounding boxes
- ✅ Spoken responses describing what it sees
- ✅ Fully offline operation

---

## 🎯 Complete Setup Steps

### **Step 1: Clone Repository on Raspberry Pi**

SSH into your Raspberry Pi and run:

```bash
cd ~
git clone https://github.com/Aniket-1149/rasp-object-detection.git
cd rasp-object-detection/rpi5_yolo_whisper
```

---

### **Step 2: Run Automated Installation**

```bash
chmod +x install_rpi5.sh
./install_rpi5.sh
```

**This will automatically:**
- ✅ Install system dependencies (Python, audio, OpenCV, etc.)
- ✅ Create Python virtual environment
- ✅ Install Python packages (YOLO, Whisper, OpenCV, etc.)
- ✅ Download AI models (YOLO11n + Whisper)
- ✅ Configure camera support

**⏱️ Time Required:** ~15-20 minutes

**During installation, it will ask:**
- "Do you have Raspberry Pi Camera Module?" → Answer `y` or `n`

---

### **Step 3: Install TigerVNC Server**

```bash
# Install TigerVNC
sudo apt-get update
sudo apt-get install -y tigervnc-standalone-server tigervnc-common

# Set VNC password
vncpasswd
# Enter password (example: raspberry)
# View-only password: n

# Create VNC startup script
mkdir -p ~/.vnc
nano ~/.vnc/xstartup
```

**Paste this into xstartup file:**
```bash
#!/bin/sh
unset SESSION_MANAGER
unset DBUS_SESSION_BUS_ADDRESS
exec startlxde
```

**Save and make executable:**
```bash
chmod +x ~/.vnc/xstartup
```

**Start VNC Server:**
```bash
vncserver :1 -geometry 1280x720 -depth 24
```

---

### **Step 4: Connect from Your PC/Phone**

#### **On Windows PC:**
1. Download [RealVNC Viewer](https://www.realvnc.com/en/connect/download/viewer/)
2. Open VNC Viewer
3. Enter: `<raspberry-pi-ip>:5901`
   - Find Pi IP with: `hostname -I` on Pi
   - Example: `192.168.1.100:5901`
4. Enter VNC password you set earlier

#### **On Phone (Android/iOS):**
1. Install **VNC Viewer** from app store
2. Add connection: `<raspberry-pi-ip>:5901`
3. Connect with your password

---

### **Step 5: Configure Camera (If Needed)**

If using **Raspberry Pi Camera Module**:

```bash
# Enable camera
sudo raspi-config
# Navigate: Interface Options → Camera → Enable → Reboot

# Edit configuration
cd ~/rasp-object-detection/rpi5_yolo_whisper
nano .env
```

Change this line:
```env
CAMERA_TYPE=picamera
```

If using **USB Webcam**, keep it as:
```env
CAMERA_TYPE=usb
```

---

### **Step 6: Run the GUI Application**

**In your VNC session terminal:**

```bash
cd ~/rasp-object-detection/rpi5_yolo_whisper
source venv/bin/activate
export DISPLAY=:1
python main_gui.py
```

**Or use the quick start script:**
```bash
cd ~/rasp-object-detection/rpi5_yolo_whisper
chmod +x start_gui.sh
./start_gui.sh
```

---

## 🎮 How to Use

### **Voice Commands**

1. **Say "IRIS"** (the wake word)
   - Wait for the red indicator to appear
   - System will say "Yes?"

2. **Say your command:**
   - "What do you see?"
   - "Detect objects"
   - "How many objects?"
   - "What's there?"
   - "What's in front of me?"

3. **Listen to the response:**
   - System detects objects
   - Draws bounding boxes on screen
   - Speaks the results
   - Shows detection summary in right panel

### **Keyboard Controls (in GUI)**

| Key | Action |
|-----|--------|
| `Q` | Quit application |
| `D` | Detect objects now (without voice) |
| `S` | Save screenshot with detections |

### **GUI Interface**

```
┌─────────────────────────────────────────────────────────┐
│ Voice-Activated Object Detection        FPS: 15        │
│ Status: Listening for 'IRIS'...       [🔴 LISTENING]  │
├─────────────────────────────────────────────┬───────────┤
│                                             │Detections:│
│                                             │Total: 3   │
│         LIVE CAMERA FEED                    │           │
│       [Person] 87%                          │person: 1  │
│         ┌──────────┐                        │chair: 2   │
│         │  Person  │                        │           │
│         └──────────┘                        │"I see one │
│    [Chair] 92%  [Chair] 85%                │ person    │
│                                             │ and two   │
│                                             │ chairs."  │
├─────────────────────────────────────────────┴───────────┤
│ Say 'IRIS' to activate                                  │
│ Then say: 'What do you see?' or 'Detect objects'       │
│ Press 'Q' to quit | 'D' to detect | 'S' to save        │
└─────────────────────────────────────────────────────────┘
```

---

## ⚙️ Configuration & Optimization

### **Basic Configuration**

Edit `.env` file:
```bash
nano .env
```

**Common settings:**
```env
# Wake word (change to anything)
WAKE_WORD=iris

# Camera type
CAMERA_TYPE=usb          # or 'picamera'

# Detection confidence (lower = more detections)
YOLO_CONFIDENCE=0.5

# Whisper model (tiny=fast, small=balanced, base=accurate)
WHISPER_MODEL=small
```

### **Performance Optimization**

**For FASTER performance:**
```env
WHISPER_MODEL=tiny
CAMERA_WIDTH=320
CAMERA_HEIGHT=240
YOLO_CONFIDENCE=0.6
```

**For BETTER accuracy:**
```env
WHISPER_MODEL=base
CAMERA_WIDTH=640
CAMERA_HEIGHT=480
YOLO_CONFIDENCE=0.4
```

---

## 🔧 Troubleshooting

### **Camera Not Working**

```bash
# For Pi Camera:
sudo raspi-config  # Enable camera
libcamera-hello    # Test camera

# For USB Camera:
ls /dev/video*     # Should show /dev/video0
```

### **No Microphone/Audio**

```bash
# List devices
arecord -l    # Microphone
aplay -l      # Speaker

# Test
arecord -d 3 test.wav
aplay test.wav
```

### **VNC Connection Failed**

```bash
# Restart VNC
vncserver -kill :1
vncserver :1 -geometry 1280x720 -depth 24

# Check VNC is running
ps aux | grep vnc
```

### **Low Performance / FPS**

1. Lower camera resolution in `.env`
2. Use `WHISPER_MODEL=tiny`
3. Close other applications
4. Increase confidence threshold

### **Memory Issues**

```bash
# Increase swap
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Set: CONF_SWAPSIZE=2048
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

---

## 🔄 Running After Reboot

**Every time you restart your Pi:**

1. **Start VNC Server:**
   ```bash
   vncserver :1 -geometry 1280x720 -depth 24
   ```

2. **Connect via VNC** from your PC/phone

3. **Run the application:**
   ```bash
   cd ~/rasp-object-detection/rpi5_yolo_whisper
   ./start_gui.sh
   ```

---

## 📚 Documentation Files

- **README_RPI5.md** - Complete documentation
- **QUICKSTART.md** - Quick start guide
- **TIGERVNC_SETUP.md** - Detailed VNC setup
- **PROJECT_SUMMARY.md** - Project overview

---

## 🎯 Expected Performance

### Raspberry Pi 5 (8GB)

| Metric | Value |
|--------|-------|
| **Live Video FPS** | 15-25 FPS |
| **Wake Word Detection** | ~0.5 seconds |
| **Speech Recognition** | ~3-4 seconds |
| **Object Detection** | ~0.5-1 second |
| **Total Response Time** | ~5-7 seconds |

---

## ✅ Success Checklist

- [ ] Repository cloned
- [ ] Installation script completed
- [ ] TigerVNC installed and running
- [ ] Can connect to VNC from PC/phone
- [ ] Camera working (tested)
- [ ] Microphone working (tested)
- [ ] GUI application runs
- [ ] Voice activation works ("IRIS" detected)
- [ ] Objects detected and displayed
- [ ] Spoken responses working

---

## 🆘 Need Help?

**Test individual components:**
```bash
source venv/bin/activate
python -c "from yolo_detector import YOLODetector; print('✅ YOLO OK')"
python -c "from whisper_stt import WhisperRecognizer; print('✅ Whisper OK')"
python -c "from offline_tts import TextToSpeech; print('✅ TTS OK')"
```

**Check system resources:**
```bash
# Memory
free -h

# CPU temperature
vcgencmd measure_temp

# Storage
df -h
```

---

## 🎉 You're Done!

You now have a fully functional voice-activated object detection system with a beautiful GUI accessible from your PC or phone via TigerVNC!

**Say "IRIS" and start detecting objects!** 🚀

---

**Repository:** https://github.com/Aniket-1149/rasp-object-detection  
**Author:** Aniket-1149  
**License:** MIT
