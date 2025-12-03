# 📋 Quick Reference Cheat Sheet

## 🚀 First Time Setup (One Time Only)

```bash
# 1. Clone repo
cd ~
git clone https://github.com/Aniket-1149/rasp-object-detection.git
cd rasp-object-detection/rpi5_yolo_whisper

# 2. Install (takes 15-20 min)
chmod +x install_rpi5.sh
./install_rpi5.sh

# 3. Run GUI
chmod +x start_gui.sh
./start_gui.sh
```

---

## 🔄 Every Time You Use It

```bash
cd ~/rasp-object-detection/rpi5_yolo_whisper
./start_gui.sh
```

---

## 🎤 Voice Commands

| Say This | What Happens |
|----------|--------------|
| **"IRIS"** | Activates listening (red dot appears) |
| "What do you see?" | Detects and describes objects |
| "Detect objects" | Same as above |
| "How many objects?" | Counts detected objects |

---

## ⌨️ Keyboard Shortcuts

| Key | Action |
|-----|--------|
| **Q** | Quit |
| **D** | Detect now (without voice) |
| **S** | Save screenshot |

---

## ⚙️ Configuration File

```bash
nano .env
```

| Setting | Change For |
|---------|------------|
| `WHISPER_MODEL=tiny` | Faster (less accurate) |
| `WHISPER_MODEL=small` | Balanced ⭐ |
| `WHISPER_MODEL=base` | Accurate (slower) |
| `CAMERA_TYPE=usb` | USB webcam ⭐ |
| `CAMERA_TYPE=picamera` | Pi Camera Module |
| `YOLO_CONFIDENCE=0.5` | Default |
| `YOLO_CONFIDENCE=0.3` | More detections |
| `YOLO_CONFIDENCE=0.7` | Fewer detections |

---

## 🔧 Quick Fixes

### Camera not working
```bash
ls /dev/video*              # Should show /dev/video0
```

### Microphone not working
```bash
arecord -d 3 test.wav       # Record 3 seconds
aplay test.wav              # Play it back
```

### Wake word not detected
```bash
nano .env
# Change: WAKE_WORD_THRESHOLD=0.5
```

### Slow performance
```bash
nano .env
# Change: WHISPER_MODEL=tiny
# Change: CAMERA_WIDTH=320
# Change: CAMERA_HEIGHT=240
```

---

## 📊 Expected Performance

- **FPS:** 15-25
- **Detection:** ~1 second
- **Total response:** 5-7 seconds

---

## 🆘 Emergency Commands

```bash
# Stop all Python processes
pkill -f python

# Restart VNC
vncserver -kill :1
vncserver :1 -geometry 1280x720

# Check temperature
vcgencmd measure_temp

# Check memory
free -h
```

---

## 📁 Important Paths

```bash
# Project location
cd ~/rasp-object-detection/rpi5_yolo_whisper

# Configuration
nano .env

# Logs
# (shown in terminal when running)
```

---

## ✅ Quick Test Checklist

- [ ] Camera feed shows ✅
- [ ] Say "IRIS" → Red dot appears ✅
- [ ] Say "What do you see?" → Detects ✅
- [ ] Bounding boxes appear ✅
- [ ] Hear spoken response ✅
- [ ] Summary shown on right ✅

**All checked?** You're good to go! 🎉

---

## 🔗 Full Documentation

- **Simple:** [SETUP_WITH_VNC.md](SETUP_WITH_VNC.md)
- **Complete:** [RASPBERRY_PI_SETUP.md](RASPBERRY_PI_SETUP.md)
- **Detailed:** [README_RPI5.md](README_RPI5.md)
