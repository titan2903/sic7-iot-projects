
# Sensor Status Dashboard

Deskripsi singkat: proyek ini adalah sebuah dashboard status sensor untuk board mikrokontroler (mis. ESP32, ESP8266, atau Arduino) yang membaca beberapa sensor dan menampilkan statusnya — cocok untuk pemantauan kondisi lingkungan atau deteksi. README ini menjelaskan cara membangun, mengunggah, menjalankan, dan menguji proyek menggunakan PlatformIO serta cara menggunakan file `wokwi.toml` jika ingin menjalankan simulasi di Wokwi.

## Fitur

- Membaca data dari sensor (konfigurasi sensor disesuaikan di `src/`)
- Menampilkan status / nilai sensor (mis. melalui serial, display OLED, atau endpoint web — lihat implementasi di `src/main.cpp`)
- Mudah dijalankan lewat PlatformIO (VS Code) dan dapat disimulasikan di Wokwi jika file konfigurasi tersedia

## Prasyarat

- PlatformIO (VS Code extension atau PlatformIO Core CLI) — https://platformio.org/
- Toolchain sesuai target board (PlatformIO akan mengelolanya otomatis ketika Anda memilih environment yang tepat di `platformio.ini`)
- Kabel USB untuk menghubungkan board ke komputer
- (Opsional) Akun / akses ke Wokwi untuk simulasi online: https://wokwi.com/

Catatan: proyek ini tidak mengasumsikan sensor tertentu di README ini karena perangkat keras yang dipakai dapat berbeda. Periksa `src/main.cpp` dan file konfigurasi terkait (mis. `include/` atau `lib/`) untuk melihat sensor apa saja yang dipakai dan pin assignment-nya.

## Struktur proyek

Root proyek ini berisi file penting berikut:

- `platformio.ini` — konfigurasi PlatformIO (board, framework, environment)
- `src/` — kode sumber C++ (mis. `main.cpp`)
- `include/` — header/config tambahan
- `lib/` — pustaka lokal (jika ada)
- `wokwi.toml` — konfigurasi simulasi Wokwi (jika disediakan)
- `test/` — kerangka test/unit (jika ada)

Contoh jalur file yang penting:

- `src/main.cpp` — titik masuk aplikasi: lihat file ini untuk detail sensor, pin, dan konfigurasi runtime

## Cara membangun dan mengunggah (PlatformIO)

Jika Anda menggunakan VS Code dengan ekstensi PlatformIO, cukup pilih environment yang sesuai di bar kiri (Project Tasks) lalu klik "Build" atau "Upload".

Dengan PlatformIO Core (CLI), buka terminal di root proyek ini dan jalankan:

```bash
# Build proyek
pio run

# Upload ke board (otomatis menggunakan environment default di platformio.ini)
pio run -t upload

# Jika Anda punya beberapa environment, tentukan dengan -e <env_name>
pio run -e <env_name> -t upload
```

Jika upload gagal karena port serial, tentukan port secara eksplisit di `platformio.ini` atau gunakan flag `-p`:

```bash
pio run -t upload -p /dev/ttyUSB0
```

## Monitor Serial

Untuk melihat output serial dari board (mis. log sensor atau status), gunakan:

```bash
pio device monitor

# Atau jika perlu tentukan baudrate dan port
pio device monitor -p /dev/ttyUSB0 -b 115200
```

Catatan: Periksa `Serial.begin(...)` di `src/main.cpp` untuk baudrate yang dipakai.

## Simulasi dengan Wokwi

Jika proyek memiliki `wokwi.toml` atau file simulasi Wokwi, Anda dapat membuka proyek di https://wokwi.com/ dan mengimpor repo atau memuat file `wokwi.toml` untuk menjalankan simulasi. Wokwi berguna untuk pengujian awal tanpa perangkat keras fisik.

Langkah singkat:

1. Buka https://wokwi.com/
2. Pilih "Open project" atau "Import project" dan unggah file `wokwi.toml` atau isi project dari GitHub/ZIP
3. Jalankan simulator dan lihat serial monitor / display virtual

(Jika Anda memakai Wokwi CLI/feature lain, ikuti dokumentasi Wokwi untuk perintah spesifik.)

## Konfigurasi (Wi‑Fi, API keys, dsb.)

Beberapa proyek membutuhkan konfigurasi sensitif (mis. SSID Wi‑Fi, password, API keys). Jika ada file konfigurasi terpisah (mis. `src/config.h`, atau `include/config.h`), jangan commit data sensitif ke VCS — gunakan contoh file `config_example.h` atau variabel lingkungan.

Contoh pola yang sering dipakai:

- `config_example.h` — template konfigurasi yang dapat Anda salin menjadi `config.h` dan isi kredensial lokal

## Debugging & Troubleshooting

- Board tidak terdeteksi: periksa kabel USB, driver (khusus Windows), permission pada Linux (pastikan user Anda berada di grup `dialout` atau gunakan `sudo` jika perlu). Port biasa: `/dev/ttyUSB0`, `/dev/ttyACM0`.
- Upload gagal: periksa environment di `platformio.ini`, pastikan board dan framework sesuai.
- Serial kosong: periksa baudrate pada `Serial.begin()` dan pada `pio device monitor -b`.
- Sensor tidak terbaca: periksa wiring, cek alamat I2C (gunakan scanner I2C jika tersedia), cek library yang di-include di `lib/` atau `platformio.ini`.

## Testing

Jika ada folder `test/` berisi unit test PlatformIO, jalankan:

```bash
pio test
```

Ini akan menjalankan test sesuai framework test yang dikonfigurasi (mis. Unity untuk embedded).

## Kontribusi

Silakan buka issue atau pull request jika Anda ingin menambahkan fitur, memperbaiki bug, atau menyarankan perbaikan dokumentasi. Sertakan deskripsi singkat, langkah reproduksi, dan patch/test jika memungkinkan.

Guidelines singkat:

- Gunakan branch feature/bugfix untuk perubahan besar
- Pastikan kode build dan test lulus sebelum membuat PR

## Lisensi

Lisensi belum ditentukan di repositori ini. Jika Anda pemilik proyek, tambahkan file `LICENSE` atau sertakan lisensi yang sesuai. Jika Anda berkontribusi, tanyakan pemilik proyek soal lisensi sebelum mengirim perubahan besar.

## Catatan akhir

Periksa `src/main.cpp` dan file-file di `include/` untuk detail implementasi sensor, pinout, dan titik konfigurasi. README ini dirancang sebagai panduan penggunaan umum; tambahkan instruksi khusus hardware di bagian atas README jika proyek akan digunakan bersama papan/sensor tertentu.


