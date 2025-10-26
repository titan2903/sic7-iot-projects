#include <Arduino.h>
/*
 * Tes Sensor Api (Digital) dengan Indikator LED dan Buzzer Pasif (Nada)
 * untuk ESP32
 *
 * Menggunakan LEDC untuk menghasilkan nada (frekuensi) tertentu
 * pada buzzer pasif.
 */

// --- Tentukan Pin ---
const int FLAME_PIN = 5;  // DO Sensor -> GPIO 5 (D5)
const int LED_PIN = 2;    // LED -> GPIO 2 (D2)
const int BUZZER_PIN = 4; // Buzzer PASIF -> GPIO 4 (D4)

// --- Pengaturan Nada (LEDC) ---
const int TONE_CHANNEL = 0;      // Channel LEDC (0-15)
const int TONE_RESOLUTION = 8;   // Resolusi bit (8 bit = 0-255)
const int ALARM_FREQUENCY = 1000; // Frekuensi nada (dalam Hz)

void setup() {
  Serial.begin(115200);
  
  // Atur pin sensor sebagai INPUT
  pinMode(FLAME_PIN, INPUT);
  
  // Atur pin LED sebagai OUTPUT
  pinMode(LED_PIN, OUTPUT);
  
  // --- Siapkan channel LEDC untuk buzzer ---
  // 1. Setup channel: ledcSetup(channel, frekuensi, resolusi)
  ledcSetup(TONE_CHANNEL, ALARM_FREQUENCY, TONE_RESOLUTION);
  
  // 2. Hubungkan channel ke pin: ledcAttachPin(pin, channel)
  ledcAttachPin(BUZZER_PIN, TONE_CHANNEL);

  // 3. Pastikan buzzer mati saat awal
  ledcWrite(TONE_CHANNEL, 0); // Duty cycle 0 = mati

  Serial.println("--- Tes Sensor Api (Digital) dengan LED & Buzzer Pasif ---");
  Serial.println("Mencari api...");
  Serial.println();
}

void loop() {
  int sensorState = digitalRead(FLAME_PIN);
  if (sensorState == LOW) {
    // Api terdeteksi — mainkan alarm kebakaran (dua nada bergantian)
    Serial.println("Api Terdeteksi!!!");

    // Loop alarm selama sensor masih mendeteksi api
    while (digitalRead(FLAME_PIN) == LOW) {
      // Nyalakan LED indikator
      digitalWrite(LED_PIN, HIGH);

      // Nada tinggi selama 300 ms
      ledcWriteTone(TONE_CHANNEL, 2000); // frekuensi tinggi
      ledcWrite(TONE_CHANNEL, 200);      // duty (0-255)
      delay(300);

      // Nada rendah selama 300 ms
      ledcWriteTone(TONE_CHANNEL, 1000); // frekuensi rendah
      ledcWrite(TONE_CHANNEL, 200);
      delay(300);

      // Singkat jeda antar siklus untuk karakter alarm
      ledcWrite(TONE_CHANNEL, 0);
      ledcWriteTone(TONE_CHANNEL, 0);
      delay(100);
    }

    // Setelah alarm selesai (sensor tidak lagi mendeteksi api), pastikan mati
    ledcWrite(TONE_CHANNEL, 0);
    ledcWriteTone(TONE_CHANNEL, 0);
    digitalWrite(LED_PIN, LOW);

  } else {
    // Aman
    Serial.println("Aman... tidak ada api.");
    digitalWrite(LED_PIN, LOW);  // Matikan LED
    // Pastikan nada mati
    ledcWrite(TONE_CHANNEL, 0);  // duty 0 = mati
    ledcWriteTone(TONE_CHANNEL, 0); // hentikan tone (reset frekuensi)
    delay(500); // Beri jeda saat kondisi aman
  }

  // Jeda singkat sebelum iterasi berikutnya
  delay(200);
}