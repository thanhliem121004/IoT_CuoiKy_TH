# ESP32-C3 Real Hardware - Arduino IDE Setup

## 📦 Cài đặt Arduino IDE

### 1. Cài ESP32 Board Manager

1. Mở Arduino IDE
2. File → Preferences
3. Thêm URL vào "Additional Board Manager URLs":
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
4. Tools → Board → Boards Manager
5. Tìm "esp32" và cài đặt "esp32 by Espressif Systems"

### 2. Cài đặt Libraries (Sketch → Include Library → Manage Libraries)

- **PubSubClient** by Nick O'Leary (cho MQTT)
- **ArduinoJson** by Benoit Blanchon (version 7.x)
- **DHT sensor library** by Adafruit
- **Adafruit Unified Sensor** by Adafruit

### 3. Cấu hình Board

- Tools → Board → ESP32 Arduino → **ESP32C3 Dev Module**
- Tools → Port → Chọn COM port của ESP32-C3 (VD: COM3, COM4...)
- Tools → Upload Speed → **115200**
- Tools → CPU Frequency → **160MHz**
- Tools → Flash Size → **4MB (32Mb)**

## 📂 Upload Code

### Cách 1: Copy code trực tiếp

1. Mở Arduino IDE
2. File → New Sketch
3. Copy toàn bộ code từ `src/main.cpp`
4. Paste vào Arduino IDE
5. Click Upload (→)

### Cách 2: Mở file trực tiếp

1. File → Open
2. Chọn file `firmware_esp32c3/src/main.cpp`
3. Arduino IDE sẽ tự tạo folder `.ino`
4. Click Upload (→)

## 🔧 Hardware Configuration

### DHT11 Sensor

- VCC → 3.3V (ESP32-C3)
- GND → GND
- DATA → GPIO2

### LED (Light)

- Built-in LED → GPIO8

### L298N Motor Driver (Fan)

| L298N | ESP32-C3 | Wire Color |
| ----- | -------- | ---------- |
| IN1   | GPIO8    | -          |
| IN2   | GPIO9    | -          |
| ENA   | GPIO10   | -          |
| GND   | GND      | Black      |
| 12V   | 5V       | Red        |
| OUT1  | Motor +  | -          |
| OUT2  | Motor -  | -          |

## 📊 Serial Monitor

- Baud rate: **115200**
- Tools → Serial Monitor
- Xem log kết nối WiFi và MQTT

## ⚙️ WiFi & MQTT (Đã config trong code)

```cpp
WiFi: "LE HUNG" / "123456789"
MQTT: 192.168.1.12:1883
Topics: demo/room1/*
```

## ✅ Test

1. Upload code
2. Mở Serial Monitor (115200 baud)
3. Xem ESP32 kết nối WiFi
4. Xem ESP32 kết nối MQTT
5. Dùng Flutter App hoặc Web để điều khiển
6. DHT11 sẽ gửi nhiệt độ/độ ẩm thật lên MQTT

## 🚨 Troubleshooting

### Lỗi upload

- Nhấn giữ nút BOOT trên ESP32-C3 khi upload
- Kiểm tra COM port đúng chưa
- Thử tốc độ upload thấp hơn (115200)

### Không kết nối WiFi

- Kiểm tra tên WiFi và password
- Kiểm tra ESP32-C3 trong vùng phủ sóng

### Không kết nối MQTT

- Kiểm tra IP broker đúng chưa (192.168.1.12)
- Kiểm tra Mosquitto Docker đang chạy: `docker ps`
- Kiểm tra firewall cho phép port 1883
