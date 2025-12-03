# 🚀 Raspberry Pi Setup Instructions

## Complete Setup Guide for GUI Object Detector

### 📋 Prerequisites

- **Raspberry Pi 5** (4GB+ RAM recommended)
- **Raspberry Pi OS** (64-bit Bookworm recommended)
- **Camera**: Raspberry Pi Camera Module (V1/V2/V3) or Arducam IMX219/IMX477 or USB webcam
- **Audio**: Speaker or headphones for voice announcements
- **Internet connection** (for initial setup only)

---

## 🎯 Step-by-Step Setup

### Step 1: Clone Repository

SSH into your Raspberry Pi and run:

```bash
cd ~
git clone https://github.com/Aniket-1149/rasp-object-detection.git
cd rasp-object-detection/rpi5_yolo_whisper
```

### Step 2: Run Installation Script

```bash
chmod +x install_rpi5.sh
./install_rpi5.sh
```

**What this installs:**
- ✅ System dependencies (Python, OpenCV, audio libraries)
- ✅ Python virtual environment
- ✅ YOLO11n model for object detection
- ✅ Whisper models for speech recognition
- ✅ GUI libraries (tkinter, Pillow)
- ✅ TTS engine (pyttsx3)

**⏱️ Time required:** 15-20 minutes

**💡 Tip:** The script will ask if you have a Pi Camera. Answer **'y'** since you're using Pi Camera Module.

### Step 3: Enable Pi Camera

**The project is configured for Raspberry Pi Camera by default.**

Enable camera interface:
```bash
sudo raspi-config
```
Navigate to: `Interface Options` → `Camera` → `Enable` → Reboot

**Verify camera is working:**
```bash
# Test Pi Camera (newer Raspberry Pi OS)
rpicam-hello --timeout 2000

# Or take a test photo
rpicam-still -o test.jpg

# Legacy commands (older OS versions)
# libcamera-hello --timeout 2000
# libcamera-still -o test.jpg
```

**If using USB Webcam instead:**

Edit `.env` file:
```bash
nano .env
```

Change camera type:
```env
CAMERA_TYPE=usb  # Change from 'picamera' to 'usb'
CAMERA_INDEX=0   # Try 0, 1, 2 if you have multiple cameras
```

### Step 4: Test Installation

**Run Camera Diagnostics (Recommended):**
```bash
chmod +x diagnose_camera.sh
./diagnose_camera.sh
```
This will check:
- Pi Camera detection
- Camera configuration
- Required Python packages
- Provide specific fix recommendations

**Manual Component Tests:**
```bash
source venv/bin/activate

# Test individual components
python -c "from yolo_detector import YOLODetector; print('✅ YOLO OK')"
python -c "from offline_tts import TextToSpeech; print('✅ TTS OK')"
python -c "import tkinter; print('✅ GUI OK')"
```

All should print "✅ OK" without errors.

### Step 5: Run GUI Detector

```bash
source venv/bin/activate
python gui_detector.py
```

**Expected behavior:**
1. GUI window opens showing camera feed
2. Voice says "Object detector ready"
3. Click "Start Detection" to begin

---

## 🎮 Using the GUI Application

### Main Interface

```
┌─────────────────────────────────────────┐
│  🎯 Real-Time Object Detection          │
├─────────────────────────────────────────┤
│  📹 Camera Feed                         │
│  [Live video with bounding boxes]       │
│                                          │
├─────────────────────────────────────────┤
│  📊 Detection Info                      │
│  I see: 2 persons, 1 chair              │
│  Objects: 3 | FPS: 12.5                 │
├─────────────────────────────────────────┤
│  [▶ Start] [🔊 Announce] [❌ Quit]      │
│  Confidence: [======●===] 0.50          │
│  ☑ Auto-announce new objects            │
└─────────────────────────────────────────┘
```

### Controls

| Button | Function |
|--------|----------|
| **▶ Start Detection** | Begin real-time object detection |
| **⏸ Stop Detection** | Pause detection |
| **🔊 Announce Now** | Manually trigger voice announcement |
| **❌ Quit** | Close application |

### Settings

- **Confidence Slider**: Adjust detection sensitivity (0.1 - 0.9)
  - Lower = More objects detected (may include false positives)
  - Higher = Only highly confident detections
  
- **Auto-announce**: When enabled, new objects are automatically announced

---

## 🔊 Voice Announcements

### Automatic Announcements

When **new objects** appear in the frame:
- ✅ "I see 2 persons, 1 chair, 1 bottle"
- ✅ Cooldown: 3 seconds between announcements

### Manual Announcements

Click **"🔊 Announce Now"** anytime to hear:
- Current objects in view
- Total count

---

## ⚙️ Configuration Options

Edit `.env` file to customize:

```bash
nano .env
```

### Key Settings

```env
# Detection Sensitivity
YOLO_CONFIDENCE=0.5        # 0.1 (sensitive) to 0.9 (strict)

# Camera Settings
CAMERA_TYPE=picamera       # 'picamera' for Pi Camera, 'usb' for USB webcam
CAMERA_INDEX=0             # Camera device number (for USB only)
CAMERA_WIDTH=640           # Resolution width
CAMERA_HEIGHT=480          # Resolution height

# Voice Settings
TTS_RATE=150               # Speech speed (100-200)
TTS_VOLUME=1.0             # Volume (0.0-1.0)
```

---

## 🔧 Troubleshooting

### Problem: GUI doesn't open

**Solution 1 - Check Display:**
```bash
echo $DISPLAY
# Should show ":0" or similar
export DISPLAY=:0
python gui_detector.py
```

