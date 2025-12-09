#!/bin/bash
# Download Piper voice models

set -e

# Default voice if none specified
VOICE="${1:-en_US-lessac-medium}"

echo "=================================================="
echo "🎤 Downloading Piper Voice Model"
echo "=================================================="
echo "Voice: $VOICE"

# Create models directory
MODELS_DIR="$HOME/.local/share/piper/voices"
mkdir -p "$MODELS_DIR"

# Base URL for voice models
BASE_URL="https://github.com/rhasspy/piper/releases/download/v1.2.0"

# Voice files
ONNX_FILE="${VOICE}.onnx"
JSON_FILE="${VOICE}.onnx.json"

echo ""
echo "📦 Downloading model files..."

# Download .onnx file
echo "  Downloading ${ONNX_FILE}..."
wget -q --show-progress -O "$MODELS_DIR/$ONNX_FILE" "$BASE_URL/$ONNX_FILE"

# Download .onnx.json file
echo "  Downloading ${JSON_FILE}..."
wget -q --show-progress -O "$MODELS_DIR/$JSON_FILE" "$BASE_URL/$JSON_FILE"

echo ""
echo "✅ Voice model downloaded successfully!"
echo "Location: $MODELS_DIR"
echo ""

# Test the voice
echo "🧪 Testing voice..."
PIPER_BIN="$HOME/.local/bin/piper"

if [ -x "$PIPER_BIN" ]; then
    echo "Hello, this is a test of the Piper text to speech system." | \
        "$PIPER_BIN" --model "$MODELS_DIR/$ONNX_FILE" --output_file /tmp/test.wav
    
    if [ -f /tmp/test.wav ]; then
        echo "✅ Voice model working!"
        
        # Try to play test audio
        if command -v aplay &> /dev/null; then
            echo "🔊 Playing test audio..."
            aplay -q /tmp/test.wav
        fi
        
        rm -f /tmp/test.wav
    fi
else
    echo "⚠️  Piper not found. Install with: ./install_piper.sh"
fi

echo ""
echo "=================================================="
echo "Available voices to download:"
echo "=================================================="
echo ""
echo "High Quality (slower):"
echo "  en_US-lessac-high        - American English (100MB)"
echo "  en_US-libritts-high      - American English, natural (200MB)"
echo ""
echo "Medium Quality (balanced) - RECOMMENDED:"
echo "  en_US-lessac-medium      - American English (63MB) ✅"
echo "  en_US-ryan-medium        - American English (40MB)"
echo "  en_GB-alan-medium        - British English (100MB)"
echo ""
echo "Low Quality (fastest):"
echo "  en_US-lessac-low         - American English (20MB)"
echo "  en_US-ryan-low           - American English (20MB)"
echo ""
echo "To download another voice:"
echo "  ./download_piper_voice.sh en_GB-alan-medium"
echo ""
