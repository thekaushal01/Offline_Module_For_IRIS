#!/usr/bin/env python3
"""
Convert YOLOv11n to NCNN format for optimized Raspberry Pi 5 inference
"""

import os
import sys
import torch
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_yolo_to_ncnn(yolo_model_path, ncnn_param_path, ncnn_bin_path):
    """
    Convert YOLOv11 PyTorch model to NCNN format

    Args:
        yolo_model_path: Path to YOLO .pt file
        ncnn_param_path: Output path for .param file
        ncnn_bin_path: Output path for .bin file
    """
    try:
        # Import required libraries
        from ultralytics import YOLO

        logger.info(f"Loading YOLO model from {yolo_model_path}")
        model = YOLO(yolo_model_path)

        # Export to ONNX first (intermediate step)
        onnx_path = yolo_model_path.replace('.pt', '.onnx')
        logger.info(f"Exporting to ONNX: {onnx_path}")

        # Export with specific parameters for NCNN compatibility
        model.export(
            format='onnx',
            imgsz=640,
            opset=11,
            simplify=True,
            dynamic=False
        )

        # Convert ONNX to NCNN using onnx2ncnn tool
        logger.info("Converting ONNX to NCNN format...")
        convert_onnx_to_ncnn(onnx_path, ncnn_param_path, ncnn_bin_path)

        logger.info("✅ YOLOv11n successfully converted to NCNN format")
        return True

    except Exception as e:
        logger.error(f"Failed to convert model: {e}")
        return False

def convert_onnx_to_ncnn(onnx_path, param_path, bin_path):
    """
    Convert ONNX model to NCNN format using onnx2ncnn tool
    """
    import subprocess

    try:
        # Run onnx2ncnn conversion
        cmd = [
            'onnx2ncnn',
            onnx_path,
            param_path,
            bin_path
        ]

        logger.info(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"onnx2ncnn failed: {result.stderr}")
            raise RuntimeError(f"onnx2ncnn conversion failed: {result.stderr}")

        logger.info("ONNX to NCNN conversion completed")

        # Optimize the NCNN model
        optimize_ncnn_model(param_path, bin_path)

    except FileNotFoundError:
        logger.error("onnx2ncnn tool not found. Please install NCNN tools:")
        logger.error("git clone https://github.com/Tencent/ncnn.git")
        logger.error("cd ncnn && mkdir build && cd build")
        logger.error("cmake -DCMAKE_BUILD_TYPE=Release .. && make -j$(nproc)")
        logger.error("sudo make install")
        raise

def optimize_ncnn_model(param_path, bin_path):
    """
    Optimize NCNN model for better performance
    """
    try:
        import subprocess

        # Use ncnnoptimize tool if available
        cmd = [
            'ncnnoptimize',
            param_path,
            bin_path,
            param_path.replace('.param', '_opt.param'),
            bin_path.replace('.bin', '_opt.bin'),
            '0'  # fp16 storage
        ]

        logger.info("Optimizing NCNN model...")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            # Replace original with optimized
            os.rename(param_path.replace('.param', '_opt.param'), param_path)
            os.rename(bin_path.replace('.bin', '_opt.bin'), bin_path)
            logger.info("✅ NCNN model optimized")
        else:
            logger.warning("NCNN optimization failed, using unoptimized model")

    except FileNotFoundError:
        logger.warning("ncnnoptimize tool not found, using unoptimized model")

def quantize_ncnn_model(param_path, bin_path, quantized_param_path, quantized_bin_path):
    """
    Quantize NCNN model to INT8 for better performance
    """
    try:
        import subprocess

        cmd = [
            'ncnn2int8',
            param_path,
            bin_path,
            quantized_param_path,
            quantized_bin_path
        ]

        logger.info("Quantizing NCNN model to INT8...")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            logger.info("✅ NCNN model quantized to INT8")
            return True
        else:
            logger.warning(f"Quantization failed: {result.stderr}")
            return False

    except FileNotFoundError:
        logger.warning("ncnn2int8 tool not found, skipping quantization")
        return False

def main():
    """Main conversion function"""
    if len(sys.argv) != 2:
        print("Usage: python convert_yolo_ncnn.py <yolo_model.pt>")
        sys.exit(1)

    yolo_model_path = sys.argv[1]

    if not os.path.exists(yolo_model_path):
        logger.error(f"Model file not found: {yolo_model_path}")
        sys.exit(1)

    # Define output paths
    base_name = os.path.splitext(yolo_model_path)[0]
    ncnn_param_path = f"{base_name}_ncnn.param"
    ncnn_bin_path = f"{base_name}_ncnn.bin"
    quantized_param_path = f"{base_name}_ncnn_int8.param"
    quantized_bin_path = f"{base_name}_ncnn_int8.bin"

    # Convert to NCNN
    if convert_yolo_to_ncnn(yolo_model_path, ncnn_param_path, ncnn_bin_path):
        # Try to quantize
        quantize_ncnn_model(
            ncnn_param_path, ncnn_bin_path,
            quantized_param_path, quantized_bin_path
        )

        print("\n" + "="*60)
        print("🎉 CONVERSION COMPLETE!")
        print("="*60)
        print(f"Original model: {yolo_model_path}")
        print(f"NCNN model: {ncnn_param_path}, {ncnn_bin_path}")
        if os.path.exists(quantized_param_path):
            print(f"Quantized model: {quantized_param_path}, {quantized_bin_path}")
        print("="*60)

if __name__ == "__main__":
    main()</content>
<parameter name="filePath">c:\Users\NITIN NAYN\Offline_Module_For_IRIS\rpi5_yolo_whisper\convert_yolo_ncnn.py