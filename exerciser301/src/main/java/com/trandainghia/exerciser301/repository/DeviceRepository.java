package com.trandainghia.exerciser301.repository;

import com.trandainghia.exerciser301.model.Device;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
import java.util.Optional;

public interface DeviceRepository extends JpaRepository<Device, Long> {
    List<Device> findByTopic(String topic);

    Optional<Device> findByName(String name);
}
