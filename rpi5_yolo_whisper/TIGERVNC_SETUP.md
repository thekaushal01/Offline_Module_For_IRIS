# 🖥️ TigerVNC GUI Setup Guide

Complete guide for running the Voice-Activated Object Detection GUI via TigerVNC on Raspberry Pi 5.

---

## 📋 Prerequisites

- Raspberry Pi 5 (4GB+ RAM recommended)
- Raspberry Pi Camera or USB Webcam
- USB Microphone
- Speakers or headphones
- Internet connection (for initial setup)
- PC/Phone with VNC Viewer installed

---

## 🚀 Quick Setup

### Step 1: Clone Repository on Raspberry Pi

```bash
cd ~
git clone https://github.com/Aniket-1149/rasp-object-detection.git
cd rasp-object-detection/rpi5_yolo_whisper
```

### Step 2: Run Installation

```bash
chmod +x install_rpi5.sh
./install_rpi5.sh
```

**⏱️ This takes ~15-20 minutes**

### Step 3: Install and Configure TigerVNC

```bash
# Install TigerVNC server
sudo apt-get update
sudo apt-get install -y tigervnc-standalone-server tigervnc-common

# Install desktop environment (if not already installed)
sudo apt-get install -y lxde-core lightdm

# Set VNC password
vncpasswd
# Enter password (e.g., "raspberry")
# View-only password: n

# Create VNC startup script
mkdir -p ~/.vnc
nano ~/.vnc/xstartup
```

Add this content to `xstartup`:
```bash
#!/bin/sh
unset SESSION_MANAGER
unset DBUS_SESSION_BUS_ADDRESS
exec startlxde
```

Make it executable:
```bash
chmod +x ~/.vnc/xstartup
```

### Step 4: Start VNC Server

```bash
# Start VNC on display :1 with 1280x720 resolution
vncserver :1 -geometry 1280x720 -depth 24

# To start on boot (optional)
sudo nano /etc/systemd/system/vncserver@.service
```

Add this content:
```ini
[Unit]
Description=Remote desktop service (VNC)
After=syslog.target network.target

[Service]
Type=simple
User=pi
PAMName=login
PIDFile=/home/pi/.vnc/%H:%i.pid
ExecStartPre=/bin/sh -c '/usr/bin/vncserver -kill :%i > /dev/null 2>&1 || :'
ExecStart=/usr/bin/vncserver :%i -geometry 1280x720 -depth 24 -localhost no
ExecStop=/usr/bin/vncserver -kill :%i

[Install]
WantedBy=multi-user.target
```

Enable service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable vncserver@1.service
sudo systemctl start vncserver@1.service
```

### Step 5: Connect from Your Device

#### On Windows PC:
1. Download [RealVNC Viewer](https://www.realvnc.com/en/connect/download/viewer/) or [TigerVNC Viewer](https://tigervnc.org/)
2. Open VNC Viewer
3. Enter: `<raspberry-pi-ip>:5901`
   - Find Pi IP: `hostname -I` on Pi
   - Example: `192.168.1.100:5901`
4. Enter the password you set with `vncpasswd`

#### On Android/iOS Phone:
1. Install **VNC Viewer** from app store
2. Add new connection: `<raspberry-pi-ip>:5901`
3. Connect and enter password

### Step 6: Run GUI Application

In the VNC session terminal:

```bash
cd ~/rasp-object-detection/rpi5_yolo_whisper
source venv/bin/activate
export DISPLAY=:1
python main_gui.py
```

---

## 🎮 Using the GUI

### Interface Overview

```
┌─────────────────────────────────────────────────────────┐
│ Voice-Activated Object Detection        FPS: 15        │
│ Status: Listening for 'IRIS'...                        │
├─────────────────────────────────────────────┬───────────┤
│                                             │           │
│                                             │Detections:│
│         LIVE CAMERA FEED                    │Total: 3   │
│       with bounding boxes                   │           │
│                                             │person: 1  │
│                                             │chair: 2   │
│                                             │           │
│                                             │           │
├─────────────────────────────────────────────┴───────────┤
│ Say 'IRIS' to activate                                  │
│ Then say: 'What do you see?' or 'Detect objects'       │
│ Press 'Q' to quit | 'D' to detect | 'S' to save        │
└─────────────────────────────────────────────────────────┘
```

### Voice Commands

1. **Say "IRIS"** (or your configured wake word)
   - Red indicator appears when listening
   - System responds: "Yes?"

2. **Say your command:**
   - "What do you see?"
   - "Detect objects"
   - "How many objects?"
   - "What's there?"

3. **Listen to response**
   - Objects are detected and labeled on screen
   - System speaks the detection summary
   - Results shown in right panel

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Q` | Quit application |
| `D` | Detect objects immediately (without voice) |
| `S` | Save current frame with detections |

### Visual Indicators

- 🔴 **Red dot** (top right): Voice activated, listening for command
- 🟢 **Green text** (top): Ready status
- 📦 **Colored boxes**: Detected objects with labels and confidence %
- 📊 **Right panel**: List of detected objects with counts

---

## ⚙️ Configuration

Edit `.env` file to customize:

```bash
nano .env
```

### Camera Settings

```env
# For Raspberry Pi Camera Module
CAMERA_TYPE=picamera

# For USB Webcam
CAMERA_TYPE=usb
CAMERA_INDEX=0

# Resolution (lower = faster)
CAMERA_WIDTH=640
CAMERA_HEIGHT=480
```

### Wake Word

```env
WAKE_WORD=iris              # Change to any word
WAKE_WORD_THRESHOLD=0.6     # Lower = more sensitive
```

### Detection Settings

