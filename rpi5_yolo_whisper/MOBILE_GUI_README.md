# 📱 Mobile-Ready GUI Object Detector

## 🌟 Features

This enhanced GUI is designed for mobile app integration with advanced controls and voice commands.

### ✨ Key Features

- **🎤 Voice Control**: Start/stop detection using voice commands
  - Say "**IRIS DETECT**" to start detection
  - Say "**IRIS STOP**" to stop detection
  
- **🎛️ Advanced Controls**:
  - **Confidence Threshold**: Adjust detection sensitivity (0.1 - 0.9)
  - **NMS IoU Threshold**: Control overlapping box filtering (0.1 - 0.9)
  - **Field of View**: Change camera resolution on the fly
  - **Auto-announce**: Toggle automatic object announcements
  
- **📊 Real-time Statistics**:
  - Live object count
  - FPS (Frames Per Second)
  - Total detections this session
  - Session time tracking
  
- **🎯 Mobile-Ready Design**:
  - Dark theme optimized for various lighting
  - Large touch-friendly buttons
  - Clean, modern interface
  - Ready for mobile app backend integration

---

## 🚀 Quick Start

### Run the Mobile GUI

```bash
cd ~/rasp-object-detection/rpi5_yolo_whisper
source venv/bin/activate
python gui_mobile_detector.py
```

---

## 🎮 How to Use

### Method 1: Voice Control (Recommended)

1. **Click "🎤 Voice Control: OFF"** to enable voice commands
2. Button turns green and says "**🎤 Voice Control: ON**"
3. **Say "IRIS"** (wake word) - GUI will show "Wake word detected!"
4. **Say your command**:
   - **"IRIS DETECT"** or **"IRIS START"** → Starts detection
   - **"IRIS STOP"** → Stops detection
   - **"IRIS WHAT DO YOU SEE"** → Announces current objects

### Method 2: Manual Control

1. **Click "▶ Manual Start"** to begin detection
2. Button changes to **"⏸ Stop Detection"**
3. **Click again** to stop detection

### Method 3: Announce Objects

- **Click "🔊 Announce"** to hear what the camera currently sees
- Works whether detection is running or not

---

## 🎛️ Settings Explained

### Confidence Threshold (0.1 - 0.9)
- **Higher = More accurate** but may miss some objects
- **Lower = Detects more** but may have false positives
- **Default: 0.5** (good balance)
- **Recommended range**: 0.3 - 0.7

### NMS IoU Threshold (0.1 - 0.9)
- Controls how overlapping bounding boxes are filtered
- **Higher = More boxes** (less aggressive filtering)
- **Lower = Fewer boxes** (more aggressive filtering)
- **Default: 0.45**

### Field of View
Choose camera resolution:
- **320x240** - Lowest quality, fastest processing
- **640x480** - Good balance (default)
- **800x600** - Higher quality
- **1280x720** - Best quality, slower processing

⚠️ **Note**: Changing FOV requires restarting the camera (click Stop → Start)

### Auto-announce New Objects
- ✅ **Enabled**: Automatically speaks when new objects appear
- ❌ **Disabled**: Only announces when you click "🔊 Announce"
- **Cooldown**: 3 seconds between announcements

---

## 📊 Understanding the Statistics

### Objects
Current number of objects detected in the latest frame

### FPS (Frames Per Second)
- **15-30 FPS**: Excellent performance
- **10-15 FPS**: Good performance (typical for Pi 5)
- **5-10 FPS**: Acceptable for object detection
- **<5 FPS**: Consider lowering resolution or confidence

### Total Detected
Cumulative count of all objects detected this session

### Session Time
How long the detector has been running (MM:SS format)

---

## 🎤 Voice Commands Guide

### Wake Word
Say **"IRIS"** to activate voice listening

### Available Commands

| Command | Action |
|---------|--------|
| **IRIS DETECT** | Start object detection |
| **IRIS START** | Start object detection |
| **IRIS STOP** | Stop object detection |
| **IRIS WHAT DO YOU SEE** | Announce current objects |

### Voice Control Tips

1. **Speak clearly** and at normal volume
2. **Wait for confirmation** after wake word
3. **Use simple commands** from the list above
4. **Check status bar** for command feedback
5. If command isn't recognized, try again with clearer pronunciation

---

## 🔧 Troubleshooting

### Voice Control Not Working

```bash
# Test microphone
arecord -d 3 test.wav
aplay test.wav

# Check audio devices
python -c "import sounddevice; print(sounddevice.query_devices())"

# Ensure audio packages installed
pip install sounddevice soundfile pyaudio
```

### Camera Not Starting

```bash
# Test camera with rpicam
rpicam-hello -t 0

# Check camera detection
./diagnose_camera.sh

# Verify picamera2 available
python -c "import picamera2; print('OK')"
```

### Low FPS

**Solutions**:
1. Lower Field of View to 320x240
2. Increase Confidence Threshold to 0.6+
3. Close other applications
4. Ensure Pi 5 has adequate cooling

### Import Errors

```bash
# Missing tkinter
sudo apt-get install python3-tk python3-pil.imagetk

# Missing other packages
source venv/bin/activate
pip install -r requirements_rpi5.txt
```

---

## 📱 Mobile App Integration

This GUI is designed to work with a mobile app backend. Here's how:

### REST API Endpoints (To be implemented)

