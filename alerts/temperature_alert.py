"""
Temperature Alert System - Discord Notifications
Theo dõi nhiệt độ từ MQTT và gửi cảnh báo qua Discord khi vượt ngưỡng
"""

import json
import time
from datetime import datetime
import paho.mqtt.client as mqtt
import requests

# =============================================================================
# CONFIGURATION
# =============================================================================

# MQTT Configuration
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_USERNAME = ""
MQTT_PASSWORD = ""
TOPIC_SENSOR = "demo/room1/sensor/state"

# Discord Webhook Configuration
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1417028997149102136/n54VbIoLlu5rVNeQMffJNCEQiwGULGTMa_1BBvylhoLyfXJNmFY6rQ9zB0wTdY6nKrFM"

# Alert Configuration
TEMP_THRESHOLD = 30.0  # Ngưỡng nhiệt độ (°C)
ALERT_COOLDOWN = 300   # Thời gian chờ giữa các cảnh báo (5 phút = 300 giây)

# =============================================================================
# GLOBAL VARIABLES
# =============================================================================

last_alert_time = 0
alert_active = False

# =============================================================================
# DISCORD FUNCTIONS
# =============================================================================

def send_discord_alert(temperature, humidity, rssi):
    """Gửi cảnh báo lên Discord"""
    global last_alert_time
    
    current_time = time.time()
    
    # Kiểm tra cooldown (tránh spam)
    if current_time - last_alert_time < ALERT_COOLDOWN:
        print(f"⏳ Cooldown active, skipping alert (wait {ALERT_COOLDOWN - (current_time - last_alert_time):.0f}s)")
        return
    
    # Tạo embed message đẹp cho Discord
    embed = {
        "title": "🚨 CẢNH BÁO NHIỆT ĐỘ CAO",
        "description": f"⚠️ Nhiệt độ vượt ngưỡng **{TEMP_THRESHOLD}°C**",
        "color": 16711680,  # Màu đỏ
        "fields": [
            {
                "name": "🌡️ Nhiệt độ hiện tại",
                "value": f"**{temperature}°C**",
                "inline": True
            },
            {
                "name": "💧 Độ ẩm",
                "value": f"{humidity}%",
                "inline": True
            },
            {
                "name": "📶 Tín hiệu",
                "value": f"{rssi} dBm",
                "inline": True
            },
            {
                "name": "⏰ Thời gian",
                "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "inline": False
            }
        ],
        "footer": {
            "text": "IoT Temperature Alert System"
        },
        "timestamp": datetime.utcnow().isoformat()
    }
    
    payload = {
        "username": "IoT Alert Bot",
        "avatar_url": "https://cdn-icons-png.flaticon.com/512/3093/3093173.png",
        "embeds": [embed]
    }
    
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        
        if response.status_code == 204:
            print(f"✅ Discord alert sent: {temperature}°C")
            last_alert_time = current_time
        else:
            print(f"❌ Failed to send Discord alert: {response.status_code}")
            print(f"   Response: {response.text}")
    
    except Exception as e:
        print(f"❌ Error sending Discord alert: {e}")

def send_discord_normal(temperature, humidity):
    """Gửi thông báo nhiệt độ đã trở về bình thường"""
    embed = {
        "title": "✅ NHIỆT ĐỘ TRỞ VỀ BÌNH THƯỜNG",
        "description": f"Nhiệt độ hiện tại dưới ngưỡng {TEMP_THRESHOLD}°C",
        "color": 65280,  # Màu xanh lá
        "fields": [
            {
                "name": "🌡️ Nhiệt độ hiện tại",
                "value": f"**{temperature}°C**",
                "inline": True
            },
            {
                "name": "💧 Độ ẩm",
                "value": f"{humidity}%",
                "inline": True
            },
            {
                "name": "⏰ Thời gian",
                "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "inline": False
            }
        ],
        "footer": {
            "text": "IoT Temperature Alert System"
        },
        "timestamp": datetime.utcnow().isoformat()
    }
    
    payload = {
        "username": "IoT Alert Bot",
        "avatar_url": "https://cdn-icons-png.flaticon.com/512/3093/3093173.png",
        "embeds": [embed]
    }
    
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        
        if response.status_code == 204:
            print(f"✅ Discord normal notification sent: {temperature}°C")
        else:
            print(f"❌ Failed to send Discord notification: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error sending Discord notification: {e}")

