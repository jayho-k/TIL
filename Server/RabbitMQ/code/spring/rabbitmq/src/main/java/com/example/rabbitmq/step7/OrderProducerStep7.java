package com.example.rabbitmq.step7;

import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.stereotype.Component;

@Component
public class OrderProducerStep7 {

    private final RabbitTemplate orderRabbitTemplate;

    public OrderProducerStep7(@Qualifier("orderRabbitTemplate") RabbitTemplate orderRabbitTemplate) {
        this.orderRabbitTemplate = orderRabbitTemplate;
    }

    public void sendShpping(String message) {

        orderRabbitTemplate.convertAndSend(
                OrderRabbitMQConfig.ORDER_EXCHANGE,
                "order.completed.shipping",
                message);
        System.out.println("[주문 완료. 배송 지시 메시지 생성 : " + message + "]");
    }
}