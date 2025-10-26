#include <Arduino.h>
#include "DHT.h"

// Pin configuration based on diagram.json
#define DHT_PIN 5        // DHT22 connected to GPIO 5 (esp:5)
#define DHT_TYPE DHT22   // DHT22 sensor type

// Initialize DHT sensor
DHT dht(DHT_PIN, DHT_TYPE);

void setup() {
  // Initialize serial communication
  Serial.begin(115200);
  
  // Initialize DHT sensor
  dht.begin();
  
  // Wait for serial connection and sensor stabilization
  delay(2000);
  
  Serial.println("DHT22 Data Logger Started");
  Serial.println("Format: timestamp_ms,temperature_C,humidity_%");
  Serial.println("----------------------------------------");
}

void loop() {
  // Read temperature and humidity from DHT22
  float temperature = dht.readTemperature();    // Temperature in Celsius
  float humidity = dht.readHumidity();          // Humidity in percentage
  
  // Check if readings are valid
  if (!isnan(temperature) && !isnan(humidity)) {
    // Send data in CSV format: timestamp,temperature,humidity
    Serial.print(millis());           // Arduino timestamp in milliseconds
    Serial.print(",");
    Serial.print(temperature, 2);     // Temperature with 2 decimal places
    Serial.print(",");
    Serial.println(humidity, 2);      // Humidity with 2 decimal places
  } else {
    // Send error message if sensor reading failed
    Serial.println("Error: Failed to read from DHT22 sensor");
  }
  
  // Wait 5 seconds before next reading (DHT22 recommended minimum interval: 2 seconds)
  delay(5000);
}