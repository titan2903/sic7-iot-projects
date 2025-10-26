// Import library yang dibutuhkan
#include "DHT.h"

// Definisi pin untuk setiap sensor
#define DHTPIN 4      // Pin DATA sensor DHT22
#define PIR_PIN 5     // Pin OUT sensor PIR
#define LDR_PIN 34     // Pin input analog untuk LDR (ADC1_CH6)

// Tipe sensor DHT yang digunakan
#define DHTTYPE DHT22

// Inisialisasi objek sensor DHT
DHT dht(DHTPIN, DHTTYPE);

// Variabel untuk timer non-blocking
unsigned long previousMillis = 0;
const long interval = 2000; // Interval pembacaan sensor setiap 2 detik

void setup() {
  // Mulai komunikasi serial pada baud rate 115200
  Serial.begin(115200);

  // Inisialisasi sensor DHT
  dht.begin();

  // Atur mode pin untuk sensor PIR sebagai INPUT
  pinMode(PIR_PIN, INPUT);

  Serial.println("Sensor Status Dashboard Siap!");
  Serial.println("--------------------------------");
}

void loop() {
  // Menggunakan millis() untuk pembacaan non-blocking agar tidak ada konflik timing
  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    // Simpan waktu terakhir pembacaan
    previousMillis = currentMillis;

    // Baca data dari semua sensor
    float humidity = dht.readHumidity();
    float temp = dht.readTemperature(); // Baca suhu dalam Celsius
    int lightValue = analogRead(LDR_PIN); // Baca nilai analog LDR (0-4095 pada ESP32)
    int motionState = digitalRead(PIR_PIN); // Baca status PIR (0 atau 1)

    // Cek jika pembacaan DHT gagal
    if (isnan(humidity) || isnan(temp)) {
      Serial.println("Gagal membaca data dari sensor DHT!");
      return;
    }

    // Format Timestamp [mm:ss]
    unsigned long totalSeconds = millis() / 1000;
    int minutes = totalSeconds / 60;
    int seconds = totalSeconds % 60;
    char timestamp[10];
    sprintf(timestamp, "[%02d:%02d]", minutes, seconds); // Format dengan leading zero

    // Tampilkan output sesuai format yang diminta
    Serial.print(timestamp);
    Serial.print(" Light: ");
    Serial.print(lightValue);
    Serial.print(" | Motion: ");
    Serial.print(motionState);
    Serial.print(" | Temp: ");
    Serial.print(temp);
    Serial.print("°C | Humidity: ");
    Serial.print(humidity);
    Serial.println("%");

    // Implementasi Logika Kondisional untuk Alert
    if (lightValue < 400) {
      Serial.println("  -> ALERT: Kondisi cahaya rendah!");
    }
    if (motionState == HIGH) {
      Serial.println("  -> ALERT: Gerakan terdeteksi!");
    }
    if (temp > 30.0) {
      Serial.println("  -> ALERT: Suhu terdeteksi tinggi!");
    }
  }
}