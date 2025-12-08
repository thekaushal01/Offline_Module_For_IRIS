"""
NCNN-based YOLO Object Detection Module
Optimized for Raspberry Pi 5 with quantized YOLOv11n
"""

import os
import logging
import time
import cv2
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)

class NCNNYOLODetector:
    """NCNN-based YOLO11 object detector optimized for Raspberry Pi 5"""

    def __init__(self,
                 model_path="models/yolo11n_ncnn_int8.param",
                 bin_path="models/yolo11n_ncnn_int8.bin",
                 confidence_threshold=0.5,
                 camera_type="picamera",
                 camera_index=0,
                 width=640,
                 height=480):
        """
        Initialize NCNN YOLO detector

        Args:
            model_path: Path to NCNN .param file
            bin_path: Path to NCNN .bin file
            confidence_threshold: Minimum confidence for detections
            camera_type: 'picamera', 'usb', or None (no camera)
            camera_index: Camera device index
            width: Camera frame width
            height: Camera frame height
        """
        self.model_path = model_path
        self.bin_path = bin_path
        self.confidence_threshold = confidence_threshold
        self.camera_type = camera_type
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.net = None
        self.labels = None
        self.cap = None

        # YOLOv11 class names (COCO dataset)
        self.labels = [
            "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck", "boat",
            "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat", "dog",
            "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella",
            "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite",
            "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle",
            "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich",
            "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair", "couch",
            "potted plant", "bed", "dining table", "toilet", "tv", "laptop", "mouse", "remote",
            "keyboard", "cell phone", "microwave", "oven", "toaster", "sink", "refrigerator", "book",
            "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush"
        ]

        logger.info(f"Initializing NCNN YOLO detector with model: {model_path}")
        self._load_model()

        if camera_type:
            self._initialize_camera()

    def _load_model(self):
        """Load NCNN model"""
        try:
            # Import NCNN Python bindings
            import ncnn

            if not os.path.exists(self.model_path) or not os.path.exists(self.bin_path):
                logger.error(f"NCNN model files not found:")
                logger.error(f"  Param: {self.model_path}")
                logger.error(f"  Bin: {self.bin_path}")
                logger.error("Please run convert_yolo_ncnn.py first to convert the model")
                raise FileNotFoundError("NCNN model files not found")

            # Create NCNN network
            self.net = ncnn.Net()

            # Load model
            self.net.load_param(self.model_path)
            self.net.load_model(self.bin_path)

            # Set up for CPU inference (Raspberry Pi 5)
            self.net.opt.use_vulkan_compute = False  # Use CPU instead of GPU
            self.net.opt.num_threads = 4  # Raspberry Pi 5 has 4 cores

            logger.info(f"✅ NCNN YOLO model loaded with {len(self.labels)} classes")
            logger.info("Using CPU inference with 4 threads")

        except ImportError as e:
            logger.error("NCNN Python bindings not installed!")
            logger.error("Install with: pip install ncnn")
            logger.error("Or build from source: https://github.com/Tencent/ncnn/wiki/how-to-build")
            raise
        except Exception as e:
            logger.error(f"Failed to load NCNN model: {e}")
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
                    logger.error("picamera2 not installed, falling back to USB camera")
                    self.camera_type = 'usb'
                    self._initialize_camera()
                except RuntimeError as e:
                    logger.error(f"Pi Camera error: {e}")
                    logger.error("Falling back to USB camera")
                    self.camera_type = 'usb'
                    self._initialize_camera()
            elif self.camera_type == 'usb':
                logger.info("Initializing USB Camera...")
                self.cap = cv2.VideoCapture(self.camera_index)
                if not self.cap.isOpened():
                    raise RuntimeError(f"Could not open USB camera {self.camera_index}")
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
                logger.info(f"✅ USB Camera initialized ({self.width}x{self.height})")
            else:
                logger.warning("No camera type specified")
        except Exception as e:
            logger.error(f"Failed to initialize camera: {e}")
            self.cap = None

    def preprocess_image(self, image):
        """
        Preprocess image for NCNN inference

        Args:
            image: Input image (BGR format)

        Returns:
            Preprocessed blob and original image dimensions
        """
        # Get original dimensions
        orig_h, orig_w = image.shape[:2]

        # Resize to model input size (640x640 for YOLOv11)
        input_size = 640
        resized = cv2.resize(image, (input_size, input_size))

        # Convert BGR to RGB
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)

        # Normalize to 0-1
        normalized = rgb.astype(np.float32) / 255.0

        # Convert to NCNN Mat
        import ncnn
        mat = ncnn.Mat.from_pixels(
            normalized.data,
            ncnn.Mat.PixelType.PIXEL_RGB,
            input_size, input_size
        )

        return mat, orig_w, orig_h

    def detect(self, image):
        """
        Run object detection on image

        Args:
            image: Input image (BGR format)

        Returns:
            List of detections [(class_id, confidence, x1, y1, x2, y2), ...]
        """
        if self.net is None:
            logger.error("Model not loaded")
            return []

        try:
            # Preprocess image
            mat, orig_w, orig_h = self.preprocess_image(image)

            # Create extractor
            ex = self.net.create_extractor()
            ex.set_num_threads(4)  # Use all 4 cores

            # Set input
            ex.input("images", mat)

            # Get output
            ret, out = ex.extract("output0")  # YOLOv11 output layer name

            if ret != 0:
                logger.error("NCNN inference failed")
                return []

            # Process detections
            detections = self._process_detections(out, orig_w, orig_h)

            return detections

        except Exception as e:
            logger.error(f"Detection failed: {e}")
            return []

    def _process_detections(self, output_mat, orig_w, orig_h):
        """
        Process NCNN output into detections

        Args:
            output_mat: NCNN output matrix
            orig_w, orig_h: Original image dimensions

        Returns:
            List of detections
        """
        detections = []

        try:
            # Get output data
            output_data = np.array(output_mat)

            # YOLOv11 output format: [batch, 84, 8400] for COCO dataset
            # 84 = 80 classes + 4 bbox coords
            # Reshape to [8400, 85] (x, y, w, h, conf, class_scores...)
            output_data = output_data.reshape(-1, 85)

            # Iterate through detections
            for detection in output_data:
                # Extract bbox coordinates
                x, y, w, h = detection[:4]

                # Objectness score
                obj_conf = detection[4]

                # Class scores
                class_scores = detection[5:]

                # Find best class
                class_id = np.argmax(class_scores)
                class_conf = class_scores[class_id]

                # Combined confidence
                confidence = obj_conf * class_conf

                if confidence > self.confidence_threshold:
                    # Convert from center-width-height to x1,y1,x2,y2
                    x1 = (x - w/2) / 640 * orig_w
                    y1 = (y - h/2) / 640 * orig_h
                    x2 = (x + w/2) / 640 * orig_w
                    y2 = (y + h/2) / 640 * orig_h

                    # Clip to image bounds
                    x1 = max(0, min(x1, orig_w))
                    y1 = max(0, min(y1, orig_h))
                    x2 = max(0, min(x2, orig_w))
                    y2 = max(0, min(y2, orig_h))

                    detections.append((
                        int(class_id),
                        float(confidence),
                        int(x1), int(y1), int(x2), int(y2)
                    ))

            # Sort by confidence
            detections.sort(key=lambda x: x[1], reverse=True)

        except Exception as e:
            logger.error(f"Failed to process detections: {e}")

        return detections

    def capture_frame(self):
        """
        Capture frame from camera

        Returns:
            Frame as numpy array (BGR format) or None if failed
        """
        if self.cap is None:
            return None

        try:
            if self.camera_type == 'picamera':
                frame = self.cap.capture_array()
                # Convert RGB to BGR for OpenCV compatibility
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            else:  # USB camera
                ret, frame = self.cap.read()
                if not ret:
                    return None

            return frame
        except Exception as e:
            logger.error(f"Failed to capture frame: {e}")
            return None

    def detect_objects(self, capture_new=True, image=None):
        """
        Detect objects in image

        Args:
            capture_new: Whether to capture new frame from camera
            image: Optional image to process instead of capturing

        Returns:
            Dict with detection results
        """
        start_time = time.time()

        # Get image
        if image is not None:
            frame = image
        elif capture_new:
            frame = self.capture_frame()
            if frame is None:
                return {"count": 0, "detections": [], "summary": "No frame captured"}
        else:
            return {"count": 0, "detections": [], "summary": "No image provided"}

        # Run detection
        detections = self.detect(frame)

        # Process results
        result = self._format_results(detections, time.time() - start_time)

        return result

    def _format_results(self, detections, inference_time):
        """
        Format detection results into readable summary

        Args:
            detections: List of detections
            inference_time: Time taken for inference

        Returns:
            Dict with formatted results
        """
        if not detections:
            return {
                "count": 0,
                "detections": [],
                "summary": "No objects detected",
                "fps": 1.0 / inference_time if inference_time > 0 else 0
            }

        # Group by class
        class_counts = {}
        detection_list = []

        for class_id, conf, x1, y1, x2, y2 in detections:
            class_name = self.labels[class_id] if class_id < len(self.labels) else f"class_{class_id}"
            detection_list.append({
                "class": class_name,
                "confidence": conf,
                "bbox": [x1, y1, x2, y2]
            })

            class_counts[class_name] = class_counts.get(class_name, 0) + 1

        # Create summary
        summary_parts = []
        for class_name, count in class_counts.items():
            if count == 1:
                summary_parts.append(f"one {class_name}")
            else:
                summary_parts.append(f"{count} {class_name}s")

        summary = f"I see {', '.join(summary_parts)}."

        return {
            "count": len(detections),
            "detections": detection_list,
            "summary": summary,
            "fps": 1.0 / inference_time if inference_time > 0 else 0
        }

    def release(self):
        """Release resources"""
        if self.cap is not None:
            if self.camera_type == 'picamera':
                self.cap.stop()
            else:
                self.cap.release()
            self.cap = None

        logger.info("NCNN YOLO detector released")</content>
<parameter name="filePath">c:\Users\NITIN NAYN\Offline_Module_For_IRIS\rpi5_yolo_whisper\ncnn_yolo_detector.py