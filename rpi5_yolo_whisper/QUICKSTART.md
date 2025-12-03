# 🚀 Quick Start Guide - Raspberry Pi 5

## For Raspberry Pi 5

### 1. Transfer Files to Raspberry Pi

```bash
# On your PC, compress the folder
cd "d:\whisper rasp"
tar -czf rpi5_yolo_whisper.tar.gz rpi5_yolo_whisper/

# Transfer to Raspberry Pi (replace pi@raspberrypi.local with your Pi's address)
scp rpi5_yolo_whisper.tar.gz pi@raspberrypi.local:~/

# On Raspberry Pi, extract
cd ~
tar -xzf rpi5_yolo_whisper.tar.gz
cd rpi5_yolo_whisper
```

### 2. Run Installation Script

```bash
chmod +x install_rpi5.sh
./install_rpi5.sh
```

This will:
- Install all system dependencies
- Create Python virtual environment
- Install Python packages
- Download AI models (YOLO + Whisper)
- Create configuration file

**Note**: Installation takes ~15-20 minutes on Raspberry Pi 5.

### 3. Configure (Optional)

Edit `.env` to customize settings:

```bash
nano .env
```

Key settings:
- `CAMERA_TYPE=picamera` or `usb`
- `WHISPER_MODEL=small` (or `tiny` for faster, `base` for balance)
- `YOLO_CONFIDENCE=0.5` (lower = more detections)

### 4. Run the App

```bash
source venv/bin/activate
python main_rpi5.py
```

### 5. Use Voice Commands

1. Say **"IRIS"** to activate
2. Say a command:
   - "What do you see?"
   - "Detect objects"
   - "How many objects?"
3. Listen to the response

---

## For Testing on Windows (Current PC)

### Option 1: Quick Test Without YOLO

Since you already have Whisper working, you can test the voice components:

```powershell
cd "d:\whisper rasp\rpi5_yolo_whisper"
..\venv311\Scripts\Activate.ps1
python -c "from offline_wake_word import OfflineWakeWordDetector; print('✅ Wake word OK')"
python -c "from whisper_stt import WhisperRecognizer; print('✅ Whisper OK')"
python -c "from offline_tts import TextToSpeech; print('✅ TTS OK')"
```

### Option 2: Full Test with YOLO

Install YOLO on Windows:

```powershell
cd "d:\whisper rasp\rpi5_yolo_whisper"
..\venv311\Scripts\Activate.ps1
pip install ultralytics
python main_rpi5.py
```

---

## Troubleshooting

### Camera Not Working (Pi)

```bash
# Enable camera in raspi-config
sudo raspi-config
# Interface Options → Camera → Enable

# Test Pi Camera
libcamera-hello

# Test USB Camera
ls /dev/video*
```

### Microphone Issues (Pi)

```bash
# List audio devices
arecord -l

# Test recording
arecord -d 3 test.wav
aplay test.wav

# Set default device
sudo nano /etc/asound.conf
```

### Low Performance (Pi)

Edit `.env`:
```env
WHISPER_MODEL=tiny        # Faster model
YOLO_CONFIDENCE=0.6       # Fewer detections
CAMERA_WIDTH=320          # Lower resolution
CAMERA_HEIGHT=240
```

### Out of Memory (Pi)

```bash
# Increase swap space
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Set: CONF_SWAPSIZE=2048
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

---

## Voice Commands Reference

| Command | Action |
|---------|--------|
| "IRIS" | Wake word - activates listening |
| "What do you see?" | Detect and describe objects |
| "Detect objects" | Run object detection |
| "How many objects?" | Count detected objects |
| "What's there?" | Describe scene |
| "What's in front of me?" | Detect objects in view |

---

## Performance Expectations

### Raspberry Pi 5 (8GB)

| Component | Time |
|-----------|------|
| Wake word detection | ~0.5s per chunk |
| Speech recognition | ~3-4s |
| YOLO detection | ~0.5-1s |
| TTS response | ~1s |
| **Total** | **~5-7s** |

### Windows PC (Testing)

| Component | Time |
|-----------|------|
| Wake word detection | ~0.3s per chunk |
| Speech recognition | ~1-2s |
| YOLO detection | ~0.1-0.3s |
| TTS response | ~0.5s |
| **Total** | **~2-3s** |

---

## File Structure

```
rpi5_yolo_whisper/
├── main_rpi5.py              # Main application
├── yolo_detector.py          # YOLO detection module
├── whisper_stt.py            # Whisper speech-to-text
├── offline_tts.py            # Text-to-speech
├── offline_wake_word.py      # Wake word detector
├── requirements_rpi5.txt     # Python dependencies
├── install_rpi5.sh           # Installation script
├── .env                      # Configuration
├── models/
│   └── yolo11n.pt           # YOLO model
└── README_RPI5.md           # Full documentation
```

---

## Next Steps

1. ✅ Transfer to Raspberry Pi
2. ✅ Run installation script
3. ✅ Test components
4. ✅ Run main app
5. ✅ Say "IRIS" and test!

**Need help?** Check `README_RPI5.md` for detailed documentation.
