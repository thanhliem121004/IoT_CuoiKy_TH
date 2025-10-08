"""
Database Viewer - Xem dữ liệu từ SQLite database
"""

import sqlite3
from datetime import datetime, timedelta
import sys

DB_FILE = "iot_data.db"

def print_header(title):
    """In header đẹp"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def view_sensor_data(limit=20):
    """Xem dữ liệu cảm biến gần nhất"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT timestamp, temperature, humidity, lux, rssi
        FROM sensor_data
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    print_header(f"🌡️  SENSOR DATA (Latest {limit} records)")
    print(f"{'Time':<20} {'Temp (°C)':<12} {'Humidity (%)':<15} {'Lux':<10} {'RSSI (dBm)':<12}")
    print("-"*80)
    
    for row in rows:
        timestamp, temp, hum, lux, rssi = row
        lux_str = str(lux) if lux else "N/A"
        rssi_str = str(rssi) if rssi else "N/A"
        print(f"{timestamp:<20} {temp:<12.1f} {hum:<15.1f} {lux_str:<10} {rssi_str:<12}")
    
    print(f"\nTotal records: {len(rows)}")

def view_device_state(limit=20):
    """Xem trạng thái thiết bị"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT timestamp, light, fan, rssi
        FROM device_state
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    print_header(f"💡 DEVICE STATE (Latest {limit} records)")
    print(f"{'Time':<20} {'Light':<10} {'Fan':<10} {'RSSI (dBm)':<12}")
    print("-"*80)
    
    for row in rows:
        timestamp, light, fan, rssi = row
        rssi_str = str(rssi) if rssi else "N/A"
        print(f"{timestamp:<20} {light:<10} {fan:<10} {rssi_str:<12}")
    
    print(f"\nTotal records: {len(rows)}")

def view_online_status(limit=10):
    """Xem lịch sử online/offline"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT timestamp, online, device_id, firmware, rssi
        FROM device_online
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    print_header(f"🟢 ONLINE STATUS (Latest {limit} records)")
    print(f"{'Time':<20} {'Status':<10} {'Device ID':<20} {'Firmware':<20} {'RSSI':<10}")
    print("-"*80)
    
    for row in rows:
        timestamp, online, device_id, firmware, rssi = row
        status = "🟢 Online" if online else "🔴 Offline"
        device_id = device_id or "N/A"
        firmware = firmware or "N/A"
        rssi_str = str(rssi) if rssi else "N/A"
        print(f"{timestamp:<20} {status:<10} {device_id:<20} {firmware:<20} {rssi_str:<10}")
    
    print(f"\nTotal records: {len(rows)}")

def view_commands(limit=20):
    """Xem lịch sử lệnh điều khiển"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT timestamp, command_type, command_value, source
        FROM commands
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    print_header(f"📥 COMMAND HISTORY (Latest {limit} records)")
    print(f"{'Time':<20} {'Type':<15} {'Value':<15} {'Source':<10}")
    print("-"*80)
    
    for row in rows:
        timestamp, cmd_type, cmd_value, source = row
        print(f"{timestamp:<20} {cmd_type:<15} {cmd_value:<15} {source:<10}")
    
    print(f"\nTotal records: {len(rows)}")

def view_statistics():
    """Xem thống kê tổng quan"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    print_header("📊 DATABASE STATISTICS")
    
    # Count records in each table
    cursor.execute("SELECT COUNT(*) FROM sensor_data")
    sensor_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM device_state")
    state_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM device_online")
    online_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM commands")
    cmd_count = cursor.fetchone()[0]
    
    print(f"📊 Total Records:")
    print(f"  • Sensor Data:    {sensor_count:>8}")
    print(f"  • Device State:   {state_count:>8}")
    print(f"  • Online Status:  {online_count:>8}")
    print(f"  • Commands:       {cmd_count:>8}")
    
    # Average temperature and humidity (last 24 hours)
    cursor.execute("""
        SELECT AVG(temperature), AVG(humidity), MIN(temperature), MAX(temperature)
        FROM sensor_data
        WHERE timestamp > datetime('now', '-24 hours')
    """)
    row = cursor.fetchone()
    if row[0]:
        avg_temp, avg_hum, min_temp, max_temp = row
        print(f"\n🌡️  Last 24 Hours:")
        print(f"  • Avg Temperature: {avg_temp:>6.1f}°C")
        print(f"  • Min Temperature: {min_temp:>6.1f}°C")
        print(f"  • Max Temperature: {max_temp:>6.1f}°C")
        print(f"  • Avg Humidity:    {avg_hum:>6.1f}%")
    
    # Device uptime percentage (last 24 hours)
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN online = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as uptime_pct
        FROM device_online
        WHERE timestamp > datetime('now', '-24 hours')
    """)
    row = cursor.fetchone()
    if row[0]:
        uptime = row[0]
        print(f"\n🟢 Device Uptime (24h): {uptime:.1f}%")
    
    conn.close()

def interactive_menu():
    """Menu tương tác"""
    while True:
        print("\n" + "="*80)
        print("  📊 IoT DATABASE VIEWER")
        print("="*80)
        print("\n[1] View Sensor Data")
        print("[2] View Device State")
        print("[3] View Online Status")
        print("[4] View Command History")
        print("[5] View Statistics")
        print("[6] View All")
        print("[0] Exit")
        
        choice = input("\nSelect option (0-6): ").strip()
        
        if choice == '1':
            limit = input("How many records? (default 20): ").strip() or "20"
            view_sensor_data(int(limit))
        elif choice == '2':
            limit = input("How many records? (default 20): ").strip() or "20"
            view_device_state(int(limit))
        elif choice == '3':
            limit = input("How many records? (default 10): ").strip() or "10"
            view_online_status(int(limit))
        elif choice == '4':
            limit = input("How many records? (default 20): ").strip() or "20"
            view_commands(int(limit))
        elif choice == '5':
            view_statistics()
        elif choice == '6':
            view_statistics()
            view_sensor_data(10)
            view_device_state(10)
            view_online_status(5)
            view_commands(10)
        elif choice == '0':
            print("\n👋 Goodbye!")
            break
        else:
            print("❌ Invalid option!")

def main():
    """Main function"""
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.close()
    except Exception as e:
        print(f"❌ Cannot open database: {e}")
        print(f"Make sure '{DB_FILE}' exists. Run mqtt_logger.py first!")
        return
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == 'sensor':
            view_sensor_data()
        elif cmd == 'state':
            view_device_state()
        elif cmd == 'online':
            view_online_status()
        elif cmd == 'commands':
            view_commands()
        elif cmd == 'stats':
            view_statistics()
        elif cmd == 'all':
            view_statistics()
            view_sensor_data(10)
            view_device_state(10)
            view_online_status(5)
            view_commands(10)
        else:
            print("Usage: python view_database.py [sensor|state|online|commands|stats|all]")
    else:
        interactive_menu()

if __name__ == "__main__":
    main()