# =============================================================================
# MQTT CALLBACKS
# =============================================================================

def on_connect(client, userdata, flags, rc):
    """Callback khi kết nối MQTT thành công"""
    if rc == 0:
        print("✅ Connected to MQTT broker: " + MQTT_BROKER)
        
        # Subscribe to sensor topic
        client.subscribe(TOPIC_SENSOR)
        print(f"📡 Subscribed to: {TOPIC_SENSOR}")
        print(f"🌡️  Monitoring temperature threshold: {TEMP_THRESHOLD}°C")
        print(f"⏱️  Alert cooldown: {ALERT_COOLDOWN} seconds")
    else:
        print(f"❌ Connection failed with code: {rc}")

def on_message(client, userdata, msg):
    """Callback khi nhận được message từ MQTT"""
    global alert_active
    
    try:
        data = json.loads(msg.payload.decode())
        
        # Lấy dữ liệu sensor (support cả simulator và real hardware)
        temperature = data.get('temperature') or data.get('temp_c')
        humidity = data.get('humidity') or data.get('hum_pct')
        rssi = data.get('rssi')
        
        if temperature is None:
            return
        
        # Hiển thị dữ liệu hiện tại
        print(f"🌡️  Current: {temperature}°C, {humidity}%, {rssi}dBm", end="")
        
        # Kiểm tra ngưỡng nhiệt độ
        if temperature > TEMP_THRESHOLD:
            print(f" → 🚨 HIGH TEMPERATURE!")
            if not alert_active:
                send_discord_alert(temperature, humidity, rssi)
                alert_active = True
        else:
            print(f" → ✅ Normal")
            if alert_active:
                # Nhiệt độ đã trở về bình thường
                send_discord_normal(temperature, humidity)
                alert_active = False
    
    except json.JSONDecodeError:
        print(f"⚠️  Invalid JSON: {msg.payload.decode()}")
    except Exception as e:
        print(f"❌ Error processing message: {e}")

# =============================================================================
# MAIN
# =============================================================================

def main():
    print("╔════════════════════════════════════════════╗")
    print("║   Temperature Alert System                 ║")
    print("║   Discord Notifications                    ║")
    print("╚════════════════════════════════════════════╝")
    print(f"📡 MQTT Broker: {MQTT_BROKER}:{MQTT_PORT}")
    print(f"🔔 Discord Webhook: Configured")
    print(f"🌡️  Temperature Threshold: {TEMP_THRESHOLD}°C")
    print(f"⏱️  Alert Cooldown: {ALERT_COOLDOWN} seconds")
    print("────────────────────────────────────────────")
    
    # Test Discord webhook
    print("\n🧪 Testing Discord webhook...")
    test_embed = {
        "title": "🚀 Alert System Started",
        "description": f"Temperature monitoring active with threshold: **{TEMP_THRESHOLD}°C**",
        "color": 3447003,  # Màu xanh dương
        "fields": [
            {
                "name": "Status",
                "value": "✅ Online",
                "inline": True
            },
            {
                "name": "MQTT Broker",
                "value": f"{MQTT_BROKER}:{MQTT_PORT}",
                "inline": True
            }
        ],
        "footer": {
            "text": "IoT Temperature Alert System"
        },
        "timestamp": datetime.utcnow().isoformat()
    }
    
    test_payload = {
        "username": "IoT Alert Bot",
        "avatar_url": "https://cdn-icons-png.flaticon.com/512/3093/3093173.png",
        "embeds": [test_embed]
    }
    
    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=test_payload)
        if response.status_code == 204:
            print("✅ Discord webhook test successful!")
        else:
            print(f"⚠️  Discord webhook test failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Discord webhook test error: {e}")
    
    print("\n────────────────────────────────────────────")
    
    # Setup MQTT client
    client = mqtt.Client(client_id="temp_alert_" + str(int(time.time())))
    client.on_connect = on_connect
    client.on_message = on_message
    
    # Connect to broker
    try:
        if MQTT_USERNAME:
            client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        
        print("\n✅ Alert system started! Press Ctrl+C to stop")
        print("────────────────────────────────────────────\n")
        
        # Start loop
        client.loop_forever()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Alert system stopped by user")
        client.disconnect()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
