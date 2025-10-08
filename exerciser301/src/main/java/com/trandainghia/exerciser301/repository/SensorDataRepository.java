package com.trandainghia.exerciser301.repository;

import com.trandainghia.exerciser301.model.SensorData;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface SensorDataRepository extends JpaRepository<SensorData, Long> {
    List<SensorData> findTop20ByDeviceIdOrderByTimestampDesc(Long deviceId);
}
