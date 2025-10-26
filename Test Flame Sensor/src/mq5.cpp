/*
 * Simple MQ-5 Gas Sensor Test dengan Deteksi
 * untuk ESP32
 *
 * Membaca nilai analog mentah dari sensor MQ-5
 * dan mencetak peringatan jika nilainya melewati ambang batas (threshold).
 */

#include <Arduino.h>

// Tentukan pin ADC yang terhubung ke pin A0 sensor MQ-5
// NOTE: Jika Anda memakai board/skrip lain (mis. main.cpp) yang juga
// memakai pin ini untuk buzzer/LED, pastikan tidak ada konflik wiring.
const int MQ5_PIN = 4; // Gunakan GPIO 4 (ADC1_CH6)

// --- Tambahan: LED dan Buzzer (pasif) ---
// Jika Anda ingin menggunakan pin berbeda, ubah BUZZER_PIN di sini
const int LED_PIN = 2;    // indikator LED
const int BUZZER_PIN = 19; // pin buzzer pasif (pilih pin yang tidak overlap dengan MQ5_PIN)

// LEDC (ESP32) settings untuk buzzer
const int TONE_CHANNEL = 1;      // Channel LEDC (0-15)
const int TONE_RESOLUTION = 8;   // Resolusi bit (8 bit = 0-255)
const int ALARM_FREQUENCY = 1000; // Frekuensi default (Hz)

// --- ATUR INI ---
// Tentukan ambang batas (threshold) deteksi gas.
// Anda HARUS MENCARI NILAI INI SENDIRI.
// 1. Jalankan kode tes sederhana sebelumnya.
// 2. Lihat nilai stabil "udara bersih" Anda (misal: 1100).
// 3. Atur threshold ini sedikit di atas nilai itu (misal: 1400).
const int TRESHOLD_GAS = 1500; // CONTOH! GANTI NILAI INI!

void setup() {
  // Mulai komunikasi serial pada 115200 baud
  Serial.begin(115200);
  
  // --- Siapkan LED dan buzzer ---
  pinMode(LED_PIN, OUTPUT);

  // Setup LEDC channel untuk buzzer
  ledcSetup(TONE_CHANNEL, ALARM_FREQUENCY, TONE_RESOLUTION);
  ledcAttachPin(BUZZER_PIN, TONE_CHANNEL);
  ledcWrite(TONE_CHANNEL, 0); // pastikan mati

  Serial.println("--- Tes Sensor MQ-5 dengan Deteksi ---");
  Serial.println("Sensor sedang melakukan pemanasan...");
  Serial.println("Mohon tunggu sekitar 20-30 detik untuk nilai stabil...");
  Serial.println();
  Serial.print("Ambang batas (threshold) diatur ke: ");
  Serial.println(TRESHOLD_GAS);
  Serial.println();
}

void loop() {
  // Baca nilai analog dari sensor
  // ESP32 memiliki 12-bit ADC, jadi nilainya antara 0 - 4095
  int sensorValue = analogRead(MQ5_PIN);

  // Cetak nilainya ke Serial Monitor
  Serial.print("Nilai Analog Mentah: ");
  Serial.print(sensorValue);

  // Periksa apakah nilai sensor melebihi ambang batas
  if (sensorValue > TRESHOLD_GAS) {
    // Jika YA, cetak peringatan dan aktifkan LED + buzzer
    Serial.println("  <-- Gas Terdeteksi!!!");

    // Nyalakan LED
    digitalWrite(LED_PIN, HIGH);

    // Mainkan alarm sederhana (dua nada bergantian) selama gas masih terdeteksi
    while (analogRead(MQ5_PIN) > TRESHOLD_GAS) {
      // Nada tinggi 2000 Hz selama 300 ms
      ledcWriteTone(TONE_CHANNEL, 2000);
      ledcWrite(TONE_CHANNEL, 200); // duty kuat
      delay(300);

      // Nada rendah 1000 Hz selama 300 ms
      ledcWriteTone(TONE_CHANNEL, 1000);
      ledcWrite(TONE_CHANNEL, 200);
      delay(300);

      // jeda singkat antar siklus
      ledcWrite(TONE_CHANNEL, 0);
      ledcWriteTone(TONE_CHANNEL, 0);
      delay(100);
    }

    // Setelah gas tidak terdeteksi lagi, matikan LED dan buzzer
    ledcWrite(TONE_CHANNEL, 0);
    ledcWriteTone(TONE_CHANNEL, 0);
    digitalWrite(LED_PIN, LOW);

  } else {
    // Jika TIDAK, cetak status normal dan pastikan LED/buzzer mati
    Serial.println("  (Udara normal)");
    digitalWrite(LED_PIN, LOW);
    ledcWrite(TONE_CHANNEL, 0);
    ledcWriteTone(TONE_CHANNEL, 0);
    delay(1000);
  }
}