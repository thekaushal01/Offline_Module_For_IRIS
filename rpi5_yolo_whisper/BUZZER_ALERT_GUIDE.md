# 🚨 Proximity Alert System with Buzzer

## Overview

Your visual assistance system now includes **smart proximity alerts** with a buzzer alarm that warns when people/objects approach within 5 feet.

---

## 🎯 Alert Levels

| Distance | Urgency | Buzzer Pattern | TTS Message Example |
|----------|---------|----------------|---------------------|
| **≤ 2.0 ft** | 🔴 **CRITICAL** | 5 rapid beeps (0.1s on/off) | "⚠️ WARNING! person very close at 1.8 feet, coming towards you!" |
| **2.0 - 3.5 ft** | 🟠 **HIGH** | 3 medium beeps (0.2s on/off) | "⚠️ Caution! person at 2.5 feet, approaching you" |
| **3.5 - 5.0 ft** | 🟡 **MODERATE** | 2 slow beeps (0.3s on/off) | "person at 4.2 feet, coming towards you" |
| **> 5.0 ft** | 🟢 **NORMAL** | No buzzer | "person at 7 feet ahead" (if auto-announce on) |

---

## 🔌 Hardware Setup

### Buzzer Wiring

```
Active Buzzer Module (3.3V compatible):
├── VCC → 3.3V (Pin 1)
├── GND → GND (Pin 6)
└── SIG → GPIO17 (Pin 11) ← Default, configurable in .env
```

**⚠️ Important:**
- Use **active buzzer** (has built-in oscillator, just needs DC voltage)
- **NOT passive piezo** (requires PWM signal)
- Use **3.3V compatible** buzzer or add transistor for 5V buzzer

### Alternative: Transistor Circuit for 5V Buzzer

If you have a 5V buzzer:

```
GPIO17 (Pin 11) → 1kΩ resistor → NPN transistor base (2N2222)
                                ├── Collector → Buzzer (+)
                                └── Emitter → GND
Buzzer (-) → GND
5V Power → Buzzer (+)
```

---

## 🧠 How It Works

### Approach Detection

The system tracks the last 5 distance readings to detect if an object is **approaching** (getting closer):

```python
# Distance history: [4.5, 4.0, 3.5, 3.0, 2.5] feet
# Trend: Decreasing → Object is APPROACHING
# Alert: "person at 2.5 feet, coming towards you"

# Distance history: [3.0, 3.2, 3.1, 3.0, 2.9] feet  
# Trend: Stable/fluctuating → Object is STATIONARY
# Alert: "person at 2.9 feet"
```

### Alert Logic

```
Person enters 5ft zone
├── Check: Is approaching? (distance decreasing)
├── Determine urgency: Critical/High/Moderate
├── Trigger buzzer pattern
├── Speak TTS alert
├── Show visual warning in GUI
├── Emit proximity_alert event
└── Wait 2 seconds cooldown (prevent spam)
```

### Example Scenarios

**Scenario 1: Person Walking Toward You**
```
Frame 1: 6.0 ft → No alert (normal range)
Frame 2: 4.5 ft → "person at 4.5 feet, coming towards you" + 2 slow beeps
Frame 3: 3.0 ft → [Cooldown, no alert]
Frame 4: 2.5 ft → "⚠️ Caution! person at 2.5 feet, approaching you" + 3 medium beeps
Frame 5: 1.5 ft → "⚠️ WARNING! person very close at 1.5 feet, coming towards you!" + 5 rapid beeps
```

**Scenario 2: Stationary Object**
```
Frame 1: 4.0 ft → "person at 4.0 feet ahead" + 2 slow beeps
Frame 2: 3.9 ft → [Cooldown, no alert]
Frame 3: 4.1 ft → [No significant change]
Frame 4: 4.0 ft → "person at 4.0 feet" (after cooldown expires)
```

---

## ⚙️ Configuration

### .env Settings

