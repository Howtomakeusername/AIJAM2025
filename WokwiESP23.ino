
#include <WiFi.h>
#include "ThingSpeak.h"
#include "DHTesp.h"

#define WIFI_NAME  "Wokwi-GUEST"
#define WIFI_PASSWORD  ""
#define CHANNEL_ID 2695758
#define API_KEY "CQMXUXQ6K1AT7OW2"

WiFiClient client;
DHTesp dhtSensor;

void setup() {
  Serial.begin(9600);
  dhtSensor.setup(15, DHTesp::DHT22);
  WiFi.begin(WIFI_NAME, WIFI_PASSWORD); // Connect to the WiFi network
  while (WiFi.status() != WL_CONNECTED){
    delay(1000);
    Serial.println("Wifi not connected"); // Print a message if WiFi is not connected
  }
  Serial.println("Wifi connected !"); // Print a message if WiFi is connected
  ThingSpeak.begin(client);
  //dhtSensor.begin();
}

void loop() {
  TempAndHumidity data = dhtSensor.getTempAndHumidity();

  ThingSpeak.setField(1,data.temperature); 
  ThingSpeak.setField(2,data.humidity);

  int x = ThingSpeak.writeFields(CHANNEL_ID,API_KEY); 

  if(x == 200){
    Serial.println("Data pushed successfully"); // Print a message if the data was successfully pushed to ThingSpeak
  }else{
    Serial.println("Push error" + String(x)); // Print an error message with the HTTP status code if there was an error pushing the data
  }
  delay(10000);
}