"""
Text-to-Speech Module
Reads out text responses using pyttsx3 or gTTS
"""

import logging
import platform
from pathlib import Path
import tempfile
import os

logger = logging.getLogger(__name__)


class TextToSpeech:
    """Text-to-speech engine for reading responses"""
    
    def __init__(self, engine="pyttsx3", rate=150, volume=1.0, voice_index=None):
        """
        Initialize TTS engine
        
        Args:
            engine: TTS engine to use ("pyttsx3" or "gtts")
            rate: Speech rate (words per minute)
            volume: Volume level (0.0 to 1.0)
            voice_index: Index of voice to use (None for default)
        """
        self.engine_type = engine
        self.rate = rate
        self.volume = volume
        self.voice_index = voice_index
        self.tts_engine = None
        
        logger.info(f"Initializing TTS engine: {engine}")
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize the selected TTS engine"""
        try:
            if self.engine_type == "pyttsx3":
                self._initialize_pyttsx3()
            elif self.engine_type == "gtts":
                self._initialize_gtts()
            else:
                raise ValueError(f"Unknown TTS engine: {self.engine_type}")
                
        except Exception as e:
            logger.error(f"Error initializing TTS engine: {e}")
            raise
    
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
