"""
Main Raspberry Pi 5 Application
Integrates YOLO Object Detection + Whisper STT + TTS
Voice-activated visual assistance with object detection
"""

import os
import sys
import logging
import argparse
import time
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import modules
from yolo_detector import YOLODetector
from whisper_stt import WhisperRecognizer
from offline_tts import TextToSpeech
from offline_wake_word import OfflineWakeWordDetector


class VoiceActivatedObjectDetector:
    """Voice-activated object detection app for Raspberry Pi 5"""
    
    def __init__(self, config=None):
        """
        Initialize the app
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or self._load_config()
        self.running = False
        
        logger.info("=" * 60)
        logger.info("🤖 RASPBERRY PI 5 - VOICE OBJECT DETECTION")
        logger.info("=" * 60)
        
        # Initialize components
        self._initialize_components()
    
    def _load_config(self):
        """Load configuration from environment"""
        load_dotenv()
        
        config = {
            # Wake word settings
            'wake_word': os.getenv('WAKE_WORD', 'iris'),
            'wake_word_threshold': float(os.getenv('WAKE_WORD_THRESHOLD', '0.6')),
            
            # Whisper settings
            'whisper_model': os.getenv('WHISPER_MODEL', 'small'),
            'whisper_device': os.getenv('WHISPER_DEVICE', 'cpu'),
            'whisper_language': os.getenv('WHISPER_LANGUAGE', 'en'),
            
            # YOLO settings
            'yolo_model': os.getenv('YOLO_MODEL', 'models/yolo11n.pt'),
            'yolo_confidence': float(os.getenv('YOLO_CONFIDENCE', '0.5')),
            
            # Camera settings
            'camera_type': os.getenv('CAMERA_TYPE', 'usb'),  # 'picamera' or 'usb'
            'camera_index': int(os.getenv('CAMERA_INDEX', '0')),
            'camera_width': int(os.getenv('CAMERA_WIDTH', '640')),
            'camera_height': int(os.getenv('CAMERA_HEIGHT', '480')),
            
            # TTS settings
            'tts_engine': os.getenv('TTS_ENGINE', 'pyttsx3'),
            'tts_rate': int(os.getenv('TTS_RATE', '150')),
            'tts_volume': float(os.getenv('TTS_VOLUME', '1.0')),
            
            # Audio settings
            'sample_rate': int(os.getenv('SAMPLE_RATE', '16000')),
        }
        
        logger.info(f"Configuration loaded:")
        logger.info(f"  Wake word: '{config['wake_word']}'")
        logger.info(f"  Whisper model: {config['whisper_model']}")
        logger.info(f"  YOLO model: {config['yolo_model']}")
        logger.info(f"  Camera: {config['camera_type']}")
        
        return config
    
    def _initialize_components(self):
        """Initialize all components"""
        try:
            # Initialize Text-to-Speech
            logger.info("Initializing Text-to-Speech...")
            self.tts = TextToSpeech(
                engine=self.config['tts_engine'],
                rate=self.config['tts_rate'],
                volume=self.config['tts_volume']
            )
            
            # Initialize YOLO Detector
            logger.info("Initializing YOLO Object Detector...")
            self.yolo = YOLODetector(
                model_path=self.config['yolo_model'],
                confidence_threshold=self.config['yolo_confidence'],
                camera_type=self.config['camera_type'],
                camera_index=self.config['camera_index'],
                width=self.config['camera_width'],
                height=self.config['camera_height']
            )
            
            # Initialize Speech Recognition
            logger.info("Initializing Whisper Speech Recognition...")
            self.speech_recognizer = WhisperRecognizer(
                model_size=self.config['whisper_model'],
                device=self.config['whisper_device'],
                language=self.config['whisper_language'],
                sample_rate=self.config['sample_rate'],
                use_faster_whisper=True
            )
            
            # Initialize Wake Word Detector
            logger.info("Initializing Offline Wake Word Detector...")
            self.wake_detector = OfflineWakeWordDetector(
                wake_word=self.config['wake_word'],
                model_size='tiny',  # Fast model for wake word
                sample_rate=self.config['sample_rate'],
                chunk_duration=2.0
            )
            
            logger.info("=" * 60)
            logger.info("✅ All components initialized successfully!")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Error initializing components: {e}")
            raise
    
    def process_voice_command(self, command_text):
        """
        Process voice command and generate response
        
        Args:
            command_text: Transcribed command text
            
        Returns:
            str: Response text
        """
        command_lower = command_text.lower().strip()
        
        logger.info(f"Processing command: '{command_text}'")
        
        # Commands that trigger object detection
        detect_triggers = [
            'what do you see',
            'detect objects',
            'what objects',
            'what is there',
            'describe',
            'look',
            'see',
            'show me',
            'what\'s there',
            'what\'s in front',
            'how many objects'
        ]
        
        should_detect = any(trigger in command_lower for trigger in detect_triggers)
        
        if should_detect:
            # Perform object detection
            logger.info("Triggering object detection...")
            results = self.yolo.detect_objects(capture_new=True)
            
            if results and results['count'] > 0:
                response = results['summary']
                
                # Add detailed info if requested
                if 'how many' in command_lower:
                    response = f"I detected {results['count']} objects total. {results['summary']}"
                
                logger.info(f"Detection result: {response}")
                return response
            else:
                response = "I don't see any objects in the frame."
                logger.info(response)
                return response
        else:
            # General response
            response = "I'm ready to help. Ask me 'what do you see' to detect objects."
            return response
    
    def run(self):
        """Run the main application loop"""
        self.running = True
        
        # Greeting
        greeting = f"Voice activated object detector ready. Say {self.config['wake_word']} to activate me."
        print(f"\n{greeting}\n")
        self.tts.speak(greeting)
        
        print("=" * 60)
        print(f"👂 Listening for wake word '{self.config['wake_word'].upper()}'...")
        print("(Press Ctrl+C to exit)")
        print("=" * 60)
        
        try:
            while self.running:
                # Listen for wake word
                logger.info(f"Waiting for wake word '{self.config['wake_word']}'...")
                detected = self.wake_detector.listen_for_wake_word()
                
                if not detected:
                    continue
                
                # Wake word detected
                print("\n" + "=" * 60)
                print(f"✅ Wake word '{self.config['wake_word'].upper()}' detected!")
                print("=" * 60)
                
                # Acknowledge
                self.tts.speak("Yes?")
                
                # Listen for command
                print("\n🎤 Listening for your command...")
                logger.info("Recording command...")
                
                try:
                    audio_data = self.speech_recognizer.record_audio(
                        duration=5,
                        silence_threshold=0.01,
                        max_silence_duration=2.0
                    )
                    
                    # Transcribe command
                    print("⚡ Processing speech...")
                    command_text = self.speech_recognizer.transcribe(audio_data)
                    
                    if command_text:
                        print(f"\n💬 You said: '{command_text}'")
                        
                        # Process command
                        response = self.process_voice_command(command_text)
                        
                        # Speak response
                        print(f"🤖 Response: {response}\n")
                        self.tts.speak(response)
                    else:
                        print("❌ Could not understand audio")
                        self.tts.speak("Sorry, I didn't catch that.")
                    
                except Exception as e:
                    logger.error(f"Error processing command: {e}")
                    self.tts.speak("Sorry, I encountered an error.")
                
                # Ready for next command
                print("\n" + "=" * 60)
                print(f"👂 Listening for wake word '{self.config['wake_word'].upper()}'...")
                print("=" * 60)
                
        except KeyboardInterrupt:
            print("\n\n✋ Shutting down...")
            self.stop()
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            self.stop()
    
    def stop(self):
        """Stop the application and cleanup"""
        self.running = False
        
        # Cleanup
        if hasattr(self, 'yolo'):
            self.yolo.release()
        
        if hasattr(self, 'wake_detector'):
            self.wake_detector.stop()
        
        logger.info("Application stopped")
        print("👋 Goodbye!")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Voice-Activated Object Detection for Raspberry Pi 5'
    )
    parser.add_argument('--config', help='Path to .env config file', default='.env')
    parser.add_argument('--camera', help='Camera type (picamera/usb)', default=None)
    parser.add_argument('--wake-word', help='Wake word to use', default=None)
    
    args = parser.parse_args()
    
    # Load environment
    if args.config and os.path.exists(args.config):
        load_dotenv(args.config)
    
    # Override config with command line args
    config_overrides = {}
    if args.camera:
        config_overrides['camera_type'] = args.camera
    if args.wake_word:
        config_overrides['wake_word'] = args.wake_word
    
    # Create and run app
    try:
        app = VoiceActivatedObjectDetector(config=config_overrides if config_overrides else None)
        app.run()
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
