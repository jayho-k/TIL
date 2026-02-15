package com.example.rabbitmq.step3;

import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.stereotype.Component;

@Component
public class NotificationPublisher {

    private final RabbitTemplate rabbitTemplate;

    public NotificationPublisher(@Qualifier("notificationRabbitTemplate") RabbitTemplate rabbitTemplate) {
        this.rabbitTemplate = rabbitTemplate;
    }

    public void publish(String message) {
        rabbitTemplate.convertAndSend(RabbitMQConfig.FANOUT_EXCHANGE, "", message); // Fanout에서 routing key는 무시됨
        System.out.println("[#] Published Notification: " + message);
    }
}