"""
Fully Offline Wake Word Detection using Whisper
Listens continuously for "IRIS" wake word using local Whisper model
No internet connection required
"""

import os
import logging
import numpy as np
import sounddevice as sd
import time
from pathlib import Path
import tempfile
import wave

logger = logging.getLogger(__name__)

class OfflineWakeWordDetector:
    """
    Fully offline wake word detector using Whisper
    Listens in small chunks and checks for wake word
    """
    
    def __init__(self, 
                 wake_word="iris",
                 model_size="tiny",  # Use tiny model for fast wake word detection
                 sample_rate=16000,
                 chunk_duration=2.0,  # Listen in 2-second chunks
                 threshold_similarity=0.6):
        """
        Initialize offline wake word detector
        
        Args:
            wake_word: The wake word to detect (default: "iris")
            model_size: Whisper model size (tiny is fastest for wake word)
            sample_rate: Audio sample rate
            chunk_duration: Duration of each listening chunk in seconds
            threshold_similarity: Similarity threshold for wake word detection
        """
        self.wake_word = wake_word.lower()
        self.sample_rate = sample_rate
        self.chunk_duration = chunk_duration
        self.chunk_samples = int(sample_rate * chunk_duration)
        self.threshold = threshold_similarity
        self.is_listening = False
        self.model = None
        
        logger.info(f"Initializing offline wake word detector for '{wake_word}'...")
        logger.info(f"Using Whisper {model_size} model (fully offline)")
        
        # Load Whisper model
        self._load_model(model_size)
    
    def _load_model(self, model_size):
        """Load Whisper model for wake word detection"""
        try:
            # Try faster-whisper first (more efficient)
            try:
                from faster_whisper import WhisperModel
                logger.info("Loading faster-whisper model...")
                self.model = WhisperModel(
                    model_size,
                    device="cpu",
                    compute_type="int8"
                )
                self.use_faster_whisper = True
                logger.info("✅ Faster-whisper model loaded (offline)")
            except ImportError:
                # Fallback to standard whisper
                import whisper
                logger.info("Loading standard whisper model...")
                self.model = whisper.load_model(model_size)
                self.use_faster_whisper = False
                logger.info("✅ Whisper model loaded (offline)")
                
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise
    
    def _transcribe_chunk(self, audio_data):
        """
        Transcribe audio chunk using Whisper
        
        Args:
            audio_data: Audio data as numpy array
            
        Returns:
            Transcribed text in lowercase
        """
        try:
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = temp_file.name
                
                # Write audio data
                with wave.open(temp_path, 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)  # 16-bit
                    wf.setframerate(self.sample_rate)
                    wf.writeframes(audio_data.tobytes())
            
            # Transcribe with Whisper
            if self.use_faster_whisper:
                segments, info = self.model.transcribe(
                    temp_path,
                    language="en",
                    beam_size=1,  # Fast inference
                    vad_filter=True  # Filter out silence
                )
                text = " ".join([segment.text for segment in segments])
            else:
                result = self.model.transcribe(
                    temp_path,
                    language="en",
                    fp16=False
                )
                text = result["text"]
            
            # Clean up temp file
            try:
                os.unlink(temp_path)
            except:
                pass
            
            return text.lower().strip()
            
        except Exception as e:
            logger.error(f"Error transcribing chunk: {e}")
            return ""
    
    def _check_wake_word(self, text):
        """
        Check if wake word is present in text
        
        Args:
            text: Transcribed text
            
        Returns:
            True if wake word detected
        """
        if not text:
            return False
        
        # Simple word matching
        words = text.split()
        
        # Check for exact match
        if self.wake_word in words:
            logger.info(f"✅ Wake word '{self.wake_word}' detected (exact match)")
            return True
        
        # Check for partial match (more lenient)
        for word in words:
            # Calculate simple similarity
            if self._simple_similarity(word, self.wake_word) >= self.threshold:
                logger.info(f"✅ Wake word detected: '{word}' matches '{self.wake_word}'")
                return True
        
        return False
    
    def _simple_similarity(self, word1, word2):
        """
        Calculate simple character-based similarity
        
        Args:
            word1: First word
            word2: Second word
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        if word1 == word2:
            return 1.0
        
        # Check if one word contains the other
        if word1 in word2 or word2 in word1:
            return 0.8
        
        # Count matching characters
        matches = sum(1 for c1, c2 in zip(word1, word2) if c1 == c2)
        max_len = max(len(word1), len(word2))
        
        if max_len == 0:
            return 0.0
        
        return matches / max_len
    
    def listen_for_wake_word(self, callback=None, timeout=None):
        """
        Listen continuously for wake word
        
        Args:
            callback: Function to call when wake word detected
            timeout: Maximum listening time in seconds (None for infinite)
            
        Returns:
            True if wake word detected, False if timeout
        """
        self.is_listening = True
        start_time = time.time()
        
        logger.info(f"🎤 Listening for wake word '{self.wake_word.upper()}'... (fully offline)")
        logger.info("Speak clearly and say the wake word...")
        
        try:
            while self.is_listening:
                # Check timeout
                if timeout and (time.time() - start_time) > timeout:
                    logger.info("Wake word listening timeout")
                    return False
                
                # Record audio chunk
                logger.debug(f"Recording {self.chunk_duration}s chunk...")
                audio_data = sd.rec(
                    self.chunk_samples,
                    samplerate=self.sample_rate,
                    channels=1,
                    dtype='int16'
                )
                sd.wait()
                
                # Transcribe chunk
                text = self._transcribe_chunk(audio_data)
                
                if text:
                    logger.debug(f"Heard: '{text}'")
                    
                    # Check for wake word
                    if self._check_wake_word(text):
                        logger.info(f"✅ Wake word '{self.wake_word.upper()}' detected!")
                        if callback:
                            callback()
                        return True
                
        except KeyboardInterrupt:
            logger.info("Wake word detection stopped by user")
            self.stop()
        except Exception as e:
            logger.error(f"Error in wake word detection: {e}")
            raise
        
        return False
    
    def stop(self):
        """Stop listening for wake word"""
        self.is_listening = False
        logger.info("Wake word detector stopped")


def test_offline_wake_word():
    """Test the offline wake word detector"""
    print("=" * 60)
    print("OFFLINE WAKE WORD DETECTOR TEST")
    print("=" * 60)
    print("\nThis test uses Whisper for fully offline wake word detection")
    print("No internet connection required!")
    print("\nWake word: IRIS")
    print("\nInstructions:")
    print("1. Speak clearly into your microphone")
    print("2. Say 'IRIS' to trigger detection")
    print("3. Press Ctrl+C to stop")
    print("\n" + "=" * 60)
    
    try:
        detector = OfflineWakeWordDetector(
            wake_word="iris",
            model_size="tiny",  # Fast model for wake word
            chunk_duration=2.0
        )
        
        print("\n🎤 Listening for 'IRIS'...\n")
        
        def on_wake_word():
            print("\n" + "=" * 60)
            print("✅ WAKE WORD DETECTED!")
            print("=" * 60)
        
        detected = detector.listen_for_wake_word(
            callback=on_wake_word,
            timeout=60  # 60 second test
        )
        
        if not detected:
            print("\n⏱️ Test timeout - no wake word detected")
        
    except KeyboardInterrupt:
        print("\n\n✋ Test stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    test_offline_wake_word()
