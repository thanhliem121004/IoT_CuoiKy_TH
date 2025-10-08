# 🔔 Temperature Alert System

Hệ thống cảnh báo nhiệt độ tự động gửi thông báo lên Discord khi vượt ngưỡng.

## ⚙️ Cấu hình

### Ngưỡng nhiệt độ

```python
TEMP_THRESHOLD = 30.0  # °C
```

### Discord Webhook

```python
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/..."
```

### Alert Cooldown

```python
ALERT_COOLDOWN = 300  # 5 phút
```

## 🚀 Cách sử dụng

### 1. Cài đặt thư viện

```bash
pip install requests paho-mqtt
```

### 2. Chạy Alert System

```bash
cd alerts
python temperature_alert.py
```

## 📊 Tính năng

### ✅ Cảnh báo nhiệt độ cao

- Gửi Discord notification khi nhiệt độ > 30°C
- Embed message đẹp với màu đỏ
- Hiển thị: nhiệt độ, độ ẩm, RSSI, thời gian

### ✅ Thông báo trở về bình thường

- Gửi notification khi nhiệt độ < 30°C
- Embed message màu xanh lá

### ✅ Cooldown

- Chờ 5 phút giữa các cảnh báo
- Tránh spam Discord

### ✅ Test notification

- Tự động test Discord webhook khi khởi động
- Gửi "Alert System Started" message

## 📱 Discord Notifications

### 🚨 High Temperature Alert

```
🚨 CẢNH BÁO NHIỆT ĐỘ CAO
⚠️ Nhiệt độ vượt ngưỡng 30°C

🌡️ Nhiệt độ hiện tại: 32.5°C
💧 Độ ẩm: 65%
📶 Tín hiệu: -55 dBm
⏰ Thời gian: 2025-10-06 20:45:30
```

### ✅ Normal Temperature

```
✅ NHIỆT ĐỘ TRỞ VỀ BÌNH THƯỜNG
Nhiệt độ hiện tại dưới ngưỡng 30°C

🌡️ Nhiệt độ hiện tại: 28.5°C
💧 Độ ẩm: 60%
⏰ Thời gian: 2025-10-06 20:50:00
```

## 🛠️ Tùy chỉnh

### Thay đổi ngưỡng

Mở `temperature_alert.py` và sửa:

```python
TEMP_THRESHOLD = 35.0  # Ngưỡng mới
```

### Thay đổi cooldown

```python
ALERT_COOLDOWN = 600  # 10 phút
```

### Thay đổi Discord webhook

```python
DISCORD_WEBHOOK_URL = "your_new_webhook_url"
```

## 📝 Log Output

```
╔════════════════════════════════════════════╗
║   Temperature Alert System                 ║
║   Discord Notifications                    ║
╚════════════════════════════════════════════╝
📡 MQTT Broker: localhost:1883
🔔 Discord Webhook: Configured
🌡️  Temperature Threshold: 30.0°C
⏱️  Alert Cooldown: 300 seconds
────────────────────────────────────────────

🧪 Testing Discord webhook...
✅ Discord webhook test successful!

────────────────────────────────────────────

✅ Connected to MQTT broker: localhost
📡 Subscribed to: demo/room1/sensor/state
🌡️  Monitoring temperature threshold: 30.0°C
⏱️  Alert cooldown: 300 seconds

✅ Alert system started! Press Ctrl+C to stop
────────────────────────────────────────────

🌡️  Current: 28.5°C, 55%, -50dBm → ✅ Normal
🌡️  Current: 31.2°C, 58%, -52dBm → 🚨 HIGH TEMPERATURE!
✅ Discord alert sent: 31.2°C
```

## 🔗 Integration

Hệ thống hoạt động độc lập, chỉ cần:

1. MQTT broker đang chạy
2. ESP32 hoặc simulator đang publish sensor data
3. Discord webhook hợp lệ

Không ảnh hưởng đến các component khác (Web, Flutter, Database).

## ⚡ Quick Start

```bash
# Terminal 1: MQTT Broker
docker start mosquitto

# Terminal 2: ESP32 (simulator or real)
python simulators/esp32_simulator.py

# Terminal 3: Alert System
cd alerts
python temperature_alert.py
```

## 🎯 Use Cases

- Giám sát phòng server
- Cảnh báo nhiệt độ kho hàng
- Thông báo nhiệt độ phòng thí nghiệm
- Alert hệ thống làm mát
