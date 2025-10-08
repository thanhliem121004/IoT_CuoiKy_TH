"""
MQTT to Database Logger
Lắng nghe MQTT messages và lưu vào SQLite database
"""

import sqlite3
import json
import time
from datetime import datetime
import paho.mqtt.client as mqtt

# =============================================================================
# CONFIGURATION
# =============================================================================

# MQTT Configuration
MQTT_BROKER = "192.168.43.218"
MQTT_PORT = 1883
MQTT_USERNAME = ""
MQTT_PASSWORD = ""
TOPIC_NS = "demo/room1"

# Database Configuration
DB_FILE = "iot_data.db"

# =============================================================================
# DATABASE SETUP
# =============================================================================

def init_database():
    """Tạo database và các bảng nếu chưa có"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Bảng sensor_data - Lưu dữ liệu cảm biến
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            device_timestamp INTEGER,
            temperature REAL,
            humidity REAL,
            lux INTEGER,
            rssi INTEGER
        )
    """)
    
    # Bảng device_state - Lưu trạng thái thiết bị
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS device_state (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            device_timestamp INTEGER,
            light TEXT,
            fan TEXT,
            rssi INTEGER
        )
    """)
    
    # Bảng device_online - Lưu trạng thái online/offline
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS device_online (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            device_timestamp INTEGER,
            online BOOLEAN,
            device_id TEXT,
            firmware TEXT,
            rssi INTEGER
        )
    """)
    
    # Bảng commands - Lưu lịch sử điều khiển
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS commands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            command_type TEXT,
            command_value TEXT,
            source TEXT
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Database initialized: " + DB_FILE)

# =============================================================================
# MQTT CALLBACKS
# =============================================================================

def on_connect(client, userdata, flags, rc):
    """Callback khi kết nối MQTT thành công"""
    if rc == 0:
        print("✅ Connected to MQTT broker: " + MQTT_BROKER)
        
        # Subscribe to all topics
        client.subscribe(f"{TOPIC_NS}/sensor/state")
        client.subscribe(f"{TOPIC_NS}/device/state")
        client.subscribe(f"{TOPIC_NS}/sys/online")
        client.subscribe(f"{TOPIC_NS}/device/cmd")
        
        print(f"📡 Subscribed to: {TOPIC_NS}/*")
    else:
        print(f"❌ Connection failed with code: {rc}")

def on_message(client, userdata, msg):
    """Callback khi nhận được message từ MQTT"""
    topic = msg.topic
    payload = msg.payload.decode()
    
    try:
        data = json.loads(payload)
        
        # Xử lý theo topic
        if topic.endswith("/sensor/state"):
            save_sensor_data(data)
        elif topic.endswith("/device/state"):
            save_device_state(data)
        elif topic.endswith("/sys/online"):
            save_online_status(data)
        elif topic.endswith("/device/cmd"):
            save_command(data)
            
    except json.JSONDecodeError:
        print(f"⚠️  Invalid JSON from {topic}: {payload}")
    except Exception as e:
        print(f"❌ Error processing message: {e}")

# =============================================================================
# DATABASE OPERATIONS
# =============================================================================

def save_sensor_data(data):
    """Lưu dữ liệu cảm biến vào database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Support both formats (simulator and real hardware)
    temperature = data.get('temperature') or data.get('temp_c')
    humidity = data.get('humidity') or data.get('hum_pct')
    lux = data.get('lux')
    rssi = data.get('rssi')
    device_timestamp = data.get('timestamp')
    
    cursor.execute("""
        INSERT INTO sensor_data (device_timestamp, temperature, humidity, lux, rssi)
        VALUES (?, ?, ?, ?, ?)
    """, (device_timestamp, temperature, humidity, lux, rssi))
    
    conn.commit()
    conn.close()
    
    print(f"🌡️  Sensor: {temperature}°C, {humidity}%, {rssi}dBm - Saved to DB")

def save_device_state(data):
    """Lưu trạng thái thiết bị vào database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    light = data.get('light')
    fan = data.get('fan')
    rssi = data.get('rssi')
    device_timestamp = data.get('timestamp')
    
    cursor.execute("""
        INSERT INTO device_state (device_timestamp, light, fan, rssi)
        VALUES (?, ?, ?, ?)
    """, (device_timestamp, light, fan, rssi))
    
    conn.commit()
    conn.close()
    
    print(f"📊 State: Light={light}, Fan={fan} - Saved to DB")

def save_online_status(data):
    """Lưu trạng thái online vào database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    online = data.get('online')
    device_id = data.get('deviceId')
    firmware = data.get('firmware')
    rssi = data.get('rssi')
    device_timestamp = data.get('timestamp')
    
    cursor.execute("""
        INSERT INTO device_online (device_timestamp, online, device_id, firmware, rssi)
        VALUES (?, ?, ?, ?, ?)
    """, (device_timestamp, online, device_id, firmware, rssi))
    
    conn.commit()
    conn.close()
    
    status = "🟢 Online" if online else "🔴 Offline"
    print(f"{status}: {device_id} - Saved to DB")

def save_command(data):
    """Lưu lệnh điều khiển vào database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Parse command
    if 'light' in data:
        cmd_type = 'light'
        cmd_value = data['light']
    elif 'fan' in data:
        cmd_type = 'fan'
        cmd_value = data['fan']
    else:
        cmd_type = 'unknown'
        cmd_value = json.dumps(data)
    
    cursor.execute("""
        INSERT INTO commands (command_type, command_value, source)
        VALUES (?, ?, ?)
    """, (cmd_type, cmd_value, 'mqtt'))
    
    conn.commit()
    conn.close()
    
    print(f"📥 Command: {cmd_type}={cmd_value} - Saved to DB")

# =============================================================================
# MAIN
# =============================================================================

def main():
    print("╔════════════════════════════════════════════╗")
    print("║   MQTT to Database Logger                  ║")
    print("╚════════════════════════════════════════════╝")
    print(f"📡 MQTT Broker: {MQTT_BROKER}:{MQTT_PORT}")
    print(f"💾 Database: {DB_FILE}")
    print(f"📊 Topic Namespace: {TOPIC_NS}")
    print("────────────────────────────────────────────")
    
    # Initialize database
    init_database()
    
    # Setup MQTT client
    client = mqtt.Client(client_id="mqtt_logger_" + str(int(time.time())))
    client.on_connect = on_connect
    client.on_message = on_message
    
    # Connect to broker
    try:
        if MQTT_USERNAME:
            client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        
        print("\n✅ Logger started! Press Ctrl+C to stop")
        print("────────────────────────────────────────────\n")
        
        # Start loop
        client.loop_forever()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Logger stopped by user")
        client.disconnect()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
