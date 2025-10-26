#!/usr/bin/env python3
"""
LED Control Test Suite
Tests all LED commands automatically
"""

import paho.mqtt.client as mqtt
import ssl
import time
import json

# MQTT Configuration for HiveMQ Cloud
MQTT_BROKER = "f0eacf8b4b0a4245a3f67db604624b4c.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_USERNAME = "dht11_user"
MQTT_PASSWORD = "Jarvis5413"
MQTT_KEEPALIVE = 60

# MQTT Topic for LED control
LED_TOPIC = "sic/dibimbing/catalina/titanio-yudista/sub/led"

# Test variables
connection_success = False
commands_tested = 0


def on_connect(client, userdata, flags, rc):
    """Callback for connection"""
    global connection_success

    if rc == 0:
        print("✅ Connected to HiveMQ Cloud for testing!")
        connection_success = True
    else:
        print(f"❌ Connection failed: {rc}")
        connection_success = False


def on_publish(client, userdata, mid):
    """Callback for published messages"""
    print("  📤 Command sent successfully")


def test_all_commands():
    """Test all LED commands"""
    global commands_tested

    print("🧪 LED Command Test Suite")
    print("=" * 40)

    # Setup MQTT client
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_publish = on_publish

    # Configure TLS for HiveMQ Cloud
    client.tls_set(
        ca_certs=None,
        certfile=None,
        keyfile=None,
        cert_reqs=ssl.CERT_REQUIRED,
        tls_version=ssl.PROTOCOL_TLS,
        ciphers=None,
    )

    # Set username and password
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    try:
        print("🔄 Connecting to HiveMQ Cloud...")
        client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE)
        client.loop_start()

        # Wait for connection
        time.sleep(2)

        if not connection_success:
            print("❌ Connection failed!")
            return False

        print(f"📡 Testing commands on topic: {LED_TOPIC}")
        print()

        # Test commands
        test_commands = [
            ("ON", "Turn LED ON", 2),
            ("OFF", "Turn LED OFF", 2),
            ("ON", "Turn LED ON again", 2),
            ("OFF", "Turn LED OFF again", 2),
            ("ON", "Final ON test", 2),
            ("OFF", "Final OFF test", 2),
        ]

        for i, (command, description, delay) in enumerate(test_commands, 1):
            print(f"🧪 Test {i}/{len(test_commands)}: {description}")
            print(f"   Command: {command}")

            result = client.publish(LED_TOPIC, command)

            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                commands_tested += 1
                print("   ✅ Published successfully")
                print(f"   ⏳ Waiting {delay}s for ESP32 to process...")
                time.sleep(delay)
            else:
                print(f"   ❌ Publish failed: {result.rc}")

            print()

        # Disconnect
        client.loop_stop()
        client.disconnect()

        print("🎉 Test suite completed!")
        print(f"📊 Commands tested: {commands_tested}/{len(test_commands)}")

        return True

    except Exception as e:
        print(f"❌ Test error: {e}")
        return False


def main():
    """Main function"""
    print("🚀 Starting LED Control Test Suite...")
    print()

    success = test_all_commands()

    print("\n" + "=" * 40)
    if success:
        print("✅ All tests completed!")
        print("\n📝 Check your ESP32 Serial Monitor to see:")
        print("   • Connection messages")
        print("   • Command processing")
        print("   • LED state changes")
        print("   • Blink/Pulse animations")
    else:
        print("❌ Tests failed!")
        print("\n🔧 Check:")
        print("   • ESP32 is connected and running")
        print("   • HiveMQ Cloud credentials are correct")
        print("   • Network connection is stable")


if __name__ == "__main__":
    main()
