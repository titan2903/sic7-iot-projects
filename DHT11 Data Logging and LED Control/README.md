# DHT11 Data Logging and LED Control System

A complete IoT solution using ESP32, DHT11 sensor, and Python for real-time environmental monitoring and LED control via MQTT.

## 🚀 Features

### Monitoring (ESP32 → Python)
- ESP32 reads DHT11 sensor data (temperature & humidity)
- ESP32 publishes data to MQTT broker
- Python script subscribes and displays real-time data

### Controlling (Python → ESP32)
- Python script publishes "ON"/"OFF" commands
- ESP32 subscribes to commands
- ESP32 controls LED based on received commands

## 📡 MQTT Topics

- **Sensor Data Publishing**: `sic/dibimbing/catalina/titanio-yudista/pub/dht`
- **LED Control**: `sic/dibimbing/catalina/titanio-yudista/sub/led`

## 🔧 Hardware Requirements

### ESP32 Setup
- ESP32 Development Board
- DHT11 Temperature & Humidity Sensor
- LED
- 220Ω Resistor (for LED)
- Breadboard and jumper wires

### Wiring Diagram
```
ESP32 Pin    Component
---------    ---------
GPIO 4   →   DHT11 Data Pin
GPIO 2   →   LED (with 220Ω resistor)
3.3V     →   DHT11 VCC
GND      →   DHT11 GND & LED GND
```

## 💻 Software Setup

### 1. ESP32 Firmware Setup

1. **Configure WiFi Credentials**
   Edit `src/main.cpp` and update:
   ```cpp
   const char* ssid = "YOUR_WIFI_SSID";
   const char* password = "YOUR_WIFI_PASSWORD";
   ```

2. **Build and Upload**
   ```bash
   # Build the project
   pio run
   
   # Upload to ESP32
   pio run --target upload
   
   # Monitor serial output
   pio device monitor
   ```

### 2. Python Scripts Setup

1. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Python Scripts (Separated Functions)**

   **Option A: Monitor DHT11 Data (Subscribe)**
   ```bash
   python3 src/subscribe_dht.py
   ```
   - Displays real-time temperature and humidity
   - Logs data to CSV file
   - Shows status indicators (Cold/Warm, Dry/Humid)

   **Option B: Control LED (Publish)**
   ```bash
   python3 src/publish_led_control.py
   ```
   - Interactive menu for LED control
   - Send ON/OFF commands
   - Custom command support

## 🎮 Usage

### ESP32 Operation
1. Power on the ESP32
2. ESP32 connects to WiFi automatically
3. ESP32 connects to MQTT broker
4. Sensor data is published every 5 seconds
5. ESP32 listens for LED control commands

### Python Client Operation
1. Run the Python script
2. View real-time sensor data
3. Use the menu to control the LED:
   - Press `1` to turn LED ON
   - Press `2` to turn LED OFF
   - Press `3` to refresh display
   - Press `4` to exit

## 📊 Data Format

### Sensor Data (JSON)
```json
{
  "temperature": 25.6,
  "humidity": 60.2,
  "timestamp": 123456789,
  "device_id": "ESP32_DHT11"
}
```

### LED Control Commands
- `"ON"` - Turn LED on
- `"OFF"` - Turn LED off

## 🛠️ Configuration

### MQTT Broker
Default: `broker.hivemq.com` (free public broker)

To use a different broker, update both:
- `src/main.cpp`: `mqtt_server` variable
- `src/pubsub.py`: `MQTT_BROKER` variable

### Sensor Reading Interval
Default: 5 seconds

To change, modify `interval` in `src/main.cpp`:
```cpp
const long interval = 5000; // milliseconds
```

## 🔍 Troubleshooting

### ESP32 Issues
1. **WiFi Connection Failed**
   - Check SSID and password
   - Ensure WiFi network is 2.4GHz
   - Check signal strength

2. **MQTT Connection Failed**
   - Verify internet connection
   - Check MQTT broker status
   - Ensure unique client ID

3. **Sensor Reading Failed**
   - Check DHT11 wiring
   - Verify power supply
   - Check sensor pin configuration

### Python Client Issues
1. **Import Error**
   ```bash
   pip install paho-mqtt
   ```

2. **Connection Timeout**
   - Check internet connection
   - Verify MQTT broker URL
   - Check firewall settings

## 📈 Monitoring and Logging

### Serial Monitor (ESP32)
Connect to ESP32 via serial monitor to see:
- WiFi connection status
- MQTT connection status
- Sensor readings
- Received LED commands

### Python Client Output
The Python client displays:
- Connection status
- Real-time sensor data
- Command confirmations
- Error messages

## 🔄 System Flow

```
┌─────────────┐    MQTT     ┌─────────────────┐
│    ESP32    │ ──publish──→│   MQTT Broker   │
│   (DHT11)   │             │                 │
│             │ ←─subscribe─│                 │
└─────────────┘             └─────────────────┘
       ↑                              │
    LED Control                   Subscribe
       │                              │
       └── MQTT ←──────────────── ┌─────────────┐
           Commands               │   Python    │
                                 │   Client    │
                                 └─────────────┘
```

## 📝 License

This project is open source and available under the MIT License.

## 👥 Contributors

- **titanio-yudista** - Project Developer

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review serial monitor output
3. Verify wiring connections
4. Check MQTT broker connectivity