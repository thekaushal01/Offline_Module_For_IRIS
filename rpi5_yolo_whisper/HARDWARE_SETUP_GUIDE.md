# 🔌 Hardware Setup Guide - Visual Assistance System
## Raspberry Pi 5 + HC-SR04 + MPU9250

---

## 📋 Components List

1. **Raspberry Pi 5** (with Raspberry Pi OS Bookworm 64-bit)
2. **HC-SR04 Ultrasonic Sensor** (distance measurement, 0.5 - 13 feet range)
3. **MPU9250 9-Axis IMU** (accelerometer, gyroscope, magnetometer for fall detection)
4. **Resistors for voltage divider** (1kΩ and 2kΩ) OR **4-channel logic level shifter**
5. **Breadboard and jumper wires**

---

## ⚠️ CRITICAL SAFETY NOTES

### **Voltage Levels:**
- **Raspberry Pi GPIO**: 3.3V logic (5V will damage GPIO pins!)
- **HC-SR04 Echo pin**: Outputs 5V (MUST be level-shifted down!)
- **MPU9250**: 3.3V device (do NOT connect to 5V!)

### **Power Supply:**
- HC-SR04: Powered by 5V, draws ~15mA
- MPU9250: Powered by 3.3V, draws ~10mA
- Total additional load: ~25mA (well within Pi 5 capacity)

---

## 🔧 Hardware Wiring

### **HC-SR04 Ultrasonic Sensor** (Distance Measurement)

#### Pin Connections:

| HC-SR04 Pin | Connection | Raspberry Pi Pin | Notes |
|-------------|------------|------------------|-------|
| **VCC** | → | **5V** (Pin 2 or 4) | Power supply |
| **GND** | → | **GND** (Pin 6) | Ground |
| **TRIG** | → | **GPIO23** (Pin 16) | Trigger (3.3V output from Pi is OK) |
| **ECHO** | ⚠️ | **GPIO24** (Pin 18) | **MUST USE VOLTAGE DIVIDER!** |

#### ⚠️ ECHO Pin Voltage Divider (REQUIRED!)

HC-SR04 Echo outputs 5V, but Pi GPIO accepts only 3.3V max. Use a voltage divider:

```
HC-SR04 ECHO pin
      |
      +--- 1kΩ resistor ---+--- GPIO24 (Pin 18)
      |                    |
      +--- 2kΩ resistor ---+--- GND
```

**Calculation:**
- Output voltage = 5V × (2kΩ / (1kΩ + 2kΩ)) = 3.33V ✅ Safe!

**Alternative:** Use a **4-channel logic level shifter module** (bi-directional, easier wiring).

#### Physical Layout:
```
Pi 5 GPIO Header (Top View)
┌─────────────────────────────┐
│  5V  5V  GND                │  Pin 2, 4, 6
│                             │
│  GPIO2  GPIO3               │  Pin 3, 5 (I2C for MPU9250)
│                             │
│              GPIO23  GPIO24 │  Pin 16, 18 (HC-SR04)
│                             │
└─────────────────────────────┘
```

---

### **MPU9250 9-Axis IMU** (Fall Detection)

#### Pin Connections:

| MPU9250 Pin | Connection | Raspberry Pi Pin | Notes |
|-------------|------------|------------------|-------|
| **VCC** | → | **3.3V** (Pin 1) | ⚠️ 3.3V ONLY! |
| **GND** | → | **GND** (Pin 6) | Ground |
| **SDA** | → | **GPIO2 (SDA)** (Pin 3) | I2C Data |
| **SCL** | → | **GPIO3 (SCL)** (Pin 5) | I2C Clock |
| **AD0** | ↓ | GND or Float | I2C address (GND=0x68, VCC=0x69) |

#### I2C Address:
- **Default**: `0x68` (AD0 pulled to GND or floating)
- **Alternative**: `0x69` (if AD0 connected to VCC)

#### Notes:
- Most MPU9250 modules have built-in pull-up resistors for SDA/SCL (typically 4.7kΩ)
- Raspberry Pi also has pull-ups enabled by default on I2C pins
- No external pull-ups needed in most cases

---

## 📐 Complete Wiring Diagram

```
Raspberry Pi 5 GPIO Header
┌────────────────────────────────────────┐
│ Pin  1: 3.3V ──────────────┐           │
│ Pin  2: 5V ────────┐       │           │
│ Pin  3: GPIO2/SDA ─┼───────┼──┐        │
│ Pin  4: 5V         │       │  │        │
│ Pin  5: GPIO3/SCL ─┼───────┼──┼──┐     │
│ Pin  6: GND ───────┼───┐   │  │  │     │
│                    │   │   │  │  │     │
│ Pin 16: GPIO23 ────┼───┼───┼──┼──┼──┐  │
│ Pin 18: GPIO24 ────┼───┼───┼──┼──┼──┼─┐│
└────────────────────┼───┼───┼──┼──┼──┼─┼┘
                     │   │   │  │  │  │ │
                     │   │   │  │  │  │ │
        HC-SR04      │   │   │  │  │  │ │
      ┌──────────┐   │   │   │  │  │  │ │
      │ VCC  ────┼───┘   │   │  │  │  │ │
      │ TRIG ────┼───────┼───┼──┼──┼──┘ │
      │ ECHO ────┼───[1kΩ]───┼──┼──────┘
      │          │       │    │  │  │
      │          │    [2kΩ]   │  │  │
      │ GND  ────┼───────┴────┘  │  │
      └──────────┘               │  │
                                 │  │
        MPU9250                  │  │
      ┌──────────┐               │  │
      │ VCC  ────┼───────────────┘  │
      │ GND  ────┼──────────────────┘
      │ SDA  ────┼─────────────────┘
      │ SCL  ────┼────────────────┘
      └──────────┘
```

