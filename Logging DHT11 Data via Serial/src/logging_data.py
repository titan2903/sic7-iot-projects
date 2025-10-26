#!/usr/bin/env python3
"""
DHT11 Data Logger - Python Script
Receives temperature and humidity data from ESP32 via serial communication
and exports to CSV file with timestamp.

Author: Tim Catalina
Date: 21 October 2025
"""

import serial
import csv
import datetime
import time
import sys
import os

# Configuration
SERIAL_PORT = "/dev/ttyUSB0"  # Linux: /dev/ttyUSBx or /dev/ttyACMx, Windows: COMx, Mac: /dev/cu.usbserial-xxx
BAUD_RATE = 115200
CSV_FILE = "data/dht11_logging_data.csv"
TIMEOUT = 1  # Serial timeout in seconds


def setup_serial_connection():
    """
    Setup serial connection to ESP32
    Returns: serial connection object or None if failed
    """
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT)
        print(f"Connected to ESP32 on {SERIAL_PORT} at {BAUD_RATE} baud")
        time.sleep(2)  # Wait for ESP32 to initialize
        return ser
    except serial.SerialException as e:
        print(f"Error connecting to {SERIAL_PORT}: {e}")
        print("\n Tips:")
        print("   - Check if ESP32 is connected")
        print("   - Verify COM port (Windows: Device Manager, Linux: ls /dev/tty*)")
        print("   - Close Arduino IDE Serial Monitor if open")
        print("   - Try different COM port")
        return None


def create_csv_file():
    """
    Create CSV file with headers if it doesn't exist
    """
    # Create data directory if it doesn't exist
    data_dir = os.path.dirname(CSV_FILE)
    if data_dir and not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
        print(f"Created directory: {data_dir}")

    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    "Timestamp",
                    "Arduino_Millis_ms",
                    "Temperature_C",
                    "Humidity_%",
                    "Heat_Index_C",
                ]
            )
        print(f"Created CSV file: {CSV_FILE}")
    else:
        print(f"Using existing CSV file: {CSV_FILE}")


def calculate_heat_index(temp_c, humidity):
    """
    Calculate heat index (feels like temperature) in Celsius
    Formula: Simplified heat index calculation
    """
    try:
        temp_f = temp_c * 9 / 5 + 32  # Convert to Fahrenheit for calculation

        # Heat index formula (valid for temp >= 80°F and humidity >= 40%)
        if temp_f >= 80 and humidity >= 40:
            hi_f = (
                -42.379
                + 2.04901523 * temp_f
                + 10.14333127 * humidity
                + -0.22475541 * temp_f * humidity
                + -0.00683783 * temp_f * temp_f
                + -0.05481717 * humidity * humidity
                + 0.00122874 * temp_f * temp_f * humidity
                + 0.00085282 * temp_f * humidity * humidity
                + -0.00000199 * temp_f * temp_f * humidity * humidity
            )

            hi_c = (hi_f - 32) * 5 / 9  # Convert back to Celsius
            return round(hi_c, 2)
        else:
            return temp_c  # Return actual temperature if conditions not met
    except:
        return temp_c  # Return actual temperature on error


def parse_sensor_data(line):
    """
    Parse sensor data from serial line
    Expected format: timestamp_ms,temperature,humidity
    Returns: (arduino_millis, temperature, humidity) or None if invalid
    """
    try:
        line = line.strip()

        # Skip header lines and error messages
        if (
            "timestamp" in line.lower()
            or "error" in line.lower()
            or "dht11" in line.lower()
            or "format" in line.lower()
            or "---" in line
        ):
            return None

        # Parse data line
        if line.count(",") == 2:
            parts = line.split(",")
            arduino_millis = int(parts[0])
            temperature = float(parts[1])
            humidity = float(parts[2])

            # Validate sensor readings
            if -40 <= temperature <= 80 and 0 <= humidity <= 100:
                return arduino_millis, temperature, humidity
            else:
                print(
                    f"Invalid sensor values: Temp={temperature}°C, Humidity={humidity}%"
                )
                return None
        else:
            return None

    except (ValueError, IndexError) as e:
        print(f"Parse error: {line} - {e}")
        return None


def log_data_to_csv(arduino_millis, temperature, humidity, heat_index):
    """
    Log sensor data to CSV file
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with open(CSV_FILE, "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(
                [timestamp, arduino_millis, temperature, humidity, heat_index]
            )
        return True
    except Exception as e:
        print(f"Error writing to CSV: {e}")
        return False


def main():
    """
    Main function - Data logging loop
    """
    print("DHT11 Data Logger Starting...")
    print("=" * 50)

    # Setup CSV file
    create_csv_file()

    # Setup serial connection
    ser = setup_serial_connection()
    if not ser:
        print("Failed to connect to ESP32. Exiting...")
        return

    print(f"Data will be saved to: {CSV_FILE}")
    print("Starting data collection... (Press Ctrl+C to stop)")
    print("-" * 50)

    data_count = 0

    try:
        while True:
            if ser.in_waiting > 0:
                try:
                    # Read line from serial
                    line = ser.readline().decode("utf-8", errors="ignore").strip()

                    if line:
                        print(f"Received: {line}")

                        # Parse sensor data
                        parsed_data = parse_sensor_data(line)

                        if parsed_data:
                            arduino_millis, temperature, humidity = parsed_data
                            heat_index = calculate_heat_index(temperature, humidity)

                            # Log to CSV
                            if log_data_to_csv(
                                arduino_millis, temperature, humidity, heat_index
                            ):
                                data_count += 1

                                # Display formatted data
                                timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                                print(
                                    f"✅ [{timestamp}] Data #{data_count:03d} logged:"
                                )
                                print(f"   🌡️  Temperature: {temperature:.2f}°C")
                                print(f"   💧 Humidity: {humidity:.2f}%")
                                print(f"   🔥 Heat Index: {heat_index:.2f}°C")
                                print(f"   ⏱️  Arduino Time: {arduino_millis}ms")
                                print("-" * 30)

                except UnicodeDecodeError:
                    # Skip lines with encoding issues
                    continue

            time.sleep(0.1)  # Small delay to prevent excessive CPU usage

    except KeyboardInterrupt:
        print(f"\nData logging stopped by user")
        print(f"Total data points collected: {data_count}")

    except Exception as e:
        print(f"\nUnexpected error: {e}")

    finally:
        if ser and ser.is_open:
            ser.close()
            print("🔌 Serial connection closed")

        print(f"Data saved in: {os.path.abspath(CSV_FILE)}")
        print("DHT11 Data Logger finished")


if __name__ == "__main__":
    # Check if required libraries are installed
    try:
        import serial
    except ImportError:
        print("PySerial library not found!")
        print("Install with: pip install pyserial")
        sys.exit(1)

    main()
