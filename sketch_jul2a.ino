#include <DHT.h>

#define DHTTYPE DHT11
#define DHTPIN 2

DHT dhtSensor(DHTPIN,DHTTYPE);

void setup() {
  Serial.begin(9600);
  dhtSensor.begin();
}

void loop() {
  // put your main code here, to run repeatedly:
  //float temp = ;
  Serial.print("Nhiet do: ");
  Serial.println(dhtSensor.readTemperature());
  Serial.print("Do am: ");
  Serial.println(dhtSensor.readHumidity());

  
  delay(1000);
}
