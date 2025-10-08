# ESP32-C3 Real Hardware Firmware

## 📋 Hardware Configuration

### ESP32-C3 Super Mini

- **DHT11 Sensor**: GPIO2 (Data)
- **LED (Light)**: GPIO8 (Built-in LED)

### L298N Motor Driver (Fan Control)

| L298N Pin | ESP32-C3 Pin | Description       |
| --------- | ------------ | ----------------- |
| IN1       | GPIO8        | Motor direction 1 |
| IN2       | GPIO9        | Motor direction 2 |
| ENA       | GPIO10       | PWM speed control |
| GND       | GND          | Ground            |
| 12V       | 5V           | Power supply      |
| OUT1/OUT2 | Motor        | Motor connections |

## 🔧 WiFi & MQTT Configuration

```cpp
WiFi SSID: "LE HUNG"
WiFi Pass: "123456789"
MQTT Broker: 192.168.1.12:1883
Topics: demo/room1/*
```

## 📦 Upload Firmware

### ⚡ Arduino IDE (Recommended)

📄 **Xem hướng dẫn chi tiết:** [`ARDUINO_SETUP.md`](ARDUINO_SETUP.md)

**Tóm tắt:**

1. Cài ESP32 board support
2. Cài libraries: PubSubClient, ArduinoJson, DHT sensor library
3. Mở file `src/main.cpp` trong Arduino IDE
4. Chọn Board: **ESP32C3 Dev Module**
5. Chọn Port: COM port của ESP32-C3
6. Click Upload (→)

### Alternative: PlatformIO

```bash
cd firmware_esp32c3
pio run --target upload
pio device monitor
```

## 📊 MQTT Topics (Same as Simulator)

- **Subscribe**: `demo/room1/device/cmd` - Receive commands
- **Publish**: `demo/room1/device/state` - Device state (retained)
- **Publish**: `demo/room1/sensor/state` - Sensor data (temp, humidity)
- **Publish**: `demo/room1/sys/online` - Online status (retained, LWT)

## ✅ Testing

1. Upload firmware to ESP32-C3
2. Open Serial Monitor (115200 baud)
3. Check WiFi connection
4. Check MQTT connection
5. Use Flutter App or Web Dashboard to control
6. DHT11 will publish real temperature/humidity data

## 🎯 Compatible with:

- ✅ Web Dashboard (no changes needed)
- ✅ Flutter Mobile App (no changes needed)
- ✅ Same MQTT topics as simulator
- ✅ Drop-in replacement for ESP32 simulator
