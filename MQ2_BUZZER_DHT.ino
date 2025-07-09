#include <DHT.h>

int dhtPin = 4;
int mq2Pin = A0;
int buzPin = 7;

DHT dht(dhtPin,DHT22);

void setup() {
  Serial.begin(9600);
  dht.begin();
  pinMode(buzPin, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  int temp = dht.readTemperature();
  //int humi = dht.readHumidity();
  int gas = analogRead(mq2Pin);

  if(temp > 30 || gas > 500){
    digitalWrite(buzPin, LOW);
    Serial.println(temp);
  }else{
    digitalWrite(buzPin, HIGH);
    Serial.println(temp);
  }
  delay(1000);
}
