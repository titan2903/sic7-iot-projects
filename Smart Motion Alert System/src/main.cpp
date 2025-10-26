// Sertakan library yang dibutuhkan
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <DHT.h>

// Konfigurasi Pin Sesuai Tugas
const int MOTION_SENSOR_PIN = 15; // Input: PIR Sensor
const int RED_LED_PIN = 25;       // Output: LED Merah untuk notifikasi gerak
const int BUZZER_PIN = 14;        // Output: Buzzer
const int RELAY_PIN = 13;         // Output: Relay
const int DHT_PIN = 4;            // Input: Sensor Suhu DHT22
const int YELLOW_LED_PIN = 26;    // Output: LED Kuning untuk notifikasi suhu tinggi

// Konfigurasi OLED Display
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// Konfigurasi Sensor Suhu DHT
#define DHTTYPE DHT22 // Bisa ganti ke DHT11 jika menggunakan sensor tersebut
DHT dht(DHT_PIN, DHTTYPE);

// Variabel untuk menyimpan status dan waktu
bool motionDetected = false;
bool lastMotionState = false;
float temperature = 0.0;
bool highTemp = false;

unsigned long lastOledUpdateTime = 0;
unsigned long lastBlinkTime = 0;
bool yellowLedState = false;

// Fungsi untuk membunyikan buzzer 3x
void beepBuzzer() {
  for (int i = 0; i < 3; i++) {
    digitalWrite(BUZZER_PIN, HIGH);
    delay(100);
    digitalWrite(BUZZER_PIN, LOW);
    delay(100);
  }
}

// Fungsi untuk mengupdate tampilan di OLED
void updateOledDisplay() {
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);

  // Tampilkan Status Gerak
  display.setCursor(0, 0);
  display.print("Status: ");
  display.println(motionDetected ? "Motion Detected!" : "No Motion");

  // Tampilkan Suhu
  display.setCursor(0, 16);
  display.print("Suhu  : ");
  // Beri tanda jika suhu tinggi
  if (highTemp) {
    display.print(temperature);
    display.println(" C (*TINGGI*)");
  } else {
    display.print(temperature);
    display.println(" C");
  }

  // Tampilkan timestamp sederhana (waktu sejak ESP32 menyala)
  display.setCursor(0, 40);
  display.print("Uptime: ");
  display.print(millis() / 1000);
  display.println(" detik");

  display.display();
}

void setup() {
  Serial.begin(115200);
  delay(1000); // Tunggu serial monitor siap
  Serial.println("\n===== Smart Motion Alert System Dimulai =====");
  Serial.println("Inisialisasi sistem...");

  // Inisialisasi pin mode
  pinMode(MOTION_SENSOR_PIN, INPUT);
  pinMode(RED_LED_PIN, OUTPUT);
  pinMode(YELLOW_LED_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(RELAY_PIN, OUTPUT);

  Serial.println("Pin configuration selesai");

  // Matikan semua output di awal
  digitalWrite(RED_LED_PIN, LOW);
  digitalWrite(YELLOW_LED_PIN, LOW);
  digitalWrite(BUZZER_PIN, LOW);
  digitalWrite(RELAY_PIN, LOW);

  Serial.println("Output pins direset ke LOW");

  // Inisialisasi DHT Sensor
  dht.begin();
  Serial.println("DHT22 sensor diinisialisasi");

  // Inisialisasi OLED
  Serial.println("Inisialisasi OLED...");
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("Alokasi SSD1306 gagal"));
    for (;;);
  }
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println("Smart Motion Alert");
  display.setCursor(0, 16);
  display.println("System Ready...");
  display.display();
  
  Serial.println("===== Sistem Siap Beroperasi =====");
  delay(2000);
}

void loop() {
  // --- BAGIAN 1: BACA SEMUA SENSOR ---

  // Baca status sensor gerak
  motionDetected = digitalRead(MOTION_SENSOR_PIN) == HIGH;

  // Requirement 2: Temperatur Display
  // Baca suhu setiap 2 detik
  if (millis() - lastOledUpdateTime > 2000) {
    lastOledUpdateTime = millis();
    // Baca suhu dari DHT, atau gunakan nilai random jika sensor error (untuk simulasi)
    float t = dht.readTemperature();
    if (isnan(t)) {
      temperature = random(20, 36); // Nilai random 20-35 jika DHT tidak terbaca
      Serial.println("DHT sensor error, menggunakan nilai simulasi: " + String(temperature) + "°C");
    } else {
      temperature = t;
      Serial.println("Suhu saat ini: " + String(temperature) + "°C");
    }
    // Update display OLED karena data suhu baru
    updateOledDisplay();
  }
  
  // Cek kondisi suhu tinggi
  highTemp = temperature > 30.0;

  // --- BAGIAN 2: LOGIKA KONTROL BERDASARKAN STATUS ---

  // Requirement 1: Motion Alert
  if (motionDetected && !lastMotionState) { // Hanya trigger saat ada perubahan dari tidak ada ke ada gerak
    Serial.println("MOTION DETECTED! Mengaktifkan alarm...");
    digitalWrite(RED_LED_PIN, HIGH);
    beepBuzzer();
  } else if (!motionDetected && lastMotionState) {
    Serial.println("Motion cleared. Mematikan alarm...");
    digitalWrite(RED_LED_PIN, LOW);
  }
  lastMotionState = motionDetected; // Simpan status terakhir

  // High Temperature Alert
  if (highTemp) {
    // Buat LED kuning berkedip
    if (millis() - lastBlinkTime > 500) {
      lastBlinkTime = millis();
      yellowLedState = !yellowLedState;
      digitalWrite(YELLOW_LED_PIN, yellowLedState);
      if (yellowLedState) {
        Serial.println("HIGH TEMPERATURE WARNING! LED Kuning menyala");
      }
    }
  } else {
    digitalWrite(YELLOW_LED_PIN, LOW); // Matikan jika suhu normal
  }

  // Requirement 3: Relay Control
  // Relay menyala jika ada gerakan ATAU suhu tinggi
  if (motionDetected || highTemp) {
    digitalWrite(RELAY_PIN, HIGH);
  } else {
    digitalWrite(RELAY_PIN, LOW);
  }
}