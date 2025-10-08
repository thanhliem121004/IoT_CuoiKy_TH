# 🚀 Hướng dẫn Setup hoàn chỉnh - IoT Lab 5 Monitor

**Đã test thành công 100% - Làm theo từng bước sẽ chạy được!**

---

## 📋 Yêu cầu hệ thống

### Phần mềm bắt buộc:
- ✅ **Python 3.8+** (đã cài sẵn trên máy)
- ✅ **Docker Desktop** (để chạy Mosquitto MQTT Broker)
- ✅ **Arduino IDE 2.x** (để upload firmware lên ESP32)
- ✅ **Git** (để clone project)

### Phần cứng bắt buộc:
- ✅ **ESP32-C3 Super Mini** (hoặc tương đương)
- ✅ **DHT11 Temperature & Humidity Sensor**
- ✅ **LED** (hoặc dùng LED built-in trên ESP32)
- ✅ **L298N Motor Driver** (hoặc relay module)
- ✅ **Breadboard và dây nối**

---

## 🔧 BƯỚC 1: Clone Project

```bash
git clone https://github.com/EurusDFIR/iot_lab5_monitor.git
cd iot_lab5_monitor
```

---

## 📦 BƯỚC 2: Cài đặt Python Dependencies

**KHÔNG cần virtual environment!** Chạy trực tiếp:

```bash
pip install paho-mqtt requests
```

**Kiểm tra đã cài:**
```bash
pip list | findstr "paho-mqtt requests"
```

Phải thấy:
```
paho-mqtt          x.x.x
requests           x.x.x
```

---

## 🐳 BƯỚC 3: Setup Mosquitto MQTT Broker (QUAN TRỌNG!)

### Windows PowerShell:

```powershell
# 1. Di chuyển vào thư mục project
cd iot_lab5_monitor

# 2. Tạo thư mục cấu hình
New-Item -ItemType Directory -Force -Path "mosquitto\config"
New-Item -ItemType Directory -Force -Path "mosquitto\data"

# 3. Tạo file mosquitto.conf với nội dung CHÍNH XÁC
Set-Content -Path "mosquitto\config\mosquitto.conf" -Value @"
listener 1883 0.0.0.0
allow_anonymous true

listener 8083 0.0.0.0
protocol websockets
allow_anonymous true

log_dest stdout
log_type all

persistence true
persistence_location /mosquitto/data/
"@

# 4. Kiểm tra file đã tạo đúng chưa
Get-Content "mosquitto\config\mosquitto.conf"

# 5. Xóa container cũ (nếu có)
docker rm -f mosquitto

# 6. Chạy Mosquitto container
docker run -d `
  --name mosquitto `
  -p 1883:1883 `
  -p 8083:8083 `
  -v "${PWD}\mosquitto\config:/mosquitto/config" `
  -v "${PWD}\mosquitto\data:/mosquitto/data" `
  eclipse-mosquitto

# 7. Kiểm tra logs (QUAN TRỌNG!)
docker logs mosquitto
```

### Linux/Mac/Git Bash:

```bash
# 1. Di chuyển vào thư mục project
cd iot_lab5_monitor

# 2. Tạo thư mục và file cấu hình
mkdir -p mosquitto/config mosquitto/data
cat > mosquitto/config/mosquitto.conf << 'EOF'
listener 1883 0.0.0.0
allow_anonymous true

listener 8083 0.0.0.0
protocol websockets
allow_anonymous true

log_dest stdout
log_type all

persistence true
persistence_location /mosquitto/data/
EOF

# 3. Xóa container cũ (nếu có)
docker rm -f mosquitto

# 4. Chạy Mosquitto container
docker run -d \
  --name mosquitto \
  -p 1883:1883 \
  -p 8083:8083 \
  -v "$(pwd)/mosquitto/config:/mosquitto/config" \
  -v "$(pwd)/mosquitto/data:/mosquitto/data" \
  eclipse-mosquitto

# 5. Kiểm tra logs
docker logs mosquitto
```

### ✅ Kết quả PHẢI thấy trong logs:

```
mosquitto version 2.0.x starting
Config loaded from /mosquitto/config/mosquitto.conf.
Opening ipv4 listen socket on port 1883.
Opening ipv6 listen socket on port 1883.
Opening websockets listen socket on port 8083.
Opening ipv6 listen socket on port 8083.
mosquitto version 2.0.x running
```

### ❌ KHÔNG được thấy:
```
Starting in local only mode
Unable to open config file
```

**Nếu thấy lỗi → Làm lại BƯỚC 3 từ đầu!**

---

