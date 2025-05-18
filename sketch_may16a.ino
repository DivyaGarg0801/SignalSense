void setup() {
  Serial.begin(9600);
  
  // Set pins 2, 3, 4 as outputs for external LEDs
  pinMode(2, OUTPUT); // Red
  pinMode(3, OUTPUT); // Yellow
  pinMode(4, OUTPUT); // Green
}

void loop() {
  if (Serial.available()) {
    String data = Serial.readStringUntil('\n');  // Example: "3,8"
    Serial.println("Received: " + data);

    int commaIndex = data.indexOf(',');
    if (commaIndex > 0) {
      String vehicleStr = data.substring(0, commaIndex);
      String timeStr = data.substring(commaIndex + 1);

      int vehicleCount = vehicleStr.toInt();
      int timeAlloc = timeStr.toInt();

      Serial.println("Vehicle Count: " + String(vehicleCount));
      Serial.println("Allocated Time: " + String(timeAlloc) + " seconds");

      // Turn ON green LED (pin 4) for timeAlloc seconds
      digitalWrite(4, HIGH);  // Green ON
      delay(timeAlloc * 1000);
      digitalWrite(4, LOW);   // Green OFF
    }
  }
}
