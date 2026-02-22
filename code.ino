#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include <FastAccelStepper.h>

WebServer server(80);

// Motor A
#define A_STEP 25
#define A_DIR  26

// Motor B
#define B_STEP 27
#define B_DIR  14

#define A_ENABLE_PIN 12
#define B_ENABLE_PIN 32

const int32_t LIMIT = 200;

const uint32_t CMD_INTERVAL_MS = 20;
uint32_t lastCmdTime = 0;

FastAccelStepperEngine engine;
FastAccelStepper *motorA = nullptr;
FastAccelStepper *motorB = nullptr;

const uint32_t SPEED_HZ = 1000;
const uint32_t ACCEL    = 1000;

int32_t clamp(int32_t val, int32_t minVal, int32_t maxVal) {
  if (val < minVal) {
    return minVal;
  }
  
  if (val > maxVal) {
    return maxVal;
  }
  
  return val;
}

void differentialMove(int32_t spin, int32_t pivot) {
  if (motorA->isRunning() || motorB->isRunning()) {
    return;
  }

  int32_t aTarget = spin + pivot;
  int32_t bTarget = spin - pivot;
  
  aTarget = clamp(aTarget, -LIMIT, LIMIT);
  bTarget = clamp(bTarget, -LIMIT, LIMIT);
  
  motorA->moveTo(aTarget);
  motorB->moveTo(bTarget);
}

void handleMove() {
  uint32_t now = millis();

  // Reject spammy commands
  if (now - lastCmdTime < CMD_INTERVAL_MS) {
    server.send(429, "text/plain", "Too fast\n");
    return;
  }
  lastCmdTime = now;

  if (!server.hasArg("spin") || !server.hasArg("pivot")) {
    server.send(400, "text/plain",
      "Use /move?spin=NUM&pivot=NUM");
    return;
  } 

  int32_t spin  = server.arg("spin").toInt();
  int32_t pivot = server.arg("pivot").toInt();

  differentialMove(spin, pivot);

  server.send(200, "text/plain", "OK\n");
}

void setup() {
  Serial.begin(115200);

  pinMode(A_ENABLE_PIN, OUTPUT);
  pinMode(B_ENABLE_PIN, OUTPUT);
  digitalWrite(A_ENABLE_PIN, HIGH);
  digitalWrite(B_ENABLE_PIN, HIGH);

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) {
    delay(100);
  }

  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  server.on("/move", handleMove);
  server.begin();

  engine.init();

  motorA = engine.stepperConnectToPin(A_STEP);
  motorB = engine.stepperConnectToPin(B_STEP);

  if (!motorA || !motorB) {
    Serial.println("Stepper init failed");
    while (1);
  }

  motorA->setDirectionPin(A_DIR);
  motorB->setDirectionPin(B_DIR);

  motorA->setEnablePin(A_ENABLE_PIN);
  motorB->setEnablePin(B_ENABLE_PIN);

  motorA->setAutoEnable(false);
  motorB->setAutoEnable(false);

  motorA->setSpeedInHz(SPEED_HZ);
  motorB->setSpeedInHz(SPEED_HZ);
  motorA->setAcceleration(ACCEL);
  motorB->setAcceleration(ACCEL);

  delay(200);
  digitalWrite(A_ENABLE_PIN, LOW);
  digitalWrite(B_ENABLE_PIN, LOW);

  motorA->setCurrentPosition(0);
  motorB->setCurrentPosition(0);

  Serial.println("Ready");
}

void loop() {
  server.handleClient();
}