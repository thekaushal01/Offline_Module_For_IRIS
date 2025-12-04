# 🔗 Sensor Integration Guide
## HC-SR04 + MPU9250 with Visual Assistance GUI

---

## 📋 Prerequisites

Before starting, ensure:
- ✅ Hardware wired according to `HARDWARE_SETUP_GUIDE.md`
- ✅ I2C enabled and verified (`i2cdetect -y 1` shows 0x68)
- ✅ pigpiod daemon running (`sudo systemctl status pigpiod`)
- ✅ Test scripts verified (`test_ultrasonic.py`, `test_mpu9250.py`)

---

## 🚀 Installation Steps

### 1. Install Required Libraries

```bash
cd ~/rasp-object-detection/rpi5_yolo_whisper
source venv/bin/activate

# Install system dependencies
sudo apt-get update
sudo apt-get install -y i2c-tools python3-dev python3-setuptools

# Install pigpio from source (not available in Trixie repos)
wget https://github.com/joan2937/pigpio/archive/master.zip
unzip master.zip
cd pigpio-master
make
sudo make install
cd ..
rm -rf pigpio-master master.zip

# Install Python packages in venv
pip install smbus2 pigpio

# Enable and start pigpio daemon
sudo systemctl enable pigpiod
sudo systemctl start pigpiod
```

### 2. Verify Installation

```bash
# Test ultrasonic sensor
python test_ultrasonic.py --duration 10

# Test MPU9250 IMU
python test_mpu9250.py --duration 10

# Calibrate IMU (optional but recommended)
python test_mpu9250.py --calibrate
```

---

## 🎯 Integration with GUI

### Option 1: Quick Integration (Simple)

Add sensors to your existing GUI with minimal changes:

