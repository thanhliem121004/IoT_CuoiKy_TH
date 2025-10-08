import 'dart:convert';
import 'dart:async';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

void main() => runApp(const MyApp());

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Exerciser 3.01',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        colorSchemeSeed: Colors.indigo,
        textTheme: const TextTheme(bodyMedium: TextStyle(fontSize: 18)),
      ),
      home: const DeviceList(),
    );
  }
}

class DeviceList extends StatefulWidget {
  const DeviceList({super.key});
  @override
  _DeviceListState createState() => _DeviceListState();
}

class _DeviceListState extends State<DeviceList> {
  final String _baseUrl = 'http://10.0.2.2:8080/api/devices';
  List<dynamic> devices = [];
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    _loadDevices();
    _timer = Timer.periodic(const Duration(seconds: 5), (_) => _loadDevices());
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  Future<void> _loadDevices() async {
    try {
      final res = await http.get(Uri.parse(_baseUrl));
      if (res.statusCode == 200) {
        setState(() {
          devices = json.decode(res.body);
        });
      } else {
        _showError('Lỗi tải thiết bị: ${res.statusCode}');
      }
    } catch (_) {
      _showError('⚠️ Không thể kết nối đến server');
    }
  }

  // === LED ===
  Future<void> _toggleLed(int id, bool on) async {
    _updateLocalDevice(id, {'ledState': on});
    try {
      final res = await http.post(
        Uri.parse('$_baseUrl/$id/led'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'on': on}),
      );
      if (res.statusCode == 200) {
        _showNotify(on ? '💡 LED đã bật' : '💤 LED đã tắt');
      } else {
        _showError('❌ Lỗi điều khiển LED');
      }
    } catch (_) {
      _showError('🚫 Không thể gửi lệnh LED');
    }
  }

  // === MOTOR ===
  Future<void> _toggleMotor(int id, int state) async {
    _updateLocalDevice(id, {'motorState': state});
    try {
      final res = await http.post(
        Uri.parse('$_baseUrl/$id/motor'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'state': state}),
      );

      if (res.statusCode == 200) {
        if (state == 1)
          _showNotify('🟩 Motor đang TIẾN');
        else if (state == -1)
          _showNotify('🟦 Motor đang LÙI');
        else
          _showNotify('⏹️ Motor đã DỪNG');
      } else {
        _showError('❌ Lỗi điều khiển motor');
      }
    } catch (_) {
      _showError('🚫 Không thể gửi lệnh motor');
    }
  }

  // === CẬP NHẬT LOCAL ===
  void _updateLocalDevice(int id, Map<String, dynamic> changes) {
    final idx = devices.indexWhere((d) => d['id'] == id);
    if (idx != -1) {
      setState(() {
        devices[idx].addAll(changes);
      });
    }
  }

  // === THÔNG BÁO ===
  void _showNotify(String msg) {
    if (!mounted) return;
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(
        SnackBar(
          content: Text(msg, style: const TextStyle(fontSize: 17)),
          backgroundColor: Colors.green.shade600,
          duration: const Duration(seconds: 2),
        ),
      );
  }

  void _showError(String msg) {
    if (!mounted) return;
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(
        SnackBar(
          content: Text(msg, style: const TextStyle(fontSize: 17)),
          backgroundColor: Colors.red.shade400,
          duration: const Duration(seconds: 3),
        ),
      );
  }

  // === GIAO DIỆN CARD ===
  Widget _buildDeviceCard(dynamic d) {
    final type = d['type'];
    return Card(
      elevation: 3,
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              d['name'] ?? 'Thiết bị',
              style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 6),
            Text(
              d['topic'] ?? '',
              style: const TextStyle(color: Colors.grey, fontSize: 16),
            ),
            const SizedBox(height: 12),
            if (type == 'LED') _buildLedControl(d),
            if (type == 'MOTOR') _buildMotorControl(d),
            if (type == 'SENSOR') _buildSensorInfo(d),
          ],
        ),
      ),
    );
  }

  Widget _buildLedControl(dynamic d) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        const Icon(Icons.lightbulb_outline, color: Colors.amber, size: 32),
        Switch.adaptive(
          value: d['ledState'] ?? false,
          onChanged: (v) => _toggleLed(d['id'], v),
          activeColor: Colors.amber,
        ),
      ],
    );
  }

  Widget _buildMotorControl(dynamic d) {
    final int state = d['motorState'] ?? 0;
    String label = '⏹️ Dừng';
    if (state == 1) label = '🟩 Tiến';
    if (state == -1) label = '🟦 Lùi';

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            const Icon(Icons.toys, color: Colors.blueAccent, size: 30),
            const SizedBox(width: 10),
            Text(
              "Trạng thái: $label",
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w500),
            ),
          ],
        ),
        const SizedBox(height: 10),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: [
            ElevatedButton.icon(
              icon: const Icon(Icons.arrow_back),
              label: const Text("Lùi"),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blue.shade300,
                padding: const EdgeInsets.symmetric(
                  horizontal: 20,
                  vertical: 12,
                ),
              ),
              onPressed: () => _toggleMotor(d['id'], -1),
            ),
            ElevatedButton.icon(
              icon: const Icon(Icons.stop_circle),
              label: const Text("Dừng"),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.grey.shade300,
                padding: const EdgeInsets.symmetric(
                  horizontal: 20,
                  vertical: 12,
                ),
              ),
              onPressed: () => _toggleMotor(d['id'], 0),
            ),
            ElevatedButton.icon(
              icon: const Icon(Icons.arrow_forward),
              label: const Text("Tiến"),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.green.shade300,
                padding: const EdgeInsets.symmetric(
                  horizontal: 20,
                  vertical: 12,
                ),
              ),
              onPressed: () => _toggleMotor(d['id'], 1),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildSensorInfo(dynamic d) {
    double temp = (d['temperature'] ?? 0).toDouble();
    double hum = (d['humidity'] ?? 0).toDouble();
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Icon(Icons.sensors, color: Colors.orange, size: 32),
        const SizedBox(height: 8),
        Text(
          '🌡️ Nhiệt độ: ${temp.toStringAsFixed(1)} °C',
          style: const TextStyle(fontSize: 18),
        ),
        Text(
          '💧 Độ ẩm: ${hum.toStringAsFixed(1)} %',
          style: const TextStyle(fontSize: 18),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    final led = devices.where((e) => e['type'] == 'LED').toList();
    final motor = devices.where((e) => e['type'] == 'MOTOR').toList();
    final sensor = devices.where((e) => e['type'] == 'SENSOR').toList();

    return DefaultTabController(
      length: 3,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('💡 Exerciser 3.01 Control'),
          bottom: const TabBar(
            tabs: [
              Tab(icon: Icon(Icons.lightbulb_outline), text: 'LED'),
              Tab(icon: Icon(Icons.directions_car), text: 'Motor'),
              Tab(icon: Icon(Icons.sensors), text: 'Cảm biến'),
            ],
          ),
          actions: [
            IconButton(
              icon: const Icon(Icons.refresh),
              onPressed: _loadDevices,
            ),
          ],
        ),
        body: TabBarView(
          children: [
            _buildDeviceList(led, 'Chưa có thiết bị LED'),
            _buildDeviceList(motor, 'Chưa có thiết bị Motor'),
            _buildDeviceList(sensor, 'Chưa có thiết bị cảm biến'),
          ],
        ),
        floatingActionButton: FloatingActionButton(
          child: const Icon(Icons.add),
          onPressed: () async {
            final ok = await Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => AddDevice(baseUrl: _baseUrl)),
            );
            if (ok == true) _loadDevices();
          },
        ),
      ),
    );
  }

  Widget _buildDeviceList(List<dynamic> list, String emptyText) {
    if (list.isEmpty) {
      return Center(
        child: Text(emptyText, style: const TextStyle(color: Colors.grey)),
      );
    }
    return ListView.builder(
      itemCount: list.length,
      itemBuilder: (_, i) => _buildDeviceCard(list[i]),
    );
  }
}

