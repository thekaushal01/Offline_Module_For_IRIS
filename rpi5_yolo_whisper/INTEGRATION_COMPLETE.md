# 🎯 Sensor Integration Complete - Ready to Use!

## ✅ What's Integrated

Your `gui_mobile_detector.py` now includes:

1. **HC-SR04 Ultrasonic Sensor** (lgpio for Pi 5)
   - Continuous distance monitoring at 5Hz
   - Combined with YOLO detections: "person at 2.3 feet"
   - Automatic announcements for objects < 6 feet

2. **MPU9250 Fall Detection** (I2C via smbus2)
   - 50Hz sampling rate
   - Multi-stage state machine
   - TTS alerts + visual GUI warnings
   - Critical events for app/SMTP

3. **Event System**
   - JSON event log: `/tmp/iris_events.jsonl`
   - Events: `distance_detection`, `fall_detected`
   - Ready for app to monitor and send SMTP alerts

---

## 🚀 Quick Start

### 1. Pull Latest Code

```bash
cd ~/rasp-object-detection
git pull origin main
cd rpi5_yolo_whisper
source venv/bin/activate
```

### 2. Install lgpio (if not already done)

```bash
sudo apt-get install -y python3-lgpio
pip install lgpio smbus2
```

### 3. Run the Integrated GUI

```bash
python gui_mobile_detector.py
```

**What happens:**
- ✅ GUI starts with camera feed
- ✅ YOLO object detection ready
- ✅ Voice commands ("IRIS detect", "IRIS stop")
- ✅ Ultrasonic distance monitoring in background
- ✅ Fall detection monitoring in background
- ✅ Combined announcements: "person at 2.5 feet"

---

## 📊 How It Works

### Distance + Object Detection

```
User walks toward camera
├── YOLO detects: "person" (confidence 0.87)
├── Ultrasonic measures: 2.3 feet
└── TTS announces: "person at 2.3 feet"
```

### Fall Detection

```
User falls
├── MPU9250 detects: freefall → impact → lying
├── FallDetector confirms: true fall (not false alarm)
├── GUI shows: 🚨 FALL DETECTED! (red alert)
├── TTS announces: "Warning, fall detected"
└── Event emitted: /tmp/iris_events.jsonl
    └── App reads event → sends SMTP alert
```

### Event Flow to App

```json
// /tmp/iris_events.jsonl
{"timestamp": 1733349234.5, "event": "distance_detection", "payload": {"object": "person", "distance_feet": 2.3, "description": "Obstacle at 2.3 feet"}}
{"timestamp": 1733349567.8, "event": "fall_detected", "payload": {"severity": "critical", "timestamp": 1733349567.8}}
```

Your app can:
- `tail -f /tmp/iris_events.jsonl` to monitor events
- Parse JSON and send SMTP on `"event": "fall_detected"`
- Filter by `"severity": "critical"` for urgent alerts

---

## 🎛️ Configuration (.env)

All sensor settings are in `.env`:

```bash
# Ultrasonic Sensor
ULTRASONIC_ENABLED=true
ULTRASONIC_TRIG_PIN=23
ULTRASONIC_ECHO_PIN=24
ULTRASONIC_ANNOUNCE_THRESHOLD=6.0  # Only announce objects < 6 feet

# Fall Detection
FALL_DETECTION_ENABLED=true
MPU9250_ADDRESS=0x68
FALL_IMPACT_THRESHOLD=2.5  # g-force
FALL_ROTATION_THRESHOLD=150  # degrees/second

# Events
EVENT_FILE=/tmp/iris_events.jsonl
```

**Tuning tips:**
- Increase `ULTRASONIC_ANNOUNCE_THRESHOLD` to 10.0 for more announcements
- Decrease `FALL_IMPACT_THRESHOLD` to 2.0 if falls not detected
- Increase `FALL_IMPACT_THRESHOLD` to 3.0 if too many false positives

---

## 🧪 Testing

### Test Distance Announcements

1. Start GUI: `python gui_mobile_detector.py`
2. Say: **"IRIS detect"** to start detection
3. Wave hand in front of ultrasonic sensor
4. Should hear: "hand at X feet" or "person at X feet"

### Test Fall Detection

1. GUI running with sensors active
2. Pick up MPU9250 (gently!)
3. Drop it onto soft surface (pillow)
4. Should see: 🚨 FALL DETECTED! in GUI
5. Should hear: "Warning, fall detected"
6. Check event: `tail -f /tmp/iris_events.jsonl`

### Test Event System

```bash
# Terminal 1: Run GUI
python gui_mobile_detector.py

# Terminal 2: Monitor events
tail -f /tmp/iris_events.jsonl

# Trigger events and watch them appear in terminal 2
```

---

## 📱 App Integration

### Option 1: File Monitoring (Simplest)

```python
# Your app code
import json
import time

def monitor_events():
    with open('/tmp/iris_events.jsonl', 'r') as f:
        # Seek to end
        f.seek(0, 2)
        
        while True:
            line = f.readline()
            if line:
                event = json.loads(line)
                
                if event['event'] == 'fall_detected':
                    send_smtp_alert(
                        subject="URGENT: Fall Detected",
                        body=f"Fall detected at {event['timestamp']}"
                    )
            else:
                time.sleep(0.1)
```

### Option 2: REST API (Advanced)

Modify `_emit_event()` in gui_mobile_detector.py:

