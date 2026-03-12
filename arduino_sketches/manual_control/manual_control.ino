/**
 * Arduino Robot Control
 * Receives commands (F,B,R,L) from Raspberry Pi
 * Implements obstacle detection and avoidance
 */

// Pin Definitions
#define RB 11    // Right motor reverse
#define RF 10   // Right motor forward
#define LB 13  // Left motor reverse
#define LF 12    // Left motor forward
#define trig 7  // Ultrasonic sensor trigger
#define echo 8  // Ultrasonic sensor echo
#define LED_PIN 6   // LED indicator
#define EN 9

// Motor control variables
unsigned long moveStartTime = 0;
unsigned long moveDuration = 0;
bool isMoving = false;

void stopMotors() {
  digitalWrite(LF, LOW);
  digitalWrite(LB, LOW);
  digitalWrite(RF, LOW);
  digitalWrite(RB, LOW);
}

float getDistance() {
  digitalWrite(trig, LOW);
  delayMicroseconds(2);
  digitalWrite(trig, HIGH);
  delayMicroseconds(10);
  digitalWrite(trig, LOW);
  
  long duration = pulseIn(echo, HIGH, 30000); // 30ms timeout (~5m range)
  float distance = (duration > 0) ? (duration * 0.0343) / 2 : 999;
  return distance;
}

void setup() {
  Serial.begin(9600);  // Standard baud rate as in your original code
  pinMode(LF, OUTPUT);
  pinMode(LB, OUTPUT);
  pinMode(RF, OUTPUT);
  pinMode(RB, OUTPUT);
  pinMode(trig, OUTPUT);
  pinMode(echo, INPUT);
  pinMode(LED_PIN, OUTPUT);
  pinMode(EN, OUTPUT);
  analogWrite(EN, 255); 
  stopMotors();
}

void loop() {
  // Check distance and update LED
  float distance = getDistance();
  digitalWrite(LED_PIN, (distance < 30) ? HIGH : LOW);
  
  // Check for commands
  if(Serial.available() > 0) {
    char cmd = Serial.read();
    if(cmd == '\n' || cmd == '\r') return;
    
    // Execute command
    executeCommand(cmd);
  }
  
  // Check if movement should stop
  if(isMoving && (millis() - moveStartTime >= moveDuration)) {
    stopMotors();
    isMoving = false;
  }
}

void executeCommand(char cmd) {
  // Get distance for obstacle detection
  float distance = getDistance();
  
  // Block forward command if obstacle detected
  if(cmd == 'F' && distance < 30) {
    return;
  }
  
  // Stop current movement
  stopMotors();
  
  // Execute new command
  switch(cmd) {
    case 'F':
      digitalWrite(LF, HIGH);
      digitalWrite(RF, HIGH);
      moveDuration = 1000;  // 1 second
      break;
    case 'B':
      digitalWrite(LB, HIGH);
      digitalWrite(RB, HIGH);
      moveDuration = 1000;  // 1 second
      break;
    case 'L':
      digitalWrite(LB, HIGH);
      digitalWrite(RF, HIGH);
      moveDuration = 500;   // 0.5 seconds
      break;
    case 'R':
      digitalWrite(LF, HIGH);
      digitalWrite(RB, HIGH);
      moveDuration = 500;   // 0.5 seconds
      break;
    case 'S':
      // Already stopped motors above
      moveDuration = 0;
      isMoving = false;
      return;
    default:
      return;
  }
  
  moveStartTime = millis();
  isMoving = true;
}