## 🔌 BƯỚC 4: Setup ESP32-C3 Hardware

### 4.1. Cài đặt Arduino IDE

1. Tải Arduino IDE 2.x: https://www.arduino.cc/en/software
2. Cài ESP32 board:
   - File → Preferences → Additional Boards Manager URLs
   - Thêm: `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
   - Tools → Board → Boards Manager → Tìm "esp32" → Cài "esp32 by Espressif"

### 4.2. Cài thư viện Arduino

Sketch → Include Library → Manage Libraries, tìm và cài:
- **PubSubClient** (MQTT client)
- **ArduinoJson** (version 7.x)
- **DHT sensor library** (Adafruit)
- **Adafruit Unified Sensor**

### 4.3. Nối dây ESP32-C3

| Component | ESP32-C3 Pin |
|-----------|--------------|
| DHT11 VCC | 3.3V         |
| DHT11 DATA| GPIO2        |
| DHT11 GND | GND          |
| LED Anode (+) | GPIO8  |
| LED Cathode (-) | GND (qua điện trở 220Ω) |
| Motor IN1 | GPIO6        |
| Motor IN2 | GPIO7        |
| Motor ENA | GPIO10       |
| Motor GND | GND          |

### 4.4. Cấu hình và Upload Firmware

1. Mở file: `firmware_esp32c3/esp32c3_iot_demo/esp32c3_iot_demo.ino`

2. **Sửa WiFi và MQTT (dòng 24-29):**
   ```cpp
   const char *WIFI_SSID = "YOUR_WIFI_NAME";        // Tên WiFi của bạn
   const char *WIFI_PASSWORD = "YOUR_WIFI_PASS";    // Mật khẩu WiFi
   const char *MQTT_HOST = "192.168.1.xxx";         // IP máy tính chạy Mosquitto
   ```

3. **Lấy IP máy tính:**
   ```bash
   # Windows:
   ipconfig
   
   # Linux/Mac:
   ifconfig
   ```
   Tìm **IPv4 Address** (ví dụ: `192.168.1.100`)

4. **Upload firmware:**
   - Kết nối ESP32-C3 với máy tính
   - Tools → Board → **ESP32C3 Dev Module**
   - Tools → Port → Chọn COM port của ESP32
   - Click **Upload** (mũi tên phải)
   - Chờ "Done uploading"

5. **Kiểm tra Serial Monitor (115200 baud):**
   ```
   ✅ WiFi connected to: YOUR_WIFI
   📍 IP Address: 192.168.x.x
   ✅ MQTT connected to: 192.168.1.xxx
   🌡️  Sensor: 28.5°C, 60.0%, -45dBm
   📊 State: Light=OFF, Fan=OFF
   🟢 Online status: true
   ```

**✅ Nếu thấy `✅ MQTT connected!` → ESP32 đã kết nối thành công!**

**❌ Nếu thấy `❌ MQTT connection failed, rc=-4`:**
- Kiểm tra IP trong code có đúng không
- Chạy `docker logs mosquitto` phải thấy "Opening... port 1883"
- ESP32 và máy tính phải cùng mạng WiFi

---

## 🌐 BƯỚC 5: Chạy Web Dashboard

### Terminal mới:

```bash
cd web/src
python -m http.server 3000
```

### Mở trình duyệt:

1. Vào: http://localhost:3000
2. Nhấn **F12** mở Console
3. Phải thấy:
   ```
   Connecting to MQTT broker...
   ✅ MQTT connected
   Subscribed to: demo/room1/sensor/state
   Subscribed to: demo/room1/device/state
   Subscribed to: demo/room1/sys/online
   ```

### Kiểm tra UI:

- ✅ **Device status:** **Online** (màu xanh)
- ✅ **Temperature:** Hiển thị nhiệt độ real-time từ DHT11
- ✅ **Humidity:** Hiển thị độ ẩm real-time
- ✅ **Signal:** Hiển thị RSSI của ESP32
- ✅ **Toggle Light/Fan:** Click để bật/tắt, ESP32 phản ứng ngay

**❌ Nếu không kết nối được WebSocket:**
- Chạy `docker logs mosquitto` phải thấy "Opening websockets... port 8083"
- Kiểm tra firewall không chặn port 8083

---

## 💾 BƯỚC 6: Chạy Database Logger (Optional)

### Terminal mới:

```bash
cd database
python mqtt_logger.py
```

Phải thấy:
```
✅ Connected to MQTT broker: localhost
📊 Subscribed to demo/room1/#
```

### Xem dữ liệu đã lưu (terminal khác):

```bash
cd database
python view_database.py all
```

---

## 🔔 BƯỚC 7: Chạy Temperature Alert (Optional)

### Tạo Discord Webhook:

1. Vào Discord Server của bạn
2. Settings → Integrations → Webhooks → New Webhook
3. Đặt tên: "IoT Temperature Alert"
4. Copy Webhook URL

### Cấu hình:

Sửa file `alerts/temperature_alert.py` (dòng ~10):
```python
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/YOUR_WEBHOOK_URL"
TEMP_THRESHOLD = 30.0  # °C
```

### Chạy (terminal mới):

```bash
cd alerts
python temperature_alert.py
```

Phải thấy:
```
✅ Discord webhook test successful!
✅ Connected to MQTT broker: localhost
🌡️  Monitoring temperature threshold: 30.0°C
```

Khi nhiệt độ > 30°C, Discord sẽ nhận thông báo!

---

## 📱 BƯỚC 8: Chạy Flutter App (Optional)

```bash
cd app_flutter
flutter pub get
flutter run
```

**Lưu ý:**
- **Android Emulator:** Sửa IP thành `10.0.2.2` trong code
- **Physical Device:** Sửa IP thành IP máy tính thật

---

## ✅ Checklist hoàn thành

Kiểm tra từng bước:

- [ ] **Python packages cài đặt:** `pip list` thấy `paho-mqtt` và `requests`
- [ ] **Mosquitto container chạy:** `docker ps` thấy mosquitto với ports 1883 và 8083
- [ ] **Mosquitto config đúng:** `docker logs mosquitto` thấy "Opening... port 1883" và "port 8083"
- [ ] **KHÔNG thấy "local only mode"** trong logs
- [ ] **ESP32 kết nối WiFi:** Serial Monitor thấy `✅ WiFi connected`
- [ ] **ESP32 kết nối MQTT:** Serial Monitor thấy `✅ MQTT connected!`
- [ ] **ESP32 gửi data:** Serial Monitor thấy `🌡️ Sensor: ...` mỗi 3 giây
- [ ] **Web kết nối MQTT:** Browser Console thấy `✅ MQTT connected`
- [ ] **Web hiển thị data:** Device status **Online** (màu xanh)
- [ ] **Sensor data cập nhật:** Temperature, Humidity, Signal thay đổi real-time
- [ ] **Toggle hoạt động:** Click Light/Fan → ESP32 Serial Monitor thấy command
- [ ] **LED/Motor phản ứng:** Hardware bật/tắt theo command
- [ ] **Database lưu data:** `python view_database.py all` thấy dữ liệu
- [ ] **Alert hoạt động:** Nhiệt độ > 30°C → Discord notification

🎉 **Nếu tất cả đều ✅, hệ thống đã chạy HOÀN HẢO!**

---

## 🔧 Troubleshooting - Khắc phục lỗi

### ❌ Lỗi 1: `ModuleNotFoundError: No module named 'paho'`

**Nguyên nhân:** Chưa cài Python packages

**Giải pháp:**
```bash
pip install paho-mqtt requests
```

### ❌ Lỗi 2: ESP32 `MQTT connection failed, rc=-4`

**Nguyên nhân:** Mosquitto không cho phép kết nối từ mạng ngoài

**Giải pháp:**
```bash
# 1. Kiểm tra logs
docker logs mosquitto

