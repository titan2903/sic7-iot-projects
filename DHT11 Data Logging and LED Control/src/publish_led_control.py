#!/usr/bin/env python3
"""
LED Control System - Python MQTT Publisher
Author: Tim Catalina
Description: Publishes LED control commands to ESP32 via MQTT
"""

import paho.mqtt.client as mqtt
import time
import os
import ssl
from datetime import datetime

# MQTT Configuration for HiveMQ Cloud
MQTT_BROKER = "f0eacf8b4b0a4245a3f67db604624b4c.s1.eu.hivemq.cloud"  # Replace with your HiveMQ Cloud cluster host
MQTT_PORT = 8883  # TLS port for HiveMQ Cloud
MQTT_USERNAME = "dht11_user"  # Replace with your HiveMQ Cloud username
MQTT_PASSWORD = "Jarvis5413"  # Replace with your HiveMQ Cloud password
MQTT_KEEPALIVE = 60

# MQTT Topic for LED control
LED_TOPIC = "sic/dibimbing/catalina/titanio-yudista/sub/led"

# Global variables
client = None
commands_sent = 0
connection_status = False


def clear_screen():
    """Clear the terminal screen"""
    os.system("cls" if os.name == "nt" else "clear")


def display_header():
    """Display application header"""
    print("=" * 60)
    print("       LED Control System")
    print("      Python MQTT Publisher")
    print("=" * 60)
    print(f"Publishing to: {LED_TOPIC}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if connection_status:
        print("Status: Connected to MQTT Broker")
    else:
        print("Status: Disconnected from MQTT Broker")

    print(f"Commands sent: {commands_sent}")
    print("=" * 60)
    print()


def display_menu():
    """Display control menu"""
    print("LED CONTROL COMMANDS:")
    print("-" * 30)
    print("1  Turn LED ON")
    print("2  Turn LED OFF")
    print("3  Send Custom Command (ON/OFF)")
    print("4  Connection Status")
    print("5  Clear Screen")
    print("0  Exit")
    print("-" * 30)
    print()


def display_status():
    """Display current system status"""
    print("SYSTEM STATUS:")
    print("-" * 20)
    print(f"MQTT Broker: {MQTT_BROKER}:{MQTT_PORT}")
    print(f"LED Topic: {LED_TOPIC}")
    print(f"Connection: {'Connected' if connection_status else 'Disconnected'}")
    print(f"Commands Sent: {commands_sent}")
    print(f"Current Time: {datetime.now().strftime('%H:%M:%S')}")
    print()


def on_connect(client, userdata, flags, rc):
    """Callback for when the client receives a CONNACK response from the server"""
    global connection_status

    if rc == 0:
        connection_status = True
        print("Connected to MQTT Broker successfully!")
        print(f"Ready to publish commands to: {LED_TOPIC}")
        print()
    else:
        connection_status = False
        print(f"Failed to connect, return code {rc}")


def on_publish(client, userdata, mid):
    """Callback for when a message is published"""
    print("Command sent successfully!")


def on_disconnect(client, userdata, rc):
    """Callback for when the client disconnects from the server"""
    global connection_status
    connection_status = False

    if rc != 0:
        print("Unexpected disconnection from MQTT Broker")
        print("Attempting to reconnect...")
    else:
        print("Disconnected from MQTT Broker")


def publish_command(command):
    """Publish LED control command"""
    global commands_sent
    global client

    if not connection_status:
        print("Not connected to MQTT broker!")
        return False

    if client is None:
        print("MQTT client not initialized!")
        return False

    try:
        # Validate and normalize command
        valid_commands = ["ON", "OFF"]
        command_upper = command.strip().upper()

        if command_upper not in valid_commands:
            print(f"Warning: '{command}' is not a valid LED command")
            print(f"Valid commands: {', '.join(valid_commands)}")
            confirm = input("Continue anyway? (y/N): ").strip().lower()
            if confirm != "y":
                return False

        # Publish the command as uppercase payload using QoS 1 and wait for completion
        payload = command_upper
        print(f"Publishing payload='{payload}' to topic='{LED_TOPIC}' (qos=1)")
        info = client.publish(LED_TOPIC, payload, qos=1)

        # Wait for the publish to complete (blocks until mid is acknowledged or timeout)
        try:
            info.wait_for_publish(timeout=5)
        except Exception:
            pass

        if info.rc == mqtt.MQTT_ERR_SUCCESS:
            commands_sent += 1
            print(f"LED Command published: '{payload}'")
            print(f"Time: {datetime.now().strftime('%H:%M:%S')}")

            # Show expected ESP32 response
            if payload == "ON":
                print("Expected: LED should turn ON")
            elif payload == "OFF":
                print("Expected: LED should turn OFF")

            return True
        else:
            print(f"Failed to publish command: rc={info.rc}")
            return False

    except Exception as e:
        print(f"Error publishing command: {e}")
        return False


def setup_mqtt_client():
    """Setup and configure MQTT client for HiveMQ Cloud"""
    global client

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_disconnect = on_disconnect

    # Configure TLS for HiveMQ Cloud
    client.tls_set(
        ca_certs=None,
        certfile=None,
        keyfile=None,
        cert_reqs=ssl.CERT_REQUIRED,
        tls_version=ssl.PROTOCOL_TLS,
        ciphers=None,
    )

    # Set username and password for HiveMQ Cloud
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    try:
        print("Connecting to HiveMQ Cloud...")
        print(f"Broker: {MQTT_BROKER}")
        print(f"Using TLS on port {MQTT_PORT}")
        client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE)
        client.loop_start()

        # Wait for connection
        time.sleep(2)
        return True

    except Exception as e:
        print(f"Connection failed: {e}")
        print("Please check your HiveMQ Cloud credentials and network connection")
        return False


