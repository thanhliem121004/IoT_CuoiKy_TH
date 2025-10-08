# 🚀 QUICK START - Hệ thống IoT

## Chạy từng lệnh theo thứ tự:

### 1. Khởi động Mosquitto MQTT Broker

```bash
docker start mosquitto
```

### 2. Chạy ESP32 (chọn 1 trong 2)

**Option A - Simulator:**

```bash
python simulators/esp32_simulator.py
```

**Option B - Real Hardware:**

- Upload firmware từ `firmware_esp32c3/esp32c3_iot_demo.ino`
- Kết nối hardware theo hướng dẫn trong `firmware_esp32c3/README.md`

### 3. Chạy Database Logger (terminal mới) - Optional

```bash
cd database
python mqtt_logger.py
```

Để xem dữ liệu (terminal khác):

```bash
cd database
python view_database.py
```

### 3b. Chạy Temperature Alert (terminal mới) - Optional

```bash
cd alerts
python temperature_alert.py
```

Gửi cảnh báo Discord khi nhiệt độ > 30°C

### 4. Chạy Web Dashboard (terminal mới)

```bash
cd web/src
python -m http.server 3000
```

Mở browser: http://localhost:3000

### 5. Chạy Flutter App (terminal mới)

```bash
cd app_flutter
flutter run
```

## Cấu hình:

- **Mosquitto**: localhost:1883 (TCP), ws://localhost:8083 (WebSocket)
- **ESP32**: localhost:1883
- **Web**: ws://localhost:8083
- **Flutter Emulator**: 10.0.2.2:1883
- **Flutter Physical Device**: 192.168.1.11:1883
