"""
Smart YOLO Detector - Automatically chooses best implementation
Uses NCNN for speed on Raspberry Pi, falls back to PyTorch
"""

import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class SmartYOLODetector:
    """Smart detector that chooses NCNN or PyTorch based on availability"""

    def __init__(self, **kwargs):
        """
        Initialize smart detector

        Automatically chooses NCNN if available, otherwise PyTorch
        """
        self.detector = None
        self.implementation = None

        # Check if NCNN model exists and NCNN is available
        ncnn_param = kwargs.get('model_path', 'models/yolo11n_ncnn_int8.param').replace('.pt', '_ncnn_int8.param')
        ncnn_bin = ncnn_param.replace('.param', '.bin')

        if os.path.exists(ncnn_param) and os.path.exists(ncnn_bin):
            try:
                # Try to import NCNN
                import ncnn
                from ncnn_yolo_detector import NCNNYOLODetector

                logger.info("🎯 Using NCNN YOLO detector (optimized)")
                self.detector = NCNNYOLODetector(**kwargs)
                self.implementation = "NCNN"
                return

            except ImportError:
                logger.warning("NCNN model exists but ncnn package not installed")

        # Fall back to PyTorch implementation
        logger.info("🔄 Using PyTorch YOLO detector")
        from yolo_detector import YOLODetector
        self.detector = YOLODetector(**kwargs)
        self.implementation = "PyTorch"

    def __getattr__(self, name):
        """Delegate all method calls to the actual detector"""
        return getattr(self.detector, name)

    def get_implementation_info(self):
        """Get information about the current implementation"""
        return {
            "implementation": self.implementation,
            "description": "NCNN (quantized)" if self.implementation == "NCNN" else "PyTorch (standard)"
        }