package com.example.rabbitmq.step7;

import com.example.rabbitmq.step3.RabbitMQConfig;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.stereotype.Component;

@Component
public class OrderDLQConsumer {

    private final RabbitTemplate orderRabbitTemplate;

    public OrderDLQConsumer(@Qualifier("orderRabbitTemplate") RabbitTemplate orderRabbitTemplate) {
        this.orderRabbitTemplate = orderRabbitTemplate;
    }

    @RabbitListener(queues = OrderRabbitMQConfig.DLQ)
    public void process(String message) {
        System.out.println("DLQ Message Received: " + message);

        try {
            // DLQ에 들어 온 값들의 문제를 확인 >> DLQ 에러 처리로직 >> 다시 원래 OrderQueue에 보냄
            String fixMessage = "success"; // 이 부분에서 잘못된 값을 처리해주는 처리로직이 필요

            orderRabbitTemplate.convertAndSend(
                    OrderRabbitMQConfig.ORDER_EXCHANGE,
                    "order.completed.shipping",
                    fixMessage
            );
            System.out.println("DLQ Message Sent: " + fixMessage);
        } catch (Exception e) {
            System.err.println("### [DLQ Consumer Error] " + e.getMessage());
        }
    }

}
