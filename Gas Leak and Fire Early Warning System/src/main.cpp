/*
 * Gas Leak and Fire Early Warning System
 * Board: ESP32 DevKit v1
 * File: main.cpp (PlatformIO compatible)
 * 
 * Hardware:
 * - MQ-2 (smoke) -> GPIO34 (ADC1, analog) - connect to AO (Analog Output)
 * - MQ-5 (LPG gas) -> GPIO35 (ADC1, analog) - connect to AO (Analog Output)
 * - Flame sensor -> GPIO33 (ADC1, analog) - connect to AO (Analog Output)
 * - LED Red (GAS) -> GPIO5
 * - LED Blue (SMOKE) -> GPIO2
 * - LED Yellow (FIRE) -> GPIO4
 * - Buzzer -> GPIO22 (PASSIVE buzzer, requires PWM/LEDC for tone generation)
 * 
 * Features:
 * 
 * - Moving average filtering (5 samples) for all sensors (MQ-2, MQ-5, Flame)
 * - Flame sensor debouncing (3 consecutive readings) to prevent false alarms
 * - Non-blocking timing for sensor reading and buzzer patterns
 * - Different buzzer tones for different hazards (PWM/LEDC frequencies)
 *   • Gas: 800 Hz (low pitch)
 *   • Smoke: 1000 Hz (medium pitch)
 *   • Fire: 1200 Hz (high pitch)
 *   • Multi-hazard: 1500 Hz (highest pitch)
 * - Serial logging every 1 second with raw ADC and status
 * - Configurable thresholds (calibration required)
 */

#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <Preferences.h>
#include <ESP32Time.h>
#include <ArduinoOTA.h>

// ============================================================================
// CONFIGURATION - Adjust these values according to your setup and calibration
// ============================================================================

// Pin definitions
const int MQ2_AO_PIN = 34;     // Smoke sensor (ADC1 channel) - connect to AO (Analog Output)
const int MQ5_AO_PIN = 35;     // LPG gas sensor (ADC1 channel) - connect to AO (Analog Output)
const int FLAME_DO_PIN = 25;   // Flame sensor (digital) - connect to DO (Digital Output)
const int LED_RED_PIN = 5;     // Gas detection LED
const int LED_BLUE_PIN = 2;    // Smoke detection LED  
const int LED_YELLOW_PIN = 4;  // Fire detection LED
const int BUZZER_PIN = 22;     // Buzzer output

// Thresholds (CALIBRATION REQUIRED!)
// These are scaled estimates for ESP32 ADC (0..4095)
// To calibrate: Take readings in clean environment for several minutes,
// calculate average, then set threshold = average + 20-40% margi
const int MQ2_THRESHOLD = 350;  // Smoke threshold (increased for safety and false alarms)
const int MQ5_THRESHOLD = 600;  // Gas threshold (increased for safety and false alarms)

// ADC saturation threshold: values >= this are considered saturated/invalid
// Increase this value (up to 4095) to be less aggressive about flagging
// saturation. Decrease it to flag saturation earlier (more conservative).
const int ADC_SATURATION = 4095;
 
// Timing intervals
const unsigned long SENSOR_READ_INTERVAL = 500;  // Read sensors every 500ms
const unsigned long SERIAL_LOG_INTERVAL = 1000;  // Log to serial every 1s
const unsigned long BUZZER_GAS_ON = 400;         // Gas buzzer pattern: 400ms ON
const unsigned long BUZZER_GAS_OFF = 400;        // Gas buzzer pattern: 400ms OFF
const unsigned long BUZZER_SMOKE_ON = 350;       // Smoke buzzer pattern: 350ms ON
const unsigned long BUZZER_SMOKE_OFF = 350;      // Smoke buzzer pattern: 350ms OFF
const unsigned long BUZZER_FIRE_ON = 300;        // Fire buzzer pattern: 300ms ON
const unsigned long BUZZER_FIRE_OFF = 300;       // Fire buzzer pattern: 300ms OFF
const unsigned long BUZZER_MULTI_ON = 200;       // Multi-hazard pattern: 200ms ON
const unsigned long BUZZER_MULTI_OFF = 100;      // Multi-hazard pattern: 100ms OFF

