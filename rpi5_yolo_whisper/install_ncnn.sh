#!/bin/bash
# Install NCNN for Raspberry Pi 5 - YOLO Optimization

echo "🚀 Installing NCNN for Raspberry Pi 5 YOLO optimization..."

# Update system
sudo apt-get update

# Install dependencies
sudo apt-get install -y \
    build-essential \
    cmake \
    git \
    libprotobuf-dev \
    protobuf-compiler \
    libvulkan-dev \
    vulkan-tools \
    python3-dev \
    python3-pip

# Install Python NCNN bindings
pip install ncnn

# Clone and build NCNN tools
echo "📦 Building NCNN tools..."
cd ~
git clone https://github.com/Tencent/ncnn.git
cd ncnn

# Create build directory
mkdir -p build
cd build

# Configure with CMake (optimized for Raspberry Pi 5)
cmake -DCMAKE_BUILD_TYPE=Release \
      -DNCNN_BUILD_TOOLS=ON \
      -DNCNN_BUILD_PYTHON=OFF \
      -DNCNN_VULKAN=OFF \
      -DNCNN_BUILD_EXAMPLES=OFF \
      -DNCNN_BUILD_TESTS=OFF \
      ..

# Build with all cores
make -j$(nproc)

# Install
sudo make install

echo "✅ NCNN installation complete!"
echo "🔧 Tools available: onnx2ncnn, ncnnoptimize, ncnn2int8"

# Go back to project directory
cd ~/rpi5_yolo_whisper

echo ""
echo "🎯 Next steps:"
echo "1. Convert YOLO model: python convert_yolo_ncnn.py models/yolo11n.pt"
echo "2. Update your code to use NCNNYOLODetector instead of YOLODetector"
echo "3. Enjoy 3-5x faster inference!"