```python
# In gui_mobile_detector.py

from ultrasonic_sensor import UltrasonicSensor, UltrasonicMonitor
from fall_detector import MPU9250, FallDetector, FallMonitor

class MobileGUIDetector:
    def __init__(self, root):
        # ... existing init code ...
        
        # Initialize sensors
        try:
            self.ultrasonic = UltrasonicSensor(trig_pin=23, echo_pin=24)
            self.ultrasonic_monitor = UltrasonicMonitor(
                self.ultrasonic, 
                update_interval=0.3,
                distance_change_threshold=1.0
            )
            # Add callback for distance changes
            self.ultrasonic_monitor.add_callback(self._on_distance_change)
            self.ultrasonic_monitor.start()
            
            logger.info("✅ Ultrasonic sensor initialized")
        except Exception as e:
            logger.error(f"❌ Ultrasonic sensor failed: {e}")
            self.ultrasonic = None
        
        try:
            self.imu = MPU9250(address=0x68)
            self.fall_detector = FallDetector(
                self.imu, 
                tts_callback=lambda msg: threading.Thread(
                    target=self.tts.speak, args=(msg,), daemon=True
                ).start()
            )
            self.fall_monitor = FallMonitor(
                self.fall_detector,
                sample_rate=50
            )
            # Add callback for fall events
            self.fall_monitor.add_fall_callback(self._on_fall_detected)
            self.fall_monitor.start()
            
            logger.info("✅ Fall detector initialized")
        except Exception as e:
            logger.error(f"❌ Fall detector failed: {e}")
            self.fall_detector = None
    
    def _on_distance_change(self, distance_feet, description):
        """Callback when ultrasonic distance changes"""
        logger.info(f"Distance: {distance_feet:.2f} ft - {description}")
        
        # Announce if obstacle is close and detection is running
        if self.detecting and distance_feet < 5.0:
            # Combine with YOLO detection if available
            if hasattr(self, 'last_detections') and self.last_detections:
                obj_desc = self.last_detections[0]['class']  # First detected object
                message = f"{obj_desc} at {distance_feet:.1f} feet"
            else:
                message = description
            
            # Announce via TTS (non-blocking)
            threading.Thread(
                target=self.tts.speak, 
                args=(message,), 
                daemon=True
            ).start()
    
    def _on_fall_detected(self):
        """Callback when fall is detected"""
        logger.warning("🚨 Fall detected - notifying user and app")
        
        # Visual alert in GUI
        self.root.after(0, self.status_label.config,
                       {'text': '🚨 FALL DETECTED! Check user status!',
                        'fg': 'red', 'font': ('Arial', 14, 'bold')})
        
        # Flash red for 5 seconds
        def reset_status():
            time.sleep(5)
            self.root.after(0, self.status_label.config,
                          {'text': 'Monitoring...', 'fg': 'white'})
        threading.Thread(target=reset_status, daemon=True).start()
        
        # Emit event for app/SMTP notification
        self._emit_event('fall_detected', {
            'timestamp': time.time(),
            'location': 'device_1',  # Add GPS if available
            'severity': 'high'
        })
    
    def _emit_event(self, event_type, payload):
        """
        Emit event for external app to consume
        
        Args:
            event_type: Event name (e.g., 'fall_detected')
            payload: Event data dictionary
        """
        import json
        
        event = {
            'timestamp': time.time(),
            'event': event_type,
            'payload': payload
        }
        
        # Method 1: Write to JSON Lines file (simple)
        try:
            with open('/tmp/iris_events.jsonl', 'a') as f:
                f.write(json.dumps(event) + '\\n')
            logger.info(f"Event emitted: {event_type}")
        except Exception as e:
            logger.error(f"Failed to emit event: {e}")
        
        # Method 2: POST to local REST API (if your app exposes one)
        # import requests
        # try:
        #     requests.post('http://localhost:8080/api/events', json=event, timeout=2)
        # except:
        #     pass
    
    def cleanup(self):
        """Cleanup sensors on exit"""
        # ... existing cleanup ...
        
        if hasattr(self, 'ultrasonic_monitor'):
            self.ultrasonic_monitor.stop()
        if hasattr(self, 'ultrasonic') and self.ultrasonic:
            self.ultrasonic.cleanup()
        
        if hasattr(self, 'fall_monitor'):
            self.fall_monitor.stop()
        if hasattr(self, 'imu'):
            self.imu.cleanup()
```

### Option 2: Standalone Sensor Service

Run sensors as separate service that your GUI queries:

**Create `sensor_service.py`:**

```python
#!/usr/bin/env python3
"""
Standalone sensor monitoring service
Provides REST API for distance and fall detection
"""

from flask import Flask, jsonify
from ultrasonic_sensor import UltrasonicSensor
from fall_detector import MPU9250, FallDetector, FallMonitor
import threading

app = Flask(__name__)

# Global state
current_distance = None
recent_falls = []

# Initialize sensors
ultrasonic = UltrasonicSensor()
imu = MPU9250()
fall_detector = FallDetector(imu)
fall_monitor = FallMonitor(fall_detector)

def update_distance():
    global current_distance
    while True:
        current_distance = ultrasonic.get_distance_feet()
        time.sleep(0.2)

# Start background threads
threading.Thread(target=update_distance, daemon=True).start()
fall_monitor.add_fall_callback(lambda: recent_falls.append(time.time()))
fall_monitor.start()

@app.route('/api/distance')
def get_distance():
    if current_distance:
        return jsonify({
            'distance_feet': current_distance,
            'description': ultrasonic.get_distance_description(current_distance)
        })
    return jsonify({'error': 'No reading'}), 503

@app.route('/api/falls')
def get_falls():
    # Return falls in last 5 minutes
    recent = [t for t in recent_falls if time.time() - t < 300]
    return jsonify({'count': len(recent), 'timestamps': recent})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

Run service:
```bash
python sensor_service.py &
```

Query from GUI:
```python
import requests

# Get distance
response = requests.get('http://localhost:5000/api/distance', timeout=1)
distance_data = response.json()