// Passive buzzer LEDC configuration
const int LEDC_CHANNEL = 0;          // LEDC channel (0-15)
const int LEDC_RESOLUTION = 8;       // 8-bit resolution (0-255)
const int BUZZER_GAS_FREQ = 800;     // Gas detection frequency (Hz)
const int BUZZER_SMOKE_FREQ = 1000;  // Smoke detection frequency (Hz)
const int BUZZER_FIRE_FREQ = 1200;   // Fire detection frequency (Hz)
const int BUZZER_MULTI_FREQ = 1500;  // Multi-hazard frequency (Hz)

// Moving average filter settings
const int FILTER_SIZE = 5;

// ============================================================================
// WIFI & MQTT CONFIGURATION
// ============================================================================

// WiFi Configuration
const char* WIFI_SSID = "kosasi kost lt 2";
const char* WIFI_PASSWORD = "kosasikost2";
const unsigned long WIFI_RECONNECT_INTERVAL = 30000; // 30 seconds
const unsigned long WIFI_TIMEOUT = 20000; // 20 seconds connection timeout

// MQTT Configuration
const char* MQTT_SERVER = "103.127.97.247";
const int MQTT_PORT = 1883;
const char* MQTT_USERNAME = "cakrawala_mqtt";
const char* MQTT_PASSWORD = "Jarvis5413$";
const char* MQTT_CLIENT_ID = "esp32_warning_sensor_001";

// MQTT Topics
const char* TOPIC_SENSOR_DATA = "home/sensors/data";
const char* TOPIC_SENSOR_STATUS = "home/sensors/status";
const char* TOPIC_SENSOR_ALERTS = "home/sensors/alerts";
const char* TOPIC_CMD_BUZZER = "home/commands/buzzer";
const char* TOPIC_CMD_CALIBRATE = "home/commands/calibrate";
const char* TOPIC_CONFIG_THRESHOLDS = "home/config/thresholds";
const char* TOPIC_CONFIG_INTERVALS = "home/config/intervals";

// NTP Configuration
const char* NTP_SERVER = "pool.ntp.org";
const long GMT_OFFSET_SEC = 7 * 3600; // UTC+7 (WIB)
const int DAYLIGHT_OFFSET_SEC = 0;

// Timing intervals for MQTT and WiFi
const unsigned long MQTT_PUBLISH_INTERVAL = 5000;   // Publish data every 5 seconds
const unsigned long MQTT_STATUS_INTERVAL = 30000;   // Publish status every 30 seconds
const unsigned long WIFI_CHECK_INTERVAL = 10000;    // Check WiFi every 10 seconds

// ============================================================================
// GLOBAL VARIABLES
// ============================================================================

// Moving average buffers
int mq2_readings[FILTER_SIZE];
int mq5_readings[FILTER_SIZE];
int mq2_index = 0;
int mq5_index = 0;
long mq2_total = 0;
long mq5_total = 0;
bool filters_initialized = false;

// Sensor values
int mq2_raw = 0;
int mq5_raw = 0;
int mq2_filtered = 0;
int mq5_filtered = 0;

// Digital flame sensor value
bool flame_digital = false; // Digital value from flame sensor DO pin (HIGH=no flame, LOW=flame detected)

// (No software debouncing for flame sensor — recommend external pull-down/hardware)

// Detection states
bool gas_detected = false;
bool smoke_detected = false;
bool fire_detected = false;

// Timing variables
unsigned long last_sensor_read = 0;
unsigned long last_serial_log = 0;
unsigned long buzzer_last_change = 0;
bool buzzer_state = false;
int buzzer_pulse_count = 0;

// ============================================================================
// WIFI & MQTT GLOBAL VARIABLES
// ============================================================================

WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);
Preferences preferences;
ESP32Time rtc;

// Network status variables
bool wifi_connected = false;
bool mqtt_connected = false;
unsigned long last_wifi_check = 0;
unsigned long last_mqtt_publish = 0;
unsigned long last_mqtt_status = 0;
unsigned long wifi_reconnect_attempts = 0;
int wifi_rssi = 0;

// Remote control variables
bool remote_buzzer_override = false;
bool remote_buzzer_state = false;
bool calibration_requested = false;

// Configurable thresholds (can be updated via MQTT)
int configurable_mq2_threshold = MQ2_THRESHOLD;
int configurable_mq5_threshold = MQ5_THRESHOLD;

// ============================================================================
// FUNCTION DECLARATIONS
// ============================================================================

void initializeFilters();
int updateMovingAverage(int new_reading, int readings[], int &index, long &total);
void readSensors();
void updateDetectionStates();
void controlLEDs();
void controlBuzzer();
void serialLog();
String getSystemStatus();

