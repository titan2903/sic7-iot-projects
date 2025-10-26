#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <ArduinoJson.h>

// WiFi credentials
const char* ssid = "kosasi kost lt 2";
const char* password = "kosasikost2";

// HiveMQ Cloud settings - Update these with your HiveMQ Cloud details
const char* mqtt_server = "f0eacf8b4b0a4245a3f67db604624b4c.s1.eu.hivemq.cloud"; // Replace with your HiveMQ Cloud host
const int mqtt_port = 8883; // TLS port for HiveMQ Cloud
const char* mqtt_client_id = "esp32_dht11_hivemq_cloud";
const char* mqtt_user = "dht11_user"; // Replace with your HiveMQ Cloud username
const char* mqtt_pass = "Jarvis5413"; // Replace with your HiveMQ Cloud password

// MQTT Topics
const char* pub_topic = "sic/dibimbing/catalina/titanio-yudista/pub/dht";
const char* sub_topic = "sic/dibimbing/catalina/titanio-yudista/sub/led";

// Pin definitions
#define DHT_PIN 4
#define DHT_TYPE DHT11
#define LED_PIN 2

// Sensor and timing variables
DHT dht(DHT_PIN, DHT_TYPE);
WiFiClientSecure espClient; // Use secure client for TLS
PubSubClient client(espClient);

unsigned long lastMsgTime = 0;
const long interval = 5000; // Send data every 5 seconds

volatile bool ledState = false; // false = OFF, true = ON

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  
  String message;
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.println(message);

  // Control LED based on received message
  if (message == "ON") {
    ledState = true;
    digitalWrite(LED_PIN, HIGH);
    Serial.println("LED turned ON");
  } else if (message == "OFF") {
    ledState = false;
    digitalWrite(LED_PIN, LOW);
    Serial.println("LED turned OFF");
  } else {
    // Handle unknown commands
    Serial.print("Unknown command received: ");
    Serial.println(message);
    Serial.println("Supported commands: ON, OFF");
  }
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting HiveMQ Cloud connection...");
    
    // Connect with username and password for HiveMQ Cloud
    if (client.connect(mqtt_client_id, mqtt_user, mqtt_pass)) {
      Serial.println("connected to HiveMQ Cloud!");
      // Subscribe to LED control topic
      client.subscribe(sub_topic);
      Serial.print("Subscribed to: ");
      Serial.println(sub_topic);
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void publishSensorData() {
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();

  // Check if any reads failed
  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }

  // Create JSON payload
  StaticJsonDocument<200> doc;
  doc["temperature"] = temperature;
  doc["humidity"] = humidity;
  doc["timestamp"] = millis();
  doc["device_id"] = "ESP32_DHT11";

  char jsonString[200];
  serializeJson(doc, jsonString);

  // Publish to MQTT
  if (client.publish(pub_topic, jsonString)) {
    Serial.print("Published: ");
    Serial.println(jsonString);
  } else {
    Serial.println("Failed to publish message");
  }

  // Also print to Serial for debugging
  Serial.print("Temperature: ");
  Serial.print(temperature);
  Serial.print("°C, Humidity: ");
  Serial.print(humidity);
  Serial.println("%");
}

void setup() {
  Serial.begin(115200);
  
  // Initialize pins
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  
  // Initialize DHT sensor
  dht.begin();
  
  // Setup WiFi and MQTT
  setup_wifi();
  
  // Configure TLS for HiveMQ Cloud
  Serial.println("Configuring TLS for HiveMQ Cloud...");
  espClient.setInsecure(); // For testing - use proper certificates in production
  
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
  
  Serial.println("DHT11 Data Logging and LED Control System Ready (HiveMQ Cloud)!");
  Serial.print("HiveMQ Cloud Host: ");
  Serial.println(mqtt_server);
  Serial.print("Publishing to: ");
  Serial.println(pub_topic);
  Serial.print("Subscribing to: ");
  Serial.println(sub_topic);
}

void loop() {
  // digitalWrite(LED_PIN, HIGH);
  if (ledState) {
    digitalWrite(LED_PIN, HIGH);
  } else {
    digitalWrite(LED_PIN, LOW);
  }
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  unsigned long now = millis();
  if (now - lastMsgTime > interval) {
    lastMsgTime = now;
    publishSensorData();
  }

  delay(100);
}