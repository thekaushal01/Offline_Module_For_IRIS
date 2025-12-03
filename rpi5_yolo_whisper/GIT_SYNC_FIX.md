# 🔧 Git Sync Issue - Quick Fix

## Problem
Your local changes are blocking the git pull. This is normal!

## ✅ Solution - Stash and Pull

Run these commands on your Raspberry Pi:

```bash
cd ~/rasp-object-detection

# Save your local changes temporarily
git stash

# Pull the latest code
git pull origin main

# Apply your local changes back (if you want them)
git stash pop

# Now you can run the new GUI
cd rpi5_yolo_whisper
source venv/bin/activate
python gui_mobile_detector.py
```

---

## 🚀 Alternative: Force Update (Recommended)

If you don't need your local changes, just reset to match GitHub:

```bash
cd ~/rasp-object-detection

# Discard all local changes and match GitHub exactly
git fetch origin
git reset --hard origin/main

# Now run the new mobile GUI
cd rpi5_yolo_whisper
source venv/bin/activate
python gui_mobile_detector.py
```

---

## 📋 What Files Changed?

The conflict is in:
- `diagnose_camera.sh` 
- `install_rpi5.sh`

These were updated on GitHub with new features. The force update will get you the latest versions.

---

## ✨ After Syncing

Once synced, you'll have the new mobile GUI with:
- ✅ Voice commands (IRIS DETECT / IRIS STOP)
- ✅ Confidence threshold slider
- ✅ NMS threshold slider
- ✅ Field of view selector
- ✅ Advanced statistics
- ✅ Mobile-ready design

---

## 🎯 Quick Reference

### Option 1: Keep your changes
```bash
git stash
git pull origin main
git stash pop
```

### Option 2: Discard your changes (recommended)
```bash
git fetch origin
git reset --hard origin/main
```

Then run:
```bash
cd rpi5_yolo_whisper
source venv/bin/activate
python gui_mobile_detector.py
```

---

**Choose Option 2 (reset) if you haven't made important custom changes!** 🚀
