# 🤖 Raspberry Pi Voice-Activated Object Detection

Voice-controlled object detection system with GUI for Raspberry Pi 5. Access via TigerVNC from PC or phone.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi%205-red)
![License](https://img.shields.io/badge/License-MIT-green)

## 🎯 Features

- 🎤 **Voice Activation** - Say "IRIS" to activate
- 🖥️ **Live Video GUI** - Real-time camera feed with bounding boxes
- 📱 **Remote Access** - Access via TigerVNC from any device
- 🎯 **Object Detection** - YOLO11n optimized for Raspberry Pi
- 🗣️ **Voice Response** - Describes detected objects
- 🔌 **Fully Offline** - No internet required after setup

## 📸 Demo

```
┌─────────────────────────────────────────────────────────┐
│ Voice-Activated Object Detection        FPS: 20        │
│ Status: Listening for 'IRIS'...       [🔴 LISTENING]  │
├─────────────────────────────────────────────┬───────────┤
│         [Person] 87%                        │Detections:│
│           ┌──────────┐                      │Total: 3   │
│           │  Person  │                      │           │
│           └──────────┘                      │person: 1  │
│    [Chair] 92%  [Chair] 85%                │chair: 2   │
│       ┌────┐       ┌────┐                  │           │
│       └────┘       └────┘                  │Summary:   │
│                                             │"I see one │
│         LIVE CAMERA FEED                    │ person    │
│                                             │ and two   │
│                                             │ chairs."  │
└─────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### 1. Clone Repository

```bash
cd ~
git clone https://github.com/Aniket-1149/rasp-object-detection.git
cd rasp-object-detection/rpi5_yolo_whisper
```

### 2. Run Installation

```bash
chmod +x install_rpi5.sh
./install_rpi5.sh
```

### 3. Setup TigerVNC

```bash
sudo apt-get install tigervnc-standalone-server
vncpasswd
vncserver :1 -geometry 1280x720 -depth 24
```

### 4. Run GUI Application

```bash
source venv/bin/activate
export DISPLAY=:1
python main_gui.py
```

### 5. Connect from PC/Phone

1. Install VNC Viewer
2. Connect to `<raspberry-pi-ip>:5901`
3. Enter VNC password
4. Enjoy!

## 📖 Documentation

- **[SETUP_WITH_VNC.md](rpi5_yolo_whisper/SETUP_WITH_VNC.md)** - ⭐ Quick setup (VNC already configured)
- **[RASPBERRY_PI_SETUP.md](rpi5_yolo_whisper/RASPBERRY_PI_SETUP.md)** - Complete setup from scratch
- **[TIGERVNC_SETUP.md](rpi5_yolo_whisper/TIGERVNC_SETUP.md)** - Detailed VNC configuration
- **[README_RPI5.md](rpi5_yolo_whisper/README_RPI5.md)** - Full documentation
- **[QUICKSTART.md](rpi5_yolo_whisper/QUICKSTART.md)** - Quick reference

## 🎮 Usage

### Voice Commands

1. Say **"IRIS"** to activate
2. Say commands like:
   - "What do you see?"
   - "Detect objects"
   - "How many objects?"

### Keyboard Controls

- `Q` - Quit
- `D` - Detect objects now
- `S` - Save screenshot

## 🛠️ Requirements

- **Hardware:**
  - Raspberry Pi 5 (4GB+ RAM)
  - Pi Camera or USB Webcam
  - USB Microphone
  - Speaker/Headphones

- **Software:**
  - Raspberry Pi OS (64-bit)
  - Python 3.11+
  - TigerVNC Server

## ⚙️ Configuration

Edit `.env` to customize:

```env
# Wake word
WAKE_WORD=iris

# Camera
CAMERA_TYPE=usb          # or 'picamera'

# Performance
WHISPER_MODEL=small      # tiny, small, or base
YOLO_CONFIDENCE=0.5      # 0.0 to 1.0
```

## 📊 Performance

| Metric | Raspberry Pi 5 |
|--------|----------------|
| Video FPS | 15-25 |
| Detection Time | 0.5-1s |
| Response Time | 5-7s |

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - see LICENSE file for details

## 👤 Author

**Aniket-1149**
- GitHub: [@Aniket-1149](https://github.com/Aniket-1149)
- Repository: [rasp-object-detection](https://github.com/Aniket-1149/rasp-object-detection)

## 🙏 Acknowledgments

- [Ultralytics YOLO](https://github.com/ultralytics/ultralytics) - Object detection
- [OpenAI Whisper](https://github.com/openai/whisper) - Speech recognition
- [Faster-Whisper](https://github.com/guillaumekln/faster-whisper) - Optimized inference
- [pyttsx3](https://github.com/nateshmbhat/pyttsx3) - Text-to-speech

---

⭐ Star this repo if you find it useful!
