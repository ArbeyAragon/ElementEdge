// Pin definitions for sensors
const int bloodPressurePin = A0; // Simulated for blood pressure
const int heartRatePin = A1;     // Simulated for heart rate
const int oxygenLevelPin = A2;   // Simulated for oxygen level
const int temperaturePin = A3;   // Simulated for body temperature

// Interval for sending data (in milliseconds)
const unsigned long sendInterval = 1000;
unsigned long previousMillis = 0;

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  
  // Configure pins as input
  pinMode(bloodPressurePin, INPUT);
  pinMode(heartRatePin, INPUT);
  pinMode(oxygenLevelPin, INPUT);
  pinMode(temperaturePin, INPUT);

  // Startup message
  Serial.println("Initializing sensor simulation...");
}

void loop() {
  // Get the current time
  unsigned long currentMillis = millis();

  // Send data at specified intervals
  if (currentMillis - previousMillis >= sendInterval) {
    previousMillis = currentMillis;

    // Simulate sensor data
    int bloodPressure = analogRead(bloodPressurePin); // Value between 0 and 1023
    int heartRate = analogRead(heartRatePin);         // Value between 0 and 1023
    int oxygenLevel = analogRead(oxygenLevelPin);     // Value between 0 and 1023
    int temperature = analogRead(temperaturePin);     // Value between 0 and 1023

    // Scale simulated values to realistic ranges
    float bloodPressureScaled = map(bloodPressure, 0, 1023, 90, 140); // Blood pressure (90-140 mmHg)
    float heartRateScaled = map(heartRate, 0, 1023, 60, 100);         // Heart rate (60-100 BPM)
    float oxygenLevelScaled = map(oxygenLevel, 0, 1023, 90, 100);     // Oxygen level (90-100%)
    float temperatureScaled = map(temperature, 0, 1023, 36, 38);      // Temperature (36-38 °C)

    // Send data via serial with labels
    Serial.print("BloodPressure: ");
    Serial.print(bloodPressureScaled);
    Serial.println(" mmHg");

    Serial.print("HeartRate: ");
    Serial.print(heartRateScaled);
    Serial.println(" BPM");

    Serial.print("OxygenLevel: ");
    Serial.print(oxygenLevelScaled);
    Serial.println(" %");

    Serial.print("Temperature: ");
    Serial.print(temperatureScaled);
    Serial.println(" °C");

    Serial.println("---"); // Separator for readability
  }
}