```bash
# Buzzer Pin (BCM GPIO numbering)
BUZZER_PIN=17

# Alert Distances (in feet)
CRITICAL_DISTANCE=2.0    # Red alert zone
WARNING_DISTANCE=3.5     # Orange alert zone
CAUTION_DISTANCE=5.0     # Yellow alert zone (trigger threshold)

# Alert Timing
PROXIMITY_ALERT_COOLDOWN=2.0  # Seconds between alerts (prevent spam)
```

### Tuning Tips

**Too Many Alerts?**
```bash
# Increase cooldown
PROXIMITY_ALERT_COOLDOWN=3.0

# Or increase trigger distance (only alert when very close)
CAUTION_DISTANCE=3.0
```

**Missing Close Approaches?**
```bash
# Decrease cooldown (more frequent alerts)
PROXIMITY_ALERT_COOLDOWN=1.5

# Or increase trigger distance (alert earlier)
CAUTION_DISTANCE=7.0
```

**Buzzer Too Loud/Annoying?**
- Add resistor in series (330Ω - 1kΩ) to reduce volume
- Or use PWM for volume control (requires code modification)

---

## 🧪 Testing

### 1. Test Buzzer Alone

```python
# Test script: test_buzzer.py
import lgpio
import time

GPIO_CHIP = 4
BUZZER_PIN = 17

h = lgpio.gpiochip_open(GPIO_CHIP)
lgpio.gpio_claim_output(h, BUZZER_PIN)

# Test patterns
print("Rapid beeps (critical)...")
for _ in range(5):
    lgpio.gpio_write(h, BUZZER_PIN, 1)
    time.sleep(0.1)
    lgpio.gpio_write(h, BUZZER_PIN, 0)
    time.sleep(0.1)

time.sleep(1)

print("Medium beeps (warning)...")
for _ in range(3):
    lgpio.gpio_write(h, BUZZER_PIN, 1)
    time.sleep(0.2)
    lgpio.gpio_write(h, BUZZER_PIN, 0)
    time.sleep(0.2)

time.sleep(1)

print("Slow beeps (caution)...")
for _ in range(2):
    lgpio.gpio_write(h, BUZZER_PIN, 1)
    time.sleep(0.3)
    lgpio.gpio_write(h, BUZZER_PIN, 0)
    time.sleep(0.3)

lgpio.gpiochip_close(h)
print("Done!")
```

Run: `python test_buzzer.py`

### 2. Test Proximity Alerts

```bash
# Start GUI
python gui_mobile_detector.py

# Say "IRIS detect" to start detection

# Test scenarios:
# A) Walk toward camera slowly
#    → Should hear "person at X feet, coming towards you"
#    → Buzzer should beep faster as you get closer
#
# B) Stand still at 3 feet
#    → Should hear "person at 3 feet"
#    → Buzzer pattern: 3 medium beeps
#
# C) Jump to < 2 feet
#    → Should hear "WARNING! person very close at..."
#    → Buzzer pattern: 5 rapid beeps
```

### 3. Test Event Emission

```bash
# Terminal 1: Run GUI
python gui_mobile_detector.py

# Terminal 2: Monitor events
tail -f /tmp/iris_events.jsonl

# Trigger proximity alert (get within 5 feet)
# Should see JSON event:
{
  "timestamp": 1733822567.8,
  "event": "proximity_alert",
  "payload": {
    "object": "person",
    "distance_feet": 2.5,
    "urgency": "high",
    "approaching": true,
    "message": "⚠️ Caution! person at 2.5 feet, approaching you"
  }
}
```

---

## 📊 Alert Messages Reference

### Critical (≤ 2.0 ft)

- **Approaching:** "⚠️ WARNING! {object} very close at {dist} feet, coming towards you!"
- **Stationary:** "⚠️ ALERT! {object} at {dist} feet!"
- **Buzzer:** 5 rapid beeps (0.1s on, 0.1s off)
- **GUI:** Red status with distance
- **Event:** `urgency: "critical"`

### High (2.0 - 3.5 ft)

- **Approaching:** "⚠️ Caution! {object} at {dist} feet, approaching you"
- **Stationary:** "Alert, {object} at {dist} feet"
- **Buzzer:** 3 medium beeps (0.2s on, 0.2s off)
- **GUI:** Orange status with distance
- **Event:** `urgency: "high"`