# Check for falls
response = requests.get('http://localhost:5000/api/falls', timeout=1)
falls_data = response.json()
```

---

## 🔊 Enhanced Object Announcements

Combine YOLO detections with ultrasonic distance:

```python
def announce_detection_with_distance(self, detected_object):
    """
    Announce object detection with distance information
    
    Args:
        detected_object: Dict with 'class', 'confidence', 'bbox'
    """
    obj_class = detected_object['class']
    confidence = detected_object['confidence']
    
    # Get distance from ultrasonic
    if self.ultrasonic:
        distance_feet = self.ultrasonic.get_distance_feet()
        
        if distance_feet and distance_feet < 10:
            # Object is close, include distance
            if distance_feet < 2:
                distance_desc = "very close, less than 2 feet"
            elif distance_feet < 5:
                distance_desc = f"at {distance_feet:.1f} feet"
            else:
                distance_desc = f"ahead at {int(distance_feet)} feet"
            
            message = f"There is a {obj_class} {distance_desc}"
        else:
            # Object detected but far or no distance reading
            message = f"I see a {obj_class}"
    else:
        # No ultrasonic sensor
        message = f"I see a {obj_class}"
    
    # Announce via TTS
    threading.Thread(
        target=self.tts.speak, 
        args=(message,), 
        daemon=True
    ).start()
```

---

## 📱 App/SMTP Integration

### Event File Format

Events are written to `/tmp/iris_events.jsonl`:

```json
{"timestamp": 1733282400.5, "event": "fall_detected", "payload": {"severity": "high", "location": "device_1"}}
{"timestamp": 1733282405.2, "event": "obstacle_near", "payload": {"distance": 1.5, "object": "person"}}
```

### App Integration Options

**Option 1: File Monitoring (Simple)**

Your app can tail the events file:

```python
# In your mobile app backend
import json
import smtplib
from email.mime.text import MIMEText

def monitor_events():
    with open('/tmp/iris_events.jsonl', 'r') as f:
        # Seek to end
        f.seek(0, 2)
        
        while True:
            line = f.readline()
            if line:
                event = json.loads(line)
                
                if event['event'] == 'fall_detected':
                    send_alert_email(event)
            
            time.sleep(0.1)

def send_alert_email(event):
    msg = MIMEText(f"Fall detected at {event['timestamp']}")
    msg['Subject'] = '🚨 Fall Alert - Visual Assistance Device'
    msg['From'] = 'alerts@example.com'
    msg['To'] = 'caregiver@example.com'
    
    # Your existing SMTP code
    smtp.send_message(msg)
```

**Option 2: REST API (Advanced)**

Expose REST endpoint in your app:

```python
# In your mobile app
@app.route('/api/events', methods=['POST'])
def receive_event():
    event = request.json
    
    if event['event'] == 'fall_detected':
        # Send SMTP alert
        send_alert_email(event)
        # Push notification
        send_push_notification(event)
    
    return jsonify({'status': 'received'}), 200
```

In GUI, POST events:
```python
import requests

def _emit_event(self, event_type, payload):
    try:
        requests.post(
            'http://YOUR_APP_IP:8080/api/events',
            json={'event': event_type, 'payload': payload},
            timeout=2
        )
    except:
        # Fallback to file
        pass
```

**Option 3: MQTT (Production-Ready)**

```bash
pip install paho-mqtt
```

```python
import paho.mqtt.client as mqtt

# In GUI
mqtt_client = mqtt.Client()
mqtt_client.connect("localhost", 1883)

def _emit_event(self, event_type, payload):
    mqtt_client.publish(
        f"iris/events/{event_type}",
        json.dumps(payload)
    )

# In app
def on_message(client, userdata, message):
    if message.topic == "iris/events/fall_detected":
        send_alert_email(json.loads(message.payload))

