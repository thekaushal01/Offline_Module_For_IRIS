"""
GUI Object Detector with TTS
Real-time camera feed with YOLO detection and voice announcements
"""

import os
import sys
import cv2
import time
import logging
import threading
from collections import Counter
from dotenv import load_dotenv

# Check if running on Raspberry Pi
try:
    import tkinter as tk
    from tkinter import ttk
    from PIL import Image, ImageTk
except ImportError:
    print("Installing required packages...")
    os.system("pip install pillow")
    import tkinter as tk
    from tkinter import ttk
    from PIL import Image, ImageTk

from yolo_detector import YOLODetector
from offline_tts import TextToSpeech

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GUIObjectDetector:
    """GUI-based object detector with TTS announcements"""
    
    def __init__(self, config=None):
        """Initialize GUI detector"""
        self.config = config or self._load_config()
        
        # Initialize TTS
        logger.info("Initializing Text-to-Speech...")
        self.tts = TextToSpeech(
            engine=self.config['tts_engine'],
            rate=self.config['tts_rate'],
            volume=self.config['tts_volume']
        )
        
        # Initialize YOLO
        logger.info("Initializing YOLO detector...")
        self.yolo = YOLODetector(
            model_path=self.config['yolo_model'],
            confidence_threshold=self.config['yolo_confidence'],
            camera_type=self.config['camera_type'],
            camera_index=self.config['camera_index'],
            width=self.config['camera_width'],
            height=self.config['camera_height']
        )
        
        # Detection state
        self.running = False
        self.detecting = False
        self.last_announcement = time.time()
        self.announcement_cooldown = 3.0  # seconds between announcements
        self.last_detected_objects = set()
        
        # Create GUI
        self._create_gui()
        
        logger.info("✅ GUI Object Detector initialized")
    
    def _load_config(self):
        """Load configuration from .env"""
        load_dotenv()
        
        config = {
            'yolo_model': os.getenv('YOLO_MODEL', 'models/yolo11n.pt'),
            'yolo_confidence': float(os.getenv('YOLO_CONFIDENCE', '0.5')),
            'camera_type': os.getenv('CAMERA_TYPE', 'usb'),
            'camera_index': int(os.getenv('CAMERA_INDEX', '0')),
            'camera_width': int(os.getenv('CAMERA_WIDTH', '640')),
            'camera_height': int(os.getenv('CAMERA_HEIGHT', '480')),
            'tts_engine': os.getenv('TTS_ENGINE', 'pyttsx3'),
            'tts_rate': int(os.getenv('TTS_RATE', '150')),
            'tts_volume': float(os.getenv('TTS_VOLUME', '1.0')),
        }
        
        return config
    
    def _create_gui(self):
        """Create the GUI interface"""
        self.root = tk.Tk()
        self.root.title("🎯 Object Detector with Voice")
        self.root.geometry("900x700")
        self.root.configure(bg='#2b2b2b')
        
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Info.TLabel', font=('Arial', 11))
        style.configure('Status.TLabel', font=('Arial', 10))
        
        # Title
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, pady=(0, 10), sticky=(tk.W, tk.E))
        
        title_label = ttk.Label(
            title_frame,
            text="🎯 Real-Time Object Detection with Voice Announcements",
            style='Title.TLabel'
        )
        title_label.pack()
        
        # Video frame
        video_frame = ttk.LabelFrame(main_frame, text="📹 Camera Feed", padding="5")
        video_frame.grid(row=1, column=0, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        video_frame.grid_rowconfigure(0, weight=1)
        video_frame.grid_columnconfigure(0, weight=1)
        
        self.video_label = ttk.Label(video_frame, text="Camera starting...")
        self.video_label.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Detection info frame
        info_frame = ttk.LabelFrame(main_frame, text="📊 Detection Info", padding="10")
        info_frame.grid(row=2, column=0, pady=5, sticky=(tk.W, tk.E))
        
        self.detection_label = ttk.Label(
            info_frame,
            text="No objects detected",
            style='Info.TLabel',
            justify=tk.LEFT
        )
        self.detection_label.pack(anchor=tk.W)
        
        self.count_label = ttk.Label(
            info_frame,
            text="Objects: 0",
            style='Status.TLabel'
        )
        self.count_label.pack(anchor=tk.W, pady=(5, 0))
        
        self.fps_label = ttk.Label(
            info_frame,
            text="FPS: 0.0",
            style='Status.TLabel'
        )
        self.fps_label.pack(anchor=tk.W)
        
        # Controls frame
        controls_frame = ttk.Frame(main_frame)
        controls_frame.grid(row=3, column=0, pady=10)
        
        self.detect_button = ttk.Button(
            controls_frame,
            text="▶ Start Detection",
            command=self.toggle_detection,
            width=20
        )
        self.detect_button.pack(side=tk.LEFT, padx=5)
        
        self.announce_button = ttk.Button(
            controls_frame,
            text="🔊 Announce Now",
            command=self.announce_objects,
            width=20
        )
        self.announce_button.pack(side=tk.LEFT, padx=5)
        
        quit_button = ttk.Button(
            controls_frame,
            text="❌ Quit",
            command=self.quit,
            width=15
        )
        quit_button.pack(side=tk.LEFT, padx=5)
        
        # Confidence slider
        slider_frame = ttk.LabelFrame(main_frame, text="⚙️ Settings", padding="10")
        slider_frame.grid(row=4, column=0, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Label(slider_frame, text="Confidence Threshold:").pack(side=tk.LEFT, padx=5)
        
        self.confidence_var = tk.DoubleVar(value=self.config['yolo_confidence'])
        self.confidence_slider = ttk.Scale(
            slider_frame,
            from_=0.1,
            to=0.9,
            orient=tk.HORIZONTAL,
            variable=self.confidence_var,
            command=self.update_confidence
        )
        self.confidence_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        self.confidence_value_label = ttk.Label(
            slider_frame,
            text=f"{self.config['yolo_confidence']:.2f}"
        )
        self.confidence_value_label.pack(side=tk.LEFT, padx=5)
        
        # Auto-announce checkbox
        self.auto_announce_var = tk.BooleanVar(value=True)
        auto_announce_check = ttk.Checkbutton(
            slider_frame,
            text="Auto-announce new objects",
            variable=self.auto_announce_var
        )
        auto_announce_check.pack(side=tk.LEFT, padx=20)
        
        # Status bar
        self.status_label = ttk.Label(
            main_frame,
            text="Ready to start detection",
            style='Status.TLabel',
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_label.grid(row=5, column=0, pady=(5, 0), sticky=(tk.W, tk.E))
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.quit)
    
    def update_confidence(self, value):
        """Update confidence threshold"""
        conf = float(value)
        self.yolo.confidence_threshold = conf
        self.confidence_value_label.config(text=f"{conf:.2f}")
    
    def toggle_detection(self):
        """Toggle detection on/off"""
        if not self.detecting:
            self.start_detection()
        else:
            self.stop_detection()
    
    def start_detection(self):
        """Start continuous detection"""
        if self.detecting:
            return
        
        self.detecting = True
        self.detect_button.config(text="⏸ Stop Detection")
        self.status_label.config(text="Detection running...")
        
        # Start detection thread
        self.detection_thread = threading.Thread(target=self._detection_loop, daemon=True)
        self.detection_thread.start()
        
        logger.info("Detection started")
        self.tts.speak("Detection started")
    
    def stop_detection(self):
        """Stop detection"""
        self.detecting = False
        self.detect_button.config(text="▶ Start Detection")
        self.status_label.config(text="Detection stopped")
        logger.info("Detection stopped")
    
    def _detection_loop(self):
        """Main detection loop running in separate thread"""
        fps_time = time.time()
        fps_counter = 0
        
        while self.detecting:
            try:
                # Capture frame
                frame = self.yolo.capture_frame()
                if frame is None:
                    time.sleep(0.1)
                    continue
                
                # Detect objects
                results = self.yolo.detect_objects(frame=frame, capture_new=False)
                
                if results:
                    # Draw detections
                    annotated_frame = self._draw_detections(frame, results['detections'])
                    
                    # Update GUI
                    self.root.after(0, self._update_display, annotated_frame, results)
                    
                    # Check for new objects and announce
                    if self.auto_announce_var.get():
                        self._check_and_announce(results)
                    
                    fps_counter += 1
                else:
                    # No detections
                    self.root.after(0, self._update_display, frame, None)
                
                # Calculate FPS
                if time.time() - fps_time >= 1.0:
                    fps = fps_counter / (time.time() - fps_time)
                    self.root.after(0, self.fps_label.config, {'text': f"FPS: {fps:.1f}"})
                    fps_counter = 0
                    fps_time = time.time()
                
            except Exception as e:
                logger.error(f"Error in detection loop: {e}")
                time.sleep(0.1)
    
    def _draw_detections(self, frame, detections):
        """Draw bounding boxes and labels on frame"""
        annotated = frame.copy()
        
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            label = f"{det['class']} {det['confidence']:.2f}"
            
            # Draw box
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw label background
            (label_width, label_height), _ = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
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
                0.5,
                (0, 0, 0),
                1
            )
        
        return annotated
    
    def _update_display(self, frame, results):
        """Update GUI display with frame and detection info"""
        # Convert frame to PhotoImage
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        
        # Resize to fit display
        display_width = 800
        aspect_ratio = img.height / img.width
        display_height = int(display_width * aspect_ratio)
        img = img.resize((display_width, display_height), Image.Resampling.LANCZOS)
        
        photo = ImageTk.PhotoImage(image=img)
        self.video_label.config(image=photo)
        self.video_label.image = photo  # Keep reference
        
        # Update detection info
        if results and results['count'] > 0:
            detection_text = results['summary']
            self.detection_label.config(text=detection_text)
            self.count_label.config(text=f"Objects: {results['count']}")
        else:
            self.detection_label.config(text="No objects detected")
            self.count_label.config(text="Objects: 0")
    
    def _check_and_announce(self, results):
        """Check for new objects and announce if found"""
        if not results or results['count'] == 0:
            return
        
        # Get current objects
        current_objects = set(results['classes'])
        
        # Check if there are new objects
        new_objects = current_objects - self.last_detected_objects
        
        # Check cooldown
        time_since_last = time.time() - self.last_announcement
        
        if new_objects and time_since_last >= self.announcement_cooldown:
            # Announce new objects
            self.announce_objects(results)
            self.last_detected_objects = current_objects
            self.last_announcement = time.time()
        elif not new_objects:
            # Update tracked objects even if not announcing
            self.last_detected_objects = current_objects
    
    def announce_objects(self, results=None):
        """Announce detected objects via TTS"""
        if results is None:
            # Capture and detect
            frame = self.yolo.capture_frame()
            if frame:
                results = self.yolo.detect_objects(frame=frame, capture_new=False)
        
        if results and results['count'] > 0:
            announcement = f"I see {results['summary']}"
            logger.info(f"Announcing: {announcement}")
            
            # Announce in separate thread to avoid blocking
            threading.Thread(
                target=self.tts.speak,
                args=(announcement,),
                daemon=True
            ).start()
            
            self.status_label.config(text=f"Announced: {results['summary']}")
        else:
            announcement = "I don't see any objects"
            logger.info(announcement)
            threading.Thread(
                target=self.tts.speak,
                args=(announcement,),
                daemon=True
            ).start()
            self.status_label.config(text="No objects to announce")
    
    def quit(self):
        """Quit the application"""
        logger.info("Shutting down...")
        self.detecting = False
        self.running = False
        
        # Cleanup
        if hasattr(self, 'yolo'):
            self.yolo.release()
        
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """Run the GUI application"""
        self.running = True
        
        # Welcome message
        self.tts.speak("Object detector ready")
        
        logger.info("Starting GUI...")
        self.root.mainloop()


def main():
    """Main entry point"""
    try:
        app = GUIObjectDetector()
        app.run()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
