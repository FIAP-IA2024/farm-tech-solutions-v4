#include <DHT.h>

// Defining the pins where the sensors are connected
#define DHTPIN 12   // Pin for the DHT22
#define BUTTON_P 23 // Pin for the P button
#define BUTTON_K 22 // Pin for the K button
#define LDRPIN 14   // Pin for the LDR (pH sensor)
#define RELAYPIN 27 // Pin for the Relay
#define LED_P 17    // Pin for the LED indicating sensor P
#define LED_K 16    // Pin for the LED indicating sensor K

// Defining the sensor type
#define DHTTYPE DHT22

// Thresholds
const float HUMIDITY_THRESHOLD = 40.0; // Minimum humidity level to trigger irrigation

DHT dht(DHTPIN, DHTTYPE);

bool sensorP = false;
bool sensorK = false;

unsigned long lastDebounceTimeP = 0;
unsigned long lastDebounceTimeK = 0;
unsigned long debounceDelay = 200;

unsigned long lastReadTime = 0;
unsigned long readInterval = 2000;

void setup()
{
  Serial.begin(115200); // Initialize serial communication
  dht.begin();          // Initialize the DHT22

  pinMode(BUTTON_P, INPUT_PULLUP); // Set the P button as input
  pinMode(BUTTON_K, INPUT_PULLUP); // Set the K button as input
  pinMode(RELAYPIN, OUTPUT);       // Set the relay pin as output
  pinMode(LED_P, OUTPUT);          // Set the LED for sensor P as output
  pinMode(LED_K, OUTPUT);          // Set the LED for sensor K as output

  digitalWrite(RELAYPIN, LOW); // Ensure the relay is off at startup
  digitalWrite(LED_P, LOW);    // Ensure the LED for sensor P is off at startup
  digitalWrite(LED_K, LOW);    // Ensure the LED for sensor K is off at startup
}

void loop()
{
  unsigned long currentTime = millis();

  // Read sensors every readInterval milliseconds
  if (currentTime - lastReadTime >= readInterval)
  {
    lastReadTime = currentTime;

    // Read humidity, temperature and LDR value
    float humidity = dht.readHumidity();
    float temperature = dht.readTemperature();
    int ldrValue = analogRead(LDRPIN);

    // Check if the reading failed and exit the loop if necessary
    if (isnan(humidity) || isnan(temperature))
    {
      Serial.println("Failed to read from DHT!");
      return;
    }

    // Logic for controlling the relay (irrigation)
    if (humidity < HUMIDITY_THRESHOLD && (sensorP || sensorK))
    {
      digitalWrite(RELAYPIN, HIGH); // Turn on the relay
      Serial.println("Irrigation ON");
    }
    else
    {
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
    Serial.println();
  }

  // Debounce and toggle sensor states when the button is pressed
  debounceButton(BUTTON_P, sensorP, lastDebounceTimeP);
  debounceButton(BUTTON_K, sensorK, lastDebounceTimeK);

  // Control LEDs based on sensor states
  digitalWrite(LED_P, sensorP ? HIGH : LOW);
  digitalWrite(LED_K, sensorK ? HIGH : LOW);
}

void debounceButton(int buttonPin, bool &sensorState, unsigned long &lastDebounceTime)
{
  int reading = digitalRead(buttonPin);
  if (reading == LOW)
  {
    if ((millis() - lastDebounceTime) > debounceDelay)
    {
      sensorState = !sensorState;
      lastDebounceTime = millis();
    }
  }
}
