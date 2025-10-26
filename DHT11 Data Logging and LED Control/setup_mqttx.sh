#!/bin/bash

echo "🚀 MQTTX Integration Helper for DHT11 System"
echo "============================================="
echo ""
echo "This script helps you configure MQTTX for optimal DHT11 monitoring"
echo ""

# Check if MQTTX CLI is available
if command -v mqttx &> /dev/null; then
    echo "✅ MQTTX CLI detected!"
    echo ""
    
    echo "🔧 Quick MQTTX CLI Commands for DHT11 System:"
    echo ""
    
    echo "📊 Subscribe to DHT11 data:"
    echo "mqttx sub -h broker.hivemq.com -t 'sic/dibimbing/catalina/titanio-yudista/pub/dht' -f"
    echo ""
    
    echo "🎛️  Control LED (Turn ON):"
    echo "mqttx pub -h broker.hivemq.com -t 'sic/dibimbing/catalina/titanio-yudista/sub/led' -m 'ON'"
    echo ""
    
    echo "🎛️  Control LED (Turn OFF):"
    echo "mqttx pub -h broker.hivemq.com -t 'sic/dibimbing/catalina/titanio-yudista/sub/led' -m 'OFF'"
    echo ""
    
    read -p "Run DHT11 subscriber now? (y/N): " choice
    if [[ $choice == "y" || $choice == "Y" ]]; then
        echo "🚀 Starting MQTTX DHT11 subscriber..."
        mqttx sub -h broker.hivemq.com -t 'sic/dibimbing/catalina/titanio-yudista/pub/dht' -f
    fi
    
else
    echo "ℹ️  MQTTX CLI not detected (Desktop app is sufficient)"
    echo ""
fi

echo "📋 MQTTX Desktop App Configuration:"
echo ""
echo "Connection Name: DHT11 ESP32 System (HiveMQ)"
echo "Host: broker.hivemq.com"
echo "Port: 1883"
echo "Protocol: mqtt://"
echo "Client ID: mqttx_$(date +%s)"
echo ""
echo "📡 Topics to use:"
echo "  Subscribe: sic/dibimbing/catalina/titanio-yudista/pub/dht"
echo "  Publish:   sic/dibimbing/catalina/titanio-yudista/sub/led"
echo ""
echo "💡 Sample Payloads for LED Control:"
echo "  ON    - Turn LED on"
echo "  OFF   - Turn LED off"
echo "  BLINK - Custom blink command"
echo ""

# Generate MQTTX connection profile
echo "📄 Generating MQTTX connection profile..."
cat > mqttx_dht11_profile.json << EOF
{
  "name": "DHT11 ESP32 System",
  "host": "broker.hivemq.com",
  "port": 1883,
  "protocol": "mqtt",
  "clientId": "mqttx_dht11_$(date +%s)",
  "username": "",
  "password": "",
  "keepAlive": 60,
  "cleanSession": true,
  "subscriptions": [
    {
      "topic": "sic/dibimbing/catalina/titanio-yudista/pub/dht",
      "qos": 0,
      "color": "#4CAF50",
      "alias": "DHT11 Sensor Data"
    }
  ]
}
EOF

echo "✅ MQTTX profile saved to: mqttx_dht11_profile.json"
echo ""
echo "📱 Import this profile in MQTTX Desktop App:"
echo "   File → Import Connections → Select mqttx_dht11_profile.json"
echo ""
echo "🎉 Happy monitoring with MQTTX!"