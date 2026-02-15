package com.example.rabbitmq.step5;

import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.stereotype.Component;

@Component
public class LogPublisher {
    private final RabbitTemplate rabbitTemplate;

    public LogPublisher(@Qualifier("logRabbitTemplate") RabbitTemplate rabbitTemplate) {
        this.rabbitTemplate = rabbitTemplate;
    }

    public void publish(String routingKey, String message) {
//        rabbitTemplate.convertAndSend(LogRabbitMQConfig.DIRECT_EXCHANGE, routingKey, message);
        rabbitTemplate.convertAndSend(LogRabbitMQConfig.TOPIC_EXCHANGE, routingKey, message);
        System.out.println("message published : "+routingKey + ":" + message);
    }
}
