# 🎯 GUI Object Detector - Quick Start

## Real-Time Object Detection with Voice Announcements

This is the **GUI version** of the object detector - perfect for visual feedback and easy control!

## ✨ Features

- 📹 **Live camera feed** with real-time object detection
- 🎯 **Bounding boxes** around detected objects
- 🔊 **Automatic voice announcements** when new objects appear
- 🎚️ **Adjustable confidence threshold** via slider
- 📊 **Live statistics** (FPS, object count)
- 🖱️ **Simple controls** - just click buttons

## 🚀 How to Run

### On Raspberry Pi 5

```bash
cd ~/rasp-object-detection/rpi5_yolo_whisper
source venv/bin/activate
python gui_detector.py
```

### First Time?

If you haven't set up yet, run:
```bash
chmod +x install_rpi5.sh
./install_rpi5.sh
```

## 🎮 Using the GUI

### Main Controls

1. **▶ Start Detection** - Begin real-time detection
2. **⏸ Stop Detection** - Pause detection  
3. **🔊 Announce Now** - Manually trigger voice announcement
4. **❌ Quit** - Close the application

### Settings

- **Confidence Slider**: Adjust from 0.1 (more sensitive) to 0.9 (more strict)
- **Auto-announce checkbox**: Toggle automatic announcements on/off

### Display Areas

- **Camera Feed**: Shows live video with bounding boxes
- **Detection Info**: Lists detected objects with counts
- **Status Bar**: Shows current state and FPS

## 🎤 Voice Announcements

The system automatically announces:
- When **new objects** appear in the frame
- Format: "I see 2 persons, 1 chair, 1 bottle"

**Cooldown**: 3 seconds between auto-announcements (prevents spam)

**Manual Announce**: Click "🔊 Announce Now" anytime to hear current objects

## ⚙️ Configuration

Edit `.env` file to customize:

```env
# Detection sensitivity
YOLO_CONFIDENCE=0.5  # Lower = more detections, Higher = only confident detections

# Camera
CAMERA_TYPE=usb      # or 'picamera' for Pi Camera
CAMERA_INDEX=0       # Usually 0 for first camera

# Voice settings
TTS_RATE=150         # Speech speed (100-200)
TTS_VOLUME=1.0       # Volume (0.0-1.0)
```

## 🔧 Troubleshooting

### GUI doesn't show up

**Raspberry Pi:**
```bash
# Make sure you're running on the Pi desktop (not SSH without X11)
export DISPLAY=:0
python gui_detector.py
```

**SSH Users:**
```bash
# Enable X11 forwarding
ssh -X pi@raspberrypi.local
python gui_detector.py
```

### Camera not working

```bash
# Check camera connection
vcgencmd get_camera      # For Pi Camera
ls /dev/video*           # For USB Camera

# Try switching camera type in .env
CAMERA_TYPE=usb          # or 'picamera'
```

### No voice output

```bash
# Test TTS
python -c "from offline_tts import TextToSpeech; tts = TextToSpeech(); tts.speak('Test')"

# Check audio output
aplay -l
```

### Slow performance

1. **Lower resolution** in `.env`:
   ```env
   CAMERA_WIDTH=320
   CAMERA_HEIGHT=240
   ```

2. **Increase confidence** (fewer detections):
   ```env
   YOLO_CONFIDENCE=0.7
   ```

3. **Close other applications** to free up resources

### "Import tkinter" error

```bash
# Install tkinter
sudo apt-get install python3-tk

# Reactivate environment and try again
source venv/bin/activate
python gui_detector.py
```

## 📝 Tips & Tricks

### Better Detection

- **Good lighting** improves accuracy
- **Position camera** at chest height for best results
- **Reduce clutter** in frame for cleaner detections
- **Adjust confidence** slider based on environment

### Voice Announcements

- **Disable auto-announce** if you only want manual announcements
- **Increase cooldown** in code if announcements are too frequent:
  ```python
  self.announcement_cooldown = 5.0  # 5 seconds
  ```

### Performance

- **Lower confidence** = slower (more objects to process)
- **Higher resolution** = slower but more accurate
- **USB camera** typically faster than Pi Camera on Raspberry Pi 5

## 🆚 GUI vs Voice-Activated Version

| Feature | GUI Version | Voice Version |
|---------|-------------|---------------|
| Visual feedback | ✅ Live video | ❌ No display |
| Ease of use | ✅ Simple buttons | ⚠️ Voice commands |
| Continuous detection | ✅ Yes | ❌ On-demand only |
| Setup complexity | ✅ Easy | ⚠️ Requires mic setup |
| Headless operation | ❌ Needs display | ✅ Works via SSH |
| Resource usage | ⚠️ Higher (GUI) | ✅ Lower |

**Recommendation**: Use GUI version for **visual assistance** and **testing**. Use voice version for **hands-free** operation.

## 🎓 Understanding Detection

### Confidence Score

- **0.9**: Very strict - only super confident detections
- **0.7**: Balanced - good for general use
- **0.5**: Default - catches most objects
- **0.3**: Sensitive - may have false positives

### Object Classes

YOLO11n can detect 80 object classes including:
- People, vehicles, animals
- Furniture, electronics
- Food items, sports equipment
- And more!

### Bounding Box Colors

- **Green boxes**: Detected objects
- **Label**: Shows class name and confidence score

## 🚀 Advanced Usage

### Running on Startup

Create a launcher script:
```bash
nano ~/start_detector.sh
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
chmod +x ~/start_detector.sh
```

Add to autostart:
```bash
nano ~/.config/autostart/detector.desktop
```

Add:
```
[Desktop Entry]
Type=Application
Name=Object Detector
Exec=/home/pi/start_detector.sh
```

### Custom Announcements

Edit `gui_detector.py` to customize announcement format:

```python
def announce_objects(self, results=None):
    # Custom announcement format
    announcement = f"Found {results['count']} items: {results['summary']}"
```

## 📞 Need Help?

Check the main README files:
- `README_RPI5.md` - Full documentation
- `QUICKSTART.md` - Setup guide
- `PROJECT_SUMMARY.md` - Technical overview

---

**Enjoy your object detector! 🎉**
