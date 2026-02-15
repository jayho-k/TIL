package com.example.rabbitmq.step1;

import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.stereotype.Component;

@Component
public class Sender {
    private final RabbitTemplate rabbitTemplate;

    public Sender(@Qualifier("basicRabbitTemplate") RabbitTemplate rabbitTemplate) {
        this.rabbitTemplate = rabbitTemplate;
    }

    public void send(String message) {
        rabbitTemplate.convertAndSend(BasicRabbitMQConfig.QUEUE_NAME, message);
        System.out.println(message);
    }
}
