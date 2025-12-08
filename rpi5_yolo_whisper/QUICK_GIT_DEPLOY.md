# 🚀 Quick Git Deployment

Deploy IRIS on Raspberry Pi 5 using Git in 3 simple steps.

## 📋 Prerequisites

- Raspberry Pi 5 with Raspberry Pi OS (64-bit)
- Internet connection on both PC and Raspberry Pi
- Git installed on both machines
- GitHub account (or other Git hosting)

---

## 🔥 Super Quick Start

### On Your PC (Windows):

```powershell
# Navigate to project and push
cd "C:\Users\NITIN NAYN\Offline_Module_For_IRIS"
.\push_to_git.ps1
```

### On Raspberry Pi:

```bash
# One-line deployment
bash <(curl -s https://raw.githubusercontent.com/thekaushal01/Offline_Module_For_IRIS/main/rpi5_yolo_whisper/deploy_on_pi.sh)
```

**Or manually:**

```bash
cd ~
git clone https://github.com/thekaushal01/Offline_Module_For_IRIS.git
cd Offline_Module_For_IRIS/rpi5_yolo_whisper
chmod +x quick_deploy.sh
./quick_deploy.sh
```

---

## 📝 Detailed Steps

### Step 1: Push Code to GitHub (PC)

#### Option A: Using PowerShell Script (Easiest)

```powershell
cd "C:\Users\NITIN NAYN\Offline_Module_For_IRIS"
.\push_to_git.ps1
```

#### Option B: Manual Commands

```powershell
cd "C:\Users\NITIN NAYN\Offline_Module_For_IRIS"

git add .
git commit -m "Add NCNN and Whisper optimizations"
git push origin main
```

### Step 2: Clone on Raspberry Pi

```bash
# SSH into your Pi or use terminal directly
cd ~
git clone https://github.com/thekaushal01/Offline_Module_For_IRIS.git
cd Offline_Module_For_IRIS/rpi5_yolo_whisper
```

### Step 3: Run Automated Setup

```bash
chmod +x quick_deploy.sh
./quick_deploy.sh
```

**This automatically:**
1. ✅ Installs system dependencies
2. ✅ Creates Python virtual environment
3. ✅ Installs Python packages
4. ✅ Builds and installs NCNN
5. ✅ Downloads YOLO model
6. ✅ Converts to optimized NCNN format
7. ✅ Runs performance benchmarks

**Time:** 20-30 minutes

---

## 🎯 Running the Application

After deployment:

```bash
cd ~/Offline_Module_For_IRIS/rpi5_yolo_whisper
source venv/bin/activate
python gui_mobile_detector.py
```

**Voice Commands:**
- Say **"IRIS"** to activate
- Say **"detect objects"** or **"what do you see"**
- System responds in 3-4 seconds

---

## 🔄 Updating After Changes

### When you make changes on PC:

```powershell
cd "C:\Users\NITIN NAYN\Offline_Module_For_IRIS"
git add .
git commit -m "Your change description"
git push origin main
```

### Update on Raspberry Pi:

```bash
cd ~/Offline_Module_For_IRIS
git pull origin main

# If dependencies changed:
cd rpi5_yolo_whisper
source venv/bin/activate
pip install -r requirements_rpi5.txt

# Restart app
python gui_mobile_detector.py
```

---

## 📊 What Gets Installed

### System Packages
- Python 3.11+
- OpenCV and camera libraries
- Audio libraries (PortAudio, espeak)
- Build tools for NCNN

### Python Packages
- ultralytics (YOLO)
- faster-whisper (Speech recognition)
- ncnn (Optimized inference)
- opencv-python (Camera)
- sounddevice (Audio)
- pyttsx3 (Text-to-speech)

### Models
- YOLO11n (~6MB)
- YOLO11n NCNN INT8 (~2MB)
- Whisper tiny (~75MB)

**Total Download:** ~500MB  
**Disk Space:** ~2GB after installation

---

## 🐛 Troubleshooting

### Git Clone Fails

```bash
# Check internet
ping github.com

# Try HTTPS instead of SSH
git clone https://github.com/thekaushal01/Offline_Module_For_IRIS.git
```

### Quick Deploy Script Fails

Run steps manually:

```bash
# Install dependencies
./install_rpi5.sh

# Install NCNN
./install_ncnn.sh

# Convert model
source venv/bin/activate
python convert_yolo_ncnn.py models/yolo11n.pt
```

### Can't Find GitHub Repository

Update the URL in scripts:
1. Edit `push_to_git.ps1` (line with git push)
2. Edit `deploy_on_pi.sh` (line with git clone)
3. Replace `thekaushal01` with your GitHub username

### Permission Denied

```bash
chmod +x *.sh
```

---

## 📁 Repository Structure

```
Offline_Module_For_IRIS/
├── .gitignore                    # Git ignore rules
├── README.md                     # Main documentation
├── push_to_git.ps1              # Windows: Push to Git
│
└── rpi5_yolo_whisper/
    ├── deploy_on_pi.sh          # Raspberry Pi: Deploy script
    ├── quick_deploy.sh          # Automated setup
    ├── install_rpi5.sh          # Install dependencies
    ├── install_ncnn.sh          # Install NCNN
    │
    ├── GIT_DEPLOYMENT_GUIDE.md  # Detailed guide
    ├── QUICK_GIT_DEPLOY.md      # This file
    │
    └── (application files...)
```

---

## ⚡ Performance After Deployment

| Metric | Value |
|--------|-------|
| YOLO FPS | 45-60 (NCNN) |
| Speech Recognition | 1-2 seconds |
| Total Response Time | 3-4 seconds |
| Memory Usage | ~500MB |
| CPU Usage | 40-50% |

---

## 🎉 Success Checklist

After deployment, verify:

- [ ] `git clone` completed successfully
- [ ] `quick_deploy.sh` ran without errors
- [ ] Virtual environment created (`venv/` folder exists)
- [ ] NCNN models exist (`models/*_ncnn_int8.*`)
- [ ] Benchmark shows 40+ FPS
- [ ] Application starts without errors
- [ ] Voice activation works ("IRIS")
- [ ] Object detection works
- [ ] Response time under 5 seconds

---

## 📞 Need Help?

Check these files:
- `GIT_DEPLOYMENT_GUIDE.md` - Detailed deployment guide
- `NCNN_OPTIMIZATION_README.md` - YOLO optimization
- `WHISPER_OPTIMIZATION_README.md` - Speech optimization
- `README.md` - Main project documentation

---

**🚀 Happy Deploying!**