```python
def _emit_event(self, event_type: str, payload: dict):
    """POST events to your app's REST API"""
    import requests
    
    try:
        event = {
            'timestamp': time.time(),
            'event': event_type,
            'payload': payload
        }
        
        # POST to your app
        requests.post(
            'http://YOUR_APP_IP:8080/api/events',
            json=event,
            timeout=2
        )
    except Exception as e:
        logger.error(f"Failed to send event: {e}")
```

### Option 3: MQTT (Most Scalable)

```bash
pip install paho-mqtt
```

```python
# In gui_mobile_detector.py initialization:
import paho.mqtt.client as mqtt

self.mqtt_client = mqtt.Client()
self.mqtt_client.connect("YOUR_MQTT_BROKER", 1883)

# In _emit_event():
def _emit_event(self, event_type: str, payload: dict):
    event = {
        'timestamp': time.time(),
        'event': event_type,
        'payload': payload
    }
    
    self.mqtt_client.publish(
        'iris/events',
        json.dumps(event)
    )
```

---

## 🔧 Troubleshooting

### Sensors Not Initializing

**Check logs:**
```bash
python gui_mobile_detector.py 2>&1 | grep -E "(sensor|fall|ultrasonic)"
```

**Expected output:**
```
INFO - Initializing HC-SR04 ultrasonic sensor...
INFO - ✅ Ultrasonic sensor ready
INFO - Initializing MPU9250 fall detector...
INFO - ✅ Fall detection ready
```

**If sensors fail:**
- Check wiring (see `HARDWARE_SETUP_GUIDE.md`)
- Verify I2C: `sudo i2cdetect -y 1` (should show 0x68)
- Check GPIO permissions: `ls -la /dev/gpiochip*`

### No Distance Announcements

**Possible causes:**
1. **Detection not active** - Say "IRIS detect" first
2. **No objects detected** - YOLO must detect something
3. **Object too far** - Default threshold is 6 feet
4. **Auto-announce off** - Check "Auto Announce" checkbox in GUI

**Fix:**
```bash
# Test ultrasonic standalone
python test_ultrasonic_lgpio.py --duration 10

# If working, issue is integration (check logs)
```

### Fall Not Detecting

**Too sensitive (false positives):**
```bash
# In .env:
FALL_IMPACT_THRESHOLD=3.0  # Increase from 2.5
FALL_ROTATION_THRESHOLD=180  # Increase from 150
```

**Not sensitive enough (missing falls):**
```bash
# In .env:
FALL_IMPACT_THRESHOLD=2.0  # Decrease from 2.5
```

**Calibrate first:**
```bash
python test_mpu9250.py --calibrate
# Keep sensor flat and still for 3 seconds
```

### Events Not Appearing

**Check file permissions:**
```bash
ls -la /tmp/iris_events.jsonl

# If doesn't exist, trigger an event first
# Then check:
cat /tmp/iris_events.jsonl
```

**Monitor in real-time:**
```bash
tail -f /tmp/iris_events.jsonl
# Trigger events (say "IRIS detect", wave hand, drop IMU)
```

---

## 🎯 Next Steps

### 1. Fine-Tune Thresholds

Run for a day and adjust based on:
- Distance announcement frequency (too much/too little?)
- Fall detection accuracy (false positives?)
- Cooldown times (announcements too close together?)

### 2. Set Up App Monitoring

Choose one integration method (file/REST/MQTT) and implement in your app.

**Test flow:**
1. Trigger fall detection
2. Verify event in `/tmp/iris_events.jsonl`
3. Confirm app receives event
4. Verify SMTP alert sent

### 3. Optimize Performance

```bash
# Check CPU usage
top -p $(pgrep -f gui_mobile_detector)

# Expected:
# - YOLO: 20-30% CPU
# - Ultrasonic: <1% CPU
# - Fall detection: 5-8% CPU
# - Total: 25-40% CPU on Pi 5
```

### 4. Deploy to User

**Safety checklist:**
- [ ] Voltage divider on ECHO pin (prevents GPIO damage)
- [ ] MPU9250 on 3.3V not 5V (prevents damage)
- [ ] Fall detection calibrated and tested
- [ ] Distance announcements not too frequent
- [ ] SMTP alerts working from app
- [ ] Battery life acceptable (6+ hours)
- [ ] User trained on voice commands

---

## 📖 Reference

| File | Purpose |
|------|---------|
| `gui_mobile_detector.py` | Main GUI with integrated sensors |
| `ultrasonic_sensor_lgpio.py` | HC-SR04 module for Pi 5 |
| `fall_detector.py` | MPU9250 fall detection |
| `test_ultrasonic_lgpio.py` | Test ultrasonic standalone |
| `test_mpu9250.py` | Test fall detection standalone |
| `.env` | Configuration (pins, thresholds, etc.) |
| `HARDWARE_SETUP_GUIDE.md` | Wiring diagrams |

---

## 🎉 You're All Set!

Your visual assistance system is now fully integrated and ready to use:

- ✅ Object detection with YOLO
- ✅ Distance measurement with ultrasonic
- ✅ Fall detection with IMU
- ✅ Voice control with IRIS
- ✅ Event system for app/SMTP
- ✅ All sensors optimized for Pi 5

**Start the system:**
```bash
python gui_mobile_detector.py
```

**First commands:**
1. Say: **"IRIS detect"**
2. Walk toward camera
3. Hear: "person at X feet"
4. Say: **"IRIS stop"**
5. Done! 🎉