// WiFi & MQTT Functions
void initWiFi();
void checkWiFiConnection();
void initMQTT();
void mqttCallback(char* topic, byte* payload, unsigned int length);
void reconnectMQTT();
void publishSensorData();
void publishStatus();
void publishAlert(String alertType, String severity);
void handleMQTTCommands();
void initNTP();
void initOTA();
unsigned long getEpochTime();

// ============================================================================
// SETUP FUNCTION
// ============================================================================

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("=== Gas Leak and Fire Early Warning System ===");
  Serial.println("Board: ESP32 DevKit v1");
  Serial.println("Buzzer Type: PASSIVE (PWM/LEDC for tone generation)");
  Serial.println("Initializing...");
  
  // Configure ADC attenuation for better range (0-3.3V)
  analogSetPinAttenuation(MQ2_AO_PIN, ADC_11db);
  analogSetPinAttenuation(MQ5_AO_PIN, ADC_11db);
  
  // Configure digital flame sensor input
  pinMode(FLAME_DO_PIN, INPUT);
  
  // Setup digital pins
  pinMode(LED_RED_PIN, OUTPUT);
  pinMode(LED_BLUE_PIN, OUTPUT);
  pinMode(LED_YELLOW_PIN, OUTPUT);
  
  // Initialize LED outputs to OFF
  digitalWrite(LED_RED_PIN, LOW);
  digitalWrite(LED_BLUE_PIN, LOW);
  digitalWrite(LED_YELLOW_PIN, LOW);
  
  // --- Setup LEDC for passive buzzer ---
  // Passive buzzer requires PWM to generate tone
  ledcSetup(LEDC_CHANNEL, BUZZER_FIRE_FREQ, LEDC_RESOLUTION);
  ledcAttachPin(BUZZER_PIN, LEDC_CHANNEL);
  ledcWrite(LEDC_CHANNEL, 0); // Start with buzzer off
  
  // Initialize moving average filters
  initializeFilters();
  
  // Initialize preferences for credential and settings storage
  preferences.begin("settings", false);
  
  // Load persisted thresholds (fallback to compile-time defaults)
  configurable_mq2_threshold = preferences.getInt("mq2_threshold", MQ2_THRESHOLD);
  configurable_mq5_threshold = preferences.getInt("mq5_threshold", MQ5_THRESHOLD);
  preferences.end();
  
  Serial.print("Loaded MQ2 threshold: ");
  Serial.println(configurable_mq2_threshold);
  Serial.print("Loaded MQ5 threshold: ");
  Serial.println(configurable_mq5_threshold);
  
  // Initialize WiFi
  initWiFi();
  
  // Initialize MQTT
  initMQTT();
  
  // Initialize NTP
  initNTP();
  
  // Initialize OTA
  initOTA();
  
  Serial.println("System ready!");
  Serial.println("IMPORTANT: MQ sensors need 24-48 hours for full stability.");
  Serial.println("For testing, allow several minutes of warm-up time.");
  Serial.println("Calibrate thresholds based on clean environment readings.");
  Serial.println("WiFi and MQTT integration enabled.");
  Serial.println();
  
  // Test passive buzzer with different frequencies at startup
  Serial.println("Testing passive buzzer (different frequencies)...");
  for (int freq = 800; freq <= 1500; freq += 200) {
    ledcSetup(LEDC_CHANNEL, freq, LEDC_RESOLUTION);
    ledcWrite(LEDC_CHANNEL, 128); // 50% duty cycle
    delay(300);
  }
  ledcWrite(LEDC_CHANNEL, 0);   // Off
  Serial.println("Buzzer test complete. Different tones should have been heard.");
  Serial.println();
  
  // Extended continuous buzzer test: 10 seconds at a single tone (Testing Buzzer)
  // Use a mid-range frequency (1000 Hz) which is audible for most passive buzzers
  // Serial.println("Extended buzzer test: continuous tone for 10 seconds...");
  // ledcSetup(LEDC_CHANNEL, BUZZER_SMOKE_FREQ, LEDC_RESOLUTION);
  // ledcWrite(LEDC_CHANNEL, 128); // 50% duty
  // delay(10000); // 10 seconds continuous tone for testing
  // ledcWrite(LEDC_CHANNEL, 0); // Turn off

  // Test Nyala LED
  digitalWrite(LED_RED_PIN, HIGH);
  digitalWrite(LED_BLUE_PIN, HIGH);
  digitalWrite(LED_YELLOW_PIN, HIGH);
  delay(3000); // 3 seconds

  Serial.println("Extended buzzer test complete.");
  Serial.println("Format: Time | MQ2_Raw/Avg | MQ5_Raw/Avg | Flame_DO | Status");
  Serial.println("------------------------------------------------------------------");
  
  delay(2000); // Allow sensors to settle
}

