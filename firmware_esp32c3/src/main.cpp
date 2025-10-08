/*
 * ESP32-C3 IoT Demo Firmware - REAL HARDWARE VERSION
 *
 * Hardware:
 * - ESP32-C3 Super Mini
 * - DHT11 Temperature & Humidity Sensor (GPIO2)
 * - Built-in LED for Light control (GPIO8)
 * - L298N Motor Driver for Fan control:
 *   - IN1: GPIO8
 *   - IN2: GPIO9
 *   - ENA (PWM): GPIO10
 *
 * Features:
 * - WiFi connection with auto-reconnect
 * - MQTT client with LWT (Last Will Testament)
 * - Real DHT11 sensor readings
 * - Device control via MQTT commands (Light & Fan)
 * - PWM fan speed control
 * - Retained device state messages for UI synchronization
 *
 * MQTT Topics:
 * - Publish sensor data: demo/room1/sensor/state
 * - Publish device state: demo/room1/device/state (retained)
 * - Publish online status: demo/room1/sys/online (retained, LWT)
 * - Subscribe commands: demo/room1/device/cmd
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <DHT.h>

// =============================================================================
// CONFIGURATION
// =============================================================================

// WiFi Configuration
const char *WIFI_SSID = "LE HUNG";
const char *WIFI_PASSWORD = "123456789";

// MQTT Broker Configuration
const char *MQTT_HOST = "192.168.1.12"; // Your computer's IP running Mosquitto
const int MQTT_PORT = 1883;
const char *MQTT_USERNAME = ""; // Empty for no auth
const char *MQTT_PASSWORD = ""; // Empty for no auth

// Device Configuration
const char *DEVICE_ID = "esp32c3_real";
const char *FIRMWARE_VERSION = "real-hw-1.0.0";
const char *TOPIC_NS = "demo/room1"; // Match simulator and apps

// GPIO Pin Configuration for ESP32-C3 Super Mini
#define DHT_PIN 2      // DHT11 Data pin
#define DHT_TYPE DHT11 // DHT11 sensor type

#define LED_PIN 8 // Built-in LED (Light control)

// L298N Motor Driver pins
#define MOTOR_IN1 8  // L298N IN1
#define MOTOR_IN2 9  // L298N IN2
#define MOTOR_ENA 10 // L298N ENA (PWM)

// PWM Configuration for Fan
#define PWM_FREQ 5000 // 5 KHz
#define PWM_CHANNEL 0
#define PWM_RESOLUTION 8 // 8-bit (0-255)

// Timing Configuration
const unsigned long SENSOR_PUBLISH_INTERVAL = 3000; // 3 seconds
const unsigned long HEARTBEAT_INTERVAL = 15000;     // 15 seconds
const unsigned long WIFI_RECONNECT_INTERVAL = 5000; // 5 seconds
const unsigned long MQTT_RECONNECT_INTERVAL = 5000; // 5 seconds

// =============================================================================
// GLOBAL VARIABLES
// =============================================================================

WiFiClient espClient;
PubSubClient mqttClient(espClient);
DHT dht(DHT_PIN, DHT_TYPE);

// Device state
bool lightState = false;
bool fanState = false;
int fanSpeed = 255; // PWM value 0-255

// Timing variables
unsigned long lastSensorPublish = 0;
unsigned long lastHeartbeat = 0;
unsigned long lastWifiCheck = 0;

// MQTT Topics
String topicSensorState;
String topicDeviceState;
String topicDeviceCmd;
String topicSysOnline;

// =============================================================================
// FUNCTION DECLARATIONS
// =============================================================================

void initGPIO();
void initTopics();
void initWiFi();
void initMQTT();
void reconnectWiFi();
void reconnectMQTT();
void mqttCallback(char *topic, byte *payload, unsigned int length);
void handleCommand(JsonDocument &doc);
void publishSensorData();
void publishDeviceState();
void publishOnlineStatus(bool online);
void setLight(bool state);
void setFan(bool state);
void setFanSpeed(int speed);

// =============================================================================
// SETUP FUNCTION
// =============================================================================

void setup()
{
    Serial.begin(115200);
    delay(1000);

    Serial.println("\n╔════════════════════════════════════════════╗");
    Serial.println("║   ESP32-C3 IoT Real Hardware Demo         ║");
    Serial.println("╚════════════════════════════════════════════╝");
    Serial.printf("🆔 Device ID: %s\n", DEVICE_ID);
    Serial.printf("📦 Firmware: %s\n", FIRMWARE_VERSION);
    Serial.printf("📡 Topic Namespace: %s\n", TOPIC_NS);
    Serial.printf("🌡️  DHT11 Sensor: GPIO%d\n", DHT_PIN);
    Serial.printf("💡 LED: GPIO%d\n", LED_PIN);
    Serial.printf("🌀 Motor: IN1=GPIO%d, IN2=GPIO%d, ENA=GPIO%d\n", MOTOR_IN1, MOTOR_IN2, MOTOR_ENA);
    Serial.println("────────────────────────────────────────────");

    // Initialize GPIO pins
    initGPIO();

    // Initialize DHT sensor
    dht.begin();
    Serial.println("✅ DHT11 sensor initialized");

    // Initialize MQTT topics
    initTopics();

    // Initialize WiFi
    initWiFi();

    // Initialize MQTT
    initMQTT();

    Serial.println("✅ Setup complete!");
    Serial.println("────────────────────────────────────────────\n");
}

// =============================================================================
// MAIN LOOP
// =============================================================================

void loop()
{
    unsigned long currentMillis = millis();

    // Check WiFi connection
    if (currentMillis - lastWifiCheck >= WIFI_RECONNECT_INTERVAL)
    {
        lastWifiCheck = currentMillis;
        if (WiFi.status() != WL_CONNECTED)
        {
            Serial.println("⚠️  WiFi disconnected, reconnecting...");
            reconnectWiFi();
        }
    }

    // Check MQTT connection
    if (!mqttClient.connected())
    {
        reconnectMQTT();
    }
    mqttClient.loop();

    // Publish sensor data periodically
    if (currentMillis - lastSensorPublish >= SENSOR_PUBLISH_INTERVAL)
    {
        lastSensorPublish = currentMillis;
        publishSensorData();
    }

    // Publish heartbeat (device state + online status)
    if (currentMillis - lastHeartbeat >= HEARTBEAT_INTERVAL)
    {
        lastHeartbeat = currentMillis;
        publishDeviceState();
        publishOnlineStatus(true);
    }
}

// =============================================================================
// GPIO INITIALIZATION
// =============================================================================

void initGPIO()
{
    // LED pin
    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, LOW);

    // Motor driver pins
    pinMode(MOTOR_IN1, OUTPUT);
    pinMode(MOTOR_IN2, OUTPUT);
    pinMode(MOTOR_ENA, OUTPUT);

    // Setup PWM for motor speed control
    ledcSetup(PWM_CHANNEL, PWM_FREQ, PWM_RESOLUTION);
    ledcAttachPin(MOTOR_ENA, PWM_CHANNEL);

    // Initial state - everything OFF
    setLight(false);
    setFan(false);

    Serial.println("✅ GPIO pins initialized");
}

// =============================================================================
// MQTT TOPICS INITIALIZATION
// =============================================================================

void initTopics()
{
    topicSensorState = String(TOPIC_NS) + "/sensor/state";
    topicDeviceState = String(TOPIC_NS) + "/device/state";
    topicDeviceCmd = String(TOPIC_NS) + "/device/cmd";
    topicSysOnline = String(TOPIC_NS) + "/sys/online";

    Serial.println("✅ MQTT topics configured:");
    Serial.printf("   📊 Sensor: %s\n", topicSensorState.c_str());
    Serial.printf("   📡 State: %s\n", topicDeviceState.c_str());
    Serial.printf("   📥 Command: %s\n", topicDeviceCmd.c_str());
    Serial.printf("   🟢 Online: %s\n", topicSysOnline.c_str());
}

// =============================================================================
// WIFI FUNCTIONS
// =============================================================================

void initWiFi()
{
    Serial.printf("🔌 Connecting to WiFi: %s\n", WIFI_SSID);
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20)
    {
        delay(500);
        Serial.print(".");
        attempts++;
    }

    if (WiFi.status() == WL_CONNECTED)
    {
        Serial.println("\n✅ WiFi connected!");
        Serial.printf("📍 IP Address: %s\n", WiFi.localIP().toString().c_str());
        Serial.printf("📶 RSSI: %d dBm\n", WiFi.RSSI());
    }
    else
    {
        Serial.println("\n❌ WiFi connection failed!");
    }
}

void reconnectWiFi()
{
    WiFi.disconnect();
    delay(100);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 10)
    {
        delay(500);
        Serial.print(".");
        attempts++;
    }

    if (WiFi.status() == WL_CONNECTED)
    {
        Serial.println("\n✅ WiFi reconnected!");
    }
}

// =============================================================================
// MQTT FUNCTIONS
// =============================================================================

void initMQTT()
{
    mqttClient.setServer(MQTT_HOST, MQTT_PORT);
    mqttClient.setCallback(mqttCallback);
    mqttClient.setKeepAlive(60);
    mqttClient.setSocketTimeout(10);

    // Set Last Will Testament (LWT) - published when device disconnects
    String lwt = "{\"online\":false,\"timestamp\":" + String(millis()) + "}";
    mqttClient.setWill(topicSysOnline.c_str(), lwt.c_str(), 1, true);

    Serial.printf("✅ MQTT configured: %s:%d\n", MQTT_HOST, MQTT_PORT);
}

void reconnectMQTT()
{
    static unsigned long lastAttempt = 0;
    unsigned long currentMillis = millis();

    if (currentMillis - lastAttempt < MQTT_RECONNECT_INTERVAL)
    {
        return;
    }
    lastAttempt = currentMillis;

    if (WiFi.status() != WL_CONNECTED)
    {
        return;
    }

    Serial.printf("🔄 Connecting to MQTT broker: %s:%d\n", MQTT_HOST, MQTT_PORT);

    String clientId = String(DEVICE_ID) + "_" + String(random(0xffff), HEX);

    bool connected = false;
    if (strlen(MQTT_USERNAME) > 0)
    {
        connected = mqttClient.connect(clientId.c_str(), MQTT_USERNAME, MQTT_PASSWORD);
    }
    else
    {
        connected = mqttClient.connect(clientId.c_str());
    }

    if (connected)
    {
        Serial.println("✅ MQTT connected!");

        // Subscribe to command topic
        mqttClient.subscribe(topicDeviceCmd.c_str());
        Serial.printf("📥 Subscribed to: %s\n", topicDeviceCmd.c_str());

        // Clear retained offline status and publish online
        mqttClient.publish(topicSysOnline.c_str(), "", true); // Clear retained
        publishOnlineStatus(true);

        // Publish initial device state
        publishDeviceState();
    }
    else
    {
        Serial.printf("❌ MQTT connection failed, rc=%d\n", mqttClient.state());
    }
}

void mqttCallback(char *topic, byte *payload, unsigned int length)
{
    // Parse JSON payload
    JsonDocument doc;
    DeserializationError error = deserializeJson(doc, payload, length);

    if (error)
    {
        Serial.printf("❌ JSON parse error: %s\n", error.c_str());
        return;
    }

    // Log received command
    String payloadStr;
    serializeJson(doc, payloadStr);
    Serial.printf("📥 Command received [%s]: %s\n", topic, payloadStr.c_str());

    // Handle command
    handleCommand(doc);
}

void handleCommand(JsonDocument &doc)
{
    bool stateChanged = false;

    // Light control
    if (doc.containsKey("light"))
    {
        String cmd = doc["light"].as<String>();
        if (cmd == "toggle")
        {
            lightState = !lightState;
            setLight(lightState);
            Serial.printf("💡 Light: %s\n", lightState ? "ON" : "OFF");
            stateChanged = true;
        }
        else if (cmd == "on")
        {
            lightState = true;
            setLight(true);
            Serial.println("💡 Light: ON");
            stateChanged = true;
        }
        else if (cmd == "off")
        {
            lightState = false;
            setLight(false);
            Serial.println("💡 Light: OFF");
            stateChanged = true;
        }
    }

    // Fan control
    if (doc.containsKey("fan"))
    {
        String cmd = doc["fan"].as<String>();
        if (cmd == "toggle")
        {
            fanState = !fanState;
            setFan(fanState);
            Serial.printf("🌀 Fan: %s\n", fanState ? "ON" : "OFF");
            stateChanged = true;
        }
        else if (cmd == "on")
        {
            fanState = true;
            setFan(true);
            Serial.println("🌀 Fan: ON");
            stateChanged = true;
        }
        else if (cmd == "off")
        {
            fanState = false;
            setFan(false);
            Serial.println("🌀 Fan: OFF");
            stateChanged = true;
        }
    }

    // Fan speed control (0-100%)
    if (doc.containsKey("fanSpeed"))
    {
        int speed = doc["fanSpeed"].as<int>();
        speed = constrain(speed, 0, 100);
        fanSpeed = map(speed, 0, 100, 0, 255); // Convert to PWM value
        if (fanState)
        {
            setFanSpeed(fanSpeed);
            Serial.printf("🌀 Fan speed: %d%%\n", speed);
        }
        stateChanged = true;
    }

    // Publish updated state if something changed
    if (stateChanged)
    {
        publishDeviceState();
    }
}

// =============================================================================
// DEVICE CONTROL FUNCTIONS
// =============================================================================

void setLight(bool state)
{
    digitalWrite(LED_PIN, state ? HIGH : LOW);
    lightState = state;
}

void setFan(bool state)
{
    fanState = state;
    if (state)
    {
        // Forward direction
        digitalWrite(MOTOR_IN1, HIGH);
        digitalWrite(MOTOR_IN2, LOW);
        setFanSpeed(fanSpeed);
    }
    else
    {
        // Stop motor
        digitalWrite(MOTOR_IN1, LOW);
        digitalWrite(MOTOR_IN2, LOW);
        ledcWrite(PWM_CHANNEL, 0);
    }
}

void setFanSpeed(int speed)
{
    speed = constrain(speed, 0, 255);
    ledcWrite(PWM_CHANNEL, speed);
}

// =============================================================================
// MQTT PUBLISH FUNCTIONS
// =============================================================================

void publishSensorData()
{
    // Read DHT11 sensor
    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();

    // Check if readings are valid
    if (isnan(temperature) || isnan(humidity))
    {
        Serial.println("⚠️  Failed to read from DHT sensor!");
        return;
    }

    // Get WiFi RSSI
    int rssi = WiFi.RSSI();

    // Create JSON payload
    JsonDocument doc;
    doc["temperature"] = round(temperature * 10) / 10.0; // 1 decimal
    doc["humidity"] = round(humidity * 10) / 10.0;
    doc["rssi"] = rssi;
    doc["timestamp"] = millis();

    String payload;
    serializeJson(doc, payload);

    // Publish to MQTT
    if (mqttClient.publish(topicSensorState.c_str(), payload.c_str()))
    {
        Serial.printf("🌡️  Sensor: %.1f°C, %.1f%%, %ddBm\n", temperature, humidity, rssi);
    }
}

void publishDeviceState()
{
    JsonDocument doc;
    doc["light"] = lightState ? "on" : "off";
    doc["fan"] = fanState ? "on" : "off";
    doc["rssi"] = WiFi.RSSI();
    doc["timestamp"] = millis();

    String payload;
    serializeJson(doc, payload);

    // Publish with retained flag
    if (mqttClient.publish(topicDeviceState.c_str(), payload.c_str(), true))
    {
        Serial.printf("📊 State: Light=%s, Fan=%s\n",
                      lightState ? "ON" : "OFF",
                      fanState ? "ON" : "OFF");
    }
}

void publishOnlineStatus(bool online)
{
    JsonDocument doc;
    doc["online"] = online;
    doc["deviceId"] = DEVICE_ID;
    doc["firmware"] = FIRMWARE_VERSION;
    doc["rssi"] = WiFi.RSSI();
    doc["timestamp"] = millis();

    String payload;
    serializeJson(doc, payload);

    // Publish with retained flag
    mqttClient.publish(topicSysOnline.c_str(), payload.c_str(), true);
    Serial.printf("🟢 Online status: %s\n", online ? "true" : "false");
}
