package com.trandainghia.exerciser301.config;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.trandainghia.exerciser301.model.Device;
import com.trandainghia.exerciser301.model.SensorData;
import com.trandainghia.exerciser301.repository.DeviceRepository;
import com.trandainghia.exerciser301.repository.SensorDataRepository;
import org.eclipse.paho.client.mqttv3.MqttConnectOptions;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.integration.annotation.ServiceActivator;
import org.springframework.integration.channel.DirectChannel;
import org.springframework.integration.mqtt.core.DefaultMqttPahoClientFactory;
import org.springframework.integration.mqtt.core.MqttPahoClientFactory;
import org.springframework.integration.mqtt.inbound.MqttPahoMessageDrivenChannelAdapter;
import org.springframework.integration.mqtt.outbound.MqttPahoMessageHandler;
import org.springframework.messaging.MessageChannel;
import org.springframework.messaging.MessageHandler;
import org.springframework.integration.mqtt.support.MqttHeaders;

import java.time.LocalDateTime;

@Configuration
public class MqttConfig {

    @Value("${mqtt.broker}")
    private String brokerUrl;

    @Autowired
    private DeviceRepository deviceRepository;

    @Autowired
    private SensorDataRepository sensorDataRepository;

    // ---------------- MQTT client factory ----------------
    @Bean
    public MqttPahoClientFactory mqttClientFactory() {
        DefaultMqttPahoClientFactory factory = new DefaultMqttPahoClientFactory();
        MqttConnectOptions options = new MqttConnectOptions();
        options.setServerURIs(new String[] { brokerUrl });
        options.setAutomaticReconnect(true);
        options.setCleanSession(true);
        factory.setConnectionOptions(options);
        return factory;
    }

    // ---------------- Inbound ----------------
    @Bean
    public MessageChannel mqttInputChannel() {
        return new DirectChannel();
    }

    @Bean
    public MqttPahoMessageDrivenChannelAdapter inbound() {
        // Nhận tất cả topic con của /esp32/
        MqttPahoMessageDrivenChannelAdapter adapter = new MqttPahoMessageDrivenChannelAdapter(
                "spring-subscriber",
                mqttClientFactory(),
                "/esp32/#");
        adapter.setQos(1);
        adapter.setOutputChannel(mqttInputChannel());
        return adapter;
    }

    @Bean
    @ServiceActivator(inputChannel = "mqttInputChannel")
    public MessageHandler mqttInboundHandler() {
        return message -> {
            String topic = message.getHeaders().get(MqttHeaders.RECEIVED_TOPIC, String.class);
            String payload = message.getPayload().toString();
            System.out.println("📥 [MQTT-IN] " + topic + " → " + payload);

            try {
                // Chỉ xử lý topic cảm biến
                if (!topic.equalsIgnoreCase("/esp32/sensor")) {
                    System.out.println("⚙️ Bỏ qua topic không phải cảm biến: " + topic);
                    return;
                }

                // ✅ Tìm đúng thiết bị cảm biến hiện có trong DB
                Device device = deviceRepository.findByTopic("/esp32/sensor")
                        .stream()
                        .findFirst()
                        .orElse(null);

                if (device == null) {
                    System.err.println("⚠️ Không tìm thấy thiết bị có topic /esp32/sensor → Bỏ qua cập nhật!");
                    return;
                }

                // ✅ Parse dữ liệu JSON
                ObjectMapper mapper = new ObjectMapper();
                JsonNode json = mapper.readTree(payload);

                Double temp = json.has("temp") ? json.get("temp").asDouble() : null;
                Double humi = json.has("humi") ? json.get("humi").asDouble() : null;

                if (temp == null && humi == null) {
                    System.err.println("⚠️ Không có dữ liệu hợp lệ trong payload: " + payload);
                    return;
                }

                // ✅ Cập nhật thông tin thiết bị
                device.setTemperature(temp);
                device.setHumidity(humi);
                device.setLastSensorUpdate(LocalDateTime.now());
                deviceRepository.save(device);

                // ✅ Lưu lịch sử sensor_data
                SensorData data = new SensorData();
                data.setDevice(device);
                data.setTemperature(temp);
                data.setHumidity(humi);
                data.setTimestamp(LocalDateTime.now());
                sensorDataRepository.save(data);

                System.out.println("💾 Cập nhật dữ liệu cảm biến thành công cho device [" +
                        device.getName() + "] → Temp: " + temp + "°C, Humi: " + humi + "%");

            } catch (Exception e) {
                System.err.println("❌ Lỗi khi xử lý MQTT message: " + e.getMessage());
                e.printStackTrace();
            }
        };
    }

    // ---------------- Outbound ----------------
    @Bean
    public MessageChannel mqttOutboundChannel() {
        return new DirectChannel();
    }

    @Bean
    @ServiceActivator(inputChannel = "mqttOutboundChannel")
    public MessageHandler mqttOutboundHandler() {
        MqttPahoMessageHandler handler = new MqttPahoMessageHandler("spring-publisher", mqttClientFactory());
        handler.setAsync(true);
        handler.setDefaultTopic("/esp32/default");
        handler.setDefaultQos(1);
        return handler;
    }
}
