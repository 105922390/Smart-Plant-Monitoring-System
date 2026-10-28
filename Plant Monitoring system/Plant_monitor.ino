#include <DHT.h>

#define DHTPIN 2
#define DHTTYPE DHT22

const int soilPin = A0;
const int relayPin = 7;
const int ledPin = 8;

DHT dht(DHTPIN, DHT22);

bool pumpOn = false;
unsigned long pumpStartTime = 0;
const unsigned long pumpRunTime = 3000;

// Thresholds
const int dryThreshold = 250;
const int wetThreshold = 400;
const float lowHumidity = 30.0;

// Soil reading smoothing to deal with browning out Arduino
int readSoil() {
  long sum = 0;

  for (int i = 0; i < 10; i++) {
    sum += analogRead(soilPin);
    delay(10);
  }

  return sum / 10;
}

// Humidity
float readHumidity() {
  float h = dht.readHumidity();
  if (isnan(h)) return -1;
  return h;
}

// Temp
float readTemp() {
  float t = dht.readTemperature();
  if (isnan(t)) return -1;
  return t;
}

void setup() {
  Serial.begin(9600);

  pinMode(relayPin, OUTPUT);
  pinMode(ledPin, OUTPUT);

  digitalWrite(relayPin, LOW);  // turn pump off
  digitalWrite(ledPin, LOW);    // turn LED off

  dht.begin();

  Serial.println("System Starting...");
}

void loop() {
  int soil = readSoil();
  float humidity = readHumidity();
  float temp = readTemp();

  // Serial output for Python script
  Serial.print(temp);
  Serial.print(",");
  Serial.print(humidity);
  Serial.print(",");
  Serial.println(soil);

  // Rules for safety control
  bool drySoil = soil < dryThreshold;
  bool wetSoil = soil > wetThreshold;
  bool lowHum = (humidity > 0 && humidity < lowHumidity);

  // Condition for pump on
  if ((drySoil || lowHum) && !pumpOn) {
    digitalWrite(relayPin, HIGH);
    digitalWrite(ledPin, HIGH);

    pumpOn = true;
    pumpStartTime = millis();

    Serial.println("Pump ON");
  }

  // Condition for pump off
  if (pumpOn &&
      (millis() - pumpStartTime > pumpRunTime ||
       (wetSoil && humidity > lowHumidity + 5))) {
    digitalWrite(relayPin, LOW);
    digitalWrite(ledPin, LOW);

    pumpOn = false;

    Serial.println("Pump OFF");
  }

  delay(500);
}