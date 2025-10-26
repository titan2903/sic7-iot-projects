# 🚨 Gas Leak and Fire Early Warning System

Sistem peringatan dini terintegrasi untuk deteksi kebocoran gas, asap, dan api menggunakan **ESP32**, **MQTT**, **InfluxDB**, **Python Dashboard**, dan **Telegram Bot**.

## 📋 Fitur Utama

### 🔧 Hardware (ESP32)
- **Sensor MQ-2**: Deteksi asap dan polutan
- **Sensor MQ-5**: Deteksi gas LPG/butana
- **Flame Sensor**: Deteksi api dengan sensor infrared
- **Buzzer PWM**: Alert audio dengan nada berbeda untuk setiap bahaya
- **LED Indikator**: Visual feedback untuk setiap jenis deteksi
- **WiFi Connectivity**: Koneksi otomatis dengan auto-reconnect
- **MQTT Integration**: Publish data real-time dan menerima remote commands
- **OTA Updates**: Update firmware over-the-air

### 🌐 Dashboard Web (Python)
- **Real-time Monitoring**: Visualisasi data sensor secara live
- **Historical Data**: Grafik data historis dari InfluxDB
- **Control Panel**: Kontrol buzzer dan threshold dari web
- **Modern UI**: Interface responsif dengan Bootstrap
- **Alert Management**: Timeline dan history alert
- **System Health**: Monitoring status perangkat dan koneksi

### 📱 Telegram Bot
- **Instant Alerts**: Notifikasi langsung saat terdeteksi bahaya
- **Remote Commands**: Kontrol perangkat via chat commands
- **Status Monitoring**: Cek status sensor kapan saja
- **Multi-user Support**: Akses grup dan individual

### 💾 Data Storage (InfluxDB)
- **Time-series Database**: Penyimpanan data sensor yang efisien
- **Data Retention**: Kebijakan retensi 30 hari untuk raw data
- **Historical Analysis**: Query data historis untuk analisis
- **High Performance**: Optimized untuk IoT data

## 🏗️ Arsitektur Sistem

```
ESP32 Device → WiFi → MQTT Broker → Python Dashboard
                         ↓              ↓
                    Telegram Bot ← InfluxDB Database
```

## ⚡ Quick Start Guide

### 1. 🔌 Hardware Setup

**Wiring ESP32:**
```
MQ-2 (Smoke)  → GPIO34 (AO pin)
MQ-5 (Gas)    → GPIO35 (AO pin)  
Flame Sensor  → GPIO25 (DO pin)
LED Red (Gas) → GPIO5
LED Blue (Smoke) → GPIO2
LED Yellow (Fire) → GPIO4
Buzzer (PWM)  → GPIO22
```

### 2. 💻 Software Setup

**Install Dependencies:**
```bash
# Python dependencies untuk dashboard
pip install -r requirements.txt

# Setup InfluxDB dengan Docker
docker-compose up -d
```

**ESP32 Firmware:**
```bash
# Compile dan upload
platformio run --target upload

# Monitor serial output
platformio device monitor
```

### 3. 🔧 Configuration

**Environment Variables:**
```bash
# Copy dan edit environment file
cp .env.example .env
```

**Update .env dengan credentials:**
```bash
INFLUXDB_TOKEN=gas-monitoring-super-secret-token
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

### 4. 🚀 Running the System

**Start Dashboard:**
```bash
python src/dashboard.py
```

**Access Applications:**
- **Dashboard**: http://localhost:8050
- **InfluxDB**: http://localhost:8086 (admin/adminpassword)
- **Grafana** (optional): http://localhost:3000 (admin/admin)

## 📊 Dashboard Features

- **Real-time Monitoring**: Live sensor values dan status
- **Control Panel**: Remote buzzer control dan threshold settings
- **Historical Data**: Time-series charts dari InfluxDB
- **Alert Management**: Timeline dan history notifikasi
- **System Health**: Device status dan network monitoring

## 📱 Telegram Commands

- `/start` - Initialize bot
- `/status` - Get current sensor status
- `/on` - Turn buzzer ON
- `/off` - Turn buzzer OFF
- `/auto` - Set buzzer to AUTO mode
- `/help` - Show command list

## 🔧 Technical Specifications

### MQTT Topics
```bash
# ESP32 Publish
home/sensors/data     # Real-time sensor readings
home/sensors/status   # Device health status
home/sensors/alerts   # Alert notifications

# ESP32 Subscribe  
home/commands/buzzer     # Buzzer control
home/config/thresholds   # Threshold updates
```

### Hardware Specs
- **ESP32**: 240MHz dual-core, 520KB RAM, WiFi 2.4GHz
- **MQ-2**: Smoke sensor, 200-10000 ppm range
- **MQ-5**: LPG sensor, 200-10000 ppm range
- **Flame**: IR digital sensor, 760-1100nm

## 🛠️ Troubleshooting

**ESP32 WiFi Issues:**
- Verify SSID/password di main.cpp
- Ensure 2.4GHz network (tidak support 5GHz)
- Check serial monitor untuk error messages

**MQTT Connection:**
- Verify broker credentials
- Test dengan MQTT client tools
- Check firewall rules

**Sensor Calibration:**
- MQ sensors perlu 24-48 jam warm-up
- Calibrate di clean environment
- Adjust thresholds di kode atau dashboard

## ⚠️ Safety Disclaimer

Sistem ini untuk **early warning** dan **educational purposes**. Untuk aplikasi critical safety, gunakan sistem komersial bersertifikat.

## 📄 Files

- `src/main.cpp` - ESP32 firmware dengan WiFi, MQTT, sensors
- `src/dashboard.py` - Python web dashboard dengan real-time monitoring
- `platformio.ini` - PlatformIO config dengan libraries
- `requirements.txt` - Python dependencies
- `docker-compose.yml` - InfluxDB & Grafana setup
- `config.json` - System configuration
- `integration.md` - Detailed technical integration guide

---

*Built with ❤️ untuk keselamatan IoT modern*