def handle_custom_command():
    """Handle custom command input"""
    print("Custom Command Mode")
    print()
    command = input("Enter LED command (ON/OFF): ")
    command = command.strip().upper()
    if command == "ON":
        print("Sending ON command...")
        return publish_command("ON")
    elif command == "OFF":
        print("Sending OFF command...")
        return publish_command("OFF")
    else:
        print("Invalid command. Please enter ON or OFF.")
        return False


def main_loop():
    """Main application loop"""
    while True:
        try:
            clear_screen()
            display_header()
            display_status()
            display_menu()

            choice = input("Enter your choice (0-5): ").strip()
            print()

            if choice == "1":
                print("Turning LED ON...")
                publish_command("ON")

            elif choice == "2":
                print("Turning LED OFF...")
                publish_command("OFF")

            elif choice == "3":
                handle_custom_command()

            elif choice == "4":
                print("Checking connection status...")
                if connection_status:
                    print("Connection is active")
                else:
                    print("Connection lost, attempting to reconnect...")
                    setup_mqtt_client()

            elif choice == "5":
                print("Screen cleared!")
                continue

            elif choice == "0":
                print("Exiting LED Control System...")
                break

            else:
                print("Invalid choice. Please enter 0-5.")

            # Pause before next iteration
            input("\nPress Enter to continue...")

        except KeyboardInterrupt:
            print("\n\n👋 Exiting...")
            break
        except EOFError:
            print("\n\n👋 Exiting...")
            break


def main():
    """Main function"""
    clear_screen()
    print("🚀 Starting LED Control System...")
    print()

    # Setup MQTT client
    if not setup_mqtt_client():
        print("Failed to setup MQTT client. Exiting.")
        return

    try:
        # Start main loop
        main_loop()

    except Exception as e:
        print(f"Unexpected error: {e}")

    finally:
        # Cleanup
        if client:
            client.loop_stop()
            client.disconnect()

        print()
        print("📊 SESSION SUMMARY:")
        print(f"   Commands sent: {commands_sent}")
        print(f"   Session duration: Started at program launch")
        print("✅ LED Control System shutdown complete!")


if __name__ == "__main__":
    main()
