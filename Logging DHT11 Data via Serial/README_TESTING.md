# DHT22 Data Logger - Testing Guide

## 📋 Overview
Proyek ini menggunakan ESP32 dengan sensor DHT22 untuk logging data suhu dan kelembaban ke file CSV melalui komunikasi serial.

## 🛠️ Setup untuk Testing

### 1. Testing di Wokwi (Simulator)
```bash
# Jalankan simulasi Wokwi
python test_wokwi.py

# Pilih opsi 1 untuk simulasi data
# Pilih opsi 2 untuk test fungsi CSV saja
```

### 2. Testing dengan Hardware Real
```bash
# Cek port serial ESP32
ls /dev/tty*

# Update SERIAL_PORT di src/data.py jika perlu
# Contoh: SERIAL_PORT = "/dev/ttyUSB0" atau "/dev/ttyACM0"

# Upload kode ke ESP32
pio run --target upload

# Jalankan data logger
python run_logger.py
```

### 3. Testing Functions Only
```bash
# Test individual functions
python test_wokwi.py
# Pilih opsi 2
```

## 📁 File Structure
```
project/
├── src/
│   ├── main.cpp          # ESP32 firmware
│   └── data.py          # Python data logger
├── data/
│   └── dht22_data.csv   # Output CSV file
├── test_wokwi.py        # Testing script untuk Wokwi
├── run_logger.py        # Main runner script
└── diagram.json         # Wokwi circuit diagram
```

## 🔧 Konfigurasi

### ESP32 (main.cpp)
- DHT22 sensor terhubung ke pin 5
- Serial baudrate: 115200
- Data format: `timestamp_ms,temperature_C,humidity_%`

### Python Logger (data.py)
- Serial port: `/dev/ttyUSB0` (Linux) atau sesuaikan
- CSV output: `data/dht22_data.csv`
- Heat index calculation included

## 📊 CSV Output Format
```csv
Timestamp,Arduino_Millis_ms,Temperature_C,Humidity_%,Heat_Index_C
2025-10-20 21:38:25,1760971105951,24.36,58.3,24.36
```

## 🧪 Testing Scenarios

### 1. Wokwi Simulation
- Simulates realistic DHT22 data
- Tests CSV creation and logging
- No hardware required

### 2. Hardware Testing
- Real ESP32 + DHT22 sensor
- Actual serial communication
- Real-time data logging

### 3. Function Testing
- Unit tests for CSV functions
- Data parsing validation
- Heat index calculation test

## 🚀 Quick Start

1. **Simulation Test:**
   ```bash
   python test_wokwi.py
   # Pilih 1 untuk simulasi lengkap
   ```

2. **Hardware Test:**
   ```bash
   # Upload firmware dulu
   pio run --target upload
   
   # Jalankan logger
   python run_logger.py
   ```

3. **Check Results:**
   ```bash
   # Lihat data CSV
   cat data/dht22_data.csv
   ```

## ⚠️ Troubleshooting

### Serial Port Issues
- Linux: Check `ls /dev/tty*`
- Update `SERIAL_PORT` in `src/data.py`
- Install pyserial: `pip install pyserial`

### CSV File Issues
- Pastikan folder `data/` ada
- Check file permissions
- Path relatif ke project root

### Wokwi Testing
- Gunakan `test_wokwi.py` untuk simulasi
- Tidak perlu hardware fisik
- Data artificial tapi realistis

## 📈 Expected Results

Setelah testing berhasil, Anda akan melihat:
- ✅ CSV file terbuat di `data/dht22_data.csv`
- ✅ Data logging dengan timestamp
- ✅ Heat index calculation
- ✅ Error handling untuk invalid data

## 🎯 Files Modified for Testing
- `src/data.py` - Fixed path dan serial port
- `test_wokwi.py` - Simulation script
- `run_logger.py` - Main runner
- `README_TESTING.md` - This guide