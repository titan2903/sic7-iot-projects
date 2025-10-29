# Troubleshooting Guide

## Common Issues dan Solutions

### 1. ESP32 Issues

#### WiFi Connection Failed
```
Symptoms: ESP32 tidak dapat connect ke WiFi
Solutions:
- Check SSID dan password benar
- Pastikan WiFi 2.4GHz (ESP32 tidak support 5GHz)
- Check jarak dari router
- Reset ESP32 dan coba lagi
- Monitor serial untuk error messages
```

#### MQTT Connection Failed  
```
Symptoms: "Failed to connect, return code -2" atau similar
Solutions:
- Pastikan HiveMQ Cloud credentials benar
- Check internet connection
- Pastikan port 8883 tidak diblokir
- Test dengan MQTT Explorer dulu
- Check SSL/TLS configuration
```

#### DHT11 Sensor Error
```
Symptoms: "Failed to read from DHT sensor!"
Solutions:
- Check wiring DHT11 (VCC, GND, DATA ke GPIO 4)
- Pastikan power supply stabil (3.3V atau 5V)
- Tambah delay setelah dht.begin()
- Coba ganti sensor DHT11
- Check pull-up resistor (10kΩ optional)
```

#### LED Not Working
```
Symptoms: LED tidak menyala/mati saat dikontrol
Solutions:
- Check wiring LED (GPIO 2 ke anode, GND ke cathode via resistor)
- Pastikan resistor 220Ω terpasang
- Test dengan digitalWrite manual
- Check LED tidak rusak
- Monitor serial untuk command received
```

### 2. Dashboard Issues

#### Dependencies Error
```
Symptoms: Import errors untuk dash, plotly, paho-mqtt
Solutions:
pip install -r requirements.txt
# atau untuk spesifik package:
pip install dash plotly paho-mqtt pandas
```

#### MQTT Connection Failed (Dashboard)
```
Symptoms: Dashboard tidak receive data dari ESP32
Solutions:
- Check HiveMQ Cloud credentials sama dengan ESP32
- Test dengan mqtt_test.py script
- Check firewall blocking port 8883
- Pastikan topic names exact match
- Monitor MQTT broker untuk messages
```

#### Dashboard Not Loading
```
Symptoms: Browser tidak bisa akses http://localhost:8050
Solutions:
- Check Python script running tanpa error
- Pastikan port 8050 tidak digunakan aplikasi lain
- Try different port: app.run_server(port=8051)
- Check firewall settings
- Try akses via IP: http://192.168.x.x:8050
```

#### Charts Not Updating
```
Symptoms: Dashboard load tapi charts kosong/tidak update
Solutions:
- Check MQTT connection status
- Pastikan ESP32 publish data
- Check console browser untuk JavaScript errors
- Verify topic names match
- Check data format JSON
```

### 3. MQTT Broker Issues

#### HiveMQ Cloud Authentication
```
Symptoms: Connection refused, authentication failed
Solutions:
- Double-check username dan password
- Pastikan permissions set ke "Publish and Subscribe"
- Check cluster status (harus running)
- Try recreate credentials
- Test dengan MQTT Explorer tool
```

#### Topic Permission Denied
```
Symptoms: Publish/subscribe failed, permission denied
Solutions:
- Check topic permissions di HiveMQ Cloud console
- Set topic pattern ke "*" untuk allow all
- Atau set specific: "sic/dibimbing/catalina/titanio-yudista/#"
- Pastikan user punya Publish dan Subscribe rights
```

#### SSL/TLS Certificate Issues
```
Symptoms: SSL handshake failed, certificate errors
Solutions:
ESP32:
espClient.setInsecure(); // bypass certificate check

Python:
context.verify_mode = ssl.CERT_NONE
context.check_hostname = False
```

### 4. Hardware Issues

#### Power Supply Problems
```
Symptoms: ESP32 restart, sensor readings inconsistent
Solutions:
- Use power supply minimal 500mA
- Check USB cable quality
- Add capacitor 100uF di power rails
- Avoid long wires untuk power
- Check voltage dengan multimeter
```

#### Wiring Issues
```
Symptoms: Sensor tidak terbaca, LED tidak kontrol
Solutions:
DHT11 Wiring:
- VCC: 3.3V atau 5V
- GND: Ground
- DATA: GPIO 4
- Optional: 10kΩ pull-up resistor DATA ke VCC

LED Wiring:
- Anode (+): GPIO 2
- Cathode (-): GND melalui resistor 220Ω
```

### 5. Development Issues

#### PlatformIO Build Errors
```
Symptoms: Compilation failed, library not found
Solutions:
- Check platformio.ini libraries
- Clean build: pio run --target clean
- Update libraries: pio lib update
- Check board definition correct
- Restart VS Code
```

#### Upload Failed
```
Symptoms: Cannot upload to ESP32
Solutions:
- Hold BOOT button saat upload
- Check COM port correct
- Try different USB cable
- Check driver ESP32 terinstall
- Reset ESP32 before upload
```

### 6. Debugging Tools

#### Serial Monitor
```bash
# PlatformIO
pio device monitor

# Arduino IDE
Tools > Serial Monitor (115200 baud)
```

#### MQTT Testing
```bash
# Test script
python3 src/mqtt_test.py

# MQTT Explorer (GUI tool)
Download: http://mqtt-explorer.com/
```

#### Network Testing
```bash
# Ping HiveMQ server
ping your-cluster-url.s1.eu.hivemq.cloud

# Check port open
telnet your-cluster-url.s1.eu.hivemq.cloud 8883
```

## Debug Checklist

### Pre-deployment:
- [ ] WiFi credentials correct
- [ ] HiveMQ Cloud credentials correct  
- [ ] All libraries installed
- [ ] Hardware wiring verified
- [ ] Serial monitor working

### Runtime Testing:
- [ ] ESP32 connects to WiFi
- [ ] ESP32 connects to MQTT
- [ ] DHT11 readings valid
- [ ] ESP32 publishes data
- [ ] Dashboard receives data
- [ ] LED control works
- [ ] Charts update real-time

### Common Commands:
```bash
# Build and upload Arduino
pio run --target upload

# Monitor serial output  
pio device monitor

# Install Python deps
pip install -r requirements.txt

# Test MQTT connection
python3 src/mqtt_test.py

# Run dashboard
python3 src/dashboard.py
```

## Getting Help

Jika masih ada issues:
1. Check dokumentasi library terkait
2. Search di Stack Overflow
3. Check HiveMQ Cloud documentation
4. Review code comments
5. Test dengan minimal example dulu