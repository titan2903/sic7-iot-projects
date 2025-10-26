
# Gas Leak & Fire Early Warning — Command Prompt

Bagian ini berisi "command prompt" (teks instruksi) dalam Bahasa Indonesia yang bisa Anda salin-tempel ke AI (mis. ChatGPT / GitHub Copilot) untuk menghasilkan kode Arduino (.ino) atau C++ (.cpp) yang berjalan pada board Arduino (PlatformIO compatible). Juga disertakan contoh pemetaan pin, nilai threshold awal untuk MQ-2 dan MQ-5, serta perintah terminal opsional untuk membuat file sumber.

Hardware yang dipakai:
- Breadboard full size
- 3 x resistor (sesuaikan nilai untuk LED, mis. 220Ω)
- 3 x LED
	- Merah: deteksi GAS (MQ-5)
	- Biru: deteksi ASAP (MQ-2)
	- Kuning: deteksi API (flame sensor)
- Buzzer pasif
- MQ-2 (sensor asap)
- MQ-5 (sensor gas LPG)
- Flame sensor (sensor api)

Contoh pemetaan pin (ubah sesuai wiring Anda). Contoh di bawah khusus untuk ESP32 DevKit v1:
- GPIO34 : MQ-2 (analog, ADC1 channel, input only)
- GPIO35 : MQ-5 (analog, ADC1 channel, input only)
- GPIO25 : Flame sensor (digital input, HIGH bila terdeteksi api)
- GPIO5  : LED Merah (GAS)   (sesuai permintaan: D5 -> GPIO5)
- GPIO2  : LED Biru (ASAP)   (sesuai permintaan: D2 -> GPIO2)
- GPIO4  : LED Kuning (API)  (sesuai permintaan: D4 -> GPIO4)
- GPIO22 : Buzzer pasif (output)

Catatan penting ADC ESP32:
- ADC default range pada banyak core ESP32 adalah 0..4095 (12-bit). Pembacaan dipengaruhi oleh attenuation (mis. ADC_0db, ADC_11db). Gunakan `analogSetPinAttenuation(pin, ADC_11db)` atau setelan yang sesuai dan lakukan kalibrasi. Hindari ADC2 pins jika Anda memakai WiFi secara bersamaan — pakai ADC1 pins (GPIO32..39) untuk sensor analog.

Nilai threshold awal (contoh untuk ESP32 — HARUS dikalibrasi pada perangkat Anda):
- MQ-2 threshold: ~1200  (perkiraan untuk ADC 0..4095)
- MQ-5 threshold: ~1000  (perkiraan untuk ADC 0..4095)

Catatan kalibrasi: nilai di atas diskalakan dari contoh 0..1023 ke 0..4095 (skala ~4x). Lakukan pembacaan baseline di lingkungan normal lalu pilih threshold sebagai baseline + margin toleransi. Periksa juga pengaturan attenuation karena akan mengubah rentang pembacaan.

---

Prompt AI (Salin & Tempel ke ChatGPT / Copilot)

Berikut prompt yang lengkap untuk meminta AI membuat kode .ino atau .cpp. Prompt ini menjelaskan semua kebutuhan fungsional dan hardware sehingga AI menghasilkan kode siap pakai (PlatformIO/Arduino IDE).

"Buatkan kode Arduino (file .ino atau file C++ yang bisa dipakai di PlatformIO) untuk project 'Gas Leak and Fire Early Warning System'. Spesifikasi:


- Board: ESP32 DevKit v1 (jika memungkinkan, buat code kompatibel PlatformIO dan Arduino IDE). Catatan: pada ESP32 gunakan ADC1 pins (GPIO32..39) untuk pembacaan analog agar tidak terganggu saat WiFi aktif. Sertakan instruksi singkat tentang `analogSetPinAttenuation(pin, ADC_11db)` dan kalibrasi.
- Hardware dan pemetaan pin (gunakan jika tidak ada konfigurasi lain):
	- GPIO34 -> MQ-2 (analog, deteksi asap)
	- GPIO35 -> MQ-5 (analog, deteksi gas LPG)
	- GPIO25 -> Flame sensor (digital, HIGH bila terdeteksi api)
	- GPIO5  -> LED merah (nyala ketika MQ-5 melewati threshold gas)   (D5)
	- GPIO2  -> LED biru (nyala ketika MQ-2 melewati threshold asap)     (D2)
	- GPIO4  -> LED kuning (nyala ketika flame sensor terdeteksi api)    (D4)
	- GPIO22 -> Buzzer pasif (nyala ketika salah satu kondisi bahaya terjadi)

