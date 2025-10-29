#!/bin/bash

# DHT11 and LED Dashboard Setup Script
# Titan Yudista - SIC Dibimbing Catalina

echo "=========================================="
echo "  DHT11 and LED Dashboard Setup Script"
echo "=========================================="
echo

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

echo "✅ pip3 found: $(pip3 --version)"

# Install Python dependencies
echo
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Python dependencies installed successfully!"
else
    echo "❌ Failed to install Python dependencies."
    exit 1
fi

# Check if PlatformIO is installed
echo
echo "🔍 Checking PlatformIO installation..."
if command -v pio &> /dev/null; then
    echo "✅ PlatformIO found: $(pio --version)"
else
    echo "⚠️  PlatformIO not found in PATH."
    echo "   Please install PlatformIO Core or use PlatformIO IDE in VS Code."
fi

# Create virtual environment (optional)
echo
read -p "📋 Create Python virtual environment? (y/n): " create_venv

if [[ $create_venv == "y" || $create_venv == "Y" ]]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    echo "✅ Virtual environment created and dependencies installed."
    echo "   To activate: source venv/bin/activate"
fi

# Display configuration instructions
echo
echo "=========================================="
echo "           CONFIGURATION REQUIRED"
echo "=========================================="
echo
echo "🔧 Before running the project, you need to:"
echo
echo "1. Setup HiveMQ Cloud:"
echo "   - Go to https://console.hivemq.cloud/"
echo "   - Create a free cluster"
echo "   - Note down the cluster URL, username, and password"
echo
echo "2. Configure Arduino (src/main.cpp):"
echo "   - WiFi SSID and password"
echo "   - HiveMQ Cloud credentials"
echo
echo "3. Configure Dashboard (src/dashboard.py):"
echo "   - HiveMQ Cloud credentials (same as Arduino)"
echo
echo "4. Hardware Setup:"
echo "   - Connect DHT11 to GPIO 4"
echo "   - Connect LED to GPIO 2"
echo "   - See README.md for detailed wiring"
echo
echo "=========================================="
echo "              NEXT STEPS"
echo "=========================================="
echo
echo "1. Upload Arduino code:"
echo "   pio run --target upload"
echo
echo "2. Monitor Arduino serial:"
echo "   pio device monitor"
echo
echo "3. Test MQTT connection:"
echo "   python3 src/mqtt_test.py"
echo
echo "4. Run dashboard:"
echo "   python3 src/dashboard.py"
echo
echo "📖 For detailed instructions, see README.md"
echo
echo "🎉 Setup completed successfully!"