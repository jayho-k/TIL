package com.example.rabbitmq.step8;

import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.stereotype.Component;

@Component
public class OrderProducerStep8 {
    private final RabbitTemplate rabbitTemplate;

    public OrderProducerStep8(@Qualifier("retryRabbitTemplate") RabbitTemplate rabbitTemplate) {
        this.rabbitTemplate = rabbitTemplate;
    }

    public void sendShipping(String message) {
        rabbitTemplate.convertAndSend(RetryRabbitMQConfig.ORDER_TOPIC_EXCHANGE, "order.completed", message);
        System.out.println("[주문 완료. 배송 지시 메시지 생성 : " + message + "]");
    }
}