#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <ArduinoJson.h>

// WiFi Configuration
const char* ssid = "kosasi kost lt 2";
const char* password = "kosasikost2";

// HiveMQ Cloud Configuration
const char* mqtt_server = "ab36ea92cee24b64acda14d3001e34d4.s1.eu.hivemq.cloud";
const int mqtt_port = 8883;
const char* mqtt_username = "cakrawala_mqtt";
const char* mqtt_password = "vXtbU7m2DjTxBSLN";

// MQTT Topics
const char* temp_humidity_topic = "sic/dibimbing/catalina/titanio-yudista/pub/dht";
const char* led_control_topic = "sic/dibimbing/catalina/titanio-yudista/sub/led";

// DHT11 Configuration
#define DHT_PIN 4
#define DHT_TYPE DHT11
DHT dht(DHT_PIN, DHT_TYPE);

// LED Configuration
#define LED_PIN 2

// MQTT and WiFi clients
WiFiClientSecure espClient;
PubSubClient client(espClient);

// Variables
unsigned long lastMsg = 0;
const unsigned long msgInterval = 5000; // Send data every 5 seconds
bool ledState = false;

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

  randomSeed(micros());

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

  // Parse JSON message for LED control
  DynamicJsonDocument doc(1024);
  deserializeJson(doc, message);
  
  if (doc.containsKey("led")) {
    String ledCommand = doc["led"];
    if (ledCommand == "on") {
      digitalWrite(LED_PIN, HIGH);
      ledState = true;
      Serial.println("LED turned ON");
    } else if (ledCommand == "off") {
      digitalWrite(LED_PIN, LOW);
      ledState = false;
      Serial.println("LED turned OFF");
    }
  }
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    
    String clientId = "ESP32Client-";
    clientId += String(random(0xffff), HEX);
    
    if (client.connect(clientId.c_str(), mqtt_username, mqtt_password)) {
      Serial.println("connected");
      
      // Subscribe to LED control topic
      client.subscribe(led_control_topic);
      Serial.print("Subscribed to: ");
      Serial.println(led_control_topic);
      
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

  // Check if readings are valid
  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }

  // Create JSON payload
  DynamicJsonDocument doc(1024);
  doc["temperature"] = temperature;
  doc["humidity"] = humidity;
  doc["timestamp"] = millis();
  doc["device_id"] = "ESP32_DHT11";

  String payload;
  serializeJson(doc, payload);

  // Publish to MQTT
  if (client.publish(temp_humidity_topic, payload.c_str())) {
    Serial.println("Data published successfully:");
    Serial.println(payload);
  } else {
    Serial.println("Failed to publish data");
  }

  // Print to Serial for debugging
  Serial.print("Temperature: ");
  Serial.print(temperature);
  Serial.print("°C, Humidity: ");
  Serial.print(humidity);
  Serial.println("%");
}

void setup() {
  Serial.begin(115200);
  
  // Initialize DHT sensor
  dht.begin();
  
  // Initialize LED pin
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  
  // Setup WiFi
  setup_wifi();
  
  // Setup MQTT
  espClient.setInsecure(); // For HiveMQ Cloud, you might need proper certificates
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
  
  Serial.println("Setup completed!");
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  unsigned long now = millis();
  if (now - lastMsg > msgInterval) {
    lastMsg = now;
    publishSensorData();
  }
}