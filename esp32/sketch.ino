#include <DHT.h>

// Defining the pins where the sensors are connected
#define DHTPIN 12  // Pin for the DHT22
#define BUTTON_P 23 // Pin for the P button
#define BUTTON_K 22 // Pin for the K button
#define LDRPIN 14   // Pin for the LDR (pH sensor)
#define RELAYPIN 27 // Pin for the Relay

// Defining the sensor type
#define DHTTYPE DHT22

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200); // Initialize serial communication
  dht.begin(); // Initialize the DHT22
  pinMode(BUTTON_P, INPUT_PULLUP); // Set the P button as input
  pinMode(BUTTON_K, INPUT_PULLUP); // Set the K button as input
  pinMode(RELAYPIN, OUTPUT); // Set the relay pin as output
  digitalWrite(RELAYPIN, LOW); // Ensure the relay is off at startup
}

void loop() {
  // Wait 2 seconds between readings
  delay(2000);

  // Read humidity
  float humidity = dht.readHumidity();
  // Read temperature
  float temperature = dht.readTemperature();
  // Read the LDR value (pH simulation)
  int ldrValue = analogRead(LDRPIN); // Read the LDR value

  // Check if the reading failed and exit the loop if necessary
  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("Failed to read from DHT!");
    return;
  }

  // Read the state of the buttons
  bool sensorP = digitalRead(BUTTON_P) == LOW; // Button pressed
  bool sensorK = digitalRead(BUTTON_K) == LOW; // Button pressed

  // Logic for controlling the relay (irrigation)
  if (humidity < 40 && sensorP && sensorK) {
    digitalWrite(RELAYPIN, HIGH); // Turn on the relay
    Serial.println("Irrigation ON");
  } else {
    digitalWrite(RELAYPIN, LOW); // Turn off the relay
    Serial.println("Irrigation OFF");
  }

  // Display the readings on the Serial Monitor
  Serial.print("Humidity: ");
  Serial.println(humidity);
  Serial.print("Temperature: ");
  Serial.println(temperature);
  Serial.print("LDR (pH) Value: ");
  Serial.println(ldrValue); // Display the LDR value
  Serial.print("Sensor P: ");
  Serial.println(sensorP ? "Active" : "Inactive");
  Serial.print("Sensor K: ");
  Serial.println(sensorK ? "Active" : "Inactive");
}
