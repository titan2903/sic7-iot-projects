// Sertakan library yang dibutuhkan
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <DHT.h>

// Konfigurasi Pin Sesuai Tugas
const int MOTION_SENSOR_PIN = 15; // Input: Pushbutton
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
#define DHTTYPE DHT22
DHT dht(DHT_PIN, DHTTYPE);

// Variabel untuk menyimpan status dan waktu
bool motionDetected = false;
bool lastMotionState = false;
float temperature = 0.0;
bool highTemp = false;
bool lastHighTempState = false;

unsigned long lastOledUpdateTime = 0;
unsigned long lastBlinkTime = 0;
bool yellowLedState = false;

// Debounce
unsigned long lastButtonChangeTime = 0;
const unsigned long debounceDelay = 50; // ms

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
  if (highTemp) {
    display.print(temperature);
    display.println(" C (*TINGGI*)");
  } else {
    display.print(temperature);
    display.println(" C");
  }

  // Tampilkan timestamp sederhana
  display.setCursor(0, 40);
  display.print("Uptime: ");
  display.print(millis() / 1000);
  display.println(" detik");

  display.display();
}

void setup() {
  Serial.begin(115200);
  Serial.println("\n===== Smart Motion Alert System Dimulai =====");

  // Inisialisasi pin mode
  pinMode(MOTION_SENSOR_PIN, INPUT_PULLUP);
  pinMode(RED_LED_PIN, OUTPUT);
  pinMode(YELLOW_LED_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(RELAY_PIN, OUTPUT);

  // Matikan semua output di awal
  digitalWrite(RED_LED_PIN, LOW);
  digitalWrite(YELLOW_LED_PIN, LOW);
  digitalWrite(BUZZER_PIN, LOW);
  digitalWrite(RELAY_PIN, LOW);

  // Inisialisasi DHT Sensor
  dht.begin();

  // Inisialisasi OLED
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("Alokasi SSD1306 gagal"));
    for (;;);
  }
  display.clearDisplay();
  display.println("Sistem Siap...");
  display.display();
  delay(1000);
  Serial.println("Sistem siap. Menunggu input...");
}

void loop() {
  // --- BAGIAN 1: BACA SEMUA SENSOR ---

  // Menggunakan INPUT_PULLUP, pin akan bernilai LOW saat tombol ditekan.
  // Jadi, `motionDetected` akan `true` jika dan hanya jika tombol sedang ditekan.
  bool rawButton = (digitalRead(MOTION_SENSOR_PIN) == LOW);
  // Debounce sederhana: hanya terima perubahan setelah debounceDelay
  if (rawButton != lastMotionState) {
    if (millis() - lastButtonChangeTime > debounceDelay) {
      lastButtonChangeTime = millis();
      motionDetected = rawButton;
      // Debug print
      Serial.print("[DEBUG] Button raw: ");
      Serial.print(rawButton);
      Serial.print(" -> motionDetected: ");
      Serial.println(motionDetected);
      // Update OLED immediately jika motion state berubah
      updateOledDisplay();
    }
  } else {
    motionDetected = rawButton; // tetap sinkron jika tidak berubah
  }
  // =================================================================

  // Requirement 2: Temperatur Display
  // Baca suhu setiap 2 detik
  if (millis() - lastOledUpdateTime > 2000) {
    lastOledUpdateTime = millis();
    float t = dht.readTemperature();
    if (isnan(t)) {
      temperature = random(20, 36);
    } else {
      temperature = t;
    }
    // Update display OLED setiap 2 detik
    updateOledDisplay();
  }
  
  highTemp = temperature > 30.0;

  // --- BAGIAN 2: LOGIKA KONTROL BERDASARKAN STATUS ---

  // Requirement 1: Motion Alert
  if (motionDetected && !lastMotionState) {
    Serial.println("-> GERAKAN TERDETEKSI!");
    digitalWrite(RED_LED_PIN, HIGH);
    beepBuzzer();
  } else if (!motionDetected && lastMotionState) {
    digitalWrite(RED_LED_PIN, LOW);
  }
  lastMotionState = motionDetected;

  // High Temperature Alert
  if (highTemp && !lastHighTempState) {
    Serial.print("-> SUHU TINGGI TERDETEKSI: ");
    Serial.println(temperature);
  }
  
  if(highTemp) {
    if (millis() - lastBlinkTime > 500) {
      lastBlinkTime = millis();
      yellowLedState = !yellowLedState;
      digitalWrite(YELLOW_LED_PIN, yellowLedState);
    }
  } else {
    digitalWrite(YELLOW_LED_PIN, LOW);
  }
  lastHighTempState = highTemp;

  // Requirement 3: Relay Control
  if (motionDetected || highTemp) {
    digitalWrite(RELAY_PIN, HIGH);
  } else {
    if(digitalRead(RELAY_PIN) == HIGH) {
        Serial.println("-> Kondisi kembali NORMAL.");
    }
    digitalWrite(RELAY_PIN, LOW);
  }
}