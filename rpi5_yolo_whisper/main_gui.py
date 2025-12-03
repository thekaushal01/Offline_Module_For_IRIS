"""
GUI Application for Raspberry Pi 5
Voice-Activated Object Detection with Live Video Feed
Access via TigerVNC
"""

import os
import sys
import logging
import argparse
import time
import threading
import queue
from pathlib import Path
from dotenv import load_dotenv
import cv2
import numpy as np

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


class VoiceActivatedGUI:
    """GUI Application for voice-activated object detection"""
    
    def __init__(self, config=None):
        """Initialize GUI application"""
        self.config = config or self._load_config()
        self.running = False
        self.detection_active = False
        self.current_frame = None
        self.detection_results = None
        self.status_message = "Initializing..."
        self.message_queue = queue.Queue()
        
        logger.info("=" * 60)
        logger.info("🖥️ GUI - VOICE OBJECT DETECTION")
        logger.info("=" * 60)
        
        # Initialize components
        self._initialize_components()
        
        # Create window
        self.window_name = "Voice-Activated Object Detection"
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, 1280, 720)
    
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
            'camera_type': os.getenv('CAMERA_TYPE', 'usb'),
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
                model_size='tiny',
                sample_rate=self.config['sample_rate'],
                chunk_duration=2.0
            )
            
            self.status_message = f"Ready! Say '{self.config['wake_word'].upper()}' to activate"
            logger.info("✅ All components initialized successfully!")
            
        except Exception as e:
            logger.error(f"Error initializing components: {e}")
            self.status_message = f"Error: {e}"
            raise
    
    def create_display_frame(self, camera_frame=None, results=None):
        """
        Create display frame with overlays
        
        Args:
            camera_frame: Camera frame with detections
            results: Detection results dictionary
            
        Returns:
            Display frame with UI overlays
        """
        # Create base frame
        if camera_frame is not None:
            display = camera_frame.copy()
        else:
            # Create blank frame
            display = np.zeros((720, 1280, 3), dtype=np.uint8)
            cv2.putText(display, "No Camera Feed", (500, 360),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 100, 100), 2)
        
        # Resize if needed
        h, w = display.shape[:2]
        if w != 1280 or h != 720:
            display = cv2.resize(display, (1280, 720))
        
        # Create overlay for UI elements
        overlay = display.copy()
        
        # Top bar - Status
        cv2.rectangle(overlay, (0, 0), (1280, 80), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, display, 0.3, 0, display)
        
        # Title
        cv2.putText(display, "Voice-Activated Object Detection", (20, 35),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Status message
        status_color = (0, 255, 0) if "Ready" in self.status_message else (255, 255, 255)
        cv2.putText(display, self.status_message, (20, 65),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 1)
        
        # Bottom bar - Instructions and results
        overlay = display.copy()
        cv2.rectangle(overlay, (0, 620), (1280, 720), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.8, display, 0.2, 0, display)
        
        # Instructions
        instructions = [
            f"Say '{self.config['wake_word'].upper()}' to activate",
            "Then say: 'What do you see?' or 'Detect objects'",
            "Press 'Q' to quit | Press 'D' to detect now | Press 'S' to save image"
        ]
        
        y_pos = 645
        for instruction in instructions:
            cv2.putText(display, instruction, (20, y_pos),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
            y_pos += 25
        
        # Display detection results if available
        if results and results['count'] > 0:
            # Right side panel for detection info
            overlay = display.copy()
            cv2.rectangle(overlay, (980, 80), (1280, 620), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.7, display, 0.3, 0, display)
            
            # Detection summary
            cv2.putText(display, "Detections:", (1000, 110),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.putText(display, f"Total: {results['count']}", (1000, 140),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
            
            # List detected objects
            y_pos = 170
            object_counts = results.get('class_counts', {})
            for obj_name, count in list(object_counts.items())[:15]:  # Max 15 items
                text = f"{obj_name}: {count}"
                cv2.putText(display, text, (1000, y_pos),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                y_pos += 25
            
            # Summary text
            if 'summary' in results:
                summary = results['summary']
                # Wrap text
                words = summary.split()
                lines = []
                current_line = ""
                for word in words:
                    test_line = current_line + " " + word if current_line else word
                    if len(test_line) < 25:
                        current_line = test_line
                    else:
                        lines.append(current_line)
                        current_line = word
                if current_line:
                    lines.append(current_line)
                
                y_pos = 550
                for line in lines[:3]:  # Max 3 lines
                    cv2.putText(display, line, (1000, y_pos),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.45, (100, 255, 255), 1)
                    y_pos += 20
        
        # Wake word indicator
        if self.detection_active:
            cv2.circle(display, (1250, 30), 15, (0, 0, 255), -1)
            cv2.putText(display, "LISTENING", (1140, 35),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        
        return display
    
    def voice_listener_thread(self):
        """Background thread for listening to wake word and commands"""
        while self.running:
            try:
                # Listen for wake word
                self.status_message = f"Listening for '{self.config['wake_word'].upper()}'..."
                logger.info("Waiting for wake word...")
                
                detected = self.wake_detector.listen_for_wake_word()
                
                if not detected or not self.running:
                    continue
                
                # Wake word detected
                self.detection_active = True
                self.status_message = f"✅ '{self.config['wake_word'].upper()}' detected! Listening..."
                logger.info("Wake word detected!")
                
                # Acknowledge
                self.tts.speak("Yes?")
                
                # Listen for command
                try:
                    audio_data = self.speech_recognizer.record_audio(
                        duration=5,
                        silence_threshold=0.01,
                        max_silence_duration=2.0
                    )
                    
                    # Transcribe
                    self.status_message = "Processing speech..."
                    command_text = self.speech_recognizer.transcribe(audio_data)
                    
                    if command_text:
                        logger.info(f"Command: {command_text}")
                        self.status_message = f"You said: '{command_text}'"
                        
                        # Process command
                        response = self.process_command(command_text)
                        
                        # Speak response
                        self.tts.speak(response)
                        
                        # Show response
                        self.status_message = f"Response: {response}"
                        time.sleep(3)  # Display for 3 seconds
                    else:
                        self.status_message = "Could not understand"
                        self.tts.speak("Sorry, I didn't catch that.")
                        time.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Error processing command: {e}")
                    self.status_message = "Error processing command"
                
                self.detection_active = False
                
            except Exception as e:
                logger.error(f"Error in voice listener: {e}")
                time.sleep(1)
    
    def process_command(self, command_text):
        """Process voice command"""
        command_lower = command_text.lower().strip()
        
        # Commands that trigger object detection
        detect_triggers = [
            'what do you see', 'detect objects', 'what objects',
            'what is there', 'describe', 'look', 'see', 'show me',
            'what\'s there', 'what\'s in front', 'how many objects'
        ]
        
        should_detect = any(trigger in command_lower for trigger in detect_triggers)
        
        if should_detect:
            # Perform detection
            self.status_message = "Detecting objects..."
            results = self.yolo.detect_objects(capture_new=True)
            
            if results and results['count'] > 0:
                self.detection_results = results
                self.current_frame = results['frame']
                response = results['summary']
                
                if 'how many' in command_lower:
                    response = f"I detected {results['count']} objects total. {results['summary']}"
                
                return response
            else:
                return "I don't see any objects in the frame."
        else:
            return "I'm ready to help. Ask me 'what do you see' to detect objects."
    
    def manual_detection(self):
        """Trigger manual detection (key press)"""
        self.status_message = "Detecting objects..."
        results = self.yolo.detect_objects(capture_new=True)
        
        if results:
            self.detection_results = results
            self.current_frame = results['frame']
            if results['count'] > 0:
                self.status_message = f"Found {results['count']} objects: {results['summary']}"
                self.tts.speak(results['summary'])
            else:
                self.status_message = "No objects detected"
                self.tts.speak("I don't see any objects")
        else:
            self.status_message = "Detection failed"
    
    def run(self):
        """Run the GUI application"""
        self.running = True
        
        # Start voice listener thread
        voice_thread = threading.Thread(target=self.voice_listener_thread, daemon=True)
        voice_thread.start()
        
        # Initial greeting
        greeting = f"Voice activated object detector ready. Say {self.config['wake_word']} to activate me."
        self.tts.speak(greeting)
        
        logger.info("GUI Application started")
        logger.info("Press 'Q' to quit, 'D' to detect, 'S' to save")
        
        # FPS calculation
        fps_start_time = time.time()
        fps_counter = 0
        fps = 0
        
        try:
            while self.running:
                # Capture frame
                frame = self.yolo.capture_frame()
                
                if frame is not None:
                    # Use detection results if available, otherwise show live feed
                    if self.current_frame is not None:
                        display_frame = self.create_display_frame(
                            self.current_frame, 
                            self.detection_results
                        )
                        # Clear after some time
                        if time.time() - getattr(self, 'detection_time', 0) > 10:
                            self.current_frame = None
                            self.detection_results = None
                    else:
                        # Show live feed
                        display_frame = self.create_display_frame(frame, None)
                        self.detection_time = time.time()
                else:
                    display_frame = self.create_display_frame(None, None)
                
                # Calculate FPS
                fps_counter += 1
                if time.time() - fps_start_time >= 1.0:
                    fps = fps_counter
                    fps_counter = 0
                    fps_start_time = time.time()
                
                # Add FPS to display
                cv2.putText(display_frame, f"FPS: {fps}", (1200, 65),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)
                
                # Show frame
                cv2.imshow(self.window_name, display_frame)
                
                # Handle key press
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q') or key == ord('Q'):
                    logger.info("Quit key pressed")
                    break
                elif key == ord('d') or key == ord('D'):
                    logger.info("Manual detection triggered")
                    self.manual_detection()
                elif key == ord('s') or key == ord('S'):
                    # Save current frame
                    filename = f"detection_{int(time.time())}.jpg"
                    cv2.imwrite(filename, display_frame)
                    self.status_message = f"Saved: {filename}"
                    logger.info(f"Frame saved: {filename}")
                
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the application"""
        logger.info("Stopping application...")
        self.running = False
        
        # Cleanup
        if hasattr(self, 'yolo'):
            self.yolo.release()
        
        if hasattr(self, 'wake_detector'):
            self.wake_detector.stop()
        
        cv2.destroyAllWindows()
        logger.info("Application stopped")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='GUI Voice-Activated Object Detection for Raspberry Pi 5'
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
        app = VoiceActivatedGUI(config=config_overrides if config_overrides else None)
        app.run()
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
