#!/usr/bin/env python3
"""
Quick script to fix ESP32 threshold values via MQTT
"""

import paho.mqtt.client as mqtt
import json
import ssl
import time

# MQTT Configuration
MQTT_BROKER = "ab36ea92cee24b64acda14d3001e34d4.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_USERNAME = "cakrawala_mqtt"
MQTT_PASSWORD = "vXtbU7m2DjTxBSLN"
MQTT_CLIENT_ID = "threshold_fix_client"

# Correct threshold values (from the updated ESP32 code)
CORRECT_THRESHOLDS = {
    "mq2_threshold": 700,  # New default for MQ2 (smoke)
    "mq5_threshold": 850,  # New default for MQ5 (gas)
}


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Connected to MQTT broker")

        # Subscribe to acknowledgment topic
        client.subscribe("home/config/thresholds/ack", qos=1)

        # Send corrected thresholds
        print(f"📤 Sending corrected thresholds: {CORRECT_THRESHOLDS}")
        payload = json.dumps(CORRECT_THRESHOLDS)
        client.publish("home/config/thresholds", payload, qos=1)

    else:
        print(f"❌ Failed to connect to MQTT broker: {rc}")


def on_message(client, userdata, msg):
    try:
        if msg.topic == "home/config/thresholds/ack":
            response = json.loads(msg.payload.decode())
            print(f"✅ ESP32 Response: {response}")

            if response.get("status") in ["saved", "current"]:
                print(f"🎯 New thresholds confirmed:")
                print(f"   MQ2 (Smoke): {response.get('mq2_threshold')}")
                print(f"   MQ5 (Gas): {response.get('mq5_threshold')}")
                print("✅ Threshold fix complete!")
                client.disconnect()

    except Exception as e:
        print(f"Error processing message: {e}")


def main():
    print("🔧 ESP32 Threshold Fix Tool")
    print("=" * 40)

    # Create MQTT client
    client = mqtt.Client(client_id=MQTT_CLIENT_ID)
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message

    # Configure TLS
    context = ssl.create_default_context()
    client.tls_set_context(context)

    try:
        print(f"🌐 Connecting to {MQTT_BROKER}:{MQTT_PORT}")
        client.connect(MQTT_BROKER, MQTT_PORT, 60)

        # Start loop and wait for completion
        client.loop_start()
        time.sleep(10)  # Wait for response
        client.loop_stop()

    except Exception as e:
        print(f"❌ Connection failed: {e}")


if __name__ == "__main__":
    main()