// ============================================================================
// MAIN LOOP
// ============================================================================

void loop() {
  unsigned long current_time = millis();
  
  // Handle OTA updates
  ArduinoOTA.handle();
  
  // Check WiFi connection
  checkWiFiConnection();
  
  // Handle MQTT
  if (wifi_connected) {
    if (!mqttClient.connected()) {
      reconnectMQTT();
    }
    mqttClient.loop();
  }
  
  // Read sensors at specified interval
  if (current_time - last_sensor_read >= SENSOR_READ_INTERVAL) {
    readSensors();
    updateDetectionStates();
    last_sensor_read = current_time;
  }
  
  // Control LEDs and buzzer
  controlLEDs();
  controlBuzzer();
  
  // Publish sensor data via MQTT
  if (wifi_connected && mqtt_connected && current_time - last_mqtt_publish >= MQTT_PUBLISH_INTERVAL) {
    publishSensorData();
    last_mqtt_publish = current_time;
  }
  
  // Publish status via MQTT
  if (wifi_connected && mqtt_connected && current_time - last_mqtt_status >= MQTT_STATUS_INTERVAL) {
    publishStatus();
    last_mqtt_status = current_time;
  }
  
  // Serial logging at specified interval
  if (current_time - last_serial_log >= SERIAL_LOG_INTERVAL) {
    serialLog();
    last_serial_log = current_time;
  }
}

// ============================================================================
// SENSOR FUNCTIONS
// ============================================================================

void initializeFilters() {
  // Initialize moving average buffers with current readings
  int initial_mq2 = analogRead(MQ2_AO_PIN);
  int initial_mq5 = analogRead(MQ5_AO_PIN);
  
  for (int i = 0; i < FILTER_SIZE; i++) {
    mq2_readings[i] = initial_mq2;
    mq5_readings[i] = initial_mq5;
  }
  
  mq2_total = initial_mq2 * FILTER_SIZE;
  mq5_total = initial_mq5 * FILTER_SIZE;
  mq2_index = 0;
  mq5_index = 0;
  filters_initialized = true;
  
  Serial.print("Filters initialized - MQ2: ");
  Serial.print(initial_mq2);
  Serial.print(", MQ5: ");
  Serial.println(initial_mq5);
}

int updateMovingAverage(int new_reading, int readings[], int &index, long &total) {
  // Remove oldest reading from total
  total = total - readings[index];
  
  // Add new reading
  readings[index] = new_reading;
  total = total + new_reading;
  
  // Advance index with wraparound
  index = (index + 1) % FILTER_SIZE;
  
  // Return filtered average
  return total / FILTER_SIZE;
}

void readSensors() {
  // Read raw analog values
  mq2_raw = analogRead(MQ2_AO_PIN);
  mq5_raw = analogRead(MQ5_AO_PIN);
  
  // Read digital flame sensor
  flame_digital = digitalRead(FLAME_DO_PIN);
  
  // DIAGNOSTIC: Check for voltage overload/disconnection
  if (mq5_raw >= ADC_SATURATION) {
    Serial.println("WARNING: MQ5 reading near max! Check wiring/voltage divider!");
  }
  if (mq2_raw >= ADC_SATURATION) {
    Serial.println("WARNING: MQ2 reading near max! Check wiring/voltage divider!");
  }
  
  // Apply moving average filter
  if (filters_initialized) {
    mq2_filtered = updateMovingAverage(mq2_raw, mq2_readings, mq2_index, mq2_total);
    mq5_filtered = updateMovingAverage(mq5_raw, mq5_readings, mq5_index, mq5_total);
  } else {
    mq2_filtered = mq2_raw;
    mq5_filtered = mq5_raw;
  }
}

