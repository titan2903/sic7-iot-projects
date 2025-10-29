#!/usr/bin/env python3
"""
MQTT Test Script
Script untuk test koneksi MQTT ke HiveMQ Cloud
"""

import paho.mqtt.client as mqtt
import json
import time
import ssl

# HiveMQ Cloud Configuration (Ganti dengan credentials Anda)
MQTT_BROKER = "your-cluster-url.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_USERNAME = "your_username"
MQTT_PASSWORD = "your_password"

# Test Topics
TEST_PUB_TOPIC = "sic/dibimbing/catalina/titanio-yudista/test/pub"
TEST_SUB_TOPIC = "sic/dibimbing/catalina/titanio-yudista/test/sub"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to MQTT Broker successfully!")
        client.subscribe(TEST_SUB_TOPIC)
        print(f"📡 Subscribed to: {TEST_SUB_TOPIC}")
    else:
        print(f"❌ Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    try:
        message = msg.payload.decode()
        print(f"📨 Received message on {msg.topic}: {message}")
    except Exception as e:
        print(f"❌ Error processing message: {e}")

def on_publish(client, userdata, mid):
    print(f"✅ Message published successfully (mid: {mid})")

def test_mqtt_connection():
    """Test MQTT connection and publish/subscribe"""
    
    print("🚀 Starting MQTT Connection Test...")
    print(f"🌐 Broker: {MQTT_BROKER}")
    print(f"🔌 Port: {MQTT_PORT}")
    print(f"👤 Username: {MQTT_USERNAME}")
    print("-" * 50)
    
    # Create MQTT client
    client = mqtt.Client()
    
    # Set credentials
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    
    # Set SSL/TLS for HiveMQ Cloud
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    client.tls_set_context(context)
    
    # Set callbacks
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_publish = on_publish
    
    try:
        # Connect to broker
        print("🔄 Connecting to MQTT broker...")
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        
        # Start loop
        client.loop_start()
        
        # Wait for connection
        time.sleep(2)
        
        # Test publishing
        test_message = {
            "message": "Hello from MQTT test!",
            "timestamp": time.time(),
            "test_id": "mqtt_test_001"
        }
        
        print(f"📤 Publishing test message to: {TEST_PUB_TOPIC}")
        result = client.publish(TEST_PUB_TOPIC, json.dumps(test_message))
        
        if result.rc == 0:
            print("✅ Test message published successfully!")
        else:
            print(f"❌ Failed to publish test message: {result.rc}")
        
        # Keep running for a few seconds to receive messages
        print("⏳ Waiting for messages... (Press Ctrl+C to stop)")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Test stopped by user")
        
    except Exception as e:
        print(f"❌ Error during MQTT test: {e}")
    
    finally:
        client.loop_stop()
        client.disconnect()
        print("🔌 Disconnected from MQTT broker")

if __name__ == "__main__":
    print("=" * 60)
    print("           MQTT CONNECTION TEST")
    print("=" * 60)
    print()
    print("⚠️  IMPORTANT: Update MQTT credentials before running!")
    print("   Edit this file and replace:")
    print("   - MQTT_BROKER")
    print("   - MQTT_USERNAME") 
    print("   - MQTT_PASSWORD")
    print()
    input("Press Enter to continue...")
    print()
    
    test_mqtt_connection()