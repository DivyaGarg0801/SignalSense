String inputString = "";
bool stringComplete = false;

struct LaneData {
  int vehicles;
  int green;
  int yellow;
  int red;
};

LaneData lanes[4];

// Lane pins: [red, yellow, green] per lane
const int lanePins[4][3] = {
  {2, 3, 4},     // Lane 1
  {5, 6, 7},     // Lane 2
  {8, 9, 10},    // Lane 3
  {11, 12, 13}   // Lane 4
};

void setup() {
  Serial.begin(9600);

  // Set all pins as OUTPUT
  for (int i = 0; i < 4; i++) {
    for (int j = 0; j < 3; j++) {
      pinMode(lanePins[i][j], OUTPUT);
      digitalWrite(lanePins[i][j], LOW);  // Turn all OFF initially
    }
  }

  Serial.println("Setup complete. Waiting for data...");
  inputString.reserve(100);
}

void loop() {
  // If new data received, parse it and update lanes[]
  if (stringComplete) {
    Serial.println("Received: " + inputString);
    parseData(inputString);
    inputString = "";
    stringComplete = false;
    Serial.println("Data parsed. Starting cycle...");
  }

  // Cycle through each lane continuously with current data
  for (int i = 0; i < 4; i++) {
    handleLane(i);
  }

  Serial.println("All lanes cycled. Repeating cycle...");
  delay(1000); // Optional short pause between cycles
}

// Read input string from serial
void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    inputString += inChar;
    if (inChar == '\n') {
      stringComplete = true;
    }
  }
}

// Parse overall 4-lane data
void parseData(String data) {
  int start = 0;
  for (int i = 0; i < 4; i++) {
    int end = data.indexOf(';', start);
    if (end == -1) end = data.indexOf('\n', start);
    if (end == -1) end = data.length();

    String laneStr = data.substring(start, end);
    lanes[i] = parseLane(laneStr);
    start = end + 1;
  }
}

// Parse a single lane's data
LaneData parseLane(String str) {
  LaneData lane;

  int c1 = str.indexOf(',');
  int c2 = str.indexOf(',', c1 + 1);
  int c3 = str.indexOf(',', c2 + 1);

  lane.vehicles = str.substring(0, c1).toInt();
  lane.green = str.substring(c1 + 1, c2).toInt();
  lane.yellow = str.substring(c2 + 1, c3).toInt();
  lane.red = str.substring(c3 + 1).toInt();

  return lane;
}

// Control lights for one lane (others show red)
void handleLane(int index) {
  Serial.print("Handling Lane ");
  Serial.println(index + 1);

  // Turn RED ON for all lanes first
  for (int i = 0; i < 4; i++) {
    digitalWrite(lanePins[i][0], HIGH);  // Red ON
    digitalWrite(lanePins[i][1], LOW);   // Yellow OFF
    digitalWrite(lanePins[i][2], LOW);   // Green OFF
  }

  // GREEN ON for current lane
  digitalWrite(lanePins[index][0], LOW);  // Red OFF
  digitalWrite(lanePins[index][2], HIGH); // Green ON
  Serial.println("Green ON for " + String(lanes[index].green) + " sec");
  delay(lanes[index].green * 1000);
  digitalWrite(lanePins[index][2], LOW); // Green OFF

  // YELLOW ON for current lane
  digitalWrite(lanePins[index][1], HIGH); // Yellow ON
  Serial.println("Yellow ON for " + String(lanes[index].yellow) + " sec");
  delay(lanes[index].yellow * 1000);
  digitalWrite(lanePins[index][1], LOW);  // Yellow OFF

  // RED ON again for current lane
  digitalWrite(lanePins[index][0], HIGH); // Red ON
  Serial.println("Back to Red");
}