### Moderate (3.5 - 5.0 ft)

- **Approaching:** "{object} at {dist} feet, coming towards you"
- **Stationary:** "{object} at {dist} feet ahead"
- **Buzzer:** 2 slow beeps (0.3s on, 0.3s off)
- **GUI:** Yellow status with distance
- **Event:** `urgency: "moderate"`

---

## 🔧 Troubleshooting

### Buzzer Not Working

**1. Check wiring:**
```bash
# Test GPIO manually
python3 -c "
import lgpio
h = lgpio.gpiochip_open(4)
lgpio.gpio_claim_output(h, 17)
lgpio.gpio_write(h, 17, 1)  # Should turn ON buzzer
import time; time.sleep(1)
lgpio.gpio_write(h, 17, 0)  # Should turn OFF buzzer
lgpio.gpiochip_close(h)
"
```

**If no sound:**
- Check VCC is connected to 3.3V (or 5V with transistor)
- Check GND connection
- Verify it's an **active** buzzer (has + and - markings)
- Try different GPIO pin (update BUZZER_PIN in .env)

**2. Check logs:**
```bash
python gui_mobile_detector.py 2>&1 | grep -i buzzer

# Expected:
# INFO - Initializing buzzer...
# INFO - ✅ Buzzer ready on GPIO17
```

**3. Volume too low?**
- Remove any resistors in series
- Use 5V power with transistor instead of 3.3V
- Try different buzzer (check dB rating, >85dB is loud)

### No Proximity Alerts

**1. Check detection is active:**
- GUI must be running
- Say "IRIS detect" to start
- YOLO must be detecting objects

**2. Check distance:**
```bash
# Test ultrasonic separately
python test_ultrasonic_lgpio.py --duration 10

# Should show distances < 5 feet when you're close
```

**3. Check cooldown:**
```bash
# If you just got an alert, wait 2 seconds before next one
# Reduce cooldown in .env:
PROXIMITY_ALERT_COOLDOWN=1.0
```

### Alerts Too Frequent

```bash
# Increase cooldown
PROXIMITY_ALERT_COOLDOWN=3.0

# Or only alert for very close objects
CAUTION_DISTANCE=3.0
```

### False "Approaching" Detection

The system tracks last 5 distance readings. If readings are noisy:

```bash
# Increase filtering by requiring larger distance change
# Edit gui_mobile_detector.py line ~795:
if len(self.last_distances) >= 5:  # Changed from 3
    is_approaching = self.last_distances[-1] < self.last_distances[-5] - 0.5  # Add threshold
```

---

## 🎯 App Integration

### SMTP Alerts for Critical Proximity

```python
# Your app code
import json
import smtplib
from email.mime.text import MIMEText

def monitor_proximity_events():
    with open('/tmp/iris_events.jsonl', 'r') as f:
        f.seek(0, 2)  # Seek to end
        
        while True:
            line = f.readline()
            if line:
                event = json.loads(line)
                
                # Alert on critical proximity
                if (event['event'] == 'proximity_alert' and 
                    event['payload']['urgency'] == 'critical'):
                    
                    send_email(
                        subject="URGENT: Critical Proximity Alert",
                        body=f"""
                        Alert: {event['payload']['message']}
                        Distance: {event['payload']['distance_feet']} feet
                        Object: {event['payload']['object']}
                        Approaching: {event['payload']['approaching']}
                        Time: {event['timestamp']}
                        """
                    )
            time.sleep(0.1)
```

---

## 📖 Summary

✅ **Buzzer alerts for 3 urgency levels** (critical/high/moderate)  
✅ **Approach detection** - knows if object is coming toward you  
✅ **Smart cooldown** - prevents alert spam  
✅ **Visual + Audio + Haptic** - multiple alert modalities  
✅ **Event logging** - for app/SMTP integration  
✅ **Configurable** - tune distances and timing via .env  

**Your visual assistance system now provides proactive warnings when people approach!** 🎉
