# 📤 Hướng dẫn Push lên GitHub

## ✅ ĐÃ PUSH THÀNH CÔNG!

Repository: **https://github.com/EurusDFIR/iot_lab5_monitor**

---

## 🚀 Hướng dẫn cho người khác clone và chạy

### Clone repository

```bash
git clone https://github.com/EurusDFIR/iot_lab5_monitor.git
cd iot_lab5_monitor
```

### Cài đặt Python dependencies

```bash
pip install paho-mqtt requests
```

### Khởi động MQTT Broker

```bash
docker run -d \
  --name mosquitto \
  -p 1883:1883 \
  -p 8083:8083 \
  -v $(pwd)/infra/mosquitto.conf:/mosquitto/config/mosquitto.conf \
  eclipse-mosquitto
```

### Chạy các thành phần

**ESP32 Simulator (nếu không có hardware):**

```bash
python simulators/esp32_simulator.py
```

**Web Dashboard:**

```bash
cd web/src
python -m http.server 3000
# Mở: http://localhost:3000
```

**Database Logger:**

```bash
cd database
python mqtt_logger.py
```

**Temperature Alert (Discord):**

```bash
# 1. Tạo Discord webhook riêng
# 2. Sửa DISCORD_WEBHOOK_URL trong alerts/temperature_alert.py
cd alerts
python temperature_alert.py
```

**Flutter App:**

```bash
cd app_flutter
flutter pub get
flutter run
```

---

## � Thông tin hệ thống

### Hardware ESP32-C3

```
- DHT11: GPIO 2
- LED: GPIO 8 (Active-LOW)
- Motor IN1: GPIO 6
- Motor IN2: GPIO 7
- Motor ENA: GPIO 10 (PWM)
```

### MQTT Topics

```
demo/room1/sensor/state    - Sensor data
demo/room1/device/state    - Device state
demo/room1/device/cmd      - Commands
demo/room1/sys/online      - Online status
```

### Database Tables

- sensor_data: Temperature, humidity, RSSI
- device_state: LED, fan status
- device_online: Connection status
- commands: Command history

---

## 🎯 Tính năng hoàn chỉnh

✅ **ESP32-C3 Real Hardware** với DHT11, LED, L298N Motor  
✅ **Web Dashboard** real-time monitoring  
✅ **Flutter Mobile App** cho Android/iOS  
✅ **SQLite Database** logging và analytics  
✅ **Discord Temperature Alerts** (30°C threshold)  
✅ **Multi-network Support** (home/hotspot/TDMU)  
✅ **Comprehensive Documentation**  
✅ **Arduino IDE Compatible** firmware  
✅ **Python Simulator** cho development

---

## 📞 Liên hệ

**Tác giả:** EurusDFIR (Enhanced Version)  
**Repository:** https://github.com/EurusDFIR/iot_lab5_monitor  
**Original Work:** Based on nguyentrungkiet/demo_chuong4_3_1  
**Email:** Liên hệ qua GitHub Issues