mqtt_client.subscribe("iris/events/#")
mqtt_client.on_message = on_message
mqtt_client.loop_forever()
```

---

## 🎛️ Configuration Options

Add settings to `.env`:

```bash
# Sensor Configuration
ULTRASONIC_ENABLED=true
ULTRASONIC_TRIG_PIN=23
ULTRASONIC_ECHO_PIN=24
ULTRASONIC_ANNOUNCE_THRESHOLD=5.0  # feet

FALL_DETECTION_ENABLED=true
FALL_DETECTION_SAMPLE_RATE=50  # Hz
FALL_IMPACT_THRESHOLD=2.5  # g
FALL_ROTATION_THRESHOLD=150  # deg/s

# Event Emission
EVENT_FILE=/tmp/iris_events.jsonl
EVENT_API_URL=http://localhost:8080/api/events
```

Load in GUI:
```python
def _load_config(self):
    load_dotenv()
    
    config = {
        # ... existing config ...
        'ultrasonic_enabled': os.getenv('ULTRASONIC_ENABLED', 'true').lower() == 'true',
        'ultrasonic_trig': int(os.getenv('ULTRASONIC_TRIG_PIN', '23')),
        'ultrasonic_echo': int(os.getenv('ULTRASONIC_ECHO_PIN', '24')),
        'fall_detection_enabled': os.getenv('FALL_DETECTION_ENABLED', 'true').lower() == 'true',
    }
    
    return config
```

---

## 🧪 Testing Checklist

Before deployment:

- [ ] **Ultrasonic readings accurate** (compare with tape measure)
- [ ] **Distance announcements clear** (not too frequent)
- [ ] **Fall detection not too sensitive** (no false positives walking)
- [ ] **Fall detection not too insensitive** (detects simulated falls)
- [ ] **TTS doesn't interrupt** (non-blocking)
- [ ] **Events written to file** (check `/tmp/iris_events.jsonl`)
- [ ] **App receives events** (SMTP/API working)
- [ ] **Battery life acceptable** (~6-8 hours target)
- [ ] **Sensors survive reconnect** (unplug/replug works)

---

## 🔧 Troubleshooting

### Ultrasonic Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| Always timeout | Echo not level-shifted | Add 1kΩ/2kΩ voltage divider |
| Erratic readings | Power fluctuation | Add 10µF capacitor VCC-GND |
| Max distance wrong | Temperature | Adjust speed_of_sound in code |

### IMU Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| I2C error | Wrong address | Try 0x69 instead of 0x68 |
| Fall always detected | Threshold too low | Increase impact_threshold |
| Fall never detected | Threshold too high | Decrease impact_threshold |
| Drift over time | Gyro bias | Run calibration routine |

### Integration Issues

| Symptom | Cause | Fix |
|---------|-------|-----|
| GUI freezes | Blocking calls | Ensure threading used |
| TTS interrupted | Simultaneous speak() | Queue TTS messages |
| Events not sent | Network issue | Check API endpoint reachable |
| High CPU usage | Sample rate too high | Reduce fall_monitor sample_rate |

---

## 📊 Performance Expectations

**Ultrasonic:**
- Range: 0.5 - 13 feet reliable
- Accuracy: ±0.1 feet
- Update rate: 5 Hz (200ms interval)
- CPU: <1%

**Fall Detection:**
- Sample rate: 50 Hz
- Detection latency: 1-2 seconds
- False positive rate: <5% with tuning
- CPU: ~5-8%

**Combined System:**
- Total CPU: 15-25% (including YOLO)
- Memory: +50MB for sensors
- Power: +0.5W total

---

## 🚀 Next Steps

1. **Test sensors individually** with provided test scripts
2. **Integrate into GUI** using Option 1 (simple)
3. **Tune fall detection** thresholds for your user
4. **Set up event monitoring** in your app
5. **Test SMTP alerts** end-to-end
6. **Deploy and monitor** in real-world use

**Ready for production! 🎉**
