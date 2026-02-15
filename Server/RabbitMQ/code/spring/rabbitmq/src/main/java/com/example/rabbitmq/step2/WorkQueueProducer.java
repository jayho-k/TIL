package com.example.rabbitmq.step2;

import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.stereotype.Component;

@Component
public class WorkQueueProducer {
    private final RabbitTemplate rabbitTemplate;

    public WorkQueueProducer(@Qualifier("workQueueRabbitTemplate") RabbitTemplate rabbitTemplate) {
        this.rabbitTemplate = rabbitTemplate;
    }

    public void sendWorkQueue(String workQueueMessage, int duration) {
        String message = workQueueMessage + "|" + duration;
        rabbitTemplate.convertAndSend(WorkQueueRabbitMQConfig.QUEUE_NAME, message);
        System.out.println("Send work queue" + message);
    }
}