// === FORM THÊM THIẾT BỊ ===
class AddDevice extends StatefulWidget {
  final String baseUrl;
  const AddDevice({Key? key, required this.baseUrl}) : super(key: key);
  @override
  _AddDeviceState createState() => _AddDeviceState();
}

class _AddDeviceState extends State<AddDevice> {
  final _name = TextEditingController();
  final _topic = TextEditingController();
  String _type = 'LED';

  Future<void> _save() async {
    if (_name.text.isEmpty || _topic.text.isEmpty) {
      _showError('⚠️ Vui lòng nhập đầy đủ thông tin');
      return;
    }
    try {
      final res = await http.post(
        Uri.parse(widget.baseUrl),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'name': _name.text,
          'topic': _topic.text,
          'type': _type,
          'ledState': false,
          'motorState': 0,
        }),
      );
      if (res.statusCode == 200 || res.statusCode == 201) {
        Navigator.pop(context, true);
      } else {
        _showError('❌ Lỗi khi thêm: ${res.body}');
      }
    } catch (_) {
      _showError('🚫 Không thể kết nối đến backend');
    }
  }

  void _showError(String msg) {
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(SnackBar(content: Text(msg)));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('➕ Thêm thiết bị')),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            TextField(
              controller: _name,
              decoration: const InputDecoration(labelText: 'Tên thiết bị'),
            ),
            const SizedBox(height: 10),
            TextField(
              controller: _topic,
              decoration: const InputDecoration(labelText: 'MQTT Topic'),
            ),
            const SizedBox(height: 20),
            DropdownButtonFormField<String>(
              value: _type,
              items: const [
                DropdownMenuItem(value: 'LED', child: Text('Bóng đèn LED')),
                DropdownMenuItem(value: 'MOTOR', child: Text('Động cơ DC')),
                DropdownMenuItem(
                  value: 'SENSOR',
                  child: Text('Cảm biến nhiệt/ẩm'),
                ),
              ],
              onChanged: (v) => setState(() => _type = v!),
              decoration: const InputDecoration(labelText: 'Loại thiết bị'),
            ),
            const SizedBox(height: 30),
            ElevatedButton.icon(
              icon: const Icon(Icons.save),
              label: const Text('Lưu', style: TextStyle(fontSize: 18)),
              style: ElevatedButton.styleFrom(
                minimumSize: const Size.fromHeight(55),
              ),
              onPressed: _save,
            ),
          ],
        ),
      ),
    );
  }
}
