"""
Optimized Whisper STT - Ultra-fast speech recognition for Raspberry Pi 5
Uses aggressive optimizations for 5-10x faster inference
"""

import os
import numpy as np
import sounddevice as sd
import soundfile as sf
import logging
from pathlib import Path
import tempfile
import time

logger = logging.getLogger(__name__)


class OptimizedWhisperRecognizer:
    """Ultra-fast Whisper recognizer optimized for Raspberry Pi 5"""
    
    def __init__(
        self,
        model_size="tiny",
        device="cpu",
        language="en",
        sample_rate=16000
    ):
        """
        Initialize optimized Whisper recognizer
        
        Args:
            model_size: Whisper model (tiny is recommended for speed)
            device: Device to run on (cpu)
            language: Language code
            sample_rate: Audio sample rate
        """
        self.model_size = model_size
        self.device = device
        self.language = language
        self.sample_rate = sample_rate
        self.model = None
        
        logger.info(f"🚀 Initializing OPTIMIZED Whisper {model_size} model...")
        self._load_model()
    
    def _load_model(self):
        """Load Whisper model with optimizations"""
        try:
            from faster_whisper import WhisperModel
            
            # Ultra-optimized settings
            self.model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type="int8",  # Quantized INT8
                num_workers=1,  # Single worker for lower latency
                cpu_threads=2,  # Use 2 cores only
                download_root=None,
                local_files_only=False
            )
            
            logger.info(f"✅ Optimized Whisper loaded (INT8, 2 threads)")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def record_audio(self, duration=3, silence_threshold=0.01, min_speech_duration=0.5):
        """
        Record audio with smart stop on silence
        
        Args:
            duration: Max duration (seconds)
            silence_threshold: Silence detection threshold
            min_speech_duration: Minimum speech before allowing stop
            
        Returns:
            Audio data
        """
        logger.info(f"🎤 Recording (max {duration}s)...")
        
        audio_chunks = []
        silence_frames = 0
        speech_frames = 0
        frames_per_check = int(self.sample_rate * 0.1)  # 100ms
        min_speech_frames = int(min_speech_duration / 0.1)
        
        try:
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype='float32'
            ) as stream:
                start_time = time.time()
                
                while (time.time() - start_time) < duration:
                    chunk, _ = stream.read(frames_per_check)
                    audio_chunks.append(chunk)
                    
                    # Check audio level
                    level = np.abs(chunk).mean()
                    
                    if level > silence_threshold:
                        speech_frames += 1
                        silence_frames = 0
                    else:
                        silence_frames += 1
                    
                    # Stop if enough speech and then silence
                    if speech_frames >= min_speech_frames and silence_frames >= 5:  # 500ms silence
                        logger.info("✅ Speech complete (silence detected)")
                        break
                
                elapsed = time.time() - start_time
                logger.info(f"Recording done ({elapsed:.1f}s)")
                
        except Exception as e:
            logger.error(f"Recording error: {e}")
            raise
        
        audio_array = np.concatenate(audio_chunks, axis=0)
        return audio_array.flatten()
    
    def transcribe(self, audio_data):
        """
        Ultra-fast transcription
        
        Args:
            audio_data: Audio array
            
        Returns:
            Transcribed text
        """
        logger.info("⚡ Transcribing (fast mode)...")
        
        try:
            # Normalize audio
            max_val = np.abs(audio_data).max()
            if max_val > 0:
                audio_data = audio_data * (0.5 / max_val)
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp_path = tmp.name
                sf.write(tmp_path, audio_data, self.sample_rate)
            
            start = time.time()
            
            # Ultra-fast transcription settings
            segments, info = self.model.transcribe(
                tmp_path,
                language=self.language,
                beam_size=1,  # Greedy decoding (fastest)
                best_of=1,
                temperature=0.0,
                vad_filter=True,  # Skip silence automatically
                vad_parameters=dict(
                    threshold=0.5,
                    min_speech_duration_ms=250,
                    min_silence_duration_ms=300,
                    speech_pad_ms=100
                ),
                condition_on_previous_text=False,
                no_speech_threshold=0.6,
                compression_ratio_threshold=2.4,
                log_prob_threshold=-1.0,
                initial_prompt="Voice command."
            )
            
            # Get text
            text = " ".join([s.text.strip() for s in segments])
            
            elapsed = time.time() - start
            logger.info(f"✅ Transcribed in {elapsed:.2f}s: '{text}'")
            
            # Cleanup
            os.unlink(tmp_path)
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return ""
    
    def recognize(self, duration=3):
        """
        Record and transcribe
        
        Args:
            duration: Max recording duration
            
        Returns:
            Transcribed text
        """
        audio = self.record_audio(duration=duration)
        return self.transcribe(audio)


class WhisperRecognizer:
    """
    Smart Whisper recognizer - auto-selects optimized or standard mode
    """
    
    def __init__(
        self,
        model_size="tiny",
        device="cpu",
        language="en",
        sample_rate=16000,
        use_faster_whisper=True,
        fast_mode=True
    ):
        """
        Initialize smart recognizer
        
        Args:
            model_size: Model size
            device: Device
            language: Language
            sample_rate: Sample rate
            use_faster_whisper: Use faster-whisper
            fast_mode: Use optimized fast mode (recommended)
        """
        if fast_mode and use_faster_whisper:
            logger.info("🚀 Using OPTIMIZED fast mode")
            self._impl = OptimizedWhisperRecognizer(
                model_size=model_size,
                device=device,
                language=language,
                sample_rate=sample_rate
            )
        else:
            logger.info("Using standard mode")
            # Import standard implementation
            from whisper_stt import WhisperRecognizer as StandardWhisper
            self._impl = StandardWhisper(
                model_size=model_size,
                device=device,
                language=language,
                sample_rate=sample_rate,
                use_faster_whisper=use_faster_whisper,
                fast_mode=False
            )
    
    def record_audio(self, *args, **kwargs):
        """Delegate to implementation"""
        return self._impl.record_audio(*args, **kwargs)
    
    def transcribe(self, *args, **kwargs):
        """Delegate to implementation"""
        if hasattr(self._impl, 'transcribe'):
            return self._impl.transcribe(*args, **kwargs)
        else:
            return self._impl.transcribe_audio(*args, **kwargs)
    
    def recognize(self, *args, **kwargs):
        """Delegate to implementation"""
        return self._impl.recognize(*args, **kwargs)


def test_speed():
    """Test recognition speed"""
    import sys
    
    print("="*60)
    print("🚀 WHISPER SPEED TEST")
    print("="*60)
    
    # Test optimized mode
    print("\n1️⃣ Testing OPTIMIZED mode (tiny model)...")
    recognizer = OptimizedWhisperRecognizer(model_size="tiny")
    
    print("\nSpeak a short command (e.g., 'detect objects')...")
    start = time.time()
    text = recognizer.recognize(duration=3)
    total = time.time() - start
    
    print(f"\n✅ Result: '{text}'")
    print(f"⏱️  Total time: {total:.2f}s")
    print(f"🎯 Speed: {'EXCELLENT' if total < 2 else 'GOOD' if total < 3 else 'ACCEPTABLE'}")
    
    print("\n" + "="*60)
    print("💡 For faster results:")
    print("  - Use 'tiny' model (1-2s)")
    print("  - Use 'base' for better accuracy (2-3s)")
    print("  - Avoid 'medium' or larger (5-10s)")
    print("="*60)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_speed()
