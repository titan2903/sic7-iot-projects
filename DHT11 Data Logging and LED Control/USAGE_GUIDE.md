# 📚 Script Usage Guide

## 🎯 Fungsi Sistem yang Sudah Dipisah

Sekarang sistem DHT11 Data Logging dan LED Control memiliki **3 script Python terpisah** sesuai dengan fungsi masing-masing:

### 📊 1. **Monitor DHT11 Data** (`subscribe_dht.py`)

**Fungsi:**
- Subscribe ke topik DHT11: `sic/dibimbing/catalina/titanio-yudista/pub/dht`
- Menampilkan data suhu dan kelembaban real-time
- Logging data ke file CSV (`dht11_data.csv`)
- Status indicator (Cold/Warm, Dry/Humid)

**Cara Menjalankan:**
```bash
python3 src/subscribe_dht.py
```

**Fitur:**
- ✅ Real-time data display
- 📄 Automatic CSV logging
- 🌡️ Temperature status (Cold/Cool/Warm/Hot)
- 💧 Humidity status (Dry/Comfortable/Humid/Very Humid)
- 📊 Data counter
- 🕒 Timestamp tracking

### 🎛️ 2. **Control LED** (`publish_led_control.py`)

**Fungsi:**
- Publish perintah ke topik LED: `sic/dibimbing/catalina/titanio-yudista/sub/led`
- Interface interaktif untuk kontrol LED
- Support custom commands

**Cara Menjalankan:**
```bash
python3 src/publish_led_control.py
```

**Menu Control:**
- 1️⃣ Turn LED ON
- 2️⃣ Turn LED OFF
- 3️⃣ Toggle LED (Smart toggle)
- 4️⃣ Send Custom Command
- 5️⃣ Connection Status
- 6️⃣ Clear Screen
- 0️⃣ Exit

### 🔄 3. **Combined Interface** (`pubsub.py`)

**Fungsi:**
- Gabungan monitor + control dalam satu interface
- Script original yang sudah ada sebelumnya

**Cara Menjalankan:**
```bash
python3 src/pubsub.py
```

## 🚀 Quick Start dengan Launcher

Gunakan script launcher untuk memilih mode yang diinginkan:

```bash
./run.sh
```

**Menu Launcher:**
```
1. 📊 Monitor DHT11 Data (Subscribe)
2. 🎛️  Control LED (Publish)
3. 🔄 Combined Interface (Original)
4. 🧪 Test MQTT Connection
0. ❌ Exit
```

## 📁 Struktur File Python

```
src/
├── main.cpp                 # ESP32 firmware
├── subscribe_dht.py         # DHT11 data monitor
├── publish_led_control.py   # LED control system
└── pubsub.py               # Combined interface
```

## 💡 Skenario Penggunaan

### **Scenario 1: Monitoring Only**
Jika Anda hanya ingin memonitor data sensor:
```bash
python3 src/subscribe_dht.py
```

### **Scenario 2: Control Only**
Jika Anda hanya ingin mengontrol LED:
```bash
python3 src/publish_led_control.py
```

### **Scenario 3: Development/Testing**
Untuk development, jalankan di 2 terminal terpisah:
```bash
# Terminal 1: Monitor
python3 src/subscribe_dht.py

# Terminal 2: Control
python3 src/publish_led_control.py
```

### **Scenario 4: All-in-One**
Untuk penggunaan normal dengan semua fitur:
```bash
python3 src/pubsub.py
```

## 📊 Data Logging

Script `subscribe_dht.py` otomatis menyimpan data ke file `dht11_data.csv` dengan format:

```csv
timestamp,temperature,humidity,device_id
2025-10-21 14:30:15,25.6,60.2,ESP32_DHT11
2025-10-21 14:30:20,25.7,60.1,ESP32_DHT11
```

## 🔧 Konfigurasi

Semua script menggunakan konfigurasi MQTT yang sama:
- **Broker:** `broker.hivemq.com:1883`
- **DHT Topic:** `sic/dibimbing/catalina/titanio-yudista/pub/dht`
- **LED Topic:** `sic/dibimbing/catalina/titanio-yudista/sub/led`

## ✅ Ready to Use!

Sistem DHT11 Data Logging dan LED Control dengan **script terpisah** sudah siap digunakan! 🎉