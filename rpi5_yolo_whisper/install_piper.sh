#!/bin/bash
# Install Piper TTS for Raspberry Pi 5

set -e

echo "=================================================="
echo "🔊 Installing Piper TTS - Neural Voice Synthesis"
echo "=================================================="

# Detect architecture
ARCH=$(uname -m)
echo "Detected architecture: $ARCH"

# Download URL for Raspberry Pi (ARM64)
if [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then
    PIPER_URL="https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_arm64.tar.gz"
    echo "Using ARM64 build for Raspberry Pi"
elif [ "$ARCH" = "armv7l" ]; then
    PIPER_URL="https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_armv7l.tar.gz"
    echo "Using ARMv7 build"
elif [ "$ARCH" = "x86_64" ]; then
    PIPER_URL="https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_amd64.tar.gz"
    echo "Using x86_64 build"
else
    echo "❌ Unsupported architecture: $ARCH"
    exit 1
fi

# Create installation directory
INSTALL_DIR="$HOME/.local/bin"
mkdir -p "$INSTALL_DIR"

echo ""
echo "📦 Downloading Piper TTS..."
cd /tmp
wget -O piper.tar.gz "$PIPER_URL"

echo "📂 Extracting..."
tar -xzf piper.tar.gz

echo "📋 Installing binary..."
cp piper/piper "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/piper"

# Add to PATH if not already there
if ! grep -q "$INSTALL_DIR" ~/.bashrc; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    echo "✅ Added to PATH in ~/.bashrc"
fi

# Clean up
rm -rf piper piper.tar.gz

echo ""
echo "✅ Piper TTS installed successfully!"
echo "Location: $INSTALL_DIR/piper"

# Test installation
"$INSTALL_DIR/piper" --version || echo "Warning: Could not verify Piper version"

echo ""
echo "=================================================="
echo "🎤 Next: Download Voice Models"
echo "=================================================="
echo ""
echo "Run the voice download script:"
echo "  ./download_piper_voice.sh en_US-lessac-medium"
echo ""
echo "Or download manually from:"
echo "  https://github.com/rhasspy/piper/releases/tag/v1.2.0"
echo ""
echo "Available voices:"
echo "  - en_US-lessac-medium (recommended, 63MB)"
echo "  - en_US-lessac-low (fast, 20MB)"
echo "  - en_US-lessac-high (best quality, 100MB)"
echo "  - en_GB-alan-medium (British, 100MB)"
echo ""
echo "=================================================="
