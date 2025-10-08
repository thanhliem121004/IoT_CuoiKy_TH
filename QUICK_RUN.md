# 🚀 IoT Lab 5 Monitor - Quick Start

Hệ thống giám sát IoT hoàn chỉnh với ESP32-C3, Web Dashboard, Mobile App và Database.

## ⚡ 3 Bước để chạy ngay

### 1. Clone & Setup

```bash
git clone https://github.com/EurusDFIR/iot_lab5_monitor.git
cd iot_lab5_monitor
pip install paho-mqtt requests
```

### 2. Khởi động MQTT Broker

```bash
docker run -d --name mosquitto -p 1883:1883 -p 8083:8083 eclipse-mosquitto
```

### 3. Chạy các thành phần

**Terminal 1 - Web Dashboard:**

```bash
cd web/src
python -m http.server 3000
```

Mở: http://localhost:3000

**Terminal 2 - Setup ESP32-C3 Hardware:**

```bash
# 1. Mở Arduino IDE
# 2. Mở file: firmware_esp32c3/esp32c3_iot_demo/esp32c3_iot_demo.ino
# 3. Sửa WiFi và MQTT config:
#    const char *WIFI_SSID = "YOUR_WIFI_NAME";
#    const char *WIFI_PASSWORD = "YOUR_WIFI_PASS";
#    const char *MQTT_HOST = "YOUR_COMPUTER_IP";
# 4. Upload lên ESP32-C3
```

**Terminal 3 - Database Logger (tùy chọn):**

```bash
cd database
python mqtt_logger.py
```

**Terminal 4 - Temperature Alert (tùy chọn):**

```bash
cd alerts
# Sửa DISCORD_WEBHOOK_URL trong temperature_alert.py trước
python temperature_alert.py
```

**Terminal 5 - Flutter App (tùy chọn):**

```bash
cd app_flutter
flutter run
```

## 🔧 Setup ESP32-C3 Hardware

**Bắt buộc - không có hardware thì không chạy được!**

1. **Chuẩn bị Arduino IDE:**

   - Tải Arduino IDE: https://www.arduino.cc/en/software
   - Cài ESP32 board: File > Preferences > Additional Boards Manager URLs
   - Thêm: `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
   - Tools > Board > Boards Manager > Tìm "esp32" > Cài "esp32 by Espressif"

2. **Cấu hình WiFi và MQTT:**

   - Mở file: `firmware_esp32c3/esp32c3_iot_demo/esp32c3_iot_demo.ino`
   - Sửa 3 thông tin quan trọng:

   ```cpp
   const char *WIFI_SSID = "YOUR_WIFI_NAME";        // Tên WiFi nhà bạn
   const char *WIFI_PASSWORD = "YOUR_WIFI_PASS";    // Mật khẩu WiFi
   const char *MQTT_HOST = "192.168.1.xxx";         // IP máy tính chạy Mosquitto
   ```

3. **Upload firmware:**

   - Kết nối ESP32-C3 với máy tính
   - Tools > Board > ESP32C3 Dev Module
   - Tools > Port > Chọn COM port của ESP32
   - Click Upload (mũi tên phải)
   - Chờ "Done uploading"

4. **Kiểm tra hoạt động:**
   - Mở Serial Monitor (Tools > Serial Monitor)
   - Thấy: "Connected to WiFi", "MQTT Connected", "Publishing sensor data"

## 📊 Kiểm tra hoạt động

- **ESP32 Hardware:** Serial Monitor hiển thị "Publishing sensor data" mỗi 2 giây
- **Web Dashboard:** http://localhost:3000 - hiển thị nhiệt độ, độ ẩm real-time từ DHT11
- **Database:** Chạy `python database/view_database.py all` để xem dữ liệu đã lưu
- **MQTT Topics:** `demo/room1/sensor/state`, `demo/room1/device/state`

## 🛠️ Troubleshooting

### ESP32 không kết nối WiFi?

- **ESP32 chỉ hỗ trợ WiFi 2.4GHz** - không phải 5GHz
- Kiểm tra tên WiFi và mật khẩu có đúng không
- Mở Serial Monitor trong Arduino IDE xem lỗi gì
- ESP32 và máy tính phải cùng mạng WiFi

### ESP32 không kết nối MQTT?

- Kiểm tra IP máy tính: `ipconfig` (Windows) hoặc `ifconfig` (Linux/Mac)
- Đảm bảo Mosquitto container đang chạy: `docker ps`
- Kiểm tra firewall không chặn port 1883

### Web Dashboard không hiển thị dữ liệu?

- Đảm bảo ESP32 đã kết nối và đang publish data
- Kiểm tra Console Browser (F12) xem có lỗi WebSocket
- Đảm bảo Mosquitto chạy trên port 8083 (WebSocket)

### Flutter App không kết nối?

- Android Emulator: Dùng IP `10.0.2.2` thay vì `localhost`
- Physical device: Dùng IP thật của máy tính
- Kiểm tra Mosquitto port 1883

### Database không lưu dữ liệu?

- Kiểm tra `mqtt_logger.py` đang chạy
- Xem console có lỗi gì không
- File `iot_data.db` sẽ tự tạo khi chạy

## 📋 Yêu cầu hệ thống

- Python 3.8+
- Docker
- Arduino IDE (cho ESP32 hardware)
- Flutter SDK (cho mobile app)

## 🎯 Tính năng

✅ **ESP32-C3 Hardware** với DHT11 sensor, LED control, L298N motor  
✅ **Real sensor data** - nhiệt độ, độ ẩm thực từ DHT11  
✅ **Device control** - bật/tắt LED và motor qua MQTT  
✅ **Web Dashboard** real-time monitoring  
✅ **SQLite Database** logging tất cả dữ liệu  
✅ **Discord Temperature Alerts** cảnh báo khi quá nhiệt  
✅ **Flutter Mobile App** điều khiển từ xa  
✅ **Multi-network support** - hoạt động trên mọi WiFi

## 📄 Credits & License

**Original Work:** Based on nguyentrungkiet's IoT demo system  
**Original Repository:** https://github.com/nguyentrungkiet/demo_chuong4_3_1  
**Enhanced by:** EurusDFIR with hardware support and advanced features

**License:** MIT License - See [LICENSE](LICENSE) for details

**Repository:** https://github.com/EurusDFIR/iot_lab5_monitor
