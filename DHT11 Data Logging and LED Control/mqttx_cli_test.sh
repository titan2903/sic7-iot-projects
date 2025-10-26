#!/bin/bash

echo "🎯 MQTTX CLI Quick Test for DHT11 System"
echo "========================================"
echo ""
echo "This script demonstrates MQTTX CLI usage with DHT11 system"
echo ""

# Function to test LED control
test_led_control() {
    echo "🎛️  Testing LED Control via MQTTX CLI..."
    echo ""
    
    echo "💡 Turning LED ON..."
    mqttx pub -h broker.hivemq.com \
              -t 'sic/dibimbing/catalina/titanio-yudista/sub/led' \
              -m 'ON' \
              --verbose
    
    echo ""
    sleep 2
    
    echo "💡 Turning LED OFF..."
    mqttx pub -h broker.hivemq.com \
              -t 'sic/dibimbing/catalina/titanio-yudista/sub/led' \
              -m 'OFF' \
              --verbose
    
    echo ""
    echo "✅ LED control test completed!"
}

# Function to subscribe to DHT11 data
subscribe_dht11() {
    echo "📊 Subscribing to DHT11 data via MQTTX CLI..."
    echo ""
    echo "⏹️  Press Ctrl+C to stop subscription"
    echo ""
    
    mqttx sub -h broker.hivemq.com \
              -t 'sic/dibimbing/catalina/titanio-yudista/pub/dht' \
              --format \
              --verbose
}

# Function to send custom commands
send_custom_command() {
    echo "🔧 Send Custom LED Command"
    echo ""
    read -p "Enter custom command (e.g., BLINK, PULSE, TOGGLE): " custom_cmd
    
    if [ ! -z "$custom_cmd" ]; then
        echo "📤 Sending custom command: $custom_cmd"
        mqttx pub -h broker.hivemq.com \
                  -t 'sic/dibimbing/catalina/titanio-yudista/sub/led' \
                  -m "$custom_cmd" \
                  --verbose
        echo "✅ Custom command sent!"
    else
        echo "❌ No command entered"
    fi
}

# Main menu
while true; do
    echo ""
    echo "🚀 MQTTX CLI Test Menu:"
    echo "======================="
    echo "1. 📊 Subscribe to DHT11 Data"
    echo "2. 🎛️  Test LED Control (ON/OFF)"
    echo "3. 🔧 Send Custom LED Command"
    echo "4. ℹ️  Show Connection Info"
    echo "0. ❌ Exit"
    echo ""
    
    read -p "Enter your choice (0-4): " choice
    
    case $choice in
        1)
            subscribe_dht11
            ;;
        2)
            test_led_control
            ;;
        3)
            send_custom_command
            ;;
        4)
            echo ""
            echo "📋 MQTTX Connection Information:"
            echo "================================"
            echo "Broker: broker.hivemq.com:1883"
            echo "DHT11 Topic: sic/dibimbing/catalina/titanio-yudista/pub/dht"
            echo "LED Topic: sic/dibimbing/catalina/titanio-yudista/sub/led"
            echo "Client ID: mqttx_cli_$(date +%s)"
            ;;
        0)
            echo ""
            echo "👋 Goodbye!"
            break
            ;;
        *)
            echo ""
            echo "❌ Invalid choice. Please try again."
            ;;
    esac
done