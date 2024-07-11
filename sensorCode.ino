#include <ESP8266WiFi.h>
#include <Wire.h>
#include <Adafruit_BMP085.h>

const char* ssid = "Piyush";
const char* password = "Piyush_02";

const char* server = "api.thingspeak.com";
const String apiKey = "ZGW3032ZU0TQ4FCU";

Adafruit_BMP085 bmp;

void setup() {
  Serial.begin(9600);
  delay(500);

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi connected");

  if (!bmp.begin()) {
    Serial.println("Could not find BMP sensor, check wiring!");
    while (1);
  }
}

void loop() {
  float temperature = bmp.readTemperature();
  float pressure = bmp.readPressure()/100.0;

  Serial.print("Temperature: ");
  Serial.print(temperature);
  Serial.println(" *C");

  Serial.print("Pressure: ");
  Serial.print(pressure);
  Serial.println(" hPa");

  sendToThingSpeak(temperature, pressure-30);

  delay(17000);
}

void sendToThingSpeak(float temperature, float pressure) {
  if (WiFi.status() == WL_CONNECTED) {
    WiFiClient client;
    if (!client.connect(server, 80)) {
      Serial.println("Connection to ThingSpeak failed");
      return;
    }

    String url = "/update?api_key=" + apiKey + "&field1=" + String(temperature) + "&field2=" + String(pressure);

    client.print(String("GET ") + url + " HTTP/1.1\r\n" +
                 "Host: " + server + "\r\n" +
                 "Connection: close\r\n\r\n");

    unsigned long timeout = millis();
    while (client.available() == 0) {
      if (millis() - timeout > 5000) {
        Serial.println("Client timeout!");
        client.stop();
        return;
      }
    }

    // while (client.available()) {
    //   String line = client.readStringUntil('\r');
    //   Serial.print(line);
    // }

    Serial.println("Data sent to ThingSpeak successfully");
    client.stop();
  } else {
    Serial.println("WiFi not connected");
  }
}
