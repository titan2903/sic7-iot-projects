#!/usr/bin/env python3
"""
MQTT Connection Test Script
Tests connectivity to the MQTT broker and topics
"""

import paho.mqtt.client as mqtt
import time
import json

# MQTT Configuration
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
TEST_TOPIC = "sic/dibimbing/catalina/titanio-yudista/test"


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to MQTT Broker successfully!")
        print(f"📡 Publishing test message to: {TEST_TOPIC}")

        # Publish test message
        test_data = {
            "test": True,
            "message": "MQTT connection test",
            "timestamp": time.time(),
        }
        client.publish(TEST_TOPIC, json.dumps(test_data))

    else:
        print(f"❌ Failed to connect, return code {rc}")


def on_publish(client, userdata, mid):
    print("✅ Test message published successfully!")
    print("🔌 Disconnecting...")
    client.disconnect()


def main():
    print("🧪 MQTT Connection Test")
    print("=" * 30)

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_publish = on_publish

    try:
        print("🔄 Connecting to MQTT Broker...")
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_forever()
        print("✅ Test completed successfully!")

    except Exception as e:
        print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    main()
