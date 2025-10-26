
# Wiring — Step by step (ESP32 DevKit v1)

Panduan ini menjelaskan langkah-langkah wiring di breadboard untuk project "Gas Leak and Fire Early Warning System" menggunakan ESP32 DevKit v1, sensor MQ-2 (asap), MQ-5 (gas LPG), flame sensor (api), 3 LED, dan buzzer pasif. Ikuti langkah secara berurutan dan pastikan semua ground bersama.

Komponen & rekomendasi nilai:
- LED ×3 (merah/ biru/ kuning) + resistor seri 220 Ω (per LED)
- Buzzer pasif (memerlukan PWM/tone). Rekomendasi: gunakan transistor NPN atau N-channel logic MOSFET untuk pengendalian.
- MQ-2 module (sensor asap)
- MQ-5 module (sensor gas LPG)
- Flame sensor module (digital output)
- Resistor untuk voltage divider (untuk membatasi output analog MQ ke 3.3V): R_top = 5.1 kΩ, R_bottom = 10 kΩ (per sensor)
- Kabel jumper, breadboard, multimeter

Catatan penting sebelum mulai:
- ESP32 ADC tidak 5V tolerant. Jika modul MQ Anda diberi daya 5V (banyak modul memakai 5V untuk heater), jangan langsung hubungkan analog OUT modul ke pin ADC ESP32. Gunakan voltage divider seperti dicontohkan di bawah, atau jalankan modul pada 3.3V jika modul tersebut mendukungnya.
- Gunakan ADC1 pins (GPIO32..39) untuk MQ-2/MQ-5 agar tidak terganggu bila WiFi/BT aktif. Contoh di sini menggunakan GPIO34 dan GPIO35.
- Pastikan semua GND (ESP32, sensor, buzzer, breadboard rails) terhubung ke ground yang sama.

Wiring langkah demi langkah (nomor langkah untuk diikuti di breadboard):

1) Siapkan power rails di breadboard
	- Sambungkan pin `5V` atau `VIN` dari ESP32 DevKit v1 ke rail + (power) di breadboard jika Anda akan memberi modul 5V.
	- Sambungkan pin `GND` dari ESP32 ke rail - (ground) di breadboard.
	- Jika Anda ingin menggunakan 3.3V untuk sensor/module, sambungkan pin `3V3` ESP32 ke rail terpisah (labelkan sebagai 3.3V).

2) Pasang MQ-2 (asap)
	- MQ-2 VCC -> 5V (rail +) *atau* 3.3V jika modul mendukung. Jika menggunakan 5V, gunakan voltage divider pada OUT.
	- MQ-2 GND -> GND (rail -).
	- MQ-2 OUT -> sambungkan ke node voltage divider:
			• MQ_OUT --- R_top (5.1 kΩ) ---+--- Node_ADC_MQ2 --- to GPIO34 (ESP32 ADC)
												|
											R_bottom (10 kΩ)
												|
											  GND
	  (Node_ADC_MQ2 adalah titik tengah antara R_top dan R_bottom; ukur tegangan di sini sebelum menyambung ke ESP32 untuk memastikan <= 3.3V)

3) Pasang MQ-5 (gas LPG)
	- MQ-5 VCC -> 5V (rail +) *atau* 3.3V jika modul mendukung.
	- MQ-5 GND -> GND (rail -).
	- MQ-5 OUT -> voltage divider (R_top 5.1k, R_bottom 10k) -> Node_ADC_MQ5 -> GPIO35 (ESP32 ADC)

4) Pasang flame sensor (api)
	- Flame module VCC -> 3.3V (lebih aman) atau 5V sesuai modul (baca datasheet).
	- Flame module GND -> GND.
	- Flame module DO (digital output) -> GPIO25 (input digital). Jika modul punya AO, jangan sambungkan AO langsung ke ESP32 tanpa memastikan tegangan.

5) Pasang LED (masing-masing dengan resistor 220 Ω)
	- LED Merah (GAS): GPIO5 -> resistor 220 Ω -> anoda LED (panjang). Katoda (pendek) -> GND.
	- LED Biru (ASAP): GPIO2 -> resistor 220 Ω -> anoda LED. Katoda -> GND.
	- LED Kuning (API): GPIO4 -> resistor 220 Ω -> anoda LED. Katoda -> GND.
	Catatan: arah LED penting — pastikan kaki pendek (katoda) ke GND.

