package com.trandainghia.exerciser301.model;

import com.fasterxml.jackson.annotation.JsonBackReference;
import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "device_actions")
public class DeviceAction {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // Liên kết tới thiết bị
    @ManyToOne
    @JoinColumn(name = "device_id", nullable = false)
    @JsonBackReference // 👈 Thêm dòng này để tránh vòng lặp JSON
    private Device device;

    // Hành động (LED_ON, MOTOR_FORWARD, ...)
    private String action;

    // Thời gian thực hiện
    private LocalDateTime timestamp = LocalDateTime.now();

    // --- Getters & Setters ---
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Device getDevice() {
        return device;
    }

    public void setDevice(Device device) {
        this.device = device;
    }

    public String getAction() {
        return action;
    }

    public void setAction(String action) {
        this.action = action;
    }

    public LocalDateTime getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(LocalDateTime timestamp) {
        this.timestamp = timestamp;
    }
}
