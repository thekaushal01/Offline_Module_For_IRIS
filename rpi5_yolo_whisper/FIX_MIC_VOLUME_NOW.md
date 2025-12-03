# 🎤 FIX MICROPHONE VOLUME NOW

## ⚠️ Problem Identified

Your logs show:
```
Number of segments: 0  ← Whisper detected NO SPEECH
Audio volume too low
```

**The medium model is working, but can't hear you!**

---

## ✅ SOLUTION: Increase Mic Volume (2 Methods)

### **Method 1: Using alsamixer (RECOMMENDED)**

```bash
# 1. Open audio mixer
alsamixer

# 2. Press F4 to switch to Capture devices
# 3. Use LEFT/RIGHT arrows to select your USB microphone
# 4. Press UP arrow repeatedly to increase volume to 80-90%
# 5. Press ESC to exit
```

**Visual Guide:**
```
┌─ Capture ──────────────────┐
│                             │
│  USB PnP Sound Device       │
│  ████████████████ 85%       │  ← Should be 80-90%
│                             │
└─────────────────────────────┘
```

### **Method 2: Using amixer (Command Line)**

```bash
# List all capture devices
amixer -c 0 contents | grep -A 10 "Mic"

# Set microphone volume to 85% (adjust card number if needed)
amixer -c 0 sset 'Mic' 85%

# Or try this if above doesn't work:
amixer set 'Capture' 85%
```

---

## 🧪 Test Your Microphone Volume

### **Quick Test Script:**

```bash
cd ~/rasp-object-detection/rpi5_yolo_whisper
source venv/bin/activate
python test_voice.py
```

**Look for this line:**
```
Audio amplitude: 0.XXXX  ← Should be > 0.05
```

**Current (TOO LOW):** `0.0079` ❌
**Target (GOOD):** `> 0.05` ✅ (ideally 0.1-0.3)

---

## 📊 Volume Comparison

| Amplitude | Status | Result |
|-----------|--------|--------|
| 0.0079 | ❌ TOO LOW | No speech detected |
| 0.02-0.04 | ⚠️ MARGINAL | Occasional detection |
| 0.05-0.1 | ✅ GOOD | Reliable detection |
| 0.1-0.3 | ✅✅ EXCELLENT | Perfect detection |
| > 0.5 | ⚠️ CLIPPING | Too loud, distortion |

---

## 🎯 Complete Fix Steps

```bash
# STEP 1: Increase microphone volume
alsamixer
# Press F4, increase USB mic to 85%, press ESC

# STEP 2: Test microphone
cd ~/rasp-object-detection/rpi5_yolo_whisper
source venv/bin/activate
python test_voice.py
# Check amplitude is > 0.05

# STEP 3: Test with GUI
python gui_mobile_detector.py
# Say "IRIS" loudly
# Say "START" clearly
```

---

## 🔍 Understanding the Logs

### **Your Current Logs Explained:**

```bash
# ✅ WAKE WORD DETECTION - WORKING!
"Wake word detected: 'i' matches 'iris'"  ← This works!

# ✅ MEDIUM MODEL LOADED - WORKING!
"Processing audio with duration 00:03.000"
"Transcription completed in 28.15s"  ← Model working!

# ❌ NO SPEECH DETECTED - TOO QUIET!
"Number of segments: 0"  ← Can't hear you!
"Audio volume too low"  ← THIS IS THE PROBLEM
```

**Wake word works** because it uses a different, more sensitive model.
**Command transcription fails** because Whisper needs louder audio.

---

## 💡 Why This Happens

1. **Wake word detector (offline_wake_word):**
   - Uses tiny model, optimized for low audio
   - Very sensitive, works with quiet audio
   - ✅ Your mic volume is ENOUGH for this

2. **Command recognition (Whisper medium):**
   - More powerful but needs clearer audio
   - Requires higher volume to detect speech
   - ❌ Your mic volume is TOO LOW for this

**Solution:** Increase mic volume for both to work well!

---

## 🎤 Hardware Check

### **Is Your USB Mic Plugged In Properly?**

```bash
# Check USB devices
lsusb | grep -i audio

# Should show something like:
# Bus 001 Device 004: ID 0d8c:0014 C-Media Electronics Inc. Audio Adapter
```

### **Check ALSA Recognizes It:**

```bash
arecord -l

# Should show:
# card 0: Device [USB PnP Sound Device], device 0: USB Audio [USB Audio]
```

---

## 🔧 Advanced Troubleshooting

### **If alsamixer shows no mic controls:**

```bash
# Install PulseAudio volume control
sudo apt-get install pavucontrol

# Run it (if you have X11/VNC access)
pavucontrol

# Go to "Input Devices" tab
# Increase USB microphone volume
```

### **If using SSH without GUI:**

```bash
# Use amixer to set volume
amixer -c 0 sset 'Mic' 85%
amixer -c 0 sset 'Capture' 85%

# Test recording directly
arecord -f cd -d 5 test.wav
aplay test.wav  # Listen to playback
```

---

## 📋 Verification Checklist

After increasing volume, verify:

- [ ] Run `python test_voice.py`
- [ ] Audio amplitude > 0.05 ✅
- [ ] Run `python gui_mobile_detector.py`
- [ ] Say "IRIS" - wake word detected ✅
- [ ] Hear "Listening for command" ✅
- [ ] Say "START" clearly and LOUDLY
- [ ] Check logs: "Number of segments: 1" ✅ (not 0!)
- [ ] Check logs: "Segment 0: 'start'" ✅
- [ ] Detection starts ✅

---

## 🎯 Expected Results After Fix

**Before (Current - TOO QUIET):**
```
Audio amplitude: 0.0079 ❌
Number of segments: 0 ❌
Audio volume too low ❌
```

**After (With Increased Volume):**
```
Audio amplitude: 0.15 ✅
Number of segments: 1 ✅
Segment 0: 'start' ✅
✅ Starting detection via voice command
```

---

## 🚨 If Still Not Working After Volume Increase

Try these additional steps:

### **1. Disable VAD Filter Completely:**

The logs show:
```
VAD filter removed 00:02.000 of audio  ← Removing ALL audio!
```

VAD should already be disabled, but let's verify:

```bash
cd ~/rasp-object-detection/rpi5_yolo_whisper
nano whisper_stt.py

# Find line ~170, ensure it says:
vad_filter=False
```

### **2. Test Without GUI:**

```bash
python -c "
import sounddevice as sd
import numpy as np
duration = 3
print('Recording...')
audio = sd.rec(int(duration * 16000), samplerate=16000, channels=1, dtype='float32')
sd.wait()
amplitude = np.abs(audio).max()
print(f'Amplitude: {amplitude}')
print('PASS' if amplitude > 0.05 else 'FAIL - TOO QUIET')
"
```

### **3. Try Different USB Port:**

```bash
# Unplug USB microphone
# Plug into different USB port
# Run alsamixer again to set volume
```

---

## 📞 Report Back

After increasing mic volume, provide:

1. **Output from test_voice.py:**
   ```
   Audio amplitude: _____
   ```

2. **Output from gui_mobile_detector.py logs:**
   ```
   Number of segments: _____
   Segment 0: '_____'
   ```

3. **alsamixer screenshot or amixer output:**
   ```bash
   amixer get Capture
   ```

---

## ✅ Quick Command Summary

```bash
# Fix mic volume
alsamixer  # F4, UP arrow to 85%, ESC

# Test mic
python test_voice.py

# Test GUI
python gui_mobile_detector.py

# Say IRIS → START (LOUDLY!)
```

---

**The medium model IS working! You just need to increase your microphone volume! 🎤📢**
