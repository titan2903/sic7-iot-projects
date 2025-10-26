# Smart Motion Alert System with Button Simulation

Proyek ini adalah sistem deteksi gerakan sederhana menggunakan sebuah tombol (pushbutton) sebagai simulasi sensor gerak, sensor suhu DHT22, OLED SSD1306 untuk tampilan, LED, buzzer, dan relay. Kode ditulis untuk ESP32 (PlatformIO) dan menampilkan status gerak serta suhu pada OLED, menyalakan LED/buzzer/relay sesuai kondisi.

## Fitur
- Deteksi "gerakan" via pushbutton (INPUT_PULLUP) dan notifikasi LED merah + buzzer 3x.
- Pembacaan suhu dari DHT22, lampu LED kuning berkedip saat suhu di atas ambang (30 °C).
- Kendali relay saat kondisi gerak atau suhu tinggi.
- Tampilan status dan uptime di OLED SSD1306 (I2C).
- Debounce sederhana dan cetak debug via Serial untuk membantu troubleshooting.

## Pinout (sesuai `diagram.json`)
- Pushbutton (simulasi motion): GPIO 15, gunakan INPUT_PULLUP, tombol menutup ke GND.
- LED merah: GPIO 25
- LED kuning: GPIO 26
- Buzzer: GPIO 14
- Relay IN: GPIO 13 (relay VCC ke 5V, GND ke GND)
- DHT22 data: GPIO 4
- OLED SSD1306 (I2C): SDA -> GPIO 21, SCL -> GPIO 22, alamat I2C: 0x3C

> Catatan: Pastikan koneksi listrik (VCC/GND) konsisten. Diagram proyek ada di `diagram.json`.

## Cara build & upload (PlatformIO)
Di VSCode dengan PlatformIO extension: klik 'Build' lalu 'Upload'.

Atau via CLI (zsh):

```bash
# build
pio run

# upload ke board (gunakan environment default di platformio.ini)
pio run -t upload

# buka serial monitor (baud 115200)
pio device monitor -b 115200
```

## Debugging: Tombol tidak mengubah teks ke "Motion Detected!"
Jika Anda menekan tombol tapi OLED tidak menampilkan "Motion Detected!", periksa hal-hal berikut:

1. Serial Monitor
- Buka serial monitor 115200. Program sekarang memberikan baris debug saat tombol berubah. Contoh output saat ditekan:
  - `[DEBUG] Button raw: 0 -> motionDetected: 1`
  Jika Anda melihat baris ini, berarti ESP32 'menerima' input tombol.

2. Wiring tombol (INPUT_PULLUP)
- Karena kode menggunakan `pinMode(pin, INPUT_PULLUP)`, pastikan tombol menghubungkan GPIO15 langsung ke GND saat ditekan.
- Jika tombol wired ke VCC (atau ada resistor eksternal), perilaku akan terbalik.
- Periksa orientasi tombol pada breadboard (tombol biasanya menghubungkan dua pasangan pin yang berlawanan).

3. OLED/I2C
- Pastikan OLED terdeteksi. Saat inisialisasi gagal, serial akan mencetak pesan kegagalan inisialisasi SSD1306.
- Jika OLED tidak menampilkan apa-apa tetapi serial menunjukkan deteksi tombol, periksa alamat I2C (0x3C). Beberapa modul memakai 0x3D.

4. Periksa pull-up/pull-down eksternal
- Jangan gunakan resistor pull-down eksternal jika Anda memakai INPUT_PULLUP internal.

5. Simulasi (Wokwi)
- Jika menggunakan Wokwi, pastikan pushbutton terhubung ke pin yang sama seperti di `diagram.json` (GPIO15) dan pin lain ke GND.

## Tips tambahan
- Untuk menguji tanpa hardware, Anda bisa menambahkan cetak berkala dari nilai `digitalRead(MOTION_SENSOR_PIN)` di `loop()` untuk melihat level pin.
- Jika OLED lambat, refresh interval default adalah 2 detik — tetapi fungsi sekarang memperbarui segera saat perubahan gerak terdeteksi.

## Struktur proyek
- `src/main.cpp` — kode utama
- `platformio.ini` — konfigurasi PlatformIO
- `diagram.json` — skematik koneksi (Wokwi)

## Lisensi
Lisensi: bebas untuk penggunaan pribadi dan edukasi (sesuaikan sesuai kebutuhan).

---
Jika mau, saya bisa menambahkan gambar wiring sederhana atau menambahkan pemeriksaan alamat I2C otomatis di startup (mencoba 0x3C lalu 0x3D) dan menampilkan hasil di Serial. Mau saya tambahkan itu?
