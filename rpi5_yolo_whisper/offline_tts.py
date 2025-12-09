"""
Text-to-Speech Module
Reads out text responses using Piper (recommended), pyttsx3 or gTTS
"""

import logging
import platform
from pathlib import Path
import tempfile
import os

# Try to import Piper TTS
try:
    from piper_tts import TextToSpeech as PiperTTS
    PIPER_AVAILABLE = True
except ImportError:
    PIPER_AVAILABLE = False
    
logger = logging.getLogger(__name__)


class TextToSpeech:
    """Text-to-speech engine for reading responses"""
    
    def __init__(self, engine="piper", rate=150, volume=1.0, voice_index=None, model=None):
        """
        Initialize TTS engine
        
        Args:
            engine: TTS engine to use ("piper", "pyttsx3", "gtts", or "auto")
            rate: Speech rate (words per minute for pyttsx3, multiplier for Piper)
            volume: Volume level (0.0 to 1.0)
            voice_index: Index of voice to use for pyttsx3 (None for default)
            model: Piper voice model (e.g., "en_US-lessac-medium")
        """
        self.engine_type = engine
        self.rate = rate
        self.volume = volume
        self.voice_index = voice_index
        self.model = model or os.getenv("PIPER_VOICE", "en_US-lessac-medium")
        self.tts_engine = None
        
        logger.info(f"Initializing TTS engine: {engine}")
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize the selected TTS engine"""
        try:
            if self.engine_type == "auto":
                # Auto-select: try Piper first, fallback to pyttsx3
                if PIPER_AVAILABLE:
                    try:
                        self._initialize_piper()
                        logger.info("✅ Using Piper TTS (best quality)")
                        return
                    except:
                        logger.warning("Piper initialization failed, trying pyttsx3")
                self._initialize_pyttsx3()
            elif self.engine_type == "piper":
                self._initialize_piper()
            elif self.engine_type == "pyttsx3":
                self._initialize_pyttsx3()
            elif self.engine_type == "gtts":
                self._initialize_gtts()
            else:
                raise ValueError(f"Unknown TTS engine: {self.engine_type}")
                
        except Exception as e:
            logger.error(f"Error initializing TTS engine: {e}")
            raise
    
    def _initialize_piper(self):
        """Initialize Piper TTS (recommended for Raspberry Pi)"""
        if not PIPER_AVAILABLE:
            raise ImportError("Piper TTS not available. Install with: ./install_piper.sh")
        
        # Convert pyttsx3 rate (words/min) to Piper rate (multiplier)
        piper_rate = self.rate / 150.0 if self.rate > 10 else self.rate
        
        self.tts_engine = PiperTTS(
            engine="piper",
            rate=piper_rate,
            volume=self.volume,
            model=self.model
        )
        logger.info(f"✅ Piper TTS initialized with model: {self.model}")
    
    def _initialize_pyttsx3(self):
        """Initialize pyttsx3 (offline, good for Raspberry Pi)"""
        import pyttsx3
        
        self.tts_engine = pyttsx3.init()
        
        # Set properties
        self.tts_engine.setProperty('rate', self.rate)
        self.tts_engine.setProperty('volume', self.volume)
        
        # List available voices
        voices = self.tts_engine.getProperty('voices')
        logger.info(f"Available voices: {len(voices)}")
        for idx, voice in enumerate(voices):
            logger.debug(f"  [{idx}] {voice.name} - {voice.languages}")
        
        # Set voice if specified
        if self.voice_index is not None and 0 <= self.voice_index < len(voices):
            self.tts_engine.setProperty('voice', voices[self.voice_index].id)
            logger.info(f"Using voice: {voices[self.voice_index].name}")
        else:
            logger.info(f"Using default voice: {voices[0].name if voices else 'Unknown'}")
        
        logger.info("pyttsx3 TTS engine initialized successfully")
    
    def _initialize_gtts(self):
        """Initialize gTTS (requires internet, but higher quality)"""
        from gtts import gTTS
        
        # gTTS doesn't need initialization, we'll use it per-request
        logger.info("gTTS TTS engine ready (requires internet connection)")
    
    def speak(self, text):
        """
        Speak the given text
        
        Args:
            text: Text to speak
        """
        if not text or not text.strip():
            logger.warning("Empty text provided, skipping TTS")
            return
        
        logger.info(f"Speaking: '{text}'")
        
        try:
            if self.engine_type == "pyttsx3":
                self._speak_pyttsx3(text)
            elif self.engine_type == "gtts":
                self._speak_gtts(text)
                
        except Exception as e:
            logger.error(f"Error speaking text: {e}")
    
    def _speak_pyttsx3(self, text):
        """Speak using pyttsx3"""
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()
    
    def _speak_gtts(self, text):
        """Speak using gTTS"""
        from gtts import gTTS
        import pygame
        
        # Create temporary audio file
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        try:
            # Generate speech
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(tmp_path)
            
            # Play audio using pygame
            pygame.mixer.init()
            pygame.mixer.music.load(tmp_path)
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            
            pygame.mixer.quit()
            
        finally:
            # Clean up
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def stop(self):
        """Stop current speech"""
        if self.engine_type == "pyttsx3" and self.tts_engine:
            try:
                self.tts_engine.stop()
            except:
                pass
    
    def set_rate(self, rate):
        """Set speech rate"""
        self.rate = rate
        if self.engine_type == "pyttsx3" and self.tts_engine:
            self.tts_engine.setProperty('rate', rate)
    
    def set_volume(self, volume):
        """Set volume (0.0 to 1.0)"""
        self.volume = volume
        if self.engine_type == "pyttsx3" and self.tts_engine:
            self.tts_engine.setProperty('volume', volume)
    
    def list_voices(self):
        """List available voices"""
        if self.engine_type == "pyttsx3" and self.tts_engine:
            voices = self.tts_engine.getProperty('voices')
            return [(idx, voice.name, voice.languages) for idx, voice in enumerate(voices)]
        return []


def test_tts():
    """Test text-to-speech"""
    print("Initializing Text-to-Speech engine...")
    
    # Test pyttsx3 (offline, best for Raspberry Pi)
    tts = TextToSpeech(engine="pyttsx3", rate=150, volume=1.0)
    
    print("\nAvailable voices:")
    voices = tts.list_voices()
    for idx, name, langs in voices:
        print(f"  [{idx}] {name} - {langs}")
    
    print("\n🔊 Testing TTS...")
    tts.speak("Hello! I am your visual assistance app. Wake word IRIS detected. How can I help you today?")
    
    print("✅ TTS test completed!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_tts()