- Behavior / fitur yang diminta:
	1. Baca nilai analog MQ-2 dan MQ-5 secara berkala (mis. setiap 500 ms).
	2. Bandingkan pembacaan dengan threshold yang dapat dikonfigurasi di bagian atas sketch (variable `MQ2_THRESHOLD` dan `MQ5_THRESHOLD`). Gunakan nilai default yang diskalakan untuk ESP32: `MQ2_THRESHOLD=1200`, `MQ5_THRESHOLD=1000` dan catat di komentar bahwa ini perlu kalibrasi.
	3. Baca flame sensor (digital). Saat terdeteksi api (digital HIGH), nyalakan LED kuning dan buzzer.
	4. Jika MQ-5 melewati threshold: nyalakan LED merah dan bunyikan buzzer dalam pola (mis. 200ms ON / 200ms OFF) sampai kondisi aman.
	5. Jika MQ-2 melewati threshold: nyalakan LED biru dan bunyikan buzzer berbeda (mis. 100ms ON / 100ms OFF) sampai kondisi aman.
	6. Bila lebih dari satu sensor mendeteksi bahaya, prioritaskan menyalakan semua LED yang relevan dan bunyikan buzzer dalam pola panjang (mis. 100ms ON / 50ms OFF x3) diikuti delay pendek.
	7. Tambahkan fungsi `isStableReading(pin)` atau filter sederhana (moving average 5 sample) untuk mengurangi noise pada sensor MQ.
	8. Tampilkan pembacaan sensor dan status (OK / GAS / SMOKE / FIRE) di Serial Monitor setiap 1 detik. Sertakan juga nilai mentah ADC (0..4095) dan nilai rata-rata jika menggunakan moving average.
	9. Tambahkan konstanta konfigurasi di bagian atas sketch (pin mapping, thresholds, read intervals) agar mudah disesuaikan.
 1.  Sertakan komentar singkat pada tiap fungsi dan instruksi singkat cara kalibrasi threshold (ambil beberapa bacaan ambient lalu pilih threshold sebagai rata-rata + X persen).

- Kriteria kualitas kode:
	- Jangan gunakan library mahal — pakai Arduino built-in API (digitalRead, analogRead, pinMode, millis).
	- Strukturkan kode: fungsi `setup()`, `loop()`, helper untuk membaca sensor, helper untuk mengendalikan LED/buzzer, dan helper untuk serial logging.
	- Gunakan non-blocking timing (`millis()`) bila memungkinkan untuk pembacaan sensor dan pola buzzer, kecuali pola alarm pendek yang sederhana.
	- Kompatibel dengan PlatformIO: beri komentar di awal yang menyebutkan board target (ESP32 DevKit v1) dan nama file.

Berikan hasil dalam satu file `.ino` lengkap yang dapat di-copy-paste ke PlatformIO/Arduino IDE. Jika ada asumsi (mis. pin default, nilai threshold), sebutkan di komentar dan beri instruksi singkat kalibrasi." 

---

Perintah terminal opsional (zsh) — membuat file sumber baru dan membuka editor:

```zsh
# buat file .ino di folder src (PlatformIO project)
mkdir -p src
touch src/gas_fire_detector.ino

# (opsional) buka file di editor (misal code = VS Code), atau gunakan editor lain
code src/gas_fire_detector.ino
```

 Catatan terakhir:
 Nilai threshold adalah contoh dan sudah disesuaikan sebagai estimasi untuk ESP32. Selalu lakukan kalibrasi di lingkungan nyata.
 Jika Anda ingin target board lain selain ESP32 (mis. AVR/Arduino Uno atau ESP8266) atau ingin menambahkan pemetaan pembacaan ke satuan ppm, sebutkan board/format yang diinginkan dan saya akan tambahkan konfigurasi ADC / mapping yang tepat.

 --
 Dokumentasi singkat ini dibuat agar Anda tinggal menyalin prompt AI di atas dan meminta generator kode untuk membuat file `.ino` atau `.cpp` yang siap dipakai.