void updateDetectionStates() {
  // Store previous states for alert detection
  bool prev_smoke = smoke_detected;
  bool prev_gas = gas_detected;
  bool prev_fire = fire_detected;
  
  // SAFETY: Ignore readings if sensor is saturated (likely wiring issue)
  smoke_detected = (mq2_filtered > configurable_mq2_threshold) && (mq2_raw < ADC_SATURATION);
  gas_detected = (mq5_filtered > configurable_mq5_threshold) && (mq5_raw < ADC_SATURATION);

  // Flame detection: Use digital DO pin (LOW = flame detected, HIGH = no flame)
  fire_detected = !flame_digital; // Inverted: LOW on DO means flame detected
  
  // Publish alerts for new detections
  if (wifi_connected && mqtt_connected) {
    if (smoke_detected && !prev_smoke) {
      publishAlert("smoke", fire_detected || gas_detected ? "critical" : "alert");
    }
    if (gas_detected && !prev_gas) {
      publishAlert("gas", fire_detected || smoke_detected ? "critical" : "alert");
    }
    if (fire_detected && !prev_fire) {
      publishAlert("fire", smoke_detected || gas_detected ? "critical" : "danger");
    }
    
    // Multi-hazard alert
    int hazard_count = (smoke_detected ? 1 : 0) + (gas_detected ? 1 : 0) + (fire_detected ? 1 : 0);
    if (hazard_count >= 2 && (prev_smoke + prev_gas + prev_fire) < 2) {
      publishAlert("multi", "critical");
    }
  }
}

// ============================================================================
// OUTPUT CONTROL FUNCTIONS
// ============================================================================

void controlLEDs() {
  // Control LEDs based on detection states
  digitalWrite(LED_BLUE_PIN, smoke_detected ? HIGH : LOW);
  digitalWrite(LED_RED_PIN, gas_detected ? HIGH : LOW);
  digitalWrite(LED_YELLOW_PIN, fire_detected ? HIGH : LOW);
}

void controlBuzzer() {
  unsigned long current_time = millis();
  
  // Handle remote buzzer override
  if (remote_buzzer_override) {
    if (remote_buzzer_state) {
      ledcSetup(LEDC_CHANNEL, BUZZER_SMOKE_FREQ, LEDC_RESOLUTION);
      ledcWrite(LEDC_CHANNEL, 128); // 50% duty cycle
    } else {
      ledcWrite(LEDC_CHANNEL, 0); // Off
    }
    return;
  }
  
  bool any_hazard = smoke_detected || gas_detected || fire_detected;
  bool multi_hazard = (smoke_detected + gas_detected + fire_detected) > 1;
  
  // Turn off buzzer if no hazards detected
  if (!any_hazard) {
    ledcWrite(LEDC_CHANNEL, 0); // Turn off PWM
    buzzer_state = false;
    buzzer_pulse_count = 0;
    return;
  }
  
  // Determine frequency and pattern based on hazard type
  int frequency = BUZZER_FIRE_FREQ; // Default
  unsigned long on_time = BUZZER_FIRE_ON; // Default initialization
  unsigned long off_time = BUZZER_FIRE_OFF; // Default initialization
  
  if (multi_hazard) {
    // Multi-hazard: Highest pitch (1500 Hz) with fast pattern
    frequency = BUZZER_MULTI_FREQ;
    on_time = BUZZER_MULTI_ON;
    off_time = BUZZER_MULTI_OFF;
  } else if (gas_detected) {
    // Gas: Low pitch (800 Hz) with slow pattern
    frequency = BUZZER_GAS_FREQ;
    on_time = BUZZER_GAS_ON;
    off_time = BUZZER_GAS_OFF;
  } else if (smoke_detected) {
    // Smoke: Medium pitch (1000 Hz) with medium pattern
    frequency = BUZZER_SMOKE_FREQ;
    on_time = BUZZER_SMOKE_ON;
    off_time = BUZZER_SMOKE_OFF;
  } else if (fire_detected) {
    // Fire: High pitch (1200 Hz) with fast pattern
    frequency = BUZZER_FIRE_FREQ;
    on_time = BUZZER_FIRE_ON;
    off_time = BUZZER_FIRE_OFF;
  }
  
  // Non-blocking on/off pattern with frequency change
  if (current_time - buzzer_last_change >= (buzzer_state ? on_time : off_time)) {
    buzzer_state = !buzzer_state;
    buzzer_last_change = current_time;
    
    if (buzzer_state) {
      // Set frequency and turn on tone
      ledcSetup(LEDC_CHANNEL, frequency, LEDC_RESOLUTION);
      ledcWrite(LEDC_CHANNEL, 128); // 50% duty cycle for tone
    } else {
      ledcWrite(LEDC_CHANNEL, 0); // Off
    }
  }
}

// ============================================================================
// LOGGING FUNCTIONS
// ============================================================================