# 2. Phải thấy "Opening ipv4 listen socket on port 1883"
# 3. KHÔNG được thấy "Starting in local only mode"

# 4. Nếu sai, kiểm tra file mosquitto.conf có "0.0.0.0"
Get-Content "mosquitto\config\mosquitto.conf"

# 5. Phải thấy:
# listener 1883 0.0.0.0
# listener 8083 0.0.0.0

# 6. Restart container
docker restart mosquitto
```

### ❌ Lỗi 3: Web `WebSocket connection failed`

**Nguyên nhân:** Mosquitto chưa bật WebSocket port 8083

**Giải pháp:**
```bash
# Kiểm tra logs
docker logs mosquitto

# Phải thấy "Opening websockets listen socket on port 8083"
# Nếu không, restart Mosquitto
docker restart mosquitto
```

### ❌ Lỗi 4: `Unable to open config file /mosquitto/config/mosquitto.conf`

**Nguyên nhân:** File cấu hình không tồn tại hoặc Docker không mount được

**Giải pháp:**
```powershell
# 1. Kiểm tra file tồn tại
Get-Content "mosquitto\config\mosquitto.conf"

# 2. Nếu không có, làm lại BƯỚC 3 từ đầu

# 3. Xóa container và tạo lại
docker rm -f mosquitto
# Chạy lại lệnh docker run ở BƯỚC 3
```

### ❌ Lỗi 5: DHT11 `Failed to read from DHT sensor`

**Nguyên nhân:**
- Nối dây sai
- DHT11 hỏng
- GPIO pin không đúng

**Giải pháp:**
1. Kiểm tra nối dây theo bảng ở BƯỚC 4.3
2. DHT11 cần 1-2 giây warm-up sau power on
3. Kiểm tra code `#define DHT_PIN 2` khớp với chân nối thật