```env
YOLO_CONFIDENCE=0.5         # Lower = more detections
WHISPER_MODEL=small         # Options: tiny, small, base
```

### Performance Tuning

For **faster performance**:
```env
WHISPER_MODEL=tiny
CAMERA_WIDTH=320
CAMERA_HEIGHT=240
YOLO_CONFIDENCE=0.6
```

For **better accuracy**:
```env
WHISPER_MODEL=base
CAMERA_WIDTH=640
CAMERA_HEIGHT=480
YOLO_CONFIDENCE=0.4
```

---

## 🔧 Troubleshooting

### VNC Connection Issues

```bash
# Check VNC is running
ps aux | grep vnc

# Restart VNC
vncserver -kill :1
vncserver :1 -geometry 1280x720 -depth 24

# Check firewall
sudo ufw allow 5901
```

### GUI Doesn't Appear

```bash
# Set display before running
export DISPLAY=:1
python main_gui.py

# Check X server
echo $DISPLAY
xdpyinfo
```

### Camera Not Working

```bash
# Enable camera interface
sudo raspi-config
# Interface Options → Camera → Enable

# Test Pi Camera
libcamera-hello

# Test USB Camera
ls /dev/video*
v4l2-ctl --list-devices
```

### No Audio / Microphone Issues

```bash
# List audio devices
arecord -l    # Microphone
aplay -l      # Speaker

# Test microphone
arecord -d 3 test.wav
aplay test.wav

# Set default device
sudo nano /etc/asound.conf
```

Example `/etc/asound.conf`:
```
pcm.!default {
    type hw
    card 1
}
ctl.!default {
    type hw
    card 1
}
```

### Low FPS / Slow Performance

1. **Lower camera resolution:**
   ```env
   CAMERA_WIDTH=320
   CAMERA_HEIGHT=240
   ```

2. **Use smaller Whisper model:**
   ```env
   WHISPER_MODEL=tiny
   ```

3. **Increase confidence threshold:**
   ```env
   YOLO_CONFIDENCE=0.6
   ```

4. **Close other applications** in VNC session

### Memory Issues

```bash
# Check memory
free -h

# Increase swap
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Set: CONF_SWAPSIZE=2048
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

---

## 🎯 Performance Expectations

### With TigerVNC on Raspberry Pi 5

| Component | Time | FPS |
|-----------|------|-----|
| Live Video Feed | - | 15-25 FPS |
| Wake Word Detection | ~0.5s | - |
| Speech Recognition | ~3-4s | - |
| Object Detection | ~0.5-1s | - |
| GUI Update | - | 15-25 FPS |

**Total Response Time:** ~5-7 seconds from wake word to spoken response

---

## 📱 Remote Access from Phone

### Setup for Mobile

1. **Install VNC Viewer** from:
   - Google Play Store (Android)
   - App Store (iOS)

2. **Add connection:**
   - Address: `<raspberry-pi-ip>:5901`
   - Name: "Raspberry Pi Object Detection"

3. **Connect and use:**
   - Touch to interact with GUI
   - Use keyboard shortcuts via on-screen keyboard
   - Voice commands work through Pi's microphone

### Tips for Mobile Usage

- Use **landscape orientation** for better view
- **Pinch to zoom** if needed
- Enable **full screen** mode in VNC app
- Consider using **Bluetooth speaker** for better audio

---

## 🔄 Starting Application After Reboot

```bash
# Connect via VNC first, then in terminal:
cd ~/rasp-object-detection/rpi5_yolo_whisper
source venv/bin/activate
export DISPLAY=:1
python main_gui.py
```

### Auto-start on Boot (Optional)

Create systemd service:

```bash
sudo nano /etc/systemd/system/object-detection-gui.service
```

Add:
```ini
[Unit]
Description=Voice-Activated Object Detection GUI
After=network.target vncserver@1.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/rasp-object-detection/rpi5_yolo_whisper
Environment="DISPLAY=:1"
ExecStart=/home/pi/rasp-object-detection/rpi5_yolo_whisper/venv/bin/python main_gui.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl daemon-reload
sudo systemctl enable object-detection-gui.service
sudo systemctl start object-detection-gui.service
```

---

## 💡 Tips & Best Practices

1. **Network Performance:**
   - Use wired Ethernet for better VNC performance
   - WiFi works but may have slight lag

2. **Voice Recognition:**
   - Speak clearly and at normal volume
   - Wait for "Yes?" confirmation before giving command
   - Reduce background noise for better accuracy

3. **Object Detection:**
   - Ensure good lighting for camera
   - Objects should be clearly visible
   - Camera should be stable (not moving)

4. **Resource Management:**
   - Close unused applications
   - Monitor temperature: `vcgencmd measure_temp`
   - Use cooling fan if available

5. **Security:**
   - Change default VNC password
   - Use VNC over SSH tunnel for remote access
   - Keep system updated: `sudo apt-get update && sudo apt-get upgrade`

---

## 🆘 Getting Help

If issues persist:

1. **Check logs:**
   ```bash
   # Application logs in terminal
   # VNC logs:
   cat ~/.vnc/*.log
   ```

2. **Test components individually:**
   ```bash
   source venv/bin/activate
   python -c "from yolo_detector import YOLODetector; print('✅ YOLO OK')"
   python -c "from whisper_stt import WhisperRecognizer; print('✅ Whisper OK')"
   python -c "from offline_tts import TextToSpeech; print('✅ TTS OK')"
   ```

3. **Check system resources:**
   ```bash
   top
   free -h
   df -h
   ```

---

## 🎉 Success!

You should now have a fully functional voice-activated object detection system with a beautiful GUI accessible via TigerVNC from your PC or phone!

Enjoy detecting objects! 🚀
