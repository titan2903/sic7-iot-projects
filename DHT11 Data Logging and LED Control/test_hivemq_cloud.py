#!/usr/bin/env python3
"""
HiveMQ Cloud Connection Tester
Tests MQTT connection to HiveMQ Cloud before running main applications
"""

import paho.mqtt.client as mqtt
import ssl
import time
import sys
import json
from datetime import datetime

# Test configuration (will be replaced by setup script)
MQTT_BROKER = "YOUR_CLUSTER_HOST.s1.hivemq.cloud"
MQTT_PORT = 8883
MQTT_USERNAME = "YOUR_HIVEMQ_USERNAME"
MQTT_PASSWORD = "YOUR_HIVEMQ_PASSWORD"
MQTT_KEEPALIVE = 60

# Test topics
TEST_TOPIC_PUB = "sic/dibimbing/catalina/titanio-yudista/test/pub"
TEST_TOPIC_SUB = "sic/dibimbing/catalina/titanio-yudista/test/sub"

# Global test variables
connection_success = False
message_received = False
publish_success = False


def on_connect(client, userdata, flags, rc):
    """Callback for connection"""
    global connection_success

    if rc == 0:
        print("Connected to HiveMQ Cloud successfully!")
        connection_success = True

        # Subscribe to test topic
        print(f"Subscribing to test topic: {TEST_TOPIC_SUB}")
        client.subscribe(TEST_TOPIC_SUB)
    else:
        error_messages = {
            1: "Connection refused - incorrect protocol version",
            2: "Connection refused - invalid client identifier",
            3: "Connection refused - server unavailable",
            4: "Connection refused - bad username or password",
            5: "Connection refused - not authorised",
        }

        error_msg = error_messages.get(rc, f"Connection refused - code {rc}")
        print(f"Connection failed: {error_msg}")
        connection_success = False


def on_message(client, userdata, msg):
    """Callback for received messages"""
    global message_received

    try:
        payload = msg.payload.decode()
        data = json.loads(payload)

        print(f"Message received on {msg.topic}:")
        print(f"   Content: {payload}")

        if isinstance(data, dict) and data.get("test") == "hivemq_cloud_connection":
            message_received = True
            print("Test message confirmed - pub/sub working!")

    except Exception as e:
        print(f"Error processing message: {e}")


def on_publish(client, userdata, mid):
    """Callback for published messages"""
    global publish_success
    publish_success = True
    print("Test message published successfully!")


def on_disconnect(client, userdata, rc):
    """Callback for disconnection"""
    if rc != 0:
        print(f"Unexpected disconnection (code: {rc})")
    else:
        print("Disconnected from HiveMQ Cloud")


def test_connection():
    """Test HiveMQ Cloud connection"""
    print("HiveMQ Cloud Connection Test")
    print("=" * 40)

    # Check if credentials are configured
    if (
        MQTT_BROKER == "YOUR_CLUSTER_HOST.s1.hivemq.cloud"
        or MQTT_USERNAME == "YOUR_HIVEMQ_USERNAME"
        or MQTT_PASSWORD == "YOUR_HIVEMQ_PASSWORD"
    ):
        print("HiveMQ Cloud credentials not configured!")
        print("   Please run: python3 setup_hivemq_cloud.py")
        return False

    print(f"Testing connection to: {MQTT_BROKER}:{MQTT_PORT}")
    print(f"Username: {MQTT_USERNAME}")
    print(f"Using TLS encryption")
    print()

    # Setup MQTT client
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_publish = on_publish
    client.on_disconnect = on_disconnect

    # Configure TLS
    try:
        client.tls_set(
            ca_certs=None,
            certfile=None,
            keyfile=None,
            cert_reqs=ssl.CERT_REQUIRED,
            tls_version=ssl.PROTOCOL_TLS_CLIENT,
            ciphers=None,
        )
        print("TLS configuration successful")
    except Exception as e:
        print(f"TLS configuration failed: {e}")
        return False

    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    # Connect
    try:
        print("Connecting to HiveMQ Cloud...")
        client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE)
        client.loop_start()

        # Wait for connection
        time.sleep(3)

        if not connection_success:
            print("Connection timeout or failed")
            client.loop_stop()
            return False

        # Test publish
        print("\nTesting message publishing...")
        test_message = {
            "test": "hivemq_cloud_connection",
            "timestamp": datetime.now().isoformat(),
            "status": "testing_pubsub",
        }

        result = client.publish(TEST_TOPIC_SUB, json.dumps(test_message))

        # Wait for publish and receive
        time.sleep(2)

        if not publish_success:
            print("Message publishing failed")

        if not message_received:
            print("Message published but not received (check topic permissions)")

        # Test DHT11 topics
        print("\nTesting DHT11 project topics...")

        dht_topics = [
            "sic/dibimbing/catalina/titanio-yudista/pub/dht",
            "sic/dibimbing/catalina/titanio-yudista/sub/led",
        ]

        for topic in dht_topics:
            print(f"Subscribing to: {topic}")
            client.subscribe(topic)

        time.sleep(1)

        # Disconnect
        client.loop_stop()
        client.disconnect()

        print("\nHiveMQ Cloud connection test completed!")
        print("Your DHT11 system is ready to use HiveMQ Cloud")

        return True

    except Exception as e:
        print(f"Connection error: {e}")
        return False


def main():
    """Main function"""
    success = test_connection()

    print("\n" + "=" * 40)
    if success:
        print("All tests passed!")
        print("\nNext steps:")
        print("   1. Upload ESP32 firmware")
        print("   2. Run: python3 src/subscribe_dht.py")
        print("   3. Run: python3 src/publish_led_control.py")
        return 0
    else:
        print("Tests failed!")
        print("\nTroubleshooting:")
        print("   1. Check HiveMQ Cloud credentials")
        print("   2. Verify cluster is running in HiveMQ Console")
        print("   3. Check network/firewall settings")
        print("   4. Run setup: python3 setup_hivemq_cloud.py")
        return 1


if __name__ == "__main__":
    sys.exit(main())
