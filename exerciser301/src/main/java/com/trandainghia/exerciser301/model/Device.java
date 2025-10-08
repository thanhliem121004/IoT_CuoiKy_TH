package com.trandainghia.exerciser301.model;

import com.fasterxml.jackson.annotation.JsonManagedReference;
import jakarta.persistence.*;
import java.time.LocalDateTime;
import java.util.List;

@Entity
@Table(name = "devices")
public class Device {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String name;
    private String topic;
    private String type; // "LED", "MOTOR", "SENSOR"

    @Column(name = "led_state", nullable = false)
    private boolean ledState = false;

    @Column(name = "motor_state", nullable = false)
    private int motorState = 0;

    private Double temperature;
    private Double humidity;
    private LocalDateTime lastSensorUpdate;

    // 🔹 Quan hệ 1-n với DeviceAction
    @OneToMany(mappedBy = "device", cascade = CascadeType.ALL, orphanRemoval = true)
    @JsonManagedReference // 👈 Thêm dòng này để tránh vòng lặp JSON
    private List<DeviceAction> actions;

    // --- Getters & Setters ---
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getTopic() {
        return topic;
    }

    public void setTopic(String topic) {
        this.topic = topic;
    }

    public String getType() {
        return type;
    }

    public void setType(String type) {
        this.type = type;
    }

    public boolean isLedState() {
        return ledState;
    }

    public void setLedState(boolean ledState) {
        this.ledState = ledState;
    }

    public int getMotorState() {
        return motorState;
    }

    public void setMotorState(int motorState) {
        this.motorState = motorState;
    }

    public Double getTemperature() {
        return temperature;
    }

    public void setTemperature(Double temperature) {
        this.temperature = temperature;
    }

    public Double getHumidity() {
        return humidity;
    }

    public void setHumidity(Double humidity) {
        this.humidity = humidity;
    }

    public LocalDateTime getLastSensorUpdate() {
        return lastSensorUpdate;
    }

    public void setLastSensorUpdate(LocalDateTime lastSensorUpdate) {
        this.lastSensorUpdate = lastSensorUpdate;
    }

    public List<DeviceAction> getActions() {
        return actions;
    }

    public void setActions(List<DeviceAction> actions) {
        this.actions = actions;
    }
}
