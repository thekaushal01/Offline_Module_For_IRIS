"""
Mobile-Ready GUI Object Detector with Voice Commands
Designed for mobile app integration with enhanced controls
"""

import os
import sys
import cv2
import time
import logging
import threading
from collections import Counter
from dotenv import load_dotenv

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from smart_yolo_detector import SmartYOLODetector
from offline_tts import TextToSpeech
from offline_wake_word import OfflineWakeWordDetector
from whisper_stt import WhisperRecognizer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MobileGUIDetector:
    """Mobile-ready GUI detector with voice commands and enhanced controls"""
    
    def __init__(self, config=None):
        """Initialize mobile GUI detector"""
        self.config = config or self._load_config()
        
        # Initialize components
        logger.info("Initializing components...")
        self._initialize_components()
        
        # Detection state
        self.running = False
        self.detecting = False
        self.voice_listening = False
        self.last_announcement = time.time()
        self.announcement_cooldown = 3.0
        self.last_detected_objects = set()
        
        # Statistics
        self.total_detections = 0
        self.session_start = time.time()
        
        # Create GUI
        self._create_gui()
        
        logger.info("✅ Mobile GUI Object Detector initialized")
    
    def _load_config(self):
        """Load configuration from .env"""
        load_dotenv()
        
        config = {
            'yolo_model': os.getenv('YOLO_MODEL', 'models/yolo11n.pt'),
            'yolo_confidence': float(os.getenv('YOLO_CONFIDENCE', '0.5')),
            'camera_type': os.getenv('CAMERA_TYPE', 'picamera'),
            'camera_index': int(os.getenv('CAMERA_INDEX', '0')),
            'camera_width': int(os.getenv('CAMERA_WIDTH', '640')),
            'camera_height': int(os.getenv('CAMERA_HEIGHT', '480')),
            'tts_engine': os.getenv('TTS_ENGINE', 'pyttsx3'),
            'tts_rate': int(os.getenv('TTS_RATE', '150')),
            'tts_volume': float(os.getenv('TTS_VOLUME', '1.0')),
            'wake_word': os.getenv('WAKE_WORD', 'iris'),
            'whisper_model': os.getenv('WHISPER_MODEL', 'tiny'),
            'whisper_fast_mode': os.getenv('WHISPER_FAST_MODE', 'true').lower() == 'true',
            'sample_rate': int(os.getenv('SAMPLE_RATE', '16000')),
        }
        
        return config
    
    def _initialize_components(self):
        """Initialize all components"""
        # Initialize TTS
        logger.info("Initializing Text-to-Speech...")
        self.tts = TextToSpeech(
            engine=self.config['tts_engine'],
            rate=self.config['tts_rate'],
            volume=self.config['tts_volume']
        )
        
        # Initialize YOLO
        logger.info("Initializing YOLO detector...")
        self.yolo = SmartYOLODetector(
            model_path=self.config['yolo_model'],
            confidence_threshold=self.config['yolo_confidence'],
            camera_type=self.config['camera_type'],
            camera_index=self.config['camera_index'],
            width=self.config['camera_width'],
            height=self.config['camera_height']
        )
        
        # Initialize Speech Recognition
        logger.info("Initializing Whisper...")
        self.speech_recognizer = WhisperRecognizer(
            model_size=self.config['whisper_model'],
            device='cpu',
            sample_rate=self.config['sample_rate'],
            use_faster_whisper=True,
            fast_mode=self.config['whisper_fast_mode']
        )
        
        # Initialize Wake Word Detector
        logger.info("Initializing Wake Word Detector...")
        self.wake_detector = OfflineWakeWordDetector(
            wake_word=self.config['wake_word'],
            model_size='tiny',
            sample_rate=self.config['sample_rate']
        )
        
        # Initialize Sensors (Pi 5 with lgpio)
        self.ultrasonic = None
        self.ultrasonic_monitor = None
        self.imu = None
        self.fall_detector = None
        self.fall_monitor = None
        
        try:
            logger.info("Initializing HC-SR04 ultrasonic sensor...")
            from ultrasonic_sensor_lgpio import UltrasonicSensor, UltrasonicMonitor
            
            self.ultrasonic = UltrasonicSensor(
                trig_pin=int(os.getenv('ULTRASONIC_TRIG_PIN', '23')),
                echo_pin=int(os.getenv('ULTRASONIC_ECHO_PIN', '24'))
            )
            
            self.ultrasonic_monitor = UltrasonicMonitor(
                self.ultrasonic,
                update_interval=0.2  # 5Hz updates
            )
            self.ultrasonic_monitor.add_callback(self._on_distance_change)
            self.ultrasonic_monitor.start()
            
            logger.info("✅ Ultrasonic sensor ready")
        except Exception as e:
            logger.warning(f"Ultrasonic sensor not available: {e}")
        
        try:
            logger.info("Initializing MPU9250 fall detector...")
            from fall_detector import MPU9250, FallDetector, FallMonitor
            
            self.imu = MPU9250(address=int(os.getenv('MPU9250_ADDRESS', '0x68'), 16))
            
            self.fall_detector = FallDetector(
                self.imu,
                tts_callback=lambda msg: threading.Thread(
                    target=self.tts.speak, args=(msg,), daemon=True
                ).start()
            )
            
            self.fall_monitor = FallMonitor(
                self.fall_detector,
                sample_rate=50  # 50Hz sampling
            )
            self.fall_monitor.add_fall_callback(self._on_fall_detected)
            self.fall_monitor.start()
            
            logger.info("✅ Fall detection ready")
        except Exception as e:
            logger.warning(f"Fall detector not available: {e}")
    
    def _create_gui(self):
        """Create mobile-ready GUI interface"""
        self.root = tk.Tk()
        self.root.title("🎯 Mobile Object Detector")
        self.root.geometry("1000x800")
        self.root.configure(bg='#1e1e1e')
        
        # Style configuration
        style = ttk.Style()
        style.theme_use('clam')
        
        # Custom colors
        bg_dark = '#1e1e1e'
        bg_medium = '#2d2d2d'
        fg_light = '#ffffff'
        accent_blue = '#0078d4'
        accent_green = '#107c10'
        
        style.configure('Dark.TFrame', background=bg_dark)
        style.configure('Medium.TFrame', background=bg_medium)
        style.configure('Title.TLabel', background=bg_dark, foreground=fg_light, 
                       font=('Arial', 18, 'bold'))
        style.configure('Info.TLabel', background=bg_medium, foreground=fg_light, 
                       font=('Arial', 11))
        style.configure('Status.TLabel', background=bg_medium, foreground='#00ff00', 
                       font=('Arial', 10, 'bold'))
        style.configure('Control.TButton', font=('Arial', 11, 'bold'))
        
        # Main container
        main_frame = ttk.Frame(self.root, style='Dark.TFrame', padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # ===== HEADER =====
        header_frame = ttk.Frame(main_frame, style='Dark.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(
            header_frame,
            text="🎯 AI Object Detector",
            style='Title.TLabel'
        )
        title_label.pack()
        
        # ===== VIDEO FEED =====
        video_container = ttk.LabelFrame(main_frame, text="📹 Live Camera Feed", 
                                        padding="5", style='Medium.TFrame')
        video_container.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create canvas with scrollbar for scrollable video
        canvas_frame = ttk.Frame(video_container, style='Medium.TFrame')
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.video_canvas = tk.Canvas(canvas_frame, bg='black', highlightthickness=0)
        scrollbar_y = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.video_canvas.yview)
        scrollbar_x = ttk.Scrollbar(video_container, orient=tk.HORIZONTAL, command=self.video_canvas.xview)
        
        self.video_canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.video_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Video label inside canvas
        self.video_label = ttk.Label(self.video_canvas, text="Camera initializing...",
                                     background='black', foreground='white')
        self.video_window = self.video_canvas.create_window((0, 0), window=self.video_label, anchor=tk.NW)
        
        # ===== CONTROLS PANEL =====
        controls_frame = ttk.LabelFrame(main_frame, text="⚙️ Controls", 
                                       padding="10", style='Medium.TFrame')
        controls_frame.pack(fill=tk.X, pady=5)
        
        # Row 1: Main action buttons
        btn_row1 = ttk.Frame(controls_frame, style='Medium.TFrame')
        btn_row1.pack(fill=tk.X, pady=5)
        
        self.voice_button = tk.Button(
            btn_row1,
            text="🎤 Voice Control: OFF",
            command=self.toggle_voice_control,
            bg='#d13438',
            fg='white',
            font=('Arial', 12, 'bold'),
            height=2,
            relief=tk.RAISED,
            borderwidth=3
        )
        self.voice_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.manual_button = tk.Button(
            btn_row1,
            text="▶ Manual Start",
            command=self.toggle_detection,
            bg='#107c10',
            fg='white',
            font=('Arial', 12, 'bold'),
            height=2,
            relief=tk.RAISED,
            borderwidth=3
        )
        self.manual_button.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Row 2: Secondary buttons
        btn_row2 = ttk.Frame(controls_frame, style='Medium.TFrame')
        btn_row2.pack(fill=tk.X, pady=5)
        
        announce_btn = tk.Button(
            btn_row2,
            text="🔊 Announce",
            command=self.announce_objects,
            bg='#0078d4',
            fg='white',
            font=('Arial', 10, 'bold'),
            relief=tk.RAISED
        )
        announce_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        reset_btn = tk.Button(
            btn_row2,
            text="🔄 Reset Stats",
            command=self.reset_stats,
            bg='#8a8a8a',
            fg='white',
            font=('Arial', 10, 'bold'),
            relief=tk.RAISED
        )
        reset_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        quit_btn = tk.Button(
            btn_row2,
            text="❌ Quit",
            command=self.quit,
            bg='#d13438',
            fg='white',
            font=('Arial', 10, 'bold'),
            relief=tk.RAISED
        )
        quit_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # ===== SETTINGS PANEL =====
        settings_frame = ttk.LabelFrame(main_frame, text="🎛️ Detection Settings", 
                                       padding="10", style='Medium.TFrame')
        settings_frame.pack(fill=tk.X, pady=5)
        
        # Confidence threshold
        conf_frame = ttk.Frame(settings_frame, style='Medium.TFrame')
        conf_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(conf_frame, text="Confidence Threshold:", 
                 style='Info.TLabel').pack(side=tk.LEFT, padx=5)
        
        self.confidence_var = tk.DoubleVar(value=self.config['yolo_confidence'])
        self.confidence_slider = ttk.Scale(
            conf_frame,
            from_=0.1,
            to=0.9,
            orient=tk.HORIZONTAL,
            variable=self.confidence_var,
            command=self.update_confidence
        )
        self.confidence_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.confidence_value_label = ttk.Label(
            conf_frame,
            text=f"{self.config['yolo_confidence']:.2f}",
            style='Info.TLabel',
            width=6
        )
        self.confidence_value_label.pack(side=tk.LEFT, padx=5)
        
        # NMS threshold (IoU)
        nms_frame = ttk.Frame(settings_frame, style='Medium.TFrame')
        nms_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(nms_frame, text="NMS IoU Threshold:", 
                 style='Info.TLabel').pack(side=tk.LEFT, padx=5)
        
        self.nms_var = tk.DoubleVar(value=0.45)
        self.nms_slider = ttk.Scale(
            nms_frame,
            from_=0.1,
            to=0.9,
            orient=tk.HORIZONTAL,
            variable=self.nms_var,
            command=self.update_nms
        )
        self.nms_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.nms_value_label = ttk.Label(
            nms_frame,
            text="0.45",
            style='Info.TLabel',
            width=6
        )
        self.nms_value_label.pack(side=tk.LEFT, padx=5)
        
        # Field of View / Image Size
        fov_frame = ttk.Frame(settings_frame, style='Medium.TFrame')
        fov_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(fov_frame, text="Field of View:", 
                 style='Info.TLabel').pack(side=tk.LEFT, padx=5)
        
        self.fov_var = tk.StringVar(value="640x480")
        fov_options = ["320x240", "640x480", "800x600", "1280x720"]
        self.fov_combo = ttk.Combobox(
            fov_frame,
            textvariable=self.fov_var,
            values=fov_options,
            state='readonly',
            width=12
        )
        self.fov_combo.pack(side=tk.LEFT, padx=5)
        self.fov_combo.bind('<<ComboboxSelected>>', self.update_fov)
        
        # Auto-announce checkbox
        self.auto_announce_var = tk.BooleanVar(value=True)
        auto_check = ttk.Checkbutton(
            settings_frame,
            text="🔊 Auto-announce new objects",
            variable=self.auto_announce_var,
            style='Info.TLabel'
        )
        auto_check.pack(anchor=tk.W, pady=5)
        
        # ===== STATISTICS PANEL =====
        stats_frame = ttk.LabelFrame(main_frame, text="📊 Detection Statistics", 
                                     padding="10", style='Medium.TFrame')
        stats_frame.pack(fill=tk.X, pady=5)
        
        stats_grid = ttk.Frame(stats_frame, style='Medium.TFrame')
        stats_grid.pack(fill=tk.X)
        
        # Detection info
        self.detection_label = ttk.Label(
            stats_grid,
            text="No objects detected",
            style='Info.TLabel',
            justify=tk.LEFT
        )
        self.detection_label.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=2)
        
        # Stats row 1
        ttk.Label(stats_grid, text="Objects:", 
                 style='Info.TLabel').grid(row=1, column=0, sticky=tk.W, padx=5)
        self.count_label = ttk.Label(stats_grid, text="0", style='Status.TLabel')
        self.count_label.grid(row=1, column=1, sticky=tk.W)
        
        ttk.Label(stats_grid, text="FPS:", 
                 style='Info.TLabel').grid(row=2, column=0, sticky=tk.W, padx=5)
        self.fps_label = ttk.Label(stats_grid, text="0.0", style='Status.TLabel')
        self.fps_label.grid(row=2, column=1, sticky=tk.W)
        
        ttk.Label(stats_grid, text="Total Detected:", 
                 style='Info.TLabel').grid(row=3, column=0, sticky=tk.W, padx=5)
        self.total_label = ttk.Label(stats_grid, text="0", style='Status.TLabel')
        self.total_label.grid(row=3, column=1, sticky=tk.W)
        
        ttk.Label(stats_grid, text="Session Time:", 
                 style='Info.TLabel').grid(row=4, column=0, sticky=tk.W, padx=5)
        self.time_label = ttk.Label(stats_grid, text="00:00", style='Status.TLabel')
        self.time_label.grid(row=4, column=1, sticky=tk.W)
        
        # ===== VOICE STATUS PANEL (NEW) =====
        voice_status_frame = ttk.LabelFrame(main_frame, text="🎤 Voice Status", 
                                           padding="10", style='Medium.TFrame')
        voice_status_frame.pack(fill=tk.X, pady=5)
        
        self.voice_status_label = ttk.Label(
            voice_status_frame,
            text="Voice control is OFF",
            style='Info.TLabel',
            font=('Arial', 12, 'bold'),
            foreground='#8a8a8a'
        )
        self.voice_status_label.pack(fill=tk.X, pady=5)
        
        # ===== STATUS BAR =====
        self.status_label = ttk.Label(
            main_frame,
            text="📍 Ready • Enable voice control or use manual start",
            style='Info.TLabel',
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=5
        )
        self.status_label.pack(fill=tk.X, pady=(5, 0))
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.quit)
    
    def update_confidence(self, value):
        """Update confidence threshold"""
        conf = float(value)
        self.yolo.confidence_threshold = conf
        self.confidence_value_label.config(text=f"{conf:.2f}")
    
    def update_nms(self, value):
        """Update NMS IoU threshold"""
        nms = float(value)
        self.nms_value_label.config(text=f"{nms:.2f}")
        # Note: YOLO's NMS threshold can be updated if needed
    
    def update_fov(self, event=None):
        """Update field of view (camera resolution)"""
        fov = self.fov_var.get()
        width, height = map(int, fov.split('x'))
        logger.info(f"FOV changed to {width}x{height}")
        
        # Stop detection if running
        was_detecting = self.detecting
        if self.detecting:
            self.stop_detection()
            time.sleep(0.5)
        
        # Reinitialize camera with new resolution
        try:
            self.yolo.release()
            self.yolo = SmartYOLODetector(
                model_path=self.config['yolo_model'],
                confidence_threshold=self.config['yolo_confidence'],
                camera_type=self.config['camera_type'],
                camera_index=self.config['camera_index'],
                width=width,
                height=height
            )
            self.status_label.config(text=f"📐 FOV updated to {width}x{height}")
            logger.info(f"Camera reinitialized with {width}x{height}")
            
            # Restart detection if it was running
            if was_detecting:
                time.sleep(0.5)
                self.start_detection()
        except Exception as e:
            logger.error(f"Failed to update FOV: {e}")
            self.status_label.config(text=f"❌ Failed to update FOV: {e}")
    
    def toggle_voice_control(self):
        """Toggle voice control on/off"""
        if not self.voice_listening:
            self.start_voice_control()
        else:
            self.stop_voice_control()
    
    def start_voice_control(self):
        """Start listening for voice commands"""
        if self.voice_listening:
            return
        
        try:
            self.voice_listening = True
            self.voice_button.config(
                text="🎤 Voice Control: ON",
                bg='#107c10'
            )
            self.voice_status_label.config(
                text="🎤 Listening for 'IRIS' wake word...",
                foreground='#00ff00'
            )
            self.status_label.config(
                text="🎤 Voice control active • Say 'IRIS' then 'START' or 'STOP'"
            )
            
            # Start voice thread
            self.voice_thread = threading.Thread(target=self._voice_loop, daemon=True)
            self.voice_thread.start()
            
            logger.info("✅ Voice control started successfully")
            threading.Thread(target=self.tts.speak, args=("Voice control activated",), daemon=True).start()
            
        except Exception as e:
            logger.error(f"Failed to start voice control: {e}")
            self.voice_listening = False
            self.voice_button.config(
                text="🎤 Voice Control: OFF",
                bg='#d13438'
            )
            self.voice_status_label.config(
                text=f"❌ Error: {e}",
                foreground='#ff0000'
            )
            self.status_label.config(text=f"❌ Voice control error: {e}")
    
    def stop_voice_control(self):
        """Stop listening for voice commands"""
        self.voice_listening = False
        self.voice_button.config(
            text="🎤 Voice Control: OFF",
            bg='#d13438'
        )
        self.voice_status_label.config(
            text="Voice control is OFF",
            foreground='#8a8a8a'
        )
        self.status_label.config(text="📍 Voice control stopped")
        logger.info("Voice control stopped")
    
    def _update_voice_status(self, text, color='#00ff00'):
        """Update voice status display"""
        self.voice_status_label.config(text=text, foreground=color)
    
    def _voice_loop(self):
        """Voice command loop"""
        while self.voice_listening:
            try:
                # Update status - listening for wake word
                self.root.after(0, self._update_voice_status, "🎤 Listening for 'IRIS'...", '#00ff00')
                logger.info("Listening for wake word 'IRIS'...")
                
                # Listen for wake word
                detected = self.wake_detector.listen_for_wake_word()
                
                if not detected or not self.voice_listening:
                    continue
                
                # Wake word detected!
                logger.info("✅ Wake word 'IRIS' detected!")
                
                # Pause detection while listening for command
                was_detecting = self.detecting
                if was_detecting:
                    logger.info("⏸️ Pausing detection to listen for command...")
                    self.detecting = False
                    time.sleep(0.2)  # Brief pause to let detection loop notice
                
                self.root.after(0, self._update_voice_status, "✅ IRIS detected! Say your command...", '#ffff00')
                self.root.after(0, self.status_label.config, 
                              {'text': "🎤 Wake word 'IRIS' detected! Listening for command..."})
                
                # Speak feedback to user
                threading.Thread(target=self.tts.speak, args=("Listening for command",), daemon=True).start()
                
                # Give user time to speak after wake word
                time.sleep(0.5)  # Slightly longer for TTS to start
                
                # Update status - recording command
                self.root.after(0, self._update_voice_status, "🎙️ Recording command...", '#ff9900')
                logger.info("Recording command...")
                
                # Listen for command with shorter duration for responsiveness
                audio_data = self.speech_recognizer.record_audio(
                    duration=3,  # Reduced from 5 to 3 seconds for faster response
                    silence_threshold=0.02,  # Slightly higher threshold
                    max_silence_duration=1.5  # Stop faster when user stops talking
                )
                
                if audio_data is None or len(audio_data) == 0:
                    logger.warning("No audio captured")
                    self.root.after(0, self._update_voice_status, "⚠️ No audio detected", '#ff9900')
                    self.root.after(0, self.status_label.config,
                                  {'text': "🎤 No audio detected, say 'IRIS' again"})
                    # Resume detection if it was paused
                    if was_detecting and not self.detecting:
                        logger.info("▶️ Resuming detection...")
                        self.detecting = True
                    time.sleep(1)
                    continue
                
                # Transcribe in background
                logger.info("Transcribing command...")
                self.root.after(0, self._update_voice_status, "⚙️ Processing speech...", '#0099ff')
                self.root.after(0, self.status_label.config,
                              {'text': "🎤 Processing your command..."})
                
                command_text = self.speech_recognizer.transcribe_audio(audio_data)
                
                if command_text and len(command_text.strip()) > 0:
                    logger.info(f"✅ Command recognized: '{command_text}'")
                    self.root.after(0, self._update_voice_status, 
                                  f"✅ Heard: '{command_text}'", '#00ff00')
                    # Process command (this will handle START/STOP)
                    self.root.after(0, self._process_voice_command, command_text, was_detecting)
                    time.sleep(2)  # Show result for 2 seconds
                else:
                    logger.warning(f"No text transcribed (command_text='{command_text}')")
                    self.root.after(0, self._update_voice_status, "❌ Could not understand", '#ff0000')
                    self.root.after(0, self.status_label.config,
                                  {'text': "🎤 Could not understand command, try again"})
                    # Resume detection if it was paused
                    if was_detecting and not self.detecting:
                        logger.info("▶️ Resuming detection after unclear command...")
                        self.detecting = True
                    time.sleep(1)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Voice loop error: {e}")
                self.root.after(0, self._update_voice_status, f"❌ Error: {str(e)}", '#ff0000')
                self.root.after(0, self.status_label.config,
                              {'text': f"🎤 Error: {str(e)}"})
                time.sleep(1)
    
    def _process_voice_command(self, command, was_detecting=False):
        """Process voice command - flexible matching for low-quality audio"""
        command_lower = command.lower().strip()
        
        logger.info(f"Processing command: '{command_lower}'")
        
        # Flexible matching for START commands
        # Handles misrecognitions like "start", "starred", "status", etc.
        start_keywords = [
            'start', 'detect', 'begin', 'go', 'run',
            'starred', 'starting', 'started',  # Common misrecognitions
            'stat', 'star',  # Partial matches
            'thank you', 'thanks',  # Very common Whisper hallucination for "START"
        ]
        
        # Flexible matching for STOP commands  
        # Handles misrecognitions like "stop", "stopped", "top", etc.
        stop_keywords = [
            'stop', 'end', 'pause', 'halt', 'finish',
            'stopped', 'stopping',  # Common misrecognitions
            'top', 'hop',  # Partial matches
        ]
        
        # Check for START command
        if any(word in command_lower for word in start_keywords):
            logger.info(f"✅ Matched START command from: '{command}'")
            self.status_label.config(text=f"✅ Starting detection: '{command}'")
            threading.Thread(target=self._speak_and_start, daemon=True).start()
            
        # Check for STOP command
        elif any(word in command_lower for word in stop_keywords):
            logger.info(f"✅ Matched STOP command from: '{command}'")
            self.status_label.config(text=f"✅ Stopping detection: '{command}'")
            threading.Thread(target=self._speak_and_stop, daemon=True).start()
            
        # Check for ANNOUNCE/WHAT commands
        elif any(phrase in command_lower for phrase in ['what', 'see', 'announce', 'tell', 'show']):
            logger.info(f"✅ Matched ANNOUNCE command from: '{command}'")
            self.status_label.config(text=f"✅ Announcing: '{command}'")
            self.announce_objects()
            # Resume detection if it was paused
            if was_detecting and not self.detecting:
                logger.info("▶️ Resuming detection after announce...")
                self.detecting = True
            
        # If nothing matches but command has any text, try to guess intent
        elif len(command_lower) > 0:
            logger.warning(f"⚠️ Unclear command: '{command}'")
            self.status_label.config(text=f"❓ Unclear command: '{command}' - Say START or STOP")
            self.tts.speak("Say START or STOP")
            # Resume detection if it was paused
            if was_detecting and not self.detecting:
                logger.info("▶️ Resuming detection after unclear command...")
                self.detecting = True
            
        else:
            logger.warning(f"❌ Empty or unrecognized command")
            self.status_label.config(text=f"❌ No command heard - Try again")
            self.tts.speak("No command heard")
            # Resume detection if it was paused
            if was_detecting and not self.detecting:
                logger.info("▶️ Resuming detection after empty command...")
                self.detecting = True
    
    def _speak_and_start(self):
        """Speak then start detection (non-blocking)"""
        self.tts.speak("Starting detection")
        self.root.after(0, self.start_detection)
    
    def _speak_and_stop(self):
        """Speak then stop detection (non-blocking)"""
        self.tts.speak("Stopping detection")
        self.root.after(0, self.stop_detection)
    
    def toggle_detection(self):
        """Toggle detection on/off (manual)"""
        if not self.detecting:
            self.start_detection()
        else:
            self.stop_detection()
    
    def start_detection(self):
        """Start continuous detection"""
        if self.detecting:
            return
        
        self.detecting = True
        self.manual_button.config(text="⏸ Stop Detection", bg='#d13438')
        self.status_label.config(text="🎯 Detection running...")
        
        # Start detection thread
        self.detection_thread = threading.Thread(target=self._detection_loop, daemon=True)
        self.detection_thread.start()
        
        logger.info("Detection started")
    
    def stop_detection(self):
        """Stop detection"""
        self.detecting = False
        self.manual_button.config(text="▶ Manual Start", bg='#107c10')
        self.status_label.config(text="⏸ Detection stopped")
        logger.info("Detection stopped")
    
    def _on_distance_change(self, distance_feet: float, description: str):
        """
        Callback for ultrasonic sensor distance changes
        Combines distance with YOLO detections for richer announcements
        """
        try:
            # Only announce if detection is active and last_detected_objects has content
            if self.detecting and self.last_detected_objects and self.auto_announce_var.get():
                current_time = time.time()
                
                # Cooldown to avoid spam
                if current_time - self.last_announcement < self.announcement_cooldown:
                    return
                
                # Get the most common object from recent detections
                if self.last_detected_objects:
                    most_common_object = list(self.last_detected_objects)[0]
                    
                    # Create combined announcement
                    if distance_feet < 6.0:  # Only announce for close objects
                        combined_message = f"{most_common_object} at {distance_feet:.1f} feet"
                        
                        # Speak in background thread
                        threading.Thread(
                            target=self.tts.speak,
                            args=(combined_message,),
                            daemon=True
                        ).start()
                        
                        self.last_announcement = current_time
                        logger.info(f"📢 Combined announcement: {combined_message}")
                        
                        # Emit event for app/SMTP
                        self._emit_event('distance_detection', {
                            'object': most_common_object,
                            'distance_feet': round(distance_feet, 1),
                            'description': description
                        })
        except Exception as e:
            logger.error(f"Distance callback error: {e}")
    
    def _on_fall_detected(self):
        """Callback for fall detection events"""
        try:
            logger.warning("🚨 FALL DETECTED!")
            
            # Visual alert in GUI
            self.root.after(0, lambda: self.status_label.config(
                text="🚨 FALL DETECTED!",
                foreground='#ff0000'
            ))
            
            # Reset status after 5 seconds
            def reset_status():
                time.sleep(5)
                self.root.after(0, lambda: self.status_label.config(
                    text="🎯 Detection running...",
                    foreground='#00ff00'
                ))
            
            threading.Thread(target=reset_status, daemon=True).start()
            
            # Emit critical event for app/SMTP
            self._emit_event('fall_detected', {
                'severity': 'critical',
                'timestamp': time.time()
            })
            
            logger.info("Fall event emitted to app")
            
        except Exception as e:
            logger.error(f"Fall callback error: {e}")
    
    def _emit_event(self, event_type: str, payload: dict):
        """
        Emit event to file for app to consume
        App can monitor this file and send SMTP alerts
        """
        try:
            import json
            event = {
                'timestamp': time.time(),
                'event': event_type,
                'payload': payload
            }
            
            event_file = os.getenv('EVENT_FILE', '/tmp/iris_events.jsonl')
            with open(event_file, 'a') as f:
                f.write(json.dumps(event) + '\n')
                
        except Exception as e:
            logger.error(f"Error emitting event: {e}")
    
    def _detection_loop(self):
        """Main detection loop - keeps camera feed running even when detection paused"""
        fps_time = time.time()
        fps_counter = 0
        
        while self.detecting or self.running:  # Keep running even if detection paused
            try:
                # Capture frame
                frame = self.yolo.capture_frame()
                if frame is None:
                    time.sleep(0.1)
                    continue
                
                # Only detect if actively detecting (not paused for voice command)
                if self.detecting:
                    # Detect objects
                    results = self.yolo.detect_objects(frame=frame, capture_new=False)
                    
                    if results:
                        # Draw detections
                        annotated_frame = self._draw_detections(frame, results['detections'])
                        
                        # Update GUI
                        self.root.after(0, self._update_display, annotated_frame, results)
                        
                        # Update stats
                        self.total_detections += results['count']
                        self.root.after(0, self.total_label.config, {'text': str(self.total_detections)})
                        
                        # Check for new objects and announce
                        if self.auto_announce_var.get():
                            self._check_and_announce(results)
                        
                        fps_counter += 1
                    else:
                        self.root.after(0, self._update_display, frame, None)
                else:
                    # Detection paused - just show camera feed without detection
                    self.root.after(0, self._update_display, frame, None)
                
                # Calculate FPS
                if time.time() - fps_time >= 1.0:
                    fps = fps_counter / (time.time() - fps_time)
                    self.root.after(0, self.fps_label.config, {'text': f"{fps:.1f}"})
                    fps_counter = 0
                    fps_time = time.time()
                
                # Update session time
                session_time = int(time.time() - self.session_start)
                mins, secs = divmod(session_time, 60)
                self.root.after(0, self.time_label.config, {'text': f"{mins:02d}:{secs:02d}"})
                
            except Exception as e:
                logger.error(f"Detection loop error: {e}")
                time.sleep(0.1)
    
    def _draw_detections(self, frame, detections):
        """Draw bounding boxes and labels"""
        annotated = frame.copy()
        
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            label = f"{det['class']} {det['confidence']:.2f}"
            
            # Draw box
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw label background
            (label_width, label_height), _ = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
            )
            cv2.rectangle(
                annotated,
                (x1, y1 - label_height - 10),
                (x1 + label_width, y1),
                (0, 255, 0),
                -1
            )
            
            # Draw label text
            cv2.putText(
                annotated,
                label,
                (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 0),
                2
            )
        
        return annotated
    
    def _update_display(self, frame, results):
        """Update GUI display"""
        # Convert frame to PhotoImage
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        
        # Don't resize - keep original size for scrolling
        # User can scroll if image is larger than display
        photo = ImageTk.PhotoImage(image=img)
        self.video_label.config(image=photo)
        self.video_label.image = photo
        
        # Update canvas scroll region to match image size
        self.video_canvas.config(scrollregion=self.video_canvas.bbox(tk.ALL))
        
        # Update detection info
        if results and results['count'] > 0:
            self.detection_label.config(text=results['summary'])
            self.count_label.config(text=str(results['count']))
        else:
            self.detection_label.config(text="No objects detected")
            self.count_label.config(text="0")
    
    def _check_and_announce(self, results):
        """Check for new objects and announce"""
        if not results or results['count'] == 0:
            return
        
        current_objects = set(results['classes'])
        new_objects = current_objects - self.last_detected_objects
        time_since_last = time.time() - self.last_announcement
        
        if new_objects and time_since_last >= self.announcement_cooldown:
            self.announce_objects(results)
            self.last_detected_objects = current_objects
            self.last_announcement = time.time()
        elif not new_objects:
            self.last_detected_objects = current_objects
    
    def announce_objects(self, results=None):
        """Announce detected objects"""
        if results is None:
            frame = self.yolo.capture_frame()
            if frame:
                results = self.yolo.detect_objects(frame=frame, capture_new=False)
        
        if results and results['count'] > 0:
            # Fix: Remove "I see" duplication - just announce the summary
            announcement = results['summary']
            logger.info(f"Announcing: {announcement}")
            threading.Thread(target=self.tts.speak, args=(announcement,), daemon=True).start()
            self.status_label.config(text=f"🔊 Announced: {results['summary']}")
        else:
            announcement = "I don't see any objects"
            threading.Thread(target=self.tts.speak, args=(announcement,), daemon=True).start()
            self.status_label.config(text="🔊 No objects to announce")
    
    def reset_stats(self):
        """Reset statistics"""
        self.total_detections = 0
        self.session_start = time.time()
        self.total_label.config(text="0")
        self.time_label.config(text="00:00")
        self.status_label.config(text="📊 Statistics reset")
        logger.info("Statistics reset")
    
    def quit(self):
        """Quit the application"""
        logger.info("Shutting down...")
        self.detecting = False
        self.voice_listening = False
        self.running = False
        
        # Cleanup sensors
        if self.ultrasonic_monitor:
            self.ultrasonic_monitor.stop()
        if self.ultrasonic:
            self.ultrasonic.cleanup()
        if self.fall_monitor:
            self.fall_monitor.stop()
        
        # Cleanup other components
        if hasattr(self, 'yolo'):
            self.yolo.release()
        if hasattr(self, 'wake_detector'):
            self.wake_detector.stop()
        
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """Run the GUI application"""
        self.running = True
        self.tts.speak("Mobile object detector ready")
        logger.info("Starting Mobile GUI...")
        self.root.mainloop()


def main():
    """Main entry point"""
    try:
        app = MobileGUIDetector()
        app.run()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
