#include <Arduino.h>
// --- Tentukan Pin ---

// Pin yang terhubung ke pin AO (Analog Out) sensor MQ-2
// HARUS pin ADC (Analog-to-Digital Converter) di ESP32
// Contoh: 32, 33, 34, 35, 36, 39. Kita pilih GPIO 34.
const int MQ2_AO_PIN = 34; 

// Pin LED tetap di GPIO 2 (D2)
const int LED_PIN = 2;

// --- Tambahan: Buzzer (pasif) LEDC ---
const int BUZZER_PIN = 19;        // pin buzzer pasif (ubah jika perlu)
const int TONE_CHANNEL = 2;       // channel LEDC untuk MQ2 (hindari konflik)
const int TONE_RESOLUTION = 8;    // resolusi bit (0-255)
const int ALARM_FREQUENCY = 1000; // frekuensi default (Hz)

// --- Tentukan Threshold (Batas) ---
// Nilai ini HARUS Anda sesuaikan sendiri.
// Cek Serial Monitor saat udara bersih, lalu beri asap
// dan tentukan nilai batas yang pas.
// Nilai analog ESP32 adalah 0 (0V) s/d 4095 (3.3V)
const int SMOKE_THRESHOLD = 300; // <== GANTI NILAI INI SETELAH TES!

void setup() {
  // Mulai komunikasi serial
  Serial.begin(115200);
  
  // Atur pin LED sebagai OUTPUT
  pinMode(LED_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);

  // Siapkan LEDC channel untuk buzzer
  ledcSetup(TONE_CHANNEL, ALARM_FREQUENCY, TONE_RESOLUTION);
  ledcAttachPin(BUZZER_PIN, TONE_CHANNEL);
  ledcWrite(TONE_CHANNEL, 0); // pastikan buzzer mati
  
  // Pin Analog (AO) tidak perlu pinMode sebagai INPUT
  
  Serial.println("--- Tes Sensor Asap MQ-2 (Analog) ---");
  Serial.println("Sensor sedang melakukan pemanasan...");
  
  // Sensor gas perlu "pemanasan" beberapa detik
  // saat pertama kali nyala agar stabil
  delay(20000); // Tunggu 20 detik
  Serial.println("Sensor Siap.");
  Serial.println();
}

void loop() {
  // Baca nilai analog dari sensor MQ-2
  int sensorValue = analogRead(MQ2_AO_PIN);

  // Cetak nilainya ke Serial Monitor (PENTING untuk kalibrasi)
  Serial.print("Nilai Sensor: ");
  Serial.println(sensorValue);

  // Periksa apakah nilai sensor melebihi batas (threshold)
  // Semakin banyak asap, nilai 'sensorValue' akan SEMAKIN TINGGI
  if (sensorValue > SMOKE_THRESHOLD) {
    Serial.println("ASAP TERDETEKSI!");
    digitalWrite(LED_PIN, HIGH); // Nyalakan LED

    // Mainkan alarm sederhana (dua nada bergantian) selama asap masih terdeteksi
    while (analogRead(MQ2_AO_PIN) > SMOKE_THRESHOLD) {
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

      // Cetak nilai sensor lagi selama alarm
      sensorValue = analogRead(MQ2_AO_PIN);
      Serial.print("Nilai Sensor: ");
      Serial.println(sensorValue);
      delay(100);
    }

    // Setelah asap tidak terdeteksi lagi, matikan LED dan buzzer
    ledcWrite(TONE_CHANNEL, 0);
    ledcWriteTone(TONE_CHANNEL, 0);
    digitalWrite(LED_PIN, LOW);
  } else {
    Serial.println("Udara Bersih.");
    digitalWrite(LED_PIN, LOW);  // Matikan LED
    ledcWrite(TONE_CHANNEL, 0);
    ledcWriteTone(TONE_CHANNEL, 0);
    delay(1000);
  }

  // Beri jeda 1 detik
  delay(1000);
}