void serialLog() {
  // Format: Time | MQ2_Raw | MQ2_Avg | MQ5_Raw | MQ5_Avg | Flame | Status
  Serial.print(millis() / 1000);
  Serial.print("s | ");
  
  Serial.print("MQ2=");
  Serial.print(mq2_raw);
  Serial.print("/");
  Serial.print(mq2_filtered);
  Serial.print(" | ");
  
  Serial.print("MQ5=");
  Serial.print(mq5_raw);
  Serial.print("/");
  Serial.print(mq5_filtered);
  Serial.print(" | ");

  Serial.print("Flame=");
  Serial.print(fire_detected ? 1 : 0);
  Serial.print(" ");
  Serial.print("(DO=");
  Serial.print(flame_digital ? "HIGH" : "LOW");
  Serial.print(") | ");
  
  // Debug - tampilkan status deteksi
  Serial.print("Gas=");
  Serial.print(gas_detected ? "YES" : "NO");
  Serial.print(",Smoke=");
  Serial.print(smoke_detected ? "YES" : "NO");
  Serial.print(",Fire=");
  Serial.print(fire_detected ? "YES" : "NO");
  Serial.print(" | ");
  
  Serial.println(getSystemStatus());
}

String getSystemStatus() {
  if (smoke_detected && gas_detected && fire_detected) {
    return "CRITICAL: GAS+SMOKE+FIRE";
  } else if (smoke_detected && gas_detected) {
    return "DANGER: GAS+SMOKE";
  } else if (smoke_detected && fire_detected) {
    return "DANGER: SMOKE+FIRE";
  } else if (gas_detected && fire_detected) {
    return "DANGER: GAS+FIRE";
  } else if (gas_detected) {
    return "ALERT: GAS DETECTED";
  } else if (smoke_detected) {
    return "ALERT: SMOKE DETECTED";
  } else if (fire_detected) {
    return "ALERT: FIRE DETECTED";
  } else {
    return "OK";
  }
}

// ============================================================================
// WIFI & MQTT FUNCTIONS
// ============================================================================

