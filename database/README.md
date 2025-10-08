# 💾 IoT Database System

Hệ thống lưu trữ và xem dữ liệu IoT sử dụng SQLite database.

## 📊 Database Schema

### Bảng `sensor_data` - Dữ liệu cảm biến

- `id`: Primary key
- `timestamp`: Thời gian lưu
- `temperature`: Nhiệt độ (°C)
- `humidity`: Độ ẩm (%)
- `lux`: Ánh sáng (lux)
- `rssi`: Cường độ tín hiệu (dBm)

### Bảng `device_state` - Trạng thái thiết bị

- `id`: Primary key
- `timestamp`: Thời gian lưu
- `light`: Trạng thái đèn (on/off)
- `fan`: Trạng thái quạt (on/off)
- `rssi`: Cường độ tín hiệu (dBm)

### Bảng `device_online` - Trạng thái kết nối

- `id`: Primary key
- `timestamp`: Thời gian lưu
- `online`: Online/Offline (true/false)
- `device_id`: ID thiết bị
- `firmware`: Phiên bản firmware
- `rssi`: Cường độ tín hiệu (dBm)

### Bảng `commands` - Lịch sử điều khiển

- `id`: Primary key
- `timestamp`: Thời gian lưu
- `command_type`: Loại lệnh (light/fan)
- `command_value`: Giá trị lệnh (on/off/toggle)
- `source`: Nguồn lệnh (mqtt/web/app)

## 🚀 Cách sử dụng

### 1. Khởi động MQTT Logger (Terminal 1)

```bash
cd database
python mqtt_logger.py
```

Logger sẽ:

- Tự động tạo database `iot_data.db`
- Lắng nghe tất cả MQTT messages
- Lưu dữ liệu vào SQLite database
- Hiển thị log real-time

### 2. Xem dữ liệu (Terminal 2)

**Interactive Menu:**

```bash
python view_database.py
```

**Command Line:**

```bash
# Xem dữ liệu cảm biến
python view_database.py sensor

# Xem trạng thái thiết bị
python view_database.py state

# Xem trạng thái online
python view_database.py online

# Xem lịch sử lệnh
python view_database.py commands

# Xem thống kê
python view_database.py stats

# Xem tất cả
python view_database.py all
```

## 📈 Ví dụ Output

### Sensor Data:

```
🌡️  SENSOR DATA (Latest 20 records)
Time                 Temp (°C)    Humidity (%)    Lux        RSSI (dBm)
--------------------------------------------------------------------------------
2025-10-06 10:30:45  32.0         55.0            N/A        -50
2025-10-06 10:30:42  32.0         55.0            N/A        -51
```

### Statistics:

```
📊 DATABASE STATISTICS
📊 Total Records:
  • Sensor Data:      1234
  • Device State:      456
  • Online Status:      89
  • Commands:          123

🌡️  Last 24 Hours:
  • Avg Temperature:   31.5°C
  • Min Temperature:   28.0°C
  • Max Temperature:   35.0°C
  • Avg Humidity:      56.2%

🟢 Device Uptime (24h): 98.5%
```

## 🛠️ Truy vấn Database trực tiếp

Sử dụng SQLite CLI:

```bash
sqlite3 iot_data.db

# Các query mẫu:
SELECT * FROM sensor_data ORDER BY id DESC LIMIT 10;
SELECT AVG(temperature) FROM sensor_data WHERE timestamp > datetime('now', '-1 hour');
SELECT COUNT(*) FROM commands WHERE command_type = 'light';
```

## 🔄 Backup Database

```bash
# Backup
cp iot_data.db iot_data_backup_$(date +%Y%m%d).db

# Restore
cp iot_data_backup_20251006.db iot_data.db
```

## 📝 Notes

- Database file: `iot_data.db` (SQLite)
- Tự động tạo tables nếu chưa có
- Hỗ trợ cả simulator và real hardware
- Real-time logging
- Historical data analysis