6) Pasang buzzer pasif (via transistor/MOSFET) — rekomendasi wiring & catatan PWM

	Buzzer pasif tidak berbunyi ketika diberi tegangan tetap seperti active buzzer; ia membutuhkan sinyal PWM (tone) untuk menghasilkan nada. Karena itu kita akan mengendalikan buzzer pasif menggunakan pin GPIO yang menghasilkan PWM (di ESP32 gunakan LEDC). Untuk keamanan arus dan daya, gunakan transistor NPN kecil atau N-channel MOSFET logic-level.

	Rekomendasi wiring (NPN transistor — mis. 2N2222 / BC547):
	• Sambungkan pin positif buzzer (+) ke rail + (5V atau 3.3V sesuai spesifikasi buzzer).
	• Sambungkan pin negatif buzzer (-) ke kolektor transistor.
	• Sambungkan emitter transistor ke GND.
	• Hubungkan resistor basis 1 kΩ antara GPIO22 (ESP32, sinyal PWM/LEDC) dan basis transistor.
	• Sambungkan GND ESP32 dan GND power rail bersama.
	• (Opsional) Tambahkan diode flyback (mis. 1N400x) paralel buzzer bila datasheet menyarankan; arah diode: katoda ke +V buzzer, anoda ke kolektor.

	Jika menggunakan MOSFET N-channel logic-level kecil:
	• Sambungkan drain MOSFET ke pin negatif buzzer (-).
	• Sambungkan source ke GND.
	• Hubungkan gate melalui resistor 100–220 Ω ke GPIO22.
	• Tambahkan pull-down 100 kΩ dari gate ke GND jika diperlukan untuk memastikan MOSFET mati saat boot.

	Catatan penting PWM / LEDC:
	- Pada kode kita menggunakan `GPIO22` sebagai pin kontrol buzzer dan LEDC (ESP32 PWM). Pastikan `src/main.cpp` juga memakai `GPIO22`.
	- Jangan hanya menyalakan pin HIGH jika ingin membuat tone — itu akan menghubungkan buzzer ke tegangan tetap dan biasanya tidak menghasilkan nada yang konsisten. Gunakan PWM/frequency (contoh: 800 Hz, 1000 Hz, 1200 Hz, 1500 Hz) untuk menghasilkan tone.
	- Duty cycle ~50% (mis. 128 pada 8-bit) menghasilkan nada dengan volume sedang.

	Jika buzzer Anda sangat berarus-rendah (datasheet menyatakan arus <20 mA) dan Anda mau eksperimen cepat, Anda *bisa* mencoba menggerakkannya langsung dari GPIO untuk uji singkat, tetapi itu TIDAK direkomendasikan untuk penggunaan jangka panjang.

7) Pastikan semua ground terhubung
	- Sambungkan GND dari ESP32, GND dari MQ modules, GND dari flame sensor, dan GND emitter transistor (atau source MOSFET) semuanya ke rail GND yang sama.

8) Pemeriksaan sebelum power-up
	- Periksa sambungan rangkaian secara visual.
	- Dengan multimeter, ukur tegangan pada Node_ADC_MQ2 dan Node_ADC_MQ5 (output divider) sambil me-referensikan ke GND; pastikan nilainya tidak lebih dari 3.3V (paling aman ~≤3.2V).
	- Jika tegangan melebihi 3.3V, hentikan dan periksa wiring divider atau jalankan modul pada 3.3V jika modul mendukung.

9) Power-up & pemanasan sensor MQ
	- Nyalakan ESP32 (via USB). MQ sensors membutuhkan waktu pemanasan (biasanya 24–48 jam untuk stabil secara penuh; untuk pengujian singkat beberapa menit–jam kadang cukup). Catat bahwa pembacaan awal mungkin tinggi/berfluktuasi.

10) Tes awal dengan sketch minimal
	- Unggah sketch yang hanya membaca ADC dari GPIO34/GPIO35 dan membaca digital GPIO25, lalu tampilkan nilai di Serial Monitor. Periksa bahwa nilai ADC bergerak dalam rentang 0..4095 dan tidak saturasi di atas nilai yang diperkirakan.

Tambahan & tips
- Jika Anda ingin menghubungkan MQ module tanpa voltage divider, periksa dokumentasi modul apakah modul itu memiliki regulator/level shifter untuk AO; beberapa modul bisa dioperasikan pada 3.3V.
- Untuk keandalan, tambahkan kapasitor 0.1 µF pada catu daya dekat modul sensor untuk meredam gangguan.
- Catat nilai baseline dengan lingkungan bersih (tanpa asap/gas) selama beberapa menit, ambil rata-rata, lalu tetapkan threshold = baseline + margin (mis. +20–40%).

Jika Anda mau, saya bisa membuat diagram breadboard sederhana (tekstual) atau membuat file gambar/schematic. Mau saya tambahkan diagram atau langsung buatkan file `.ino`/`.cpp` untuk menguji wiring ini?

