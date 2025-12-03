# 🎥 Pi Camera Quick Fix Guide

## ⚡ Quick Diagnostics

Run this first:
```bash
./diagnose_camera.sh
```

## 🔧 Common Issues & Fixes

### Issue 1: "USB camera not connected" error (but you have Pi Camera)

**Cause:** `.env` file has wrong camera type

**Fix:**
```bash
nano .env
# Make sure it says:
CAMERA_TYPE=picamera
```
Press `Ctrl+X`, then `Y`, then `Enter` to save.

---

### Issue 2: "Camera not detected"

**Check:**
```bash
vcgencmd get_camera
```

**If shows `detected=0`:**

✅ **Check cable connection:**
- Disconnect and reconnect ribbon cable
- Blue side faces camera module
- Contacts face the connectors (not the cable)
- Push fully into connector until it clicks
- Lock the black clips

✅ **Enable camera:**
```bash
sudo raspi-config
```
- Navigate: `Interface Options` → `Camera` → `Enable`
- Reboot: `sudo reboot`

---

### Issue 3: "picamera2 not found"

**Fix:**
```bash
# System-wide install (recommended for Pi)
sudo apt-get update
sudo apt-get install python3-picamera2

# Or install in virtual environment
source venv/bin/activate
pip install picamera2
```

---

### Issue 4: RuntimeError when starting camera

**Test camera separately:**
```bash
# Newer Raspberry Pi OS (Bookworm+)
rpicam-hello --timeout 2000
rpicam-still -o test.jpg

# Older Raspberry Pi OS
libcamera-hello --timeout 2000
libcamera-still -o test.jpg
```

**If this fails:**
- Camera hardware issue
- Try different cable
- Try different camera module
- Check for physical damage
- For Arducam cameras: Check if requires special drivers

**If this works but Python fails:**
```bash
# Reinstall picamera2
source venv/bin/activate
pip uninstall picamera2
pip install picamera2 --no-cache-dir
```

**For Arducam IMX219 specifically:**
- ✅ Works with standard picamera2 (no special drivers needed)
- ✅ Raspberry Pi 5 fully supports IMX219 sensor
- ✅ Should work exactly like official Pi Camera V2

---

## 🎯 Step-by-Step Camera Setup

1. **Connect Camera**
   - Power off Pi: `sudo shutdown -h now`
   - Connect ribbon cable:
     - Blue side → Camera module
     - Silver contacts → Connector
   - Power on Pi

2. **Enable Camera Interface**
   ```bash
   sudo raspi-config
   # Interface Options → Camera → Enable
   sudo reboot
   ```

3. **Verify Detection**
   ```bash
   vcgencmd get_camera
   # Should show: supported=1 detected=1
   ```

4. **Test Camera**
   ```bash
   # Newer OS (recommended)
   rpicam-hello --timeout 2000
   # or for older OS:
   libcamera-hello --timeout 2000
   # Should show preview window
   ```

5. **Configure .env**
   ```bash
   nano .env
   # Set: CAMERA_TYPE=picamera
   ```

6. **Install picamera2**
   ```bash
   sudo apt-get install python3-picamera2
   ```

7. **Run Application**
   ```bash
   source venv/bin/activate
   python gui_detector.py
   ```

---

## 🔍 Verify Everything

```bash
# Run full diagnostics
./diagnose_camera.sh

# Should show all green checkmarks ✅
```

---

## 📸 Pi Camera Ribbon Cable Guide

```
Camera Module          Raspberry Pi Board
    Side                    CSI Port
     
[Camera]                  [Pi Board]
   |                          |
   |  Blue side up            |
   +-------[Cable]------------+
           Silver              Black
         contacts             latch
         face down            
```

**Correct Connection:**
- Camera end: Blue tab visible on top
- Pi end: Blue tab visible, contacts face connectors
- Cable fully inserted until resistance stops
- Black latches locked down

**Test:**
```bash
vcgencmd get_camera
# Should show: detected=1

# Also test with rpicam/libcamera
rpicam-still -t 0  # Take immediate photo (newer OS)
# or: libcamera-still -o test.jpg  # older OS
```

---

## 🆘 Still Not Working?

1. **Try different camera orientation in cable slot**
   - Sometimes contacts need to face opposite direction
   - Try flipping the cable 180°

2. **Check for damaged cable/camera**
   - Look for bent pins
   - Check cable for tears or kinks
   - Try a different cable if available

3. **Update system**
   ```bash
   sudo apt-get update
   sudo apt-get upgrade
   sudo reboot
   ```

4. **Check system logs**
   ```bash
   dmesg | grep -i camera
   ```

5. **Try legacy camera stack** (last resort)
   ```bash
   sudo raspi-config
   # Advanced → Legacy Camera → Enable
   sudo reboot
   ```

---

## ✅ Success Checklist

- [ ] `vcgencmd get_camera` shows `detected=1`
- [ ] `rpicam-hello` or `libcamera-hello` shows preview
- [ ] `rpicam-still -t 0` takes a photo successfully
- [ ] `.env` has `CAMERA_TYPE=picamera`
- [ ] `python -c "import picamera2"` works
- [ ] `./diagnose_camera.sh` shows all ✅
- [ ] `python gui_detector.py` opens with camera feed

---

**If all checked, camera is ready! 🎉**

## � Arducam IMX219 Notes

**Your Camera: Arducam IMX219 8MP V2.3**

✅ **Fully compatible** with Raspberry Pi 5 and picamera2
✅ **No special drivers needed** - works like official Pi Camera V2
✅ **8MP resolution** - Same as official Pi Camera V2
✅ **Uses standard IMX219 sensor** - Excellent quality

**Working Commands:**
```bash
# Your camera works with:
rpicam-still -t 0           # Immediate photo (newer OS)
rpicam-hello --timeout 2000 # Preview window
vcgencmd get_camera         # Should show detected=1
```

**No Changes Needed:**
- Configuration in `.env` is already correct (`CAMERA_TYPE=picamera`)
- Python picamera2 library handles it automatically
- Same performance as official Pi Camera

---

## �📚 More Help

- **Full guide:** `RASPBERRY_PI_SETUP.md`
- **Diagnostics:** `./diagnose_camera.sh`
- **Official docs:** https://www.raspberrypi.com/documentation/computers/camera_software.html
- **Arducam IMX219:** https://www.arducam.com/product/arducam-8mp-imx219/