### ❌ Lỗi 6: LED/Motor không hoạt động

**Nguyên nhân:**
- GPIO pins sai
- Nối dây sai
- Không có nguồn

**Giải pháp:**
1. Serial Monitor phải thấy: `📥 Command received [demo/room1/device/cmd]:`
2. Nếu thấy command nhưng không phản ứng → Kiểm tra nối dây GPIO
3. L298N cần nguồn 5V từ VIN của ESP32

---

## 📊 Thông tin hệ thống

### Cấu hình mạng:
- **Mosquitto MQTT (TCP):** `0.0.0.0:1883` - Cho ESP32, Python, Flutter native
- **Mosquitto WebSocket:** `0.0.0.0:8083` - Cho Web Dashboard
- **ESP32 Hardware:** Kết nối đến IP máy tính (VD: `192.168.1.100:1883`)
- **Web Dashboard:** `ws://localhost:8083`
- **Flutter Emulator:** `10.0.2.2:1883`
- **Flutter Physical Device:** IP máy tính thật

### MQTT Topics:
- `demo/room1/sensor/state` - Dữ liệu cảm biến (temperature, humidity, rssi)
- `demo/room1/device/state` - Trạng thái thiết bị (light, fan)
- `demo/room1/device/cmd` - Lệnh điều khiển (toggle light/fan)
- `demo/room1/sys/online` - Trạng thái online/offline

### Database Tables:
- `sensor_data` - Lịch sử nhiệt độ, độ ẩm
- `device_state` - Lịch sử trạng thái LED/Motor
- `device_online` - Lịch sử kết nối
- `commands` - Lịch sử lệnh điều khiển

---

## 🎯 Tính năng hoàn chỉnh

✅ **ESP32-C3 Real Hardware** - DHT11, LED, L298N Motor  
✅ **Real-time Sensor Data** - Nhiệt độ, độ ẩm thực từ DHT11  
✅ **Device Control** - Bật/tắt LED và motor qua MQTT  
✅ **Web Dashboard** - Monitoring real-time với WebSocket  
✅ **SQLite Database** - Logging và analytics  
✅ **Discord Temperature Alerts** - Cảnh báo khi > 30°C  
✅ **Flutter Mobile App** - Điều khiển từ xa  
✅ **Multi-network Support** - Hoạt động trên mọi WiFi 2.4GHz  
✅ **GPIO Configurable** - Dễ dàng thay đổi GPIO pins

---

## 📖 Tài liệu thêm

- **[QUICK_START.md](QUICK_START.md)** - Hướng dẫn nhanh
- **[QUICK_RUN.md](QUICK_RUN.md)** - Hướng dẫn chi tiết hardware
- **[firmware_esp32c3/ARDUINO_SETUP.md](firmware_esp32c3/ARDUINO_SETUP.md)** - Setup Arduino IDE
- **[database/README.md](database/README.md)** - Database logging
- **[alerts/README.md](alerts/README.md)** - Discord alerts

---

## 🆘 Cần trợ giúp?

1. **Kiểm tra Checklist** - Đảm bảo tất cả các bước đã làm đúng
2. **Xem Troubleshooting** - Hầu hết lỗi đã có giải pháp
3. **Kiểm tra logs:**
   - Mosquitto: `docker logs mosquitto`
   - ESP32: Serial Monitor (115200 baud)
   - Web: Browser Console (F12)
4. **Mở Issue trên GitHub** - Nếu vẫn không được

---

## 📄 License & Credits

**Original Work:** Based on nguyentrungkiet's IoT demo system  
**Original Repository:** https://github.com/nguyentrungkiet/demo_chuong4_3_1  
**Enhanced by:** EurusDFIR with hardware support, database, alerts, bug fixes

**License:** MIT License - See [LICENSE](LICENSE)

**Repository:** https://github.com/EurusDFIR/iot_lab5_monitor

---

⭐ **Star repo nếu hữu ích!** | 🐛 **Report bugs in Issues** | 💬 **Ask questions**

**Đã test thành công 100% - Follow từng bước sẽ chạy được ngay!** 🎉