void initWiFi() {
  Serial.println("Initializing WiFi...");
  
  // Initialize preferences for credential storage
  preferences.begin("wifi_creds", false);
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  Serial.print("Connecting to WiFi");
  unsigned long start_time = millis();
  
  while (WiFi.status() != WL_CONNECTED && millis() - start_time < WIFI_TIMEOUT) {
    delay(500);
    Serial.print(".");
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    wifi_connected = true;
    wifi_rssi = WiFi.RSSI();
    Serial.println();
    Serial.println("WiFi connected!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
    Serial.print("Signal strength (RSSI): ");
    Serial.print(wifi_rssi);
    Serial.println(" dBm");
  } else {
    wifi_connected = false;
    Serial.println();
    Serial.println("WiFi connection failed!");
  }
}

void checkWiFiConnection() {
  unsigned long current_time = millis();
  
  if (current_time - last_wifi_check >= WIFI_CHECK_INTERVAL) {
    last_wifi_check = current_time;
    
    if (WiFi.status() != WL_CONNECTED) {
      if (wifi_connected) {
        Serial.println("WiFi disconnected! Attempting to reconnect...");
        wifi_connected = false;
        mqtt_connected = false;
      }
      
      WiFi.reconnect();
      wifi_reconnect_attempts++;
    } else {
      if (!wifi_connected) {
        Serial.println("WiFi reconnected!");
        wifi_connected = true;
        wifi_rssi = WiFi.RSSI();
      }
      wifi_rssi = WiFi.RSSI();
    }
  }
}

void initMQTT() {
  mqttClient.setServer(MQTT_SERVER, MQTT_PORT);
  mqttClient.setCallback(mqttCallback);
  
  if (wifi_connected) {
    reconnectMQTT();
  }
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  
  Serial.print("MQTT message received [");
  Serial.print(topic);
  Serial.print("]: ");
  Serial.println(message);
  
  // Handle buzzer commands
  if (String(topic) == TOPIC_CMD_BUZZER) {
    if (message == "ON") {
      remote_buzzer_override = true;
      remote_buzzer_state = true;
      Serial.println("Remote buzzer: ON");
    } else if (message == "OFF") {
      remote_buzzer_override = true;
      remote_buzzer_state = false;
      Serial.println("Remote buzzer: OFF");
    } else if (message == "AUTO") {
      remote_buzzer_override = false;
      Serial.println("Remote buzzer: AUTO");
    }
  }
  
  // Handle calibration commands
  else if (String(topic) == TOPIC_CMD_CALIBRATE) {
    if (message == "START") {
      calibration_requested = true;
      Serial.println("Calibration requested via MQTT");
    }
  }
  
  // Handle threshold configuration
  else if (String(topic) == TOPIC_CONFIG_THRESHOLDS) {
    StaticJsonDocument<200> doc;
    DeserializationError error = deserializeJson(doc, message);
    
    if (!error) {
      bool changed = false;
      if (doc.containsKey("mq2_threshold")) {
        configurable_mq2_threshold = doc["mq2_threshold"];
        Serial.print("MQ2 threshold updated: ");
        Serial.println(configurable_mq2_threshold);
        changed = true;
      }
      if (doc.containsKey("mq5_threshold")) {
        configurable_mq5_threshold = doc["mq5_threshold"];
        Serial.print("MQ5 threshold updated: ");
        Serial.println(configurable_mq5_threshold);
        changed = true;
      }
      
      // Persist to NVS so thresholds survive reboot
      if (changed) {
        preferences.begin("settings", false);
        preferences.putInt("mq2_threshold", configurable_mq2_threshold);
        preferences.putInt("mq5_threshold", configurable_mq5_threshold);
        preferences.end();
        
        Serial.println("Thresholds saved to NVS");
        
        // Optional: send acknowledgment back to dashboard
        StaticJsonDocument<200> ack;
        ack["mq2_threshold"] = configurable_mq2_threshold;
        ack["mq5_threshold"] = configurable_mq5_threshold;
        ack["status"] = "saved";
        String ackPayload;
        serializeJson(ack, ackPayload);
        mqttClient.publish("home/config/thresholds/ack", ackPayload.c_str(), true);
      }
    }
  }
}

void reconnectMQTT() {
  if (!wifi_connected) return;
  
  if (!mqttClient.connected()) {
    Serial.print("Attempting MQTT connection...");
    
    if (mqttClient.connect(MQTT_CLIENT_ID, MQTT_USERNAME, MQTT_PASSWORD)) {
      Serial.println(" connected!");
      mqtt_connected = true;
      
      // Subscribe to command topics
      mqttClient.subscribe(TOPIC_CMD_BUZZER, 1);
      mqttClient.subscribe(TOPIC_CMD_CALIBRATE, 1);
      mqttClient.subscribe(TOPIC_CONFIG_THRESHOLDS, 1);
      mqttClient.subscribe(TOPIC_CONFIG_INTERVALS, 1);
      
      Serial.println("Subscribed to command topics");
      
      // Publish online status
      publishStatus();
      
    } else {
      mqtt_connected = false;
      Serial.print(" failed, rc=");
      Serial.print(mqttClient.state());
      Serial.println(" retrying in 5 seconds");
    }
  }
}

void publishSensorData() {
  if (!mqtt_connected) return;
  
  StaticJsonDocument<300> doc;
  doc["mq2_raw"] = mq2_raw;
  doc["mq2_filtered"] = mq2_filtered;
  doc["mq5_raw"] = mq5_raw;
  doc["mq5_filtered"] = mq5_filtered;
  doc["flame"] = fire_detected ? 1 : 0;
  doc["gas_detected"] = gas_detected ? 1 : 0;
  doc["smoke_detected"] = smoke_detected ? 1 : 0;
  doc["fire_detected"] = fire_detected ? 1 : 0;
  doc["timestamp"] = getEpochTime();
  
  String payload;
  serializeJson(doc, payload);
  
  mqttClient.publish(TOPIC_SENSOR_DATA, payload.c_str(), true);
}

void publishStatus() {
  if (!mqtt_connected) return;
  
  StaticJsonDocument<200> doc;
  doc["device_id"] = MQTT_CLIENT_ID;
  doc["online"] = true;
  doc["uptime"] = millis() / 1000;
  doc["free_heap"] = ESP.getFreeHeap();
  doc["wifi_rssi"] = wifi_rssi;
  doc["wifi_reconnects"] = wifi_reconnect_attempts;
  
  String payload;
  serializeJson(doc, payload);
  
  mqttClient.publish(TOPIC_SENSOR_STATUS, payload.c_str(), true);
}

void publishAlert(String alertType, String severity) {
  if (!mqtt_connected) return;
  
  StaticJsonDocument<200> doc;
  doc["alert_type"] = alertType;
  doc["severity"] = severity;
  doc["timestamp"] = getEpochTime();
  doc["device_id"] = MQTT_CLIENT_ID;
  
  String payload;
  serializeJson(doc, payload);
  
  mqttClient.publish(TOPIC_SENSOR_ALERTS, payload.c_str(), true);
}

void initNTP() {
  if (!wifi_connected) return;
  
  Serial.println("Initializing NTP...");
  configTime(GMT_OFFSET_SEC, DAYLIGHT_OFFSET_SEC, NTP_SERVER);
  
  struct tm timeinfo;
  if (getLocalTime(&timeinfo)) {
    Serial.println("NTP time synchronized");
    rtc.setTimeStruct(timeinfo);
  } else {
    Serial.println("Failed to obtain time from NTP");
  }
}

void initOTA() {
  if (!wifi_connected) return;
  
  ArduinoOTA.setHostname("ESP32-Gas-Monitor");
  ArduinoOTA.setPassword("gas_monitor_ota");
  
  ArduinoOTA.onStart([]() {
    String type;
    if (ArduinoOTA.getCommand() == U_FLASH) {
      type = "sketch";
    } else {
      type = "filesystem";
    }
    Serial.println("Start updating " + type);
  });
  
  ArduinoOTA.onEnd([]() {
    Serial.println("\nEnd");
  });
  
  ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
    Serial.printf("Progress: %u%%\r", (progress / (total / 100)));
  });
  
  ArduinoOTA.onError([](ota_error_t error) {
    Serial.printf("Error[%u]: ", error);
    if (error == OTA_AUTH_ERROR) {
      Serial.println("Auth Failed");
    } else if (error == OTA_BEGIN_ERROR) {
      Serial.println("Begin Failed");
    } else if (error == OTA_CONNECT_ERROR) {
      Serial.println("Connect Failed");
    } else if (error == OTA_RECEIVE_ERROR) {
      Serial.println("Receive Failed");
    } else if (error == OTA_END_ERROR) {
      Serial.println("End Failed");
    }
  });
  
  ArduinoOTA.begin();
  Serial.println("OTA Ready");
}

