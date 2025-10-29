# DHT11 dan LED Dashboard

Proyek ini terdiri dari dua bagian:
1. **Arduino ESP32** - Membaca sensor DHT11 dan mengontrol LED via MQTT
2. **Dashboard Python** - Monitoring dan kontrol melalui web interface

## Hardware Requirements

### Arduino ESP32:
- ESP32 Development Board
- DHT11 Temperature & Humidity Sensor
- LED
- Resistor 220Ω (untuk LED)
- Resistor 10kΩ (pull-up untuk DHT11, opsional)
- Breadboard dan jumper wires

### Wiring:
```
DHT11:
- VCC → 3.3V
- GND → GND  
- DATA → GPIO 4

LED:
- Anode (+) → GPIO 2
- Cathode (-) → GND (melalui resistor 220Ω)
```

## Setup Arduino

### 1. Install PlatformIO
Pastikan PlatformIO sudah terinstall di VS Code.

### 2. Konfigurasi WiFi dan MQTT
Edit file `src/main.cpp` dan ganti:
```cpp
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

const char* mqtt_server = "your-cluster-url.s1.eu.hivemq.cloud";
const char* mqtt_username = "your_username";
const char* mqtt_password = "your_password";
```

### 3. Upload ke ESP32
```bash
pio run --target upload
```

### 4. Monitor Serial
```bash
pio device monitor
```

## Setup Dashboard Python

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Konfigurasi MQTT
Edit file `src/dashboard.py` dan ganti:
```python
MQTT_BROKER = "your-cluster-url.s1.eu.hivemq.cloud"
MQTT_USERNAME = "your_username"
MQTT_PASSWORD = "your_password"
```

### 3. Jalankan Dashboard
```bash
cd src
python dashboard.py
```

Dashboard akan tersedia di: http://localhost:8050

## HiveMQ Cloud Setup

### 1. Buat Akun HiveMQ Cloud
- Daftar di https://console.hivemq.cloud/
- Buat cluster baru (gratis)
- Catat URL cluster, username, dan password

### 2. Konfigurasi Credentials
- Cluster URL: Contoh `abc123def.s1.eu.hivemq.cloud`
- Port: 8883 (untuk TLS/SSL)
- Username dan password sesuai yang dibuat

### 3. Test Connection
Gunakan MQTT client seperti MQTT Explorer untuk test koneksi.

## Fitur

### Arduino ESP32:
- ✅ Membaca sensor DHT11 setiap 5 detik
- ✅ Publish data suhu & kelembaban ke MQTT
- ✅ Subscribe untuk kontrol LED
- ✅ LED bisa dinyalakan/dimatikan via MQTT

### Dashboard Python:
- ✅ Real-time monitoring suhu dan kelembaban
- ✅ Grafik historical data
- ✅ Tombol kontrol LED ON/OFF
- ✅ Status LED real-time
- ✅ Auto-refresh setiap 2 detik

## MQTT Topics

### Publish (ESP32 → Dashboard):
- **Topic**: `sic/dibimbing/catalina/titanio-yudista/pub/dht`
- **Format**: 
```json
{
  "temperature": 25.6,
  "humidity": 60.2,
  "timestamp": 123456789,
  "device_id": "ESP32_DHT11"
}
```

### Subscribe (Dashboard → ESP32):
- **Topic**: `sic/dibimbing/catalina/titanio-yudista/sub/led`
- **Format**:
```json
{
  "led": "on"    // atau "off"
}
```

## Troubleshooting

### ESP32 tidak connect ke WiFi:
- Pastikan SSID dan password benar
- Check jarak dari router
- Reset ESP32 dan coba lagi

### MQTT connection failed:
- Pastikan credentials HiveMQ Cloud benar
- Check internet connection
- Pastikan port 8883 tidak diblokir firewall

### Dashboard tidak menerima data:
- Check koneksi MQTT di dashboard
- Pastikan ESP32 sudah publish data
- Check topic MQTT sudah benar

### DHT11 error:
- Check wiring DHT11
- Pastikan power supply stabil
- Coba ganti sensor DHT11

## File Structure
```
├── src/
│   ├── main.cpp          # Arduino code
│   └── dashboard.py      # Python dashboard
├── platformio.ini        # PlatformIO config
├── requirements.txt      # Python dependencies
└── README.md            # Dokumentasi ini
```

## Libraries Used

### Arduino:
- WiFi (ESP32 built-in)
- PubSubClient (MQTT)
- DHT sensor library
- ArduinoJson

### Python:
- Dash (Web framework)
- Plotly (Charting)
- Paho-MQTT (MQTT client)
- Pandas (Data handling)