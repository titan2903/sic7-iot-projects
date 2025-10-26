#!/usr/bin/env python3
"""
Wokwi Testing Script - Simulate serial data for testing CSV logging
This script simulates DHT22 data as if it's coming from Wokwi serial monitor
"""

import sys
import os
import time
import random

# Add src directory to path so we can import our modules
sys.path.append("src")
from logging_data import (
    create_csv_file,
    parse_sensor_data,
    log_data_to_csv,
    calculate_heat_index,
)


def simulate_wokwi_data():
    """
    Simulate DHT22 data similar to what Wokwi would output
    """
    print("🧪 WOKWI SIMULATION MODE")
    print("=" * 50)

    # Create CSV file first
    create_csv_file()

    # Simulate ESP32 startup messages
    startup_messages = [
        "DHT22 Data Logger Started",
        "Format: timestamp_ms,temperature_C,humidity_%",
        "========================================",
    ]

    print("\n📡 Simulating ESP32 startup:")
    for msg in startup_messages:
        print(f"   {msg}")
        time.sleep(0.5)

    print("\n🔄 Starting simulated data collection...")
    print("-" * 50)

    data_count = 0
    start_time = time.time() * 1000  # Convert to milliseconds

    try:
        for i in range(20):  # Simulate 20 data points
            # Simulate realistic sensor values
            temperature = round(random.uniform(20.0, 35.0), 2)  # 20-35°C
            humidity = round(random.uniform(40.0, 80.0), 2)  # 40-80%
            arduino_millis = int(start_time + (i * 5000))  # Every 5 seconds

            # Create simulated serial line (same format as ESP32)
            simulated_line = f"{arduino_millis},{temperature},{humidity}"

            print(f"📡 Simulated serial: {simulated_line}")

            # Parse the simulated data
            parsed_data = parse_sensor_data(simulated_line)

            if parsed_data:
                arduino_millis, temperature, humidity = parsed_data
                heat_index = calculate_heat_index(temperature, humidity)

                # Log to CSV
                if log_data_to_csv(arduino_millis, temperature, humidity, heat_index):
                    data_count += 1

                    # Display formatted data
                    print(f"✅ Data #{data_count:03d} logged:")
                    print(f"   🌡️  Temperature: {temperature:.2f}°C")
                    print(f"   💧 Humidity: {humidity:.2f}%")
                    print(f"   🔥 Heat Index: {heat_index:.2f}°C")
                    print(f"   ⏱️  Arduino Time: {arduino_millis}ms")
                    print("-" * 30)

            time.sleep(1)  # Wait 1 second between readings

    except KeyboardInterrupt:
        print(f"\n🛑 Simulation stopped by user")

    print(f"\n📈 Total simulated data points: {data_count}")
    print(f"📁 Data saved in: {os.path.abspath('data/dht22_data.csv')}")
    print("✅ Wokwi simulation completed!")


def test_csv_functions():
    """
    Test individual CSV functions
    """
    print("🧪 TESTING CSV FUNCTIONS")
    print("=" * 30)

    # Test 1: CSV file creation
    print("Test 1: CSV file creation")
    create_csv_file()
    print("✅ CSV creation test passed\n")

    # Test 2: Data parsing
    print("Test 2: Data parsing")
    test_lines = [
        "12345,25.50,65.30",
        "DHT22 Data Logger Started",  # Should be ignored
        "23456,invalid,75.20",  # Should fail
        "34567,28.75,55.80",
    ]

    for line in test_lines:
        result = parse_sensor_data(line)
        if result:
            print(f"   ✅ Parsed: {line} -> {result}")
        else:
            print(f"   ⚠️  Ignored: {line}")

    print("\n✅ Data parsing test completed\n")

    # Test 3: Heat index calculation
    print("Test 3: Heat index calculation")
    test_temps = [(25.0, 60.0), (30.0, 80.0), (35.0, 70.0)]

    for temp, humidity in test_temps:
        heat_index = calculate_heat_index(temp, humidity)
        print(f"   🌡️  {temp}°C, {humidity}% -> Heat Index: {heat_index}°C")

    print("✅ Heat index test completed")


if __name__ == "__main__":
    print("🚀 DHT22 Wokwi Testing Suite")
    print("=" * 40)

    choice = input(
        "\nChoose test mode:\n1. Simulate Wokwi data\n2. Test CSV functions only\n\nEnter choice (1 or 2): "
    )

    if choice == "1":
        simulate_wokwi_data()
    elif choice == "2":
        test_csv_functions()
    else:
        print("Invalid choice. Running simulation...")
        simulate_wokwi_data()
