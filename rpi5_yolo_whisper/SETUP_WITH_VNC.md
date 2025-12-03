# 🚀 Quick Setup Guide (VNC Already Configured)

Since you already have VNC running, here's the streamlined setup for the GUI application.

---

## 📋 Prerequisites (Already Done ✅)
- ✅ VNC Server running on Raspberry Pi
- ✅ Can connect to Pi via VNC from PC/Phone

---

## 🎯 Setup Steps

### **Step 1: Clone Repository on Raspberry Pi**

In your VNC session terminal:

```bash
cd ~
git clone https://github.com/Aniket-1149/rasp-object-detection.git
cd rasp-object-detection/rpi5_yolo_whisper
```

---

### **Step 2: Run Installation Script**

```bash
chmod +x install_rpi5.sh
./install_rpi5.sh
```

**What it does:**
- ✅ Installs system packages (Python, OpenCV, audio libraries)
- ✅ Creates Python virtual environment
- ✅ Installs Python packages (YOLO, Whisper, etc.)
- ✅ Downloads AI models (YOLO11n + Whisper)
- ✅ Configures camera support

**⏱️ Time:** ~15-20 minutes

**During installation:**
- It will ask: "Do you have Raspberry Pi Camera Module?" 
  - Press `y` if you have Pi Camera
  - Press `n` if you have USB webcam

---

### **Step 3: Configure Camera (If Needed)**

#### **For Raspberry Pi Camera Module:**

Enable camera interface:
```bash
sudo raspi-config
```
Navigate: **Interface Options → Camera → Enable → Reboot**

Edit configuration:
```bash
cd ~/rasp-object-detection/rpi5_yolo_whisper
nano .env
```

Change this line:
```env
CAMERA_TYPE=picamera
```

#### **For USB Webcam:**
No changes needed! Default is already `usb`.

---

### **Step 4: Run GUI Application**

In your VNC session:

```bash
cd ~/rasp-object-detection/rpi5_yolo_whisper
source venv/bin/activate
python main_gui.py
```

**Or use the quick start script:**
```bash
chmod +x start_gui.sh
./start_gui.sh
```

---

## 🎮 Using the GUI

### **Voice Commands**

1. **Say "IRIS"** (the wake word)
   - 🔴 Red indicator appears top-right
   - You'll hear "Yes?"

2. **Say your command:**
   - "What do you see?"
   - "Detect objects"
   - "How many objects?"
   - "What's there?"
   - "What's in front of me?"

3. **Watch and listen:**
   - Objects detected on screen
   - Bounding boxes appear
   - System speaks the results
   - Summary shown in right panel

### **Keyboard Controls**

| Key | Action |
|-----|--------|
| **Q** | Quit application |
| **D** | Detect objects immediately (no voice needed) |
| **S** | Save screenshot with detections |

---

## 🖥️ GUI Layout

```
┌─────────────────────────────────────────────────────────┐
│ Voice-Activated Object Detection        FPS: 20        │
│ Status: Listening for 'IRIS'...       [🔴 LISTENING]  │
├─────────────────────────────────────────────┬───────────┤
│                                             │           │
│         [Person] 87%                        │Detections:│
│           ┌──────────┐                      │Total: 3   │
│           │  Person  │                      │           │
│           └──────────┘                      │person: 1  │
│    [Chair] 92%  [Chair] 85%                │chair: 2   │
│       ┌────┐       ┌────┐                  │           │
│       │    │       │    │                  │Summary:   │
│       └────┘       └────┘                  │           │
│                                             │"I see one │
│         LIVE CAMERA FEED                    │ person    │
│      (Your camera view here)                │ and two   │
│                                             │ chairs."  │
│                                             │           │
├─────────────────────────────────────────────┴───────────┤
│ Say 'IRIS' to activate                                  │
│ Then say: 'What do you see?' or 'Detect objects'       │
│ Press 'Q' to quit | 'D' to detect | 'S' to save        │
└─────────────────────────────────────────────────────────┘
```

---

## ⚙️ Quick Configuration

Edit settings if needed:

```bash
nano .env
```

### **Common Settings:**

```env
# Wake word (change to any word you want)
WAKE_WORD=iris

# Camera type
CAMERA_TYPE=usb          # or 'picamera'

# Detection sensitivity (lower = more detections)
YOLO_CONFIDENCE=0.5

# Whisper model (affects speed vs accuracy)
WHISPER_MODEL=small      # Options: tiny, small, base
```

### **For Better Performance:**
```env
WHISPER_MODEL=tiny       # Faster response
CAMERA_WIDTH=320         # Lower resolution
CAMERA_HEIGHT=240
YOLO_CONFIDENCE=0.6      # Fewer detections
```

