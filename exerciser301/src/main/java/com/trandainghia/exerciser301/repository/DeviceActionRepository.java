package com.trandainghia.exerciser301.repository;

import com.trandainghia.exerciser301.model.DeviceAction;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface DeviceActionRepository extends JpaRepository<DeviceAction, Long> {
    List<DeviceAction> findByDeviceId(Long deviceId);
}
