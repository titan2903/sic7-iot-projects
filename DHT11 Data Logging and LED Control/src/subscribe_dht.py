#!/usr/bin/env python3
"""
DHT11 Data Monitoring - Python MQTT Subscriber
Author: Tim Catalina
Description: Subscribes to DHT11 sensor data and displays real-time monitoring
"""

import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime
import os
import csv
import ssl

# MQTT Configuration for HiveMQ Cloud
MQTT_BROKER = "f0eacf8b4b0a4245a3f67db604624b4c.s1.eu.hivemq.cloud"  # Replace with your HiveMQ Cloud cluster host
MQTT_PORT = 8883  # TLS port for HiveMQ Cloud
MQTT_USERNAME = "dht11_user"  # Replace with your HiveMQ Cloud username
MQTT_PASSWORD = "Jarvis5413"  # Replace with your HiveMQ Cloud password
MQTT_KEEPALIVE = 60

# MQTT Topic for DHT11 data
DHT_TOPIC = "sic/dibimbing/catalina/titanio-yudista/pub/dht"

# Logging configuration
LOG_FILE = "dht11_data_log.csv"
ENABLE_LOGGING = True

# Global variables
sensor_data = {}
data_count = 0


def clear_screen():
    """Clear the terminal screen"""
    os.system("cls" if os.name == "nt" else "clear")


def display_header():
    """Display application header"""
    print("=" * 60)
    print("     DHT11 Data Monitoring System")
    print("           Python MQTT Subscriber")
    print("=" * 60)
    print(f"Listening to: {DHT_TOPIC}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if ENABLE_LOGGING:
        print(f"Logging to: {LOG_FILE}")
    print("=" * 60)
    print()


def display_sensor_data():
    """Display current sensor data"""
    if sensor_data:
        print("LATEST SENSOR READING:")
        print("-" * 40)
        print(f"Temperature: {sensor_data.get('temperature', 'N/A')}°C")
        print(f"Humidity:    {sensor_data.get('humidity', 'N/A')}%")
        print(f"Timestamp:   {sensor_data.get('last_update', 'N/A')}")
        print(f"Device ID:   {sensor_data.get('device_id', 'N/A')}")
        print(f"Data Count:  {data_count}")

        # Temperature status indicator
        temp = sensor_data.get("temperature")
        if temp is not None:
            if temp < 20:
                temp_status = "Cold"
            elif temp < 25:
                temp_status = "Cool"
            elif temp < 30:
                temp_status = "Warm"
            else:
                temp_status = "Hot"
            print(f"Status:     {temp_status}")

        # Humidity status indicator
        humidity = sensor_data.get("humidity")
        if humidity is not None:
            if humidity < 30:
                humidity_status = "Dry"
            elif humidity < 60:
                humidity_status = "Comfortable"
            elif humidity < 80:
                humidity_status = "Humid"
            else:
                humidity_status = "Very Humid"
            print(f"Status:     {humidity_status}")

        print("-" * 40)
    else:
        print("SENSOR DATA: Waiting for data from ESP32...")
        print("Make sure ESP32 is connected and publishing data...")
    print()


def log_data_to_csv(data):
    """Log sensor data to CSV file"""
    if not ENABLE_LOGGING:
        return
    try:
        # Check if file exists, if not create with headers
        file_exists = os.path.isfile(LOG_FILE)

        with open(LOG_FILE, "a", newline="") as csvfile:
            fieldnames = ["timestamp", "temperature", "humidity", "device_id"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            writer.writerow(
                {
                    "timestamp": data.get("last_update"),
                    "temperature": data.get("temperature"),
                    "humidity": data.get("humidity"),
                    "device_id": data.get("device_id"),
                }
            )

        print(f"Data logged to {LOG_FILE}")

    except Exception as e:
        print(f"Error logging data: {e}")


def on_connect(client, userdata, flags, rc):
    """Callback for when the client receives a Connect response from the server"""
    if rc == 0:
        print("Connected to MQTT Broker!")
        print(f"Subscribing to: {DHT_TOPIC}")
        client.subscribe(DHT_TOPIC)
        print("Waiting for sensor data...")
        print()
    else:
        print(f"Failed to connect, return code {rc}")


def on_message(client, userdata, msg):
    """Callback for when a PUBLISH message is received from the server"""
    global sensor_data, data_count
    try:
        # Decode the JSON payload
        payload = json.loads(msg.payload.decode())

        # Update sensor data
        sensor_data = {
            "temperature": payload.get("temperature"),
            "humidity": payload.get("humidity"),
            "device_id": payload.get("device_id"),
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "raw_timestamp": payload.get("timestamp"),
        }

        # Increment data counter
        data_count += 1

        # Clear screen and display updated data
        clear_screen()
        display_header()

        # Log the received data
        print(f"New data received! (#{data_count})")
        print(f"   Temperature: {payload.get('temperature')}°C")
        print(f"   Humidity: {payload.get('humidity')}%")
        print()

        # Display current sensor data
        display_sensor_data()

        # Log to CSV file
        if ENABLE_LOGGING:
            log_data_to_csv(sensor_data)

        # Display menu
        print("CONTROLS:")
        print("-" * 20)
        print("Press Ctrl+C to exit")
        print("Data updates automatically...")
        print()

    except json.JSONDecodeError:
        print("Error: Invalid JSON received")
        print(f"Raw message: {msg.payload.decode()}")
    except Exception as e:
        print(f"Error processing message: {e}")


def on_disconnect(client, userdata, rc):
    """Callback for when the client disconnects from the server"""
    if rc != 0:
        print("Unexpected disconnection from MQTT Broker")
        print("Attempting to reconnect...")
    else:
        print("Disconnected from MQTT Broker")


def setup_mqtt_client():
    """Setup and configure MQTT client for HiveMQ Cloud"""
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
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
        print("🔄 Connecting to HiveMQ Cloud...")
        print(f"📡 Broker: {MQTT_BROKER}")
        print(f"🔐 Using TLS on port {MQTT_PORT}")
        client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE)
        return client
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("💡 Please check your HiveMQ Cloud credentials and network connection")
        return None


def main():
    """Main function"""
    clear_screen()
    print("🚀 Starting DHT11 Data Monitoring System...")
    print()

    # Setup MQTT client
    client = setup_mqtt_client()
    if not client:
        print("Failed to setup MQTT client. Exiting.")
        return

    # Display initial interface
    display_header()
    display_sensor_data()

    try:
        # Start the MQTT loop
        client.loop_forever()

    except KeyboardInterrupt:
        print("\n\n👋 Shutting down DHT11 monitor...")
        client.disconnect()

        if data_count > 0:
            print(f"📊 Total data received: {data_count} readings")
            if ENABLE_LOGGING:
                print(f"📄 Data saved to: {LOG_FILE}")

        print("✅ Goodbye!")

    except Exception as e:
        print(f"Unexpected error: {e}")
        client.disconnect()


if __name__ == "__main__":
    main()
