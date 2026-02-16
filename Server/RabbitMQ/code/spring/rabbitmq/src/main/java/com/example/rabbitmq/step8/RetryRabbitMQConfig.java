package com.example.rabbitmq.step8;

import org.springframework.amqp.core.*;
import org.springframework.amqp.rabbit.connection.ConnectionFactory;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class RetryRabbitMQConfig {
    // 큐, 교환기, 라우팅 키 이름 정의
    public static final String ORDER_COMPLETED_QUEUE = "orderCompletedQueue";
    public static final String DLQ = "deadLetterQueue";
    public static final String ORDER_TOPIC_EXCHANGE = "orderExchange";
    public static final String ORDER_TOPIC_DLX = "deadLetterExchange";
    public static final String DEAD_LETTER_ROUTING_KEY = "dead.letter";

    @Bean
    public RabbitTemplate retryRabbitTemplate(ConnectionFactory connectionFactory) {
        return new RabbitTemplate(connectionFactory);
    }

    // 원래 큐에 연결된 Topic Exchange
    @Bean
    public TopicExchange orderExchangeStep8() {
        return new TopicExchange(ORDER_TOPIC_EXCHANGE);
    }

    // Dead Letter Exchange
    @Bean
    public TopicExchange deadLetterExchange() {
        return new TopicExchange(ORDER_TOPIC_DLX);
    }

    // 원래 큐 설정
    @Bean
    public Queue orderQueueStep8() {
        return QueueBuilder.durable(ORDER_COMPLETED_QUEUE)
                .withArgument("x-dead-letter-exchange", ORDER_TOPIC_DLX) // DLX 설정
                .withArgument("x-dead-letter-routing-key", DEAD_LETTER_ROUTING_KEY) // DLQ로 이동할 라우팅 키 설정
                .build();
    }

    // Dead Letter Queue 설정
    @Bean
    public Queue deadLetterQueueStep8() {
        return QueueBuilder.durable(DLQ).build();
    }

    // 원래 큐와 Exchange 바인딩
    @Bean
    public Binding orderQueueBinding() {
        return BindingBuilder.bind(orderQueueStep8()).to(orderExchangeStep8()).with("order.completed");
    }

    // Dead Letter Queue와 Dead Letter Exchange 바인딩
    @Bean
    public Binding deadLetterQueueBinding() {
        return BindingBuilder.bind(deadLetterQueueStep8()).to(deadLetterExchange()).with(DEAD_LETTER_ROUTING_KEY);
    }

}
