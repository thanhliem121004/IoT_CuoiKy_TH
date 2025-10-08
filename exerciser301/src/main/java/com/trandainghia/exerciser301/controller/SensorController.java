package com.trandainghia.exerciser301.controller;

import com.trandainghia.exerciser301.model.SensorData;
import com.trandainghia.exerciser301.repository.SensorDataRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/sensors")
@CrossOrigin("*")
public class SensorController {

    @Autowired
    private SensorDataRepository repo;

    @GetMapping("/{deviceId}")
    public List<SensorData> getRecentData(@PathVariable Long deviceId) {
        return repo.findTop20ByDeviceIdOrderByTimestampDesc(deviceId);
    }
}
