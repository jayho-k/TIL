package com.example.rabbitmq.step8;

import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.core.retry.RetryTemplate;
import org.springframework.core.retry.RetryException;
import org.springframework.stereotype.Component;

@Component
public class OrderConsumerStep8 {
    private final RabbitTemplate rabbitTemplate;
    private final RetryTemplate retryTemplate;

    public OrderConsumerStep8(@Qualifier("retryRabbitTemplate") RabbitTemplate rabbitTemplate, RetryTemplate retryTemplate) {
        this.rabbitTemplate = rabbitTemplate;
        this.retryTemplate = retryTemplate;
    }

    @RabbitListener(queues = RetryRabbitMQConfig.ORDER_COMPLETED_QUEUE)
    public void consume(String message) {
        try {
            retryTemplate.execute(() -> {
                System.out.println("# 리시브 메시지 : " + message);
                // 실패 조건
                if ("fail".equalsIgnoreCase(message)) {
                    throw new RuntimeException(message);
                }
                System.out.println("# message success " + message);
                return null;
            });
        } catch (RetryException e) {
            System.err.println("Retry failed after max attempts: " + e.getMessage());
        } catch (Exception e) {
            System.err.println("Execution failed: " + e.getMessage());
        }
    }

}
