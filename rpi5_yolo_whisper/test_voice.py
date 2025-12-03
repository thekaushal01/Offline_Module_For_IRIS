"""
Test Voice Recognition Components
Use this to debug voice command issues
"""

import logging
import time
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_imports():
    """Test if all voice libraries can be imported"""
    print("\n" + "="*50)
    print("Testing Imports...")
    print("="*50)
    
    try:
        import sounddevice as sd
        print("✅ sounddevice imported")
        print(f"   Available devices: {len(sd.query_devices())}")
    except Exception as e:
        print(f"❌ sounddevice failed: {e}")
        return False
    
    try:
        import soundfile as sf
        print("✅ soundfile imported")
    except Exception as e:
        print(f"❌ soundfile failed: {e}")
        return False
    
    try:
        from faster_whisper import WhisperModel
        print("✅ faster-whisper imported")
    except Exception as e:
        print(f"❌ faster-whisper failed: {e}")
        return False
    
    try:
        from offline_wake_word import OfflineWakeWordDetector
        print("✅ offline_wake_word imported")
    except Exception as e:
        print(f"❌ offline_wake_word failed: {e}")
        return False
    
    try:
        from whisper_stt import WhisperRecognizer
        print("✅ whisper_stt imported")
    except Exception as e:
        print(f"❌ whisper_stt failed: {e}")
        return False
    
    return True

def test_microphone():
    """Test microphone access"""
    print("\n" + "="*50)
    print("Testing Microphone...")
    print("="*50)
    
    try:
        import sounddevice as sd
        import numpy as np
        
        print("\n📋 Available Audio Devices:")
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            print(f"  [{i}] {device['name']}")
            print(f"      Inputs: {device['max_input_channels']}, Outputs: {device['max_output_channels']}")
        
        print("\n🎤 Testing microphone recording (2 seconds)...")
        print("   Say something!")
        
        duration = 2
        sample_rate = 16000
        audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, 
                      channels=1, dtype='float32')
        sd.wait()
        
        # Check if we got audio
        max_amplitude = np.max(np.abs(audio))
        print(f"\n✅ Recording successful!")
        print(f"   Max amplitude: {max_amplitude:.4f}")
        
        if max_amplitude < 0.001:
            print("⚠️  Warning: Very low audio level. Check microphone!")
        else:
            print("✅ Audio level looks good!")
        
        return True
        
    except Exception as e:
        print(f"❌ Microphone test failed: {e}")
        return False

def test_wake_word():
    """Test wake word detection"""
    print("\n" + "="*50)
    print("Testing Wake Word Detection...")
    print("="*50)
    
    try:
        from offline_wake_word import OfflineWakeWordDetector
        
        print("Initializing wake word detector...")
        detector = OfflineWakeWordDetector(
            wake_word='iris',
            model_size='tiny',
            sample_rate=16000
        )
        print("✅ Wake word detector initialized")
        
        print("\n🎤 Say 'IRIS' within 10 seconds...")
        print("   (This will timeout after 10 seconds if not detected)")
        
        import threading
        detected = [False]
        
        def listen():
            result = detector.listen_for_wake_word()
            detected[0] = result
        
        thread = threading.Thread(target=listen, daemon=True)
        thread.start()
        thread.join(timeout=10)
        
        if detected[0]:
            print("✅ Wake word 'IRIS' detected!")
            return True
        else:
            print("❌ Wake word not detected (timeout)")
            print("   Try saying 'IRIS' louder or closer to microphone")
            return False
            
    except Exception as e:
        print(f"❌ Wake word test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_speech_recognition():
    """Test speech recognition"""
    print("\n" + "="*50)
    print("Testing Speech Recognition...")
    print("="*50)
    
    try:
        from whisper_stt import WhisperRecognizer
        
        print("Initializing Whisper (this may take a moment)...")
        recognizer = WhisperRecognizer(
            model_size='small',
            device='cpu',
            sample_rate=16000,
            use_faster_whisper=True
        )
        print("✅ Whisper initialized")
        
        print("\n🎤 Recording for 3 seconds...")
        print("   Say something like 'detect' or 'start'")
        
        audio_data = recognizer.record_audio(
            duration=3,
            silence_threshold=0.02,
            max_silence_duration=1.5
        )
        
        if audio_data is None or len(audio_data) == 0:
            print("❌ No audio captured")
            return False
        
        print("✅ Audio recorded, transcribing...")
        text = recognizer.transcribe_audio(audio_data)
        
        if text:
            print(f"✅ Transcription: '{text}'")
            return True
        else:
            print("❌ No text transcribed")
            return False
            
    except Exception as e:
        print(f"❌ Speech recognition test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🔍 Voice Recognition Test Suite")
    print("="*60)
    
    results = {}
    
    # Test 1: Imports
    results['imports'] = test_imports()
    if not results['imports']:
        print("\n❌ Import test failed. Install missing packages:")
        print("   pip install sounddevice soundfile faster-whisper")
        return
    
    # Test 2: Microphone
    results['microphone'] = test_microphone()
    if not results['microphone']:
        print("\n❌ Microphone test failed. Check hardware connection.")
    
    # Test 3: Wake Word (optional, can timeout)
    print("\n⏭️  Skipping wake word test (takes time)")
    print("   To test manually, uncomment in code")
    # results['wake_word'] = test_wake_word()
    
    # Test 4: Speech Recognition
    results['speech'] = test_speech_recognition()
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60)
    for test, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test.capitalize()}: {status}")
    
    print("\n" + "="*60)
    if all(results.values()):
        print("🎉 All tests passed! Voice recognition should work.")
    else:
        print("⚠️  Some tests failed. Review errors above.")
    print("="*60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
