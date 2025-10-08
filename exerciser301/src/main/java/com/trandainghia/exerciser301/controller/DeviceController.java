package com.trandainghia.exerciser301.controller;

import com.trandainghia.exerciser301.model.Device;
import com.trandainghia.exerciser301.model.DeviceAction;
import com.trandainghia.exerciser301.repository.DeviceActionRepository;
import com.trandainghia.exerciser301.repository.DeviceRepository;
import com.trandainghia.exerciser301.service.MqttPublisherService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/devices")
@CrossOrigin("*")
public class DeviceController {

    @Autowired
    private DeviceRepository repo;

    @Autowired
    private MqttPublisherService mqttPublisherService;

    @Autowired
    private DeviceActionRepository actionRepo;

    // ✅ Lấy danh sách tất cả thiết bị
    @GetMapping
    public List<Device> getAll() {
        return repo.findAll();
    }

    // ✅ Đăng ký thiết bị mới
    @PostMapping
    public Device create(@RequestBody Device device) {
        if (!"LED".equals(device.getType()) &&
                !"MOTOR".equals(device.getType()) &&
                !"SENSOR".equals(device.getType())) {
            throw new IllegalArgumentException("Loại thiết bị không hợp lệ (chỉ LED, MOTOR, SENSOR)");
        }
        return repo.save(device);
    }

    // ✅ Điều khiển LED ON/OFF
    @PostMapping("/{id}/led")
    public ResponseEntity<String> controlLed(@PathVariable Long id, @RequestBody Map<String, Boolean> req) {
        Device device = repo.findById(id).orElse(null);
        if (device == null) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body("Không tìm thấy thiết bị id=" + id);
        }

        Boolean onObj = req.get("on");
        if (onObj == null) {
            return ResponseEntity.badRequest().body("Thiếu tham số 'on' (true/false)");
        }

        boolean on = onObj;
        device.setLedState(on);
        repo.save(device);

        mqttPublisherService.publish(device.getTopic() + "/led", on ? "ON" : "OFF");

        DeviceAction log = new DeviceAction();
        log.setDevice(device);
        log.setAction(on ? "LED_ON" : "LED_OFF");
        actionRepo.save(log);

        return ResponseEntity.ok("LED " + (on ? "ON" : "OFF"));
    }

    // ✅ Điều khiển Motor (state = -1, 0, 1)
    @PostMapping("/{id}/motor")
    public ResponseEntity<String> controlMotor(@PathVariable Long id, @RequestBody Map<String, Integer> req) {
        Device device = repo.findById(id).orElse(null);
        if (device == null) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body("Device with id " + id + " not found");
        }

        Integer stateObj = req.get("state");
        if (stateObj == null) {
            return ResponseEntity.badRequest()
                    .body("Thiếu tham số 'state'. Gửi JSON như: {\"state\": -1|0|1}");
        }

        int state = stateObj;
        device.setMotorState(state);
        repo.save(device);

        mqttPublisherService.publish(device.getTopic() + "/motor", String.valueOf(state));

        String actionName = switch (state) {
            case -1 -> "MOTOR_REVERSE";
            case 0 -> "MOTOR_STOP";
            case 1 -> "MOTOR_FORWARD";
            default -> "MOTOR_UNKNOWN";
        };

        DeviceAction log = new DeviceAction();
        log.setDevice(device);
        log.setAction(actionName);
        actionRepo.save(log);

        return ResponseEntity.ok("Motor state: " + state);
    }

    // ✅ Xoá thiết bị theo ID (xoá luôn log nhờ cascade)
    @DeleteMapping("/{id}")
    public ResponseEntity<String> deleteDevice(@PathVariable Long id) {
        Device device = repo.findById(id).orElse(null);
        if (device == null) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body("Không tìm thấy thiết bị id=" + id);
        }

        try {
            // Gửi thông báo MQTT trước khi xoá
            mqttPublisherService.publish(device.getTopic() + "/delete", "DEVICE_DELETED");
        } catch (Exception e) {
            System.err.println("⚠️ Không gửi được MQTT khi xoá: " + e.getMessage());
        }

        // Hibernate sẽ tự động xoá tất cả DeviceAction liên quan
        repo.delete(device);

        return ResponseEntity.ok("✅ Đã xoá thiết bị id=" + id + " và toàn bộ log liên quan");
    }
}
