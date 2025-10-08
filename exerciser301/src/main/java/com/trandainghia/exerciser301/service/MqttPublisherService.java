// src/main/java/com/trandainghia/exerciser301/service/MqttPublisherService.java
package com.trandainghia.exerciser301.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.integration.mqtt.support.MqttHeaders;
import org.springframework.integration.support.MessageBuilder;
import org.springframework.messaging.MessageChannel;
import org.springframework.stereotype.Service;

@Service
public class MqttPublisherService {

    @Autowired
    @Qualifier("mqttOutboundChannel")
    private MessageChannel mqttOutboundChannel;

    public void publish(String topic, String payload) {
        try {
            System.out.println("📤 [MQTT OUT] " + topic + " → " + payload);
            mqttOutboundChannel.send(
                    MessageBuilder.withPayload(payload)
                            .setHeader(MqttHeaders.TOPIC, topic)
                            .setHeader(MqttHeaders.QOS, 1)
                            .build());
        } catch (Exception e) {
            System.err.println("❌ [MQTT ERROR] " + e.getMessage());
        }
    }
}
