"""
Speech Recognition Module using Whisper
Optimized for Raspberry Pi 5 with medium model
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


class WhisperRecognizer:
    """Speech recognition using OpenAI Whisper (medium model)"""
    
    def __init__(
        self,
        model_size="small",
        device="cpu",
        language="en",
        sample_rate=16000,
        use_faster_whisper=True,
        fast_mode=True
    ):
        """
        Initialize Whisper speech recognizer
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
            device: Device to run on (cpu, cuda)
            language: Language code for transcription
            sample_rate: Audio sample rate in Hz
            use_faster_whisper: Use faster-whisper for better performance
        """
        self.model_size = model_size
        self.device = device
        self.language = language
        self.sample_rate = sample_rate
        self.use_faster_whisper = use_faster_whisper
        self.fast_mode = fast_mode
        self.model = None
        
        logger.info(f"Initializing Whisper {model_size} model...")
        self._load_model()
    
    def _load_model(self):
        """Load the Whisper model"""
        try:
            if self.use_faster_whisper:
                # faster-whisper is optimized for CPU and uses less memory
                from faster_whisper import WhisperModel
                
                logger.info("Using faster-whisper for better performance")
                
                # Use int8 quantization for speed (faster) or float32 for accuracy
                compute_type = "int8" if self.fast_mode else "float16"
                
                self.model = WhisperModel(
                    self.model_size,
                    device=self.device,
                    compute_type=compute_type,
                    num_workers=2,  # Use 2 threads for faster startup
                    cpu_threads=2
                )
                logger.info(f"faster-whisper {self.model_size} model loaded (compute_type={compute_type})")
            else:
                # Original OpenAI Whisper
                import whisper
                
                logger.info("Using OpenAI Whisper")
                self.model = whisper.load_model(self.model_size, device=self.device)
                logger.info(f"Whisper {self.model_size} model loaded successfully")
                
        except ImportError as e:
            logger.error(f"Failed to import whisper library: {e}")
            logger.info("Please install: pip install faster-whisper or pip install openai-whisper")
            raise
        except Exception as e:
            logger.error(f"Error loading Whisper model: {e}")
            raise
    
    def record_audio(self, duration=5, silence_threshold=0.003, max_silence_duration=2.0):
        """
        Record audio from microphone with automatic silence detection
        
        Args:
            duration: Maximum recording duration in seconds
            silence_threshold: Audio level below which is considered silence (lowered for quiet mics)
            max_silence_duration: Stop recording after this many seconds of silence
            
        Returns:
            numpy array of audio data
        """
        logger.info(f"Recording audio (max {duration}s, auto-stop on silence)...")
        print("🎤 Listening... (speak now)")
        
        audio_data = []
        silence_start = None
        recording_started = False
        
        try:
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype='float32'
            ) as stream:
                start_time = time.time()
                
                while time.time() - start_time < duration:
                    # Read audio chunk
                    chunk, _ = stream.read(int(self.sample_rate * 0.1))  # 100ms chunks
                    audio_data.append(chunk)
                    
                    # Calculate audio level
                    audio_level = np.abs(chunk).mean()
                    
                    # Detect speech start
                    if not recording_started and audio_level > silence_threshold:
                        recording_started = True
                        logger.debug("Speech detected, recording started")
                    
                    # Detect silence after speech started
                    if recording_started:
                        if audio_level < silence_threshold:
                            if silence_start is None:
                                silence_start = time.time()
                            elif time.time() - silence_start > max_silence_duration:
                                logger.info("Silence detected, stopping recording")
                                break
                        else:
                            silence_start = None
                
                elapsed = time.time() - start_time
                logger.info(f"Recording completed ({elapsed:.1f}s)")
                
        except Exception as e:
            logger.error(f"Error recording audio: {e}")
            raise
        
        # Combine chunks
        audio_array = np.concatenate(audio_data, axis=0)
        return audio_array.flatten()
    
    def transcribe_audio(self, audio_data):
        """
        Transcribe audio data using Whisper
        
        Args:
            audio_data: numpy array of audio samples
            
        Returns:
            Transcribed text
        """
        logger.info("Transcribing audio...")
        
        try:
            # Amplify audio for low-volume microphones
            original_max = np.abs(audio_data).max()
            logger.info(f"Original audio amplitude: {original_max:.4f}")
            
            if original_max > 0:
                # Normalize to use full dynamic range (amplify by up to 10x)
                target_amplitude = 0.3  # Target peak amplitude
                amplification_factor = min(target_amplitude / original_max, 10.0)
                audio_data = audio_data * amplification_factor
                logger.info(f"Amplified audio by {amplification_factor:.2f}x to {np.abs(audio_data).max():.4f}")
            
            # Save audio to temporary file (Whisper expects file path)
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                tmp_path = tmp_file.name
                sf.write(tmp_path, audio_data, self.sample_rate)
            
            # Transcribe
            start_time = time.time()
            
            if self.use_faster_whisper:
                # Fast mode: optimized for speed (1-2s inference)
                # Standard mode: balanced quality/speed (3-4s inference)
                if self.fast_mode:
                    segments, info = self.model.transcribe(
                        tmp_path,
                        language=self.language,
                        beam_size=1,  # Greedy decoding (fastest)
                        best_of=1,
                        temperature=0.0,  # Deterministic, fastest
                        vad_filter=True,  # Skip silence
                        vad_parameters=dict(
                            threshold=0.5,
                            min_speech_duration_ms=250,
                            min_silence_duration_ms=500,
                            speech_pad_ms=200
                        ),
                        condition_on_previous_text=False,
                        no_speech_threshold=0.6,
                        compression_ratio_threshold=2.4,
                        log_prob_threshold=-1.0,
                        initial_prompt="Voice commands for object detection."
                    )
                else:
                    segments, info = self.model.transcribe(
                        tmp_path,
                        language=self.language,
                        beam_size=3,
                        best_of=3,
                        temperature=[0.0, 0.2],  # Limited temperature search
                        initial_prompt="Voice commands: start, stop, begin, end, detect, detection.",
                        vad_filter=True,
                        vad_parameters=dict(
                            threshold=0.5,
                            min_speech_duration_ms=250
                        ),
                        condition_on_previous_text=False,
                        no_speech_threshold=0.5,
                        compression_ratio_threshold=2.4,
                        log_prob_threshold=-1.0
                    )
                
                # Convert generator to list and combine segments
                segment_list = list(segments)
                logger.info(f"Number of segments: {len(segment_list)}")
                
                # Log each segment for debugging
                for i, segment in enumerate(segment_list):
                    logger.info(f"Segment {i}: '{segment.text.strip()}'")
                
                text = " ".join([segment.text.strip() for segment in segment_list])
                
                logger.info(f"Detected language: {info.language} (probability: {info.language_probability:.2f})")
            else:
                result = self.model.transcribe(
                    tmp_path,
                    language=self.language,
                    fp16=False  # CPU doesn't support fp16
                )
                text = result["text"]
            
            elapsed = time.time() - start_time
            logger.info(f"Transcription completed in {elapsed:.2f}s")
            
            # Clean up
            os.unlink(tmp_path)
            
            # Clean and return text
            text = text.strip()
            logger.info(f"Transcribed text: '{text}'")
            
            # If text is empty, log warning
            if not text:
                logger.warning("⚠️ Whisper returned empty transcription!")
                logger.warning("This could mean:")
                logger.warning("  1. Audio volume too low")
                logger.warning("  2. No speech detected")
                logger.warning("  3. Background noise only")
                logger.warning("Try speaking LOUDER and closer to microphone")
            
            return text
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return ""
    
    def recognize(self, duration=5):
        """
        Record audio and transcribe it
        
        Args:
            duration: Maximum recording duration in seconds
            
        Returns:
            Transcribed text
        """
        audio_data = self.record_audio(duration)
        text = self.transcribe_audio(audio_data)
        return text


def test_whisper():
    """Test Whisper speech recognition"""
    print("Initializing Whisper speech recognizer...")
    recognizer = WhisperRecognizer(
        model_size="medium",
        device="cpu",
        use_faster_whisper=True
    )
    
    print("\nReady! Speak after the prompt...")
    text = recognizer.recognize(duration=10)
    
    print(f"\n✅ You said: '{text}'")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_whisper()
