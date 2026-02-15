package com.example.rabbitmq.step5;

import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Component;

@Component
public class LogConsumer {

    @RabbitListener(queues = LogRabbitMQConfig.ERROR_QUEUE)
    public void consumeError(String message) {
        System.out.println("[ERROR] : " + message);
    }

    @RabbitListener(queues = LogRabbitMQConfig.WARN_QUEUE)
    public void consumeWarn(String message) {
        System.out.println("[WARN] : " + message);
    }

    @RabbitListener(queues = LogRabbitMQConfig.INFO_QUEUE)
    public void consumeInfo(String message) {
        System.out.println("[INFO] : " + message);
    }

    @RabbitListener(queues = LogRabbitMQConfig.ALL_LOG_QUEUE)
    public void consumeAll(String message) {
        System.out.println("[ALL] : " + message);
    }
}
