# Integrasi dari Perangkat IoT (project Gas Leak, Smoke and Fire Early Warning System) ke MQTT Broker, Python Dashboard, InfluxDB, dan Telegram Bot

# Hal-hal yang saya inginkan untuk diintegrasikan:
1. **MQTT Broker**: Gunakan broker MQTT untuk menerima data
2. **Python Dashboard**: Gunakan library seperti Dash, Plotly atau Flask untuk membuat dashboard web yang menampilkan data secara real-time
3. **InfluxDB**: Simpan data sensor ke InfluxDB untuk analisis jangka panjang
4. **Telegram Bot**: Kirim notifikasi ke Telegram ketika terdeteksi gas, asap, atau api

# Keperluan integrasi
1. **MQTT Broker**:
   - Gunakan library PubSubClient di ESP32 untuk mengirim data sensor ke broker MQTT.
   - Format Data JSON untuk semua sensor dalam satu payload
   - Topik Publish:
     - `home/sensors/data` (JSON: {"mq2_raw":value, "mq2_filtered":value, "mq5_raw":value, "mq5_filtered":value, "flame":0/1, "gas_detected":0/1, "smoke_detected":0/1, "fire_detected":0/1, "timestamp":epoch})
     - `home/sensors/status` (JSON: {"device_id":"esp32_001", "online":true, "uptime":seconds, "free_heap":bytes})
     - `home/sensors/alerts` (JSON: {"alert_type":"gas/smoke/fire/multi", "severity":"alert/danger/critical", "timestamp":epoch})
   - Topik Subscribe:
     - `home/commands/buzzer` (perintah: "ON" atau "OFF" untuk kontrol buzzer jarak jauh)
     - `home/commands/calibrate` (perintah: "START" untuk kalibrasi ulang threshold)
     - `home/config/thresholds` (JSON: {"mq2_threshold":value, "mq5_threshold":value})
     - `home/config/intervals` (JSON: {"sensor_read_ms":value, "log_interval_ms":value})
   - QoS Level: 1 untuk reliability
   - Retain: true untuk status dan config messages
   - Informasi MQTT broker:
     - Username: cakrawala_mqtt
     - Password: Jarvis5413$
     - Host: 103.127.97.247
     - Port: 1883 (non-TLS)
     - Client ID: esp32_warning_sensor_001
2. **Python Dashboard**:
   - Gunakan Plotly dan library Dash untuk membuat dashboard web yang menampilkan data sensor secara real-time.
   - Library Dependencies: dash, plotly, paho-mqtt, influxdb-client, python-telegram-bot
   - Fitur Dashboard:
     - **Real-time Monitoring Panel:**
       - Grafik waktu nyata untuk nilai MQ-2 raw/filtered dan MQ-5 raw/filtered
       - Gauge indicator untuk current sensor values
       - Status LED indicator untuk flame sensor (ON/OFF)
       - System status card (OK/ALERT/DANGER/CRITICAL)
     - **Historical Data Panel:**
       - Time-series charts (1h, 6h, 24h, 1w views)
       - Alert events timeline
       - Statistical summary (min/max/avg values)
     - **Control Panel:**
       - Tombol ON/OFF buzzer dengan MQTT publish ke `home/commands/buzzer`
       - Threshold adjustment sliders untuk MQ-2 dan MQ-5
       - Calibration trigger button
       - Device configuration panel
     - **Alert Management:**
       - Active alerts table dengan timestamp dan severity
       - Alert history log dengan filter by type/date
       - Alert acknowledgment system
     - **System Health:**
       - Device online/offline status
       - Network connectivity indicator
       - Memory usage dan uptime display
       - ADC saturation warnings
