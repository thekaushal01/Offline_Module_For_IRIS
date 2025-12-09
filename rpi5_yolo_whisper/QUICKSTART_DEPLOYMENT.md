# 🎯 QUICK START - 5 Minutes to Running System

## On Windows PC (1 minute)

```powershell
# Navigate to project
cd "C:\Users\NITIN NAYN\Offline_Module_For_IRIS"

# Commit and push all changes
git add .
git commit -m "Add NCNN and Whisper optimizations"
git push origin main
```

## On Raspberry Pi 5 (30 minutes)

### Step 1: Clone Repository (2 min)
```bash
ssh pi@raspberrypi.local
cd ~
git clone https://github.com/thekaushal01/Offline_Module_For_IRIS.git
cd Offline_Module_For_IRIS/rpi5_yolo_whisper
```

### Step 2: Run Deployment Script (25 min)
```bash
chmod +x deploy_rpi5.sh
./deploy_rpi5.sh
```

**Wait for completion**, then reboot if prompted:
```bash
sudo reboot
```

### Step 3: Run System (1 min)
```bash
cd ~/Offline_Module_For_IRIS/rpi5_yolo_whisper
source venv/bin/activate
python gui_mobile_detector.py
```

## 🎤 Test Voice Commands

1. Say: **"IRIS"**
2. System responds: **"Yes?"**
3. Say: **"Detect objects"**
4. System detects and describes objects

---

## ⚡ Performance Expected

- **Voice recognition**: 1-2 seconds
- **Object detection**: 45-60 FPS
- **Total response**: 3-4 seconds
- **CPU usage**: 40-50%
- **Memory**: ~500MB

---

## 🆘 Quick Fixes

### Script fails?
```bash
./deploy_rpi5.sh 2>&1 | tee deployment.log
cat deployment.log  # Check errors
```

### Camera not working?
```bash
sudo raspi-config
# Interface Options → Camera → Enable
sudo reboot
```

### Slow performance?
```bash
# Check if NCNN is used
python -c "from smart_yolo_detector import SmartYOLODetector; d = SmartYOLODetector(camera_type=None); print(d.get_implementation_info())"
# Should show: NCNN (quantized)
```

### Audio issues?
```bash
arecord -l  # List microphones
alsamixer   # Adjust volume
```

---

## 📖 Full Documentation

See **DEPLOYMENT_GUIDE.md** for detailed instructions and troubleshooting.

**🎉 That's it! Your system is ready!**