---

## 🔍 Verification Steps

### 1. Enable I2C Interface

```bash
# Method 1: Using raspi-config
sudo raspi-config
# Navigate: Interface Options → I2C → Enable → Finish → Reboot

# Method 2: Direct edit (advanced)
sudo nano /boot/firmware/config.txt
# Add or uncomment: dtparam=i2c_arm=on
# Save and reboot
```

### 2. Install Required Tools

```bash
sudo apt-get update
sudo apt-get install -y i2c-tools pigpio python3-pigpio
```

### 3. Enable pigpio Daemon (for ultrasonic timing)

```bash
sudo systemctl enable pigpiod
sudo systemctl start pigpiod
sudo systemctl status pigpiod
# Should show: active (running)
```

### 4. Verify I2C Connection

```bash
# Scan I2C bus for MPU9250
sudo i2cdetect -y 1

# Expected output:
#      0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
# 00:                         -- -- -- -- -- -- -- --
# 10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
# 20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
# 30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
# 40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
# 50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
# 60: -- -- -- -- -- -- -- -- 68 -- -- -- -- -- -- --  ← MPU9250
# 70: -- -- -- -- -- -- -- --
```

If you see `68` (or `69`), MPU9250 is detected! ✅

### 5. Test GPIO Access for HC-SR04

```bash
# Check pigpio is working
pigs hwver
# Should return Pi hardware version number

# Test GPIO read (should not error)
pigs r 24
```

---

## 🛠️ Troubleshooting

### **HC-SR04 Issues:**

| Problem | Solution |
|---------|----------|
| No distance reading | Check voltage divider on ECHO pin; verify pigpiod is running |
| Erratic readings | Add 10µF capacitor between VCC and GND on sensor |
| Constant 0 or timeout | Check wiring, ensure TRIG and ECHO are not swapped |

### **MPU9250 Issues:**

| Problem | Solution |
|---------|----------|
| Not detected (no `68` or `69`) | Check wiring; ensure VCC is 3.3V not 5V; verify I2C enabled |
| Wrong address | Check AD0 pin (GND=0x68, VCC=0x69); modify code accordingly |
| I2C errors | Ensure pull-ups present (4.7kΩ typical); check SCL/SDA not swapped |

### **General:**

- **Permission errors**: Add user to `gpio` group:
  ```bash
  sudo usermod -a -G gpio $USER
  ```
  Log out and back in.

- **I2C speed issues**: Default 100kHz is fine. If needed, increase:
  ```bash
  sudo nano /boot/firmware/config.txt
  # Add: dtparam=i2c_arm_baudrate=400000
  ```

---

## 📏 Sensor Specifications

### **HC-SR04 Ultrasonic:**
- **Range**: 2cm to 400cm (0.65 ft to 13 ft)
- **Accuracy**: ±3mm (±0.01 ft)
- **Angle**: 15° cone
- **Frequency**: 40kHz ultrasonic
- **Trigger**: 10µs pulse
- **Echo**: Proportional to distance (58µs per cm)

### **MPU9250 IMU:**
- **Accelerometer**: ±2g, ±4g, ±8g, ±16g (configurable)
- **Gyroscope**: ±250, ±500, ±1000, ±2000 °/s
- **Magnetometer**: ±4800µT (AK8963 internal)
- **Output rate**: Up to 1kHz accel/gyro; 100Hz mag
- **Temperature sensor**: Built-in

---

## 🎯 Next Steps

After wiring and verification:

1. ✅ **Install Python libraries** (next guide)
2. ✅ **Run test scripts** to verify sensor readings
3. ✅ **Integrate with GUI** for real-time announcements
4. ✅ **Configure fall detection** algorithm
5. ✅ **Setup event notifications** for app/SMTP

---

## 📸 Recommended Physical Setup

For a visual assistance device:

1. **HC-SR04**: Mount facing forward at chest/waist height
   - Detects obstacles 1-10 feet ahead
   - 15° cone covers ~1.5 ft width at 5 ft distance

2. **MPU9250**: Mount on body/belt, oriented:
   - Z-axis pointing up when standing
   - X-axis pointing forward
   - Y-axis pointing left

3. **Raspberry Pi 5**: In protective case with:
   - Heat sink/fan (optional but recommended)
   - Power bank (for portable use)
   - Velcro/strap for wearing

---

## ⚡ Power Considerations

**For Portable Operation:**

- **Raspberry Pi 5**: Requires 5V/3A min (15W)
- **Recommended**: 25,000mAh USB-C PD power bank (5V/5A)
- **Runtime**: ~6-8 hours with camera + sensors + TTS

**Battery Monitor Script:**
```bash
vcgencmd get_throttled
# 0x0 = OK
# Non-zero = undervoltage/throttling
```

---

## 📝 Safety Checklist

Before powering on:

- [ ] MPU9250 connected to 3.3V (NOT 5V)
- [ ] HC-SR04 ECHO has voltage divider (or level shifter)
- [ ] No short circuits (check with multimeter continuity)
- [ ] All ground connections secure
- [ ] I2C pull-ups present (built-in or external)
- [ ] pigpiod enabled and running

**Ready to proceed with software setup!** ✅