unsigned long getEpochTime() {
  struct tm timeinfo;
  if (getLocalTime(&timeinfo)) {
    return mktime(&timeinfo);
  }
  return millis() / 1000; // Fallback to relative time
}

// ============================================================================
// CALIBRATION INSTRUCTIONS (in comments)
// ============================================================================

/*
 * CALIBRATION PROCEDURE:
 * 
 * 1. Place sensors in clean environment (no smoke, gas, or fire)
 * 2. Let MQ sensors warm up for at least 5-10 minutes (ideally 24-48 hours)
 * 3. Monitor Serial output and record baseline values for MQ2 and MQ5
 * 4. Calculate average baseline over several minutes
 * 5. Set thresholds as: baseline + 20-40% margin
 *    Example: if MQ2 baseline = 800, set MQ2_THRESHOLD = 800 + (800 * 0.3) = 1040
 * 6. Test with actual smoke/gas sources to verify detection
 * 7. Adjust thresholds if needed for sensitivity vs false alarms
 * 
 * WIRING NOTES:
 * - If MQ modules are powered by 5V, use voltage dividers on analog outputs
 * - Ensure all grounds are connected together
 * - Use current limiting resistor (220-470Ω) for buzzer if connecting directly to GPIO
 * - Consider using transistor driver for buzzer for better current handling
 * 
 * PASSIVE BUZZER NOTES:
 * - Passive buzzer requires PWM signal to produce sound (different from active buzzer)
 * - Uses LEDC (LED PWM Controller) to generate different tone frequencies
 * - Different frequencies create different tones/alerts for each hazard type:
 *   • Gas: 800 Hz (lower pitch)
 *   • Smoke: 1000 Hz (medium pitch)  
 *   • Fire: 1200 Hz (higher pitch)
 *   • Multi-hazard: 1500 Hz (highest pitch)
 * - Duty cycle affects volume (50% = moderate volume)
 * 
 * PASSIVE BUZZER WIRING (recommended for reliable operation):
 * GPIO22 → 1kΩ → Base(NPN), Emitter → GND, Collector → Buzzer(-), Buzzer(+) → 5V
 * OR for low-current passive buzzer: GPIO22 → Buzzer(+), Buzzer(-) → GND
 * 
 * ADC CONFIGURATION:
 * - ADC_11db attenuation allows 0-3.3V input range
 * - ADC resolution is 12-bit (0-4095)
 * - Use ADC1 pins (GPIO32-39) to avoid WiFi interference
 */