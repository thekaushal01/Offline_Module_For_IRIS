#!/usr/bin/env python3
"""
Test and benchmark YOLO detectors
Compare PyTorch vs NCNN performance
"""

import os
import time
import logging
import argparse
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_detector(detector_class, model_path, num_runs=10):
    """Test a detector implementation"""
    try:
        logger.info(f"Testing {detector_class.__name__}...")

        # Initialize detector (no camera for testing)
        detector = detector_class(
            model_path=model_path,
            camera_type=None  # No camera for benchmark
        )

        # Create test image (640x480 random image)
        import numpy as np
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

        # Warm up
        logger.info("Warming up...")
        for _ in range(3):
            detector.detect_objects(capture_new=False, image=test_image)

        # Benchmark
        logger.info(f"Running {num_runs} inference runs...")
        start_time = time.time()
        fps_values = []

        for i in range(num_runs):
            result = detector.detect_objects(capture_new=False, image=test_image)
            if 'fps' in result:
                fps_values.append(result['fps'])

        total_time = time.time() - start_time
        avg_fps = sum(fps_values) / len(fps_values) if fps_values else 0
        avg_time = total_time / num_runs

        detector.release()

        return {
            'success': True,
            'avg_fps': avg_fps,
            'avg_time': avg_time,
            'total_time': total_time
        }

    except Exception as e:
        logger.error(f"Test failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def main():
    parser = argparse.ArgumentParser(description='Benchmark YOLO detectors')
    parser.add_argument('--runs', type=int, default=20, help='Number of test runs')
    parser.add_argument('--model', default='models/yolo11n.pt', help='PyTorch model path')
    args = parser.parse_args()

    print("🚀 YOLO Detector Benchmark")
    print("=" * 50)

    results = {}

    # Test PyTorch implementation
    try:
        from yolo_detector import YOLODetector
        result = test_detector(YOLODetector, args.model, args.runs)
        results['PyTorch'] = result
    except Exception as e:
        results['PyTorch'] = {'success': False, 'error': str(e)}

    # Test NCNN implementation
    try:
        from ncnn_yolo_detector import NCNNYOLODetector
        ncnn_model = args.model.replace('.pt', '_ncnn_int8.param')
        ncnn_bin = ncnn_model.replace('.param', '.bin')

        if os.path.exists(ncnn_model) and os.path.exists(ncnn_bin):
            result = test_detector(NCNNYOLODetector, ncnn_model, args.runs)
            results['NCNN'] = result
        else:
            results['NCNN'] = {'success': False, 'error': 'NCNN model not found'}
    except Exception as e:
        results['NCNN'] = {'success': False, 'error': str(e)}

    # Print results
    print("\n📊 RESULTS:")
    print("=" * 50)

    for impl, result in results.items():
        print(f"\n{impl} Implementation:")
        if result['success']:
            print(".2f"            print(".3f"            print(".1f")
        else:
            print(f"  ❌ Failed: {result['error']}")

    # Compare implementations
    if 'PyTorch' in results and 'NCNN' in results:
        if results['PyTorch']['success'] and results['NCNN']['success']:
            pytorch_fps = results['PyTorch']['avg_fps']
            ncnn_fps = results['NCNN']['avg_fps']

            speedup = ncnn_fps / pytorch_fps if pytorch_fps > 0 else 0

            print("
🎯 COMPARISON:"            print(".1f"            print(".2f")

if __name__ == "__main__":
    main()