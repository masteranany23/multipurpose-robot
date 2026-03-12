// Arduino Line Follower Car with 2 IR Sensors
// - White surface with black line
// - Single enable pin for all motors
// - Optimized for stability
// - Corrected IR sensor logic (HIGH for black, LOW for white)

// Motor pin definitions
#define RB 2       // Right motor reverse
#define RF 3       // Right motor forward
#define LB 4       // Left motor reverse
#define LF 5       // Left motor forward
#define ENABLE 6   // Enable pin for all motors (PWM for speed control)

// IR sensor pin definitions
#define LEFT_IR A4  // Left IR sensor
#define RIGHT_IR A5 // Right IR sensor

// Constants for sensor thresholds and motor speeds
#define IR_THRESHOLD 500  // Threshold to differentiate black/white (may need adjustment)
#define BASE_SPEED 100    // Base speed for motors (0-255)

// Variables for sensor readings
int leftIRValue = 0;
int rightIRValue = 0;
bool leftOnBlack = false;
bool rightOnBlack = false;

// Timing variables for debugging and optimization
unsigned long lastDebugTime = 0;
const unsigned long debugInterval = 2000; // 2 seconds between debug messages

void setup() {
  // Initialize motor pins as outputs
  pinMode(RB, OUTPUT);
  pinMode(RF, OUTPUT);
  pinMode(LB, OUTPUT);
  pinMode(LF, OUTPUT);
  pinMode(ENABLE, OUTPUT);
  
  // Initialize IR sensor pins as inputs
  pinMode(LEFT_IR, INPUT);
  pinMode(RIGHT_IR, INPUT);
  
  // Stop motors initially
  stopMotors();
  
  // Begin serial communication for debugging
  Serial.begin(9600);
  Serial.println(F("Line Follower Robot initialized"));
  
  // Small delay to ensure everything is initialized
  delay(1000);
}

void loop() {
  // Read IR sensor values
  readSensors();
  
  // Determine robot action based on sensor readings
  determineAction();
  
  // Optional: Print debug information periodically
  debugOutput();
  
  // Small delay to stabilize readings and prevent rapid oscillations
  delay(20);
}

void readSensors() {
  // Read analog values from IR sensors
  leftIRValue = analogRead(LEFT_IR);
  rightIRValue = analogRead(RIGHT_IR);
  
  // Determine if sensors are on black line
  // CORRECTED: For your sensors, HIGH values = BLACK, LOW values = WHITE
  leftOnBlack = (leftIRValue > IR_THRESHOLD);  // Changed < to >
  rightOnBlack = (rightIRValue > IR_THRESHOLD); // Changed < to >
}

void determineAction() {
  // Set motor speed (constant for all motors via ENABLE pin)
  analogWrite(ENABLE, BASE_SPEED);
  
  // Both sensors on white (correct position) - move forward
  if (!leftOnBlack && !rightOnBlack) {
    moveForward();
  }
  // Left sensor detects black - turn right to get back on track
  else if (leftOnBlack && !rightOnBlack) {
    //turnRight();
    turnLeft();
  }
  // Right sensor detects black - turn left to get back on track
  else if (!leftOnBlack && rightOnBlack) {
    //turnLeft();
    turnRight();
  }
  // Both sensors on black - decision point or thick line
  // This condition should rarely occur with your setup
  else {
    // Continue moving forward but with reduced speed
    analogWrite(ENABLE, BASE_SPEED / 2);
    moveForward();
  }
}

// Motor control functions
// Since we're using a single ENABLE pin for speed control,
// these functions only control direction

void moveForward() {
  digitalWrite(RF, HIGH);
  digitalWrite(LF, HIGH);
  digitalWrite(RB, LOW);
  digitalWrite(LB, LOW);
}

void turnLeft() {
  digitalWrite(RF, HIGH);
  digitalWrite(LF, LOW);
  digitalWrite(RB, LOW);
  digitalWrite(LB, HIGH);
}

void turnRight() {
  digitalWrite(RF, LOW);
  digitalWrite(LF, HIGH);
  digitalWrite(RB, HIGH);
  digitalWrite(LB, LOW);
}

void stopMotors() {
  // Turn off all direction pins
  digitalWrite(RF, LOW);
  digitalWrite(LF, LOW);
  digitalWrite(RB, LOW);
  digitalWrite(LB, LOW);
  
  // Disable motors by setting ENABLE to LOW
  digitalWrite(ENABLE, LOW);
}

void debugOutput() {
  // Print debug information periodically
  unsigned long currentMillis = millis();
  if (currentMillis - lastDebugTime >= debugInterval) {
    lastDebugTime = currentMillis;
    
    Serial.println(F("---------- Debug Info ----------"));
    Serial.print(F("Left IR: "));
    Serial.print(leftIRValue);
    Serial.print(F(" ("));
    // CORRECTED: Display BLACK for high values, WHITE for low values
    Serial.print(leftOnBlack ? F("BLACK") : F("WHITE"));
    Serial.println(F(")"));
    
    Serial.print(F("Right IR: "));
    Serial.print(rightIRValue);
    Serial.print(F(" ("));
    // CORRECTED: Display BLACK for high values, WHITE for low values
    Serial.print(rightOnBlack ? F("BLACK") : F("WHITE"));
    Serial.println(F(")"));
    Serial.print(F("Motor Speed: "));
    Serial.println(BASE_SPEED);
    Serial.println(F("------------------------------"));
  }
}
