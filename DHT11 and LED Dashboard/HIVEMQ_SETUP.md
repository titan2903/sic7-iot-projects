# HiveMQ Cloud Configuration Example
# 
# Ikuti langkah-langkah berikut untuk setup HiveMQ Cloud:

## 1. Membuat Akun HiveMQ Cloud

1. Buka https://console.hivemq.cloud/
2. Klik "Sign Up" untuk membuat akun baru
3. Verifikasi email Anda
4. Login ke console

## 2. Membuat Cluster

1. Di dashboard, klik "Create Cluster"
2. Pilih "Serverless" (gratis)
3. Pilih region terdekat (contoh: eu-west-1)
4. Beri nama cluster (contoh: "dht11-dashboard")
5. Klik "Create"

## 3. Setup Access Management

1. Setelah cluster dibuat, masuk ke cluster
2. Pergi ke tab "Access Management"
3. Klik "Add Credentials"
4. Buat username dan password (contoh: user: "esp32user", pass: "secretpassword123")
5. Set permissions: "Publish and Subscribe" untuk topic "*"

## 4. Mendapatkan Connection Details

Setelah cluster aktif, Anda akan mendapatkan informasi seperti:

```
Cluster URL: abc123def456.s1.eu.hivemq.cloud
Port: 8883 (TLS)
Username: esp32user
Password: secretpassword123
```

## 5. Update Konfigurasi

### Arduino (src/main.cpp):
```cpp
const char* mqtt_server = "abc123def456.s1.eu.hivemq.cloud";
const int mqtt_port = 8883;
const char* mqtt_username = "esp32user";
const char* mqtt_password = "secretpassword123";
```

### Dashboard (src/dashboard.py):
```python
MQTT_BROKER = "abc123def456.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_USERNAME = "esp32user"
MQTT_PASSWORD = "secretpassword123"
```

## 6. Test Connection

Gunakan MQTT client untuk test:
- MQTT Explorer: http://mqtt-explorer.com/
- Atau gunakan script: `python3 src/mqtt_test.py`

## Troubleshooting

### Connection Refused:
- Pastikan credentials benar
- Check port 8883 tidak diblokir firewall
- Pastikan cluster sudah running

### Authentication Failed:
- Double-check username dan password
- Pastikan permissions sudah diset

### SSL/TLS Errors:
- Pastikan menggunakan port 8883
- ESP32: gunakan `espClient.setInsecure()`
- Python: context dengan `verify_mode = ssl.CERT_NONE`

## Limits (Free Tier)

- Concurrent connections: 100
- Messages per month: 10M
- Data transfer: 10GB/month
- Message retention: 1 day

Ini lebih dari cukup untuk proyek DHT11 dashboard!