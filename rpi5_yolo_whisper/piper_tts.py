"""
Piper TTS Module - High Quality Neural TTS for Raspberry Pi
Fast, offline, natural-sounding speech synthesis
"""

import os
import logging
import subprocess
import tempfile
from pathlib import Path
import wave

logger = logging.getLogger(__name__)


class PiperTTS:
    """
    Piper TTS - Neural text-to-speech optimized for Raspberry Pi
    
    Features:
    - High quality neural voices
    - Fast inference (real-time on Pi 5)
    - Fully offline
    - Low memory footprint
    - Multiple voice options
    """
    
    def __init__(self, 
                 model="en_US-lessac-medium",
                 rate=1.0,
                 volume=1.0,
                 piper_path=None,
                 models_dir=None):
        """
        Initialize Piper TTS
        
        Args:
            model: Voice model name (e.g., "en_US-lessac-medium")
            rate: Speech rate multiplier (0.5-2.0, default 1.0)
            volume: Volume level (0.0-1.0)
            piper_path: Path to piper binary (auto-detected if None)
            models_dir: Directory containing voice models
        """
        self.model = model
        self.rate = rate
        self.volume = volume
        self.models_dir = models_dir or os.path.expanduser("~/.local/share/piper/voices")
        
        # Find piper executable
        self.piper_path = piper_path or self._find_piper()
        
        # Verify model exists
        self.model_path = self._get_model_path()
        
        logger.info(f"✅ Piper TTS initialized")
        logger.info(f"  Model: {self.model}")
        logger.info(f"  Rate: {self.rate}x")
        logger.info(f"  Piper: {self.piper_path}")
    
    def _find_piper(self):
        """Find piper executable"""
        # Check common locations
        locations = [
            "/usr/local/bin/piper",
            "/usr/bin/piper",
            os.path.expanduser("~/.local/bin/piper"),
            "./piper/piper"
        ]
        
        for loc in locations:
            if os.path.isfile(loc) and os.access(loc, os.X_OK):
                return loc
        
        # Try which command
        try:
            result = subprocess.run(
                ["which", "piper"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except:
            pass
        
        raise FileNotFoundError(
            "Piper executable not found. Install with:\n"
            "  ./install_piper.sh\n"
            "Or manually: https://github.com/rhasspy/piper"
        )
    
    def _get_model_path(self):
        """Get path to model file"""
        model_file = f"{self.model}.onnx"
        model_path = os.path.join(self.models_dir, model_file)
        
        if not os.path.exists(model_path):
            logger.warning(f"Model not found: {model_path}")
            logger.info("Available models:")
            self._list_available_models()
            raise FileNotFoundError(
                f"Model not found: {model_file}\n"
                f"Download with: ./download_piper_voice.sh {self.model}"
            )
        
        return model_path
    
    def _list_available_models(self):
        """List available voice models"""
        if os.path.exists(self.models_dir):
            models = [f.replace('.onnx', '') for f in os.listdir(self.models_dir) if f.endswith('.onnx')]
            for model in models:
                logger.info(f"  - {model}")
        else:
            logger.info(f"  Models directory not found: {self.models_dir}")
    
    def speak(self, text, blocking=True):
        """
        Speak text using Piper TTS
        
        Args:
            text: Text to speak
            blocking: Wait for speech to complete (default True)
        """
        if not text or not text.strip():
            logger.warning("Empty text provided to TTS")
            return
        
        try:
            # Create temporary WAV file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                wav_path = tmp_file.name
            
            # Generate speech with Piper
            cmd = [
                self.piper_path,
                "--model", self.model_path,
                "--output_file", wav_path,
                "--length_scale", str(1.0 / self.rate)  # Piper uses length_scale (inverse of rate)
            ]
            
            logger.debug(f"Piper command: {' '.join(cmd)}")
            
            # Run Piper with text input
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input=text)
            
            if process.returncode != 0:
                logger.error(f"Piper failed: {stderr}")
                raise RuntimeError(f"Piper synthesis failed: {stderr}")
            
            # Play the generated audio
            self._play_audio(wav_path, blocking=blocking)
            
            # Clean up
            try:
                os.unlink(wav_path)
            except:
                pass
                
        except Exception as e:
            logger.error(f"Error in Piper TTS: {e}")
            raise
    
    def _play_audio(self, wav_path, blocking=True):
        """Play audio file using aplay (Raspberry Pi)"""
        try:
            # Adjust volume if needed
            if self.volume < 1.0:
                self._adjust_volume(wav_path, self.volume)
            
            # Play with aplay (standard on Raspberry Pi)
            cmd = ["aplay", "-q", wav_path]
            
            if blocking:
                subprocess.run(cmd, check=True)
            else:
                subprocess.Popen(cmd)
                
        except FileNotFoundError:
            # Fallback to other players
            logger.warning("aplay not found, trying alternative players...")
            self._play_audio_fallback(wav_path, blocking)
    
    def _play_audio_fallback(self, wav_path, blocking=True):
        """Fallback audio players"""
        players = ["paplay", "ffplay -nodisp -autoexit", "mpg123", "play"]
        
        for player in players:
            try:
                cmd = player.split() + [wav_path]
                if blocking:
                    subprocess.run(cmd, check=True, stderr=subprocess.DEVNULL)
                else:
                    subprocess.Popen(cmd, stderr=subprocess.DEVNULL)
                return
            except:
                continue
        
        logger.error("No audio player found!")
        raise RuntimeError("Could not play audio - install aplay, paplay, or ffplay")
    
    def _adjust_volume(self, wav_path, volume):
        """Adjust WAV file volume"""
        try:
            import numpy as np
            
            # Read WAV file
            with wave.open(wav_path, 'rb') as wf:
                frames = wf.readframes(wf.getnframes())
                params = wf.getparams()
            
            # Convert to numpy array
            audio = np.frombuffer(frames, dtype=np.int16)
            
            # Apply volume
            audio = (audio * volume).astype(np.int16)
            
            # Write back
            with wave.open(wav_path, 'wb') as wf:
                wf.setparams(params)
                wf.writeframes(audio.tobytes())
                
        except Exception as e:
            logger.warning(f"Could not adjust volume: {e}")


class TextToSpeech:
    """
    Smart TTS wrapper - supports both Piper and pyttsx3
    Automatically selects best available engine
    """
    
    def __init__(self, engine="piper", rate=150, volume=1.0, voice_index=None, model=None):
        """
        Initialize TTS engine
        
        Args:
            engine: "piper" (recommended), "pyttsx3", or "auto"
            rate: Speech rate (words per minute for pyttsx3, multiplier for Piper)
            volume: Volume (0.0-1.0)
            voice_index: Voice index for pyttsx3
            model: Piper model name (e.g., "en_US-lessac-medium")
        """
        self.engine_type = engine
        self.rate = rate
        self.volume = volume
        self.voice_index = voice_index
        self.model = model or "en_US-lessac-medium"
        self.tts_engine = None
        
        logger.info(f"🔊 Initializing TTS: {engine}")
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize the selected TTS engine"""
        try:
            if self.engine_type == "auto":
                # Try Piper first, fallback to pyttsx3
                try:
                    self._initialize_piper()
                    logger.info("✅ Using Piper TTS (best quality)")
                except:
                    logger.warning("Piper not available, using pyttsx3")
                    self._initialize_pyttsx3()
            elif self.engine_type == "piper":
                self._initialize_piper()
            elif self.engine_type == "pyttsx3":
                self._initialize_pyttsx3()
            else:
                raise ValueError(f"Unknown TTS engine: {self.engine_type}")
                
        except Exception as e:
            logger.error(f"Error initializing TTS: {e}")
            raise
    
    def _initialize_piper(self):
        """Initialize Piper TTS"""
        # Convert pyttsx3 rate (words/min) to Piper rate (multiplier)
        piper_rate = self.rate / 150.0 if self.rate > 10 else self.rate
        
        self.tts_engine = PiperTTS(
            model=self.model,
            rate=piper_rate,
            volume=self.volume
        )
        self.engine_type = "piper"
    
    def _initialize_pyttsx3(self):
        """Initialize pyttsx3 (fallback)"""
        import pyttsx3
        
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', self.rate)
        self.tts_engine.setProperty('volume', self.volume)
        
        # Set voice if specified
        if self.voice_index is not None:
            voices = self.tts_engine.getProperty('voices')
            if 0 <= self.voice_index < len(voices):
                self.tts_engine.setProperty('voice', voices[self.voice_index].id)
        
        self.engine_type = "pyttsx3"
        logger.info("✅ pyttsx3 TTS initialized")
    
    def speak(self, text):
        """
        Speak text
        
        Args:
            text: Text to speak
        """
        if not text or not text.strip():
            return
        
        try:
            if self.engine_type == "piper":
                self.tts_engine.speak(text)
            else:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
                
        except Exception as e:
            logger.error(f"Error speaking text: {e}")


# Available Piper voice models
PIPER_VOICES = {
    # High quality voices
    "en_US-lessac-medium": "American English (Lessac) - Medium quality, balanced",
    "en_US-lessac-high": "American English (Lessac) - High quality, slower",
    "en_US-libritts-high": "American English (LibriTTS) - High quality, natural",
    
    # Fast voices
    "en_US-lessac-low": "American English (Lessac) - Low quality, fastest",
    "en_US-ryan-low": "American English (Ryan) - Low quality, fast",
    "en_US-ryan-medium": "American English (Ryan) - Medium quality",
    
    # Other accents
    "en_GB-alan-medium": "British English (Alan) - Medium quality",
    "en_GB-southern_english_female-low": "British English (Female) - Low quality",
}


def test_piper():
    """Test Piper TTS"""
    print("🔊 Testing Piper TTS")
    print("=" * 50)
    
    try:
        tts = TextToSpeech(engine="piper")
        
        test_texts = [
            "Hello, I am using Piper text to speech.",
            "Object detection completed. I see one person and two chairs.",
            "Warning, fall detected. Are you okay?"
        ]
        
        for text in test_texts:
            print(f"\n📢 Speaking: {text}")
            tts.speak(text)
        
        print("\n✅ Piper TTS test complete!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_piper()
