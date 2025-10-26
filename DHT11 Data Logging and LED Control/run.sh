#!/bin/bash

echo "🚀 DHT11 Data Logging and LED Control System"
echo "============================================"
echo ""
echo "Choose how you want to interact with the DHT11 system:"
echo ""
echo "📱 MQTTX Desktop App Options:"
echo "4. 🔧 Setup MQTTX Configuration"
echo "5. 📋 View MQTTX Connection Details"
echo ""
echo "🐍 Python Script Options:"
echo "1. 📊 Monitor DHT11 Data (Subscribe)"
echo "   - Real-time temperature & humidity display"
echo "   - Data logging to CSV file"
echo "   - Status indicators"
echo ""
echo "2. 🎛️  Control LED (Publish)" 
echo "   - Interactive LED control menu"
echo "   - Send ON/OFF commands"
echo "   - Custom command support"
echo ""
echo "🧪 Testing & Utilities:"
echo "3. 🔌 Test MQTT Connection"
echo "   - Verify broker connectivity"
echo ""
echo "0. ❌ Exit"
echo ""

read -p "Enter your choice (0-5): " choice

case $choice in
    1)
        echo ""
        echo "🚀 Starting DHT11 Data Monitor..."
        python3 src/subscribe_dht.py
        ;;
    2)
        echo ""
        echo "🚀 Starting LED Control System..."
        python3 src/publish_led_control.py
        ;;
    3)
        echo ""
        echo "🚀 Testing MQTT Connection..."
        python3 test_mqtt.py
        ;;
    4)
        echo ""
        echo "🚀 Setting up MQTTX Configuration..."
        ./setup_mqttx.sh
        ;;
    5)
        echo ""
        echo "📋 MQTTX Connection Details:"
        echo "================================"
        echo "Host: broker.hivemq.com"
        echo "Port: 1883"
        echo "Protocol: mqtt://"
        echo "Client ID: mqttx_fff05771 (or use unique ID)"
        echo ""
        echo "📡 Topics:"
        echo "  DHT11 Data: sic/dibimbing/catalina/titanio-yudista/pub/dht"
        echo "  LED Control: sic/dibimbing/catalina/titanio-yudista/sub/led"
        echo ""
        echo "💡 LED Commands: ON, OFF, TOGGLE, BLINK"
        echo ""
        echo "🎯 Recommended MQTTX Setup:"
        echo "1. Open MQTTX Desktop App"
        echo "2. Create new connection with above settings"
        echo "3. Subscribe to DHT11 topic for monitoring"
        echo "4. Use Publish tab for LED control"
        echo ""
        read -p "Press Enter to continue..."
        ;;
    0)
        echo ""
        echo "👋 Goodbye!"
        ;;
    *)
        echo ""
        echo "❌ Invalid choice. Please run the script again."
        ;;
esac