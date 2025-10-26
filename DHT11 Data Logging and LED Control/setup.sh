#!/bin/bash

echo "🚀 Setting up DHT11 Data Logging and LED Control System"
echo "=================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python3 first."
    exit 1
fi

echo "✅ Python3 found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3 first."
    exit 1
fi

echo "✅ pip3 found"

# Show Python executable path
echo "🐍 Python executable: $(which python3)"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Python dependencies installed successfully"
else
    echo "❌ Failed to install Python dependencies"
    exit 1
fi

# Verify paho-mqtt installation
echo "🔍 Verifying paho-mqtt installation..."
if python3 -c "import paho.mqtt.client; print('✅ paho-mqtt imported successfully')" 2>/dev/null; then
    echo "✅ paho-mqtt is working correctly"
else
    echo "❌ paho-mqtt import failed, trying alternative installation..."
    python3 -m pip install --force-reinstall paho-mqtt==1.6.1
fi

# Make pubsub.py executable
chmod +x src/pubsub.py
chmod +x test_mqtt.py

# Test MQTT connectivity
echo ""
echo "🧪 Testing MQTT connectivity..."
python3 test_mqtt.py

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Configure WiFi credentials in src/main.cpp"
echo "2. Build and upload ESP32 firmware: pio run --target upload"
echo "3. Run Python client: python3 src/pubsub.py"
echo ""
echo "💡 If VS Code still shows import errors, try:"
echo "   - Press Ctrl+Shift+P and select 'Python: Select Interpreter'"
echo "   - Choose: $(which python3)"
echo "   - Reload VS Code window"
echo ""