```python
# Get current detection status
GET /api/status
→ {"detecting": true, "objects": [...], "fps": 12.5}

# Start/stop detection
POST /api/detection/start
POST /api/detection/stop

# Get settings
GET /api/settings
→ {"confidence": 0.5, "nms": 0.45, "fov": "640x480"}

# Update settings
POST /api/settings
{"confidence": 0.7, "auto_announce": true}

# Get statistics
GET /api/stats
→ {"total": 150, "session_time": 300, "fps": 12.5}
```

### WebSocket for Real-time Updates

```python
# Connect to WebSocket
ws://raspberry-pi:8000/ws

# Receive real-time detections
{"type": "detection", "objects": [...], "timestamp": ...}

# Receive status updates
{"type": "status", "detecting": true, "fps": 12.5}
```

### Configuration from Mobile App

The mobile app can:
- ✅ Start/stop detection remotely
- ✅ Adjust confidence threshold
- ✅ Change field of view
- ✅ Enable/disable auto-announce
- ✅ Receive real-time detection stream
- ✅ Get live statistics

---

## 🎨 GUI Color Scheme

Designed for accessibility and mobile viewing:

- **Background**: Dark gray (#1e1e1e) - Reduces eye strain
- **Panels**: Medium gray (#2d2d2d) - Clear separation
- **Text**: White (#ffffff) - High contrast
- **Accent**: Blue (#0078d4) - Info buttons
- **Success**: Green (#107c10) - Active states
- **Warning**: Red (#d13438) - Stop/Alert actions
- **Status**: Lime green - Real-time info

---

## 🔒 Security Considerations

When integrating with mobile app:

1. **Use HTTPS** for all API calls
2. **Implement authentication** (API keys, tokens)
3. **Rate limiting** to prevent abuse
4. **Input validation** for all settings
5. **CORS policy** for web access
6. **Secure WebSocket** (WSS) connections

---

## 📝 Configuration File (.env)

```bash
# Camera settings
CAMERA_TYPE=picamera
CAMERA_WIDTH=640
CAMERA_HEIGHT=480

# YOLO settings
YOLO_MODEL=models/yolo11n.pt
YOLO_CONFIDENCE=0.5

# Voice settings
WAKE_WORD=iris
WHISPER_MODEL=small

# TTS settings
TTS_ENGINE=pyttsx3
TTS_RATE=150
TTS_VOLUME=1.0

# Audio settings
SAMPLE_RATE=16000
```

---

## 🆚 Comparison: Simple vs Mobile GUI

| Feature | gui_detector.py | gui_mobile_detector.py |
|---------|----------------|------------------------|
| Voice Commands | ❌ | ✅ IRIS DETECT/STOP |
| Confidence Slider | ✅ | ✅ Enhanced |
| NMS Threshold | ❌ | ✅ |
| Field of View | ❌ | ✅ |
| Statistics | Basic | ✅ Comprehensive |
| Mobile-Ready | ❌ | ✅ |
| API Ready | ❌ | ✅ Structure ready |
| Dark Theme | ❌ | ✅ |
| Session Tracking | ❌ | ✅ |

---

## 🎯 Performance Tips

### For Best FPS on Raspberry Pi 5

1. **Use 640x480 resolution** (default)
2. **Set confidence to 0.5-0.6**
3. **Close unnecessary applications**
4. **Ensure good cooling** (heatsink + fan)
5. **Use Raspberry Pi OS 64-bit**
6. **Keep system updated**

### Expected FPS

- **Pi 5 4GB**: 10-15 FPS @ 640x480
- **Pi 5 8GB**: 12-18 FPS @ 640x480
- **With GPU acceleration**: 20-25 FPS (future enhancement)

---

## 🐛 Known Issues

1. **Changing FOV requires restart** - Will be fixed in v2
2. **Voice commands English only** - Multi-language coming soon
3. **No GPU acceleration yet** - In development

---

## 🔄 Next Steps

To integrate with mobile app:

1. **Add Flask/FastAPI backend** for REST API
2. **Implement WebSocket** for real-time streaming
3. **Add authentication** for security
4. **Create mobile app** (React Native / Flutter)
5. **Add remote configuration** from mobile
6. **Implement video streaming** to mobile

---

## 📚 Related Files

- **yolo_detector.py** - Core detection logic
- **offline_tts.py** - Text-to-speech engine
- **offline_wake_word.py** - Wake word detection
- **whisper_stt.py** - Speech recognition
- **requirements_rpi5.txt** - Python dependencies
- **.env** - Configuration settings

---

## 💡 Tips for Mobile Integration

### Use Case 1: Home Security
- Run detection continuously
- Mobile app receives alerts when new objects detected
- View live feed from anywhere

### Use Case 2: Smart Assistant
- Voice-controlled object identification
- Mobile app for remote commands
- TTS feedback through Pi's speakers

### Use Case 3: Accessibility
- Help visually impaired users
- Voice announcements of surroundings
- Mobile app for configuration

---

## ✅ Testing Checklist

Before deploying:

- [ ] Voice commands work correctly
- [ ] Camera initializes properly
- [ ] Detection runs smoothly (8+ FPS)
- [ ] TTS announcements clear
- [ ] All buttons functional
- [ ] Settings persist correctly
- [ ] Statistics update in real-time
- [ ] GUI responsive and clean
- [ ] Wake word detection accurate
- [ ] No crashes or errors

---

## 🎉 You're Ready!

Run the mobile-ready GUI:

```bash
python gui_mobile_detector.py
```

Say **"IRIS DETECT"** to start detecting! 🚀

---

**Questions?** Check the main [RASPBERRY_PI_SETUP.md](RASPBERRY_PI_SETUP.md) guide!