3. **InfluxDB**:
   - Gunakan library InfluxDB-Python untuk menyimpan data sensor ke InfluxDB.
   - Database Configuration:
     - URL: http://localhost:8086 (atau cloud instance)
     - Organization: gas_monitoring_org
     - Bucket: sensor_data
     - Token: [generate dari InfluxDB UI]
   - Struktur Data:
     - **Measurement: `sensor_readings`**
       - Fields: mq2_raw (int), mq2_filtered (int), mq5_raw (int), mq5_filtered (int), flame_digital (int)
       - Tags: device_id, location, sensor_type
       - Timestamp: RFC3339 format
     - **Measurement: `detection_events`**
       - Fields: gas_detected (bool), smoke_detected (bool), fire_detected (bool), system_status (string)
       - Tags: device_id, location, alert_level
       - Timestamp: RFC3339 format
     - **Measurement: `device_health`**
       - Fields: uptime (int), free_heap (int), wifi_rssi (int), adc_saturation_count (int)
       - Tags: device_id, firmware_version
       - Timestamp: RFC3339 format
   - Retention Policy: 30 days untuk raw data, 1 year untuk aggregated data
   - Batch Writing: buffer 100 points atau 10 seconds interval
   - Error Handling: retry mechanism dengan exponential backoff
4. **Telegram Bot**:
   - Gunakan library python-telegram-bot untuk mengirim notifikasi ke Telegram.
   - Bot Configuration:
     - Bot Token: [dari @BotFather]
     - Chat ID: [individual atau group chat ID]
     - Webhook URL: [optional untuk production]
   - Fitur Bot:
     - **Alert Notifications:**
       - Kirim pesan notifikasi ke grup/individu ketika terdeteksi gas, asap, atau api
       - Format pesan: "🚨 [ALERT TYPE] DETECTED! 🚨\nDevice: ESP32_001\nTime: 2025-10-26 14:30:25\nMQ-2: 450 (Smoke)\nMQ-5: 750 (Gas)\nFlame: DETECTED\nSeverity: CRITICAL"
       - Include sensor values dan timestamp
       - Different emoji untuk setiap jenis bahaya (🔥💨⛽)
     - **Bot Commands:**
       - `/start` - Initialize bot dan show welcome message
       - `/help` - Display available commands
       - `/status all` - Get current status semua sensor
       - `/status gas` - Get MQ-5 gas sensor status
       - `/status smoke` - Get MQ-2 smoke sensor status  
       - `/status fire` - Get flame sensor status
       - `/on` - Turn ON buzzer remotely (publish ke MQTT)
       - `/off` - Turn OFF buzzer remotely
       - `/calibrate` - Trigger sensor calibration
       - `/thresholds` - Show current threshold values
       - `/logs` - Get recent device activity logs
       - `/health` - Get device health status (uptime, memory, etc.)
     - **Alert Management:**
       - Rate limiting untuk prevent spam (max 1 alert per 30 seconds per type)
       - Alert acknowledgment dengan inline keyboard
       - Escalation untuk critical alerts (multiple notifications)
       - Silent hours configuration (no alerts 10 PM - 6 AM)
     - **User Authorization:**
       - Whitelist chat IDs untuk security
       - Admin-only commands untuk device control
       - User role management (admin, viewer, operator)

# Implementasi Requirements
## ESP32 Code Requirements (main.cpp):
- Include WiFi connectivity dengan auto-reconnect
- Include MQTT client dengan QoS 1 dan retain untuk status
- JSON payload formatting untuk sensor data
- MQTT subscribe untuk remote commands (buzzer, calibration, config)
- Error handling untuk network failures
- Watchdog timer untuk system reliability
- OTA update capability (optional)

## Python Dashboard Requirements (dashboard.py):
- Multi-threaded: MQTT client, InfluxDB writer, Telegram bot, Dash server
- Real-time data updates menggunakan Dash callbacks dan intervals
- WebSocket atau Server-Sent Events untuk real-time updates
- MQTT command publishing untuk device control
- InfluxDB query optimization untuk historical data
- Telegram bot integration dengan async handling
- Configuration file untuk credentials dan settings
- Logging system untuk debugging dan monitoring

## Security Considerations:
- MQTT credentials di environment variables atau config file
- InfluxDB token security
- Telegram bot token protection
- Network firewall rules untuk MQTT broker
- Device authentication dan authorization
- Input validation untuk MQTT commands dan web inputs

## Deployment Architecture:
```
ESP32 Device → MQTT Broker → Python Dashboard Service
                    ↓
               InfluxDB Database
                    ↓
              Telegram Bot API
```

## File Structure:
```
/project_root/
├── src/main.cpp (ESP32 firmware)
├── src/dashboard.py (Python service)
├── requirements.txt (Python dependencies)
├── config.json (configuration file)
├── docker-compose.yml (optional containerization)
└── README.md (setup instructions)
```