**Solution 2 - SSH with X11:**
```bash
# On your PC, connect with X11 forwarding
ssh -X pi@raspberrypi.local
cd rasp-object-detection/rpi5_yolo_whisper
source venv/bin/activate
python gui_detector.py
```

**Solution 3 - Install tkinter:**
```bash
sudo apt-get install python3-tk
```

### Problem: Camera not detected

**🔍 Run Diagnostics First:**
```bash
./diagnose_camera.sh
```
This script will automatically check everything and tell you exactly what's wrong!

**Manual Checks for Pi Camera:**
```bash
# Check if camera is detected
vcgencmd get_camera
# Should show: supported=1 detected=1

# Test camera (use rpicam-* for newer OS, libcamera-* for older)
rpicam-hello --timeout 2000
# or: libcamera-hello --timeout 2000

# Check camera interface is enabled
sudo raspi-config
# Go to: Interface Options → Camera → Enable
```

**Common Pi Camera Issues:**

1. **Camera not detected (supported=0 detected=0)**
   - Ribbon cable not properly connected
   - Check: Blue side faces camera module, contacts face connectors
   - Make sure cable is fully inserted into both connectors

2. **Camera supported but not detected (supported=1 detected=0)**
   ```bash
   # Enable camera interface
   sudo raspi-config
   # Interface Options → Camera → Enable
   sudo reboot
   ```

3. **picamera2 not installed**
   ```bash
   sudo apt-get update
   sudo apt-get install python3-picamera2
   # Or try system-wide install
   pip install picamera2
   ```

**For USB camera users:**
```bash
# Check USB camera
ls /dev/video*
# Should show: /dev/video0

# Change to USB in .env
nano .env
# Set: CAMERA_TYPE=usb
```

### Problem: No voice output

**Test audio:**
```bash
# Check speakers
aplay -l

# Test TTS
source venv/bin/activate
python -c "from offline_tts import TextToSpeech; tts = TextToSpeech(); tts.speak('Testing audio')"
```

**Install audio dependencies:**
```bash
sudo apt-get install espeak espeak-data libespeak-dev
pip install pyttsx3 --force-reinstall
```

### Problem: Slow performance

**Optimize settings:**

1. **Lower resolution:**
   ```env
   CAMERA_WIDTH=320
   CAMERA_HEIGHT=240
   ```

2. **Increase confidence:**
   ```env
   YOLO_CONFIDENCE=0.7
   ```

3. **Close other applications**

4. **Optimize Pi Camera settings** (adjust resolution and frame rate)

### Problem: Import errors

**Reinstall dependencies:**
```bash
source venv/bin/activate
pip install -r requirements_rpi5.txt
```

---

## 📱 Alternative: Voice-Activated Version

If GUI isn't working or you prefer headless operation:

```bash
source venv/bin/activate
python main_rpi5.py
```

**Usage:**
1. Say "IRIS" (wake word)
2. Say "What do you see?"
3. Listen to detection results

---

## 🚀 Running on Startup (Optional)

### Create Launcher Script

```bash
nano ~/start_gui_detector.sh
```

Add:
```bash
#!/bin/bash
cd ~/rasp-object-detection/rpi5_yolo_whisper
source venv/bin/activate
python gui_detector.py
```

Make executable:
```bash
chmod +x ~/start_gui_detector.sh
```

### Add to Autostart

```bash
mkdir -p ~/.config/autostart
nano ~/.config/autostart/object-detector.desktop
```

Add:
```
[Desktop Entry]
Type=Application
Name=Object Detector
Exec=/home/pi/start_gui_detector.sh
Terminal=false
```

**Note:** This will auto-start when you boot to desktop.

---

## 🎯 Quick Reference

### Every Time You Want to Run

```bash
cd ~/rasp-object-detection/rpi5_yolo_whisper
source venv/bin/activate
python gui_detector.py
```

### Update from GitHub

```bash
cd ~/rasp-object-detection
git pull origin main
```

### Stop Detection

- Click "❌ Quit" button, or
- Press `Ctrl+C` in terminal

---

## 📊 Performance Tips

### For Best Results:

✅ **Good lighting** - Natural daylight is best
✅ **Clean background** - Less clutter = better detection
✅ **Stable camera** - Mount or place on steady surface
✅ **Close other apps** - Free up Pi's resources
✅ **Pi Camera V2/V3** - Works great with Raspberry Pi 5

### Expected Performance:

| Configuration | FPS | Quality |
|--------------|-----|---------|
| 640x480, conf=0.5 | 10-15 | Good |
| 320x240, conf=0.7 | 15-25 | Fast |
| 640x480, conf=0.3 | 5-10 | Slow but sensitive |

---

## 🆘 Need More Help?

### Documentation Files:
- `GUI_README.md` - GUI-specific help
- `README_RPI5.md` - Full documentation
- `QUICKSTART.md` - Quick setup guide

### Test Individual Components:
```bash
source venv/bin/activate

# Test YOLO
python -c "from yolo_detector import YOLODetector; d = YOLODetector(); print('Camera:', d.cap is not None)"

# Test TTS
python -c "from offline_tts import TextToSpeech; TextToSpeech().speak('Hello')"

# Test camera capture
python -c "from yolo_detector import YOLODetector; import cv2; d = YOLODetector(); f = d.capture_frame(); print('Frame:', f is not None)"
```

---

## ✅ Success Checklist

After setup, you should be able to:

- [ ] Open GUI window
- [ ] See live camera feed
- [ ] Click "Start Detection" 
- [ ] See bounding boxes around objects
- [ ] Hear voice announcements
- [ ] Adjust confidence slider
- [ ] Get smooth performance (5+ FPS)

If all checked, you're ready to go! 🎉

---

**🎊 Congratulations! Your Raspberry Pi object detector is ready!**
