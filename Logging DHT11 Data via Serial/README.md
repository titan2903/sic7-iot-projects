# DHT22 Data Logger Project

Proyek untuk logging data suhu dan kelembaban dari sensor DHT22 menggunakan ESP32 dan Python.

## 📋 Komponen Yang Dibutuhkan

- ESP32 DevKit v1
- Sensor DHT22
- Breadboard
- Kabel jumper
- Kabel USB untuk ESP32

## 🔌 Koneksi Hardware

Berdasarkan `diagram.json`:

| DHT22 Pin | ESP32 Pin | Keterangan |
|-----------|-----------|------------|
| VCC       | 3.3V      | Power supply |
| GND       | GND       | Ground |
| DATA      | GPIO 5    | Data signal |

## 🚀 Cara Menggunakan

### 1. Setup ESP32

1. **Install PlatformIO** di VS Code
2. **Build dan Upload** kode ke ESP32:
   ```bash
   pio run -t upload
   ```

### 2A. Untuk Hardware Real (ESP32 Fisik)

1. **Install Python library** yang diperlukan:
   ```bash
   pip install pyserial
   ```

2. **Edit port COM** di `data.py`:
   ```python
   SERIAL_PORT = 'COM7'  # Windows
   # SERIAL_PORT = '/dev/ttyUSB0'  # Linux
   # SERIAL_PORT = '/dev/cu.usbserial-xxx'  # Mac
   ```

3. **Jalankan script Python**:
   ```bash
   python src/data.py
   ```

### 2B. Untuk Simulasi Wokwi

**⚠️ PENTING**: Wokwi tidak bisa menjalankan script Python secara langsung, sehingga CSV file tidak otomatis terbuat.

#### Opsi 1: Manual Copy-Paste dari Wokwi
1. **Gunakan code khusus Wokwi**:
   - Ganti `main.cpp` dengan `main_wokwi_csv.cpp`
   - Atau copy-paste code dari `main_wokwi_csv.cpp` ke `main.cpp`

2. **Jalankan simulasi di Wokwi**:
   - Buka Serial Monitor di Wokwi
   - Data sudah dalam format CSV siap copy-paste

3. **Buat file CSV manual**:
   ```
   - Copy semua output CSV dari Serial Monitor Wokwi
   - Paste ke Excel atau Google Sheets
   - Save sebagai CSV file
   ```

#### Opsi 2: Konverter Otomatis
1. **Copy output Wokwi** ke file `wokwi_output.txt`
2. **Jalankan converter**:
   ```bash
   python wokwi_csv_converter.py
   ```
3. **File CSV** akan otomatis terbuat: `dht22_wokwi_data.csv`

### 3. Monitoring Data

#### Hardware Real:
- **Serial Monitor**: Buka PlatformIO Serial Monitor untuk melihat data mentah
- **Python Console**: Lihat data yang diproses dan disimpan
- **CSV File**: File `dht22_data.csv` akan dibuat otomatis

#### Simulasi Wokwi:
- **Wokwi Serial Monitor**: Data ditampilkan dalam format CSV siap copy
- **Manual CSV**: Copy-paste ke Excel/Google Sheets
- **Auto Converter**: Gunakan `wokwi_csv_converter.py`

## 📊 Format Data Output

### Serial Output (ESP32):
```
timestamp_ms,temperature_C,humidity_%
5000,25.60,60.40
10000,25.80,59.20
```

### CSV Output:
| Timestamp | Arduino_Millis_ms | Temperature_C | Humidity_% | Heat_Index_C |
|-----------|-------------------|---------------|------------|--------------|
| 2025-10-20 10:15:30 | 5000 | 25.60 | 60.40 | 26.15 |
| 2025-10-20 10:15:35 | 10000 | 25.80 | 59.20 | 26.30 |

## 🛠️ Troubleshooting

### ESP32 Upload Issues:
- Tekan tombol **BOOT** saat uploading
- Cek **COM port** di Device Manager
- Pastikan **kabel USB** support data transfer

### Python Connection Issues:
- **Tutup Serial Monitor** Arduino/PlatformIO sebelum menjalankan Python
- **Cek COM port** yang benar
- **Install driver** CH340/CP2102 jika diperlukan

### Sensor Reading Issues:
- **Cek wiring** DHT22 ke ESP32
- **Tunggu 2 detik** setelah power on untuk stabilisasi sensor
- **Ganti sensor** jika tetap mendapat nilai NaN

### ⚠️ Wokwi Simulation Issues:

#### "CSV file tidak terbuat otomatis"
**Penyebab**: Wokwi hanya menjalankan kode Arduino/ESP32, tidak bisa menjalankan script Python secara bersamaan.

**Solusi**:
1. **Gunakan `main_wokwi_csv.cpp`** - Output langsung format CSV
2. **Manual copy-paste** dari Wokwi Serial Monitor ke Excel
3. **Gunakan converter tool** `wokwi_csv_converter.py`

#### "Data tidak muncul di Serial Monitor Wokwi"
**Solusi**:
- Pastikan baud rate `115200` di Serial Monitor Wokwi
- Tunggu 2-3 detik setelah start simulasi
- Cek wiring DHT22 di diagram Wokwi

#### "Data format tidak sesuai"
**Solusi**:
- Pastikan menggunakan `main_wokwi_csv.cpp` untuk simulasi
- Format output: `Timestamp,Millis,Temp,Humidity,HeatIndex`
- Skip baris yang dimulai dengan `//` (komentar)

#### Step-by-step untuk Wokwi:
1. ✅ Upload `main_wokwi_csv.cpp` ke Wokwi
2. ✅ Start simulasi 
3. ✅ Buka Serial Monitor (115200 baud)
4. ✅ Tunggu data muncul (5 detik interval)
5. ✅ Copy semua data CSV
6. ✅ Paste ke Excel/Google Sheets, atau
7. ✅ Save ke `wokwi_output.txt` → run `python wokwi_csv_converter.py`

## 📈 Fitur

✅ **Real-time monitoring** suhu dan kelembaban  
✅ **Automatic CSV logging** dengan timestamp  
✅ **Heat index calculation** (feels like temperature)  
✅ **Error handling** untuk pembacaan sensor yang gagal  
✅ **Data validation** untuk memastikan nilai sensor valid  
✅ **Reconnection handling** jika koneksi serial terputus  

## 🔧 Kustomisasi

### Mengubah Interval Pembacaan:
Edit di `main.cpp`:
```cpp
delay(5000);  // 5 detik (ubah sesuai kebutuhan)
```

### Mengubah Format Output:
Edit di `data.py` bagian `log_data_to_csv()`.

### Menambah Sensor Lain:
Tambahkan pembacaan sensor lain di `main.cpp` dan sesuaikan parsing di `data.py`.

## 📝 License

Proyek ini dibuat untuk pembelajaran Samsung Innovation Campus.

---
**Author**: Titanio Yudista  
**Date**: October 2025