### **For Better Accuracy:**
```env
WHISPER_MODEL=base       # More accurate
CAMERA_WIDTH=640         # Higher resolution
CAMERA_HEIGHT=480
YOLO_CONFIDENCE=0.4      # More detections
```

---

## 🔧 Quick Troubleshooting

### **Camera Not Working**

```bash
# Test USB camera
ls /dev/video*           # Should show /dev/video0

# Test Pi Camera
libcamera-hello          # Shows camera preview

# Enable Pi Camera
sudo raspi-config        # Interface Options → Camera → Enable
```

### **No Microphone/Audio**

```bash
# List devices
arecord -l               # Shows microphone
aplay -l                 # Shows speaker

# Test microphone
arecord -d 3 test.wav
aplay test.wav
```

### **Application Won't Start**

```bash
# Check if virtual environment is activated
source venv/bin/activate

# Test components
python -c "from yolo_detector import YOLODetector; print('✅ YOLO OK')"
python -c "from whisper_stt import WhisperRecognizer; print('✅ Whisper OK')"
python -c "from offline_tts import TextToSpeech; print('✅ TTS OK')"
```

### **Low FPS / Slow Performance**

Quick fixes:
```bash
nano .env
```

Change these:
```env
WHISPER_MODEL=tiny
CAMERA_WIDTH=320
CAMERA_HEIGHT=240
```

### **Wake Word Not Detected**

Make sure:
- ✅ Microphone is plugged in and working
- ✅ Speak clearly: "IRIS"
- ✅ Not too far from microphone
- ✅ Minimal background noise

Try adjusting sensitivity:
```bash
nano .env
```
```env
WAKE_WORD_THRESHOLD=0.5    # Lower = more sensitive (try 0.4 or 0.5)
```

---

## 🔄 Running After Reboot

Every time you restart your Pi or reconnect via VNC:

```bash
cd ~/rasp-object-detection/rpi5_yolo_whisper
./start_gui.sh
```

That's it! Quick and simple.

---

## 💡 Pro Tips

1. **Use keyboard shortcuts** for quick testing:
   - Press `D` to test detection without voice
   - Press `S` to save interesting detections

2. **Position camera properly:**
   - Good lighting helps detection
   - Stable mount (not moving)
   - Clear view of objects

3. **Voice commands work best when:**
   - Speaking at normal volume
   - Clear pronunciation
   - Waiting for "Yes?" confirmation
   - Quiet environment

4. **Monitor performance:**
   - Check FPS in top-right corner
   - Should be 15-25 FPS on Pi 5
   - If too low, reduce resolution

5. **Check system temperature:**
   ```bash
   vcgencmd measure_temp
   ```
   - Should be under 80°C
   - Use cooling fan if needed

---

## 🎯 Expected Performance

On Raspberry Pi 5 with GUI via VNC:

| Metric | Expected Value |
|--------|----------------|
| **Video FPS** | 15-25 FPS |
| **Detection Time** | 0.5-1 second |
| **Wake Word Response** | ~0.5 seconds |
| **Speech Recognition** | 3-4 seconds |
| **Total Response** | 5-7 seconds |

---

## ✅ Quick Test

After running the GUI:

1. ✅ Can you see the live camera feed?
2. ✅ Say "IRIS" - Does red indicator appear?
3. ✅ Say "What do you see?" - Does it detect?
4. ✅ Do bounding boxes appear on objects?
5. ✅ Do you hear the spoken response?
6. ✅ Is the summary shown in the right panel?

If all YES → **You're all set!** 🎉

If any NO → Check troubleshooting section above

---

## 🆘 Still Need Help?

### Check Logs
The terminal will show detailed logs about what's happening.

### Test Individual Components
```bash
source venv/bin/activate

# Test YOLO
python -c "from yolo_detector import YOLODetector; d = YOLODetector(); print('✅')"

# Test Whisper
python -c "from whisper_stt import WhisperRecognizer; w = WhisperRecognizer(); print('✅')"

# Test TTS
python -c "from offline_tts import TextToSpeech; t = TextToSpeech(); t.speak('Hello'); print('✅')"
```

### Check System Resources
```bash
# Memory usage
free -h

# CPU temperature
vcgencmd measure_temp

# Storage space
df -h
```

---

## 🎉 That's It!

You're ready to use voice-activated object detection with a live GUI!

**Commands to remember:**
- Start: `./start_gui.sh`
- Wake word: **"IRIS"**
- Quit: Press **Q**
- Manual detect: Press **D**

Enjoy! 🚀

---

**Repository:** https://github.com/Aniket-1149/rasp-object-detection  
**Full Documentation:** See README_RPI5.md for more details
