package com.example.rabbitmq.step4;

import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.stereotype.Component;

@Component
public class NewsPublisher {

    private final RabbitTemplate rabbitTemplate;
    public NewsPublisher(@Qualifier("newsRabbitTemplate") RabbitTemplate rabbitTemplate) {
        this.rabbitTemplate = rabbitTemplate;
    }

    private String publishMessage(String news, String messageSuffix) {
        String message = news + messageSuffix;
        rabbitTemplate.convertAndSend(NewsRabbitMQConfig.FANOUT_EXCHANGE_FOR_NEWS, news, message);
        System.out.println("News Published: " + message);
        return message;
    }

    public String publish(String news) {
        return publishMessage(news, " 관련 새 소식이 있어요!");
    }

    public String publishAPI(String news) {
        return publishMessage(news, " - 관련 새 소식이 나왔습니다. (API)");
    }
}
