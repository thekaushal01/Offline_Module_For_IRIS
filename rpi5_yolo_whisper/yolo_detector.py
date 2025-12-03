"""
YOLO Object Detection Module
Optimized for Raspberry Pi 5 with YOLO11n
"""

import os
import logging
import time
import cv2
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)

class YOLODetector:
    """YOLO11 object detector optimized for Raspberry Pi 5"""
    
    def __init__(self, 
                 model_path="models/yolo11n.pt",
                 confidence_threshold=0.5,
                 camera_type="picamera",
                 camera_index=0,
                 width=640,
                 height=480):
        """
        Initialize YOLO detector
        
        Args:
            model_path: Path to YOLO model file
            confidence_threshold: Minimum confidence for detections
            camera_type: 'picamera', 'usb', or None (no camera)
            camera_index: Camera device index
            width: Camera frame width
            height: Camera frame height
        """
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.camera_type = camera_type
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.model = None
        self.labels = None
        self.cap = None
        
        logger.info(f"Initializing YOLO detector with model: {model_path}")
        self._load_model()
        
        if camera_type:
            self._initialize_camera()
    
    def _load_model(self):
        """Load YOLO model"""
        try:
            from ultralytics import YOLO
            
            if not os.path.exists(self.model_path):
                logger.warning(f"Model not found at {self.model_path}")
                logger.info("Downloading YOLO11n model...")
                self.model = YOLO('yolo11n.pt')
                # Save to models directory
                os.makedirs('models', exist_ok=True)
                os.rename('yolo11n.pt', self.model_path)
            else:
                self.model = YOLO(self.model_path, task='detect')
            
            self.labels = self.model.names
            logger.info(f"✅ YOLO model loaded with {len(self.labels)} classes")
            
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            raise
    
    def _initialize_camera(self):
        """Initialize camera based on type"""
        try:
            if self.camera_type == 'picamera':
                logger.info("Initializing Raspberry Pi Camera...")
                try:
                    from picamera2 import Picamera2
                    self.cap = Picamera2()
                    config = self.cap.create_video_configuration(
                        main={"format": 'RGB888', "size": (self.width, self.height)}
                    )
                    self.cap.configure(config)
                    self.cap.start()
                    logger.info(f"✅ Pi Camera initialized ({self.width}x{self.height})")
                except ImportError:
                    logger.warning("picamera2 not available, falling back to USB camera")
                    self.camera_type = 'usb'
                    self._initialize_camera()
                    
            elif self.camera_type == 'usb':
                logger.info(f"Initializing USB camera {self.camera_index}...")
                self.cap = cv2.VideoCapture(self.camera_index)
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
                
                if not self.cap.isOpened():
                    raise RuntimeError(f"Failed to open camera {self.camera_index}")
                
                logger.info(f"✅ USB camera initialized ({self.width}x{self.height})")
                
        except Exception as e:
            logger.error(f"Failed to initialize camera: {e}")
            self.cap = None
    
    def capture_frame(self):
        """
        Capture a frame from camera
        
        Returns:
            numpy array: Captured frame in BGR format, or None if failed
        """
        if not self.cap:
            logger.error("Camera not initialized")
            return None
        
        try:
            if self.camera_type == 'picamera':
                frame_rgb = self.cap.capture_array()
                frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
            elif self.camera_type == 'usb':
                ret, frame = self.cap.read()
                if not ret:
                    logger.error("Failed to capture frame from USB camera")
                    return None
            
            return frame
            
        except Exception as e:
            logger.error(f"Error capturing frame: {e}")
            return None
    
    def detect_objects(self, frame=None, capture_new=True):
        """
        Detect objects in frame
        
        Args:
            frame: Input frame (BGR format), or None to capture from camera
            capture_new: If True and frame is None, capture new frame
            
        Returns:
            dict: Detection results with format:
                {
                    'frame': annotated frame,
                    'detections': list of {'class': name, 'confidence': conf, 'bbox': (x1,y1,x2,y2)},
                    'count': total number of detections,
                    'classes': list of detected class names,
                    'summary': text summary
                }
        """
        # Get frame
        if frame is None and capture_new:
            frame = self.capture_frame()
            if frame is None:
                return None
        elif frame is None:
            logger.error("No frame provided and capture_new=False")
            return None
        
        try:
            # Run inference
            t_start = time.time()
            results = self.model(frame, verbose=False)
            inference_time = time.time() - t_start
            
            # Extract detections
            detections = results[0].boxes
            detection_list = []
            class_counts = {}
            
            # Process each detection
            for i in range(len(detections)):
                # Get confidence
                conf = detections[i].conf.item()
                
                # Filter by confidence threshold
                if conf < self.confidence_threshold:
                    continue
                
                # Get bounding box
                xyxy_tensor = detections[i].xyxy.cpu()
                xyxy = xyxy_tensor.numpy().squeeze()
                x1, y1, x2, y2 = xyxy.astype(int)
                
                # Get class
                class_idx = int(detections[i].cls.item())
                class_name = self.labels[class_idx]
                
                # Store detection
                detection_list.append({
                    'class': class_name,
                    'confidence': conf,
                    'bbox': (x1, y1, x2, y2)
                })
                
                # Count classes
                if class_name in class_counts:
                    class_counts[class_name] += 1
                else:
                    class_counts[class_name] = 1
                
                # Draw on frame
                color = self._get_color(class_idx)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                
                # Draw label
                label = f'{class_name}: {int(conf*100)}%'
                label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                label_y = max(y1, label_size[1] + 10)
                cv2.rectangle(frame, (x1, label_y - label_size[1] - 10), 
                            (x1 + label_size[0], label_y - 5), color, cv2.FILLED)
                cv2.putText(frame, label, (x1, label_y - 7), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
            
            # Generate summary
            summary = self._generate_summary(class_counts, len(detection_list))
            
            # Add info to frame
            cv2.putText(frame, f'Objects: {len(detection_list)}', (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f'Time: {inference_time:.2f}s', (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            logger.info(f"Detected {len(detection_list)} objects in {inference_time:.2f}s")
            
            return {
                'frame': frame,
                'detections': detection_list,
                'count': len(detection_list),
                'classes': list(class_counts.keys()),
                'class_counts': class_counts,
                'summary': summary,
                'inference_time': inference_time
            }
            
        except Exception as e:
            logger.error(f"Error during detection: {e}")
            return None
    
    def _get_color(self, class_idx):
        """Get color for bounding box based on class index"""
        colors = [
            (164, 120, 87), (68, 148, 228), (93, 97, 209), (178, 182, 133),
            (88, 159, 106), (96, 202, 231), (159, 124, 168), (169, 162, 241),
            (98, 118, 150), (172, 176, 184)
        ]
        return colors[class_idx % len(colors)]
    
    def _generate_summary(self, class_counts, total_count):
        """
        Generate natural language summary of detections
        
        Args:
            class_counts: Dictionary of {class_name: count}
            total_count: Total number of detections
            
        Returns:
            str: Natural language summary
        """
        if total_count == 0:
            return "I don't see any objects in the frame."
        
        # Sort by count
        sorted_classes = sorted(class_counts.items(), key=lambda x: x[1], reverse=True)
        
        if total_count == 1:
            class_name = sorted_classes[0][0]
            return f"I see one {class_name}."
        
        # Multiple objects
        summary_parts = []
        for class_name, count in sorted_classes[:5]:  # Top 5 classes
            if count == 1:
                summary_parts.append(f"one {class_name}")
            else:
                summary_parts.append(f"{count} {class_name}s")
        
        if len(summary_parts) == 1:
            summary = f"I see {summary_parts[0]}."
        elif len(summary_parts) == 2:
            summary = f"I see {summary_parts[0]} and {summary_parts[1]}."
        else:
            summary = f"I see {', '.join(summary_parts[:-1])}, and {summary_parts[-1]}."
        
        return summary
    
    def release(self):
        """Release camera resources"""
        if self.cap:
            try:
                if self.camera_type == 'picamera':
                    self.cap.stop()
                elif self.camera_type == 'usb':
                    self.cap.release()
                logger.info("Camera released")
            except Exception as e:
                logger.error(f"Error releasing camera: {e}")


def test_yolo_detector():
    """Test YOLO detector"""
    print("=" * 60)
    print("YOLO DETECTOR TEST")
    print("=" * 60)
    
    try:
        # Initialize detector
        detector = YOLODetector(
            model_path="models/yolo11n.pt",
            confidence_threshold=0.5,
            camera_type='usb',  # Change to 'picamera' on Raspberry Pi
            camera_index=0
        )
        
        print("\n✅ Detector initialized")
        print("\nPress 'q' to quit, 's' to save frame, 'c' to capture and detect")
        
        while True:
            # Detect objects
            results = detector.detect_objects()
            
            if results:
                # Display frame
                cv2.imshow('YOLO Detection', results['frame'])
                
                # Print summary
                print(f"\n{results['summary']}")
                print(f"Detected {results['count']} objects:")
                for det in results['detections']:
                    print(f"  - {det['class']}: {det['confidence']:.2f}")
            
            # Handle key press
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                cv2.imwrite('detection_capture.jpg', results['frame'])
                print("Frame saved!")
        
        # Cleanup
        detector.release()
        cv2.destroyAllWindows()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    test_yolo_detector()
