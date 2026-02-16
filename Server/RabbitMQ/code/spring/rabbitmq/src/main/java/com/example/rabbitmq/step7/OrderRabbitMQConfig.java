package com.example.rabbitmq.step7;

import org.springframework.amqp.core.*;
import org.springframework.amqp.rabbit.connection.ConnectionFactory;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class OrderRabbitMQConfig {

    public static final String ORDER_COMPLETED_QUEUE = "order_completed_queue";
    public static final String ORDER_EXCHANGE = "order_exchange";
    public static final String DLQ = "deadLetterQueue";
    public static final String DLX = "deadLetterExchange";

    @Bean
    public RabbitTemplate orderRabbitTemplate(ConnectionFactory connectionFactory) {
        return new RabbitTemplate(connectionFactory);
    }

    @Bean
    public TopicExchange orderExchangeStep7() {
        return new TopicExchange(ORDER_EXCHANGE);
    }

    @Bean
    public TopicExchange deadLetterExchangeStep7() {
        return new TopicExchange(DLX);
    }

    // message가 처리되지 못했을 경우 자동으로 DLQ 이동
    @Bean
    public Queue orderQueueStep7() {
        return QueueBuilder.durable(ORDER_COMPLETED_QUEUE)
                .withArgument("x-dead-letter-exchange", DLX)
                .withArgument("x-dead-letter-routing-key",DLQ)
                .ttl(5000)
                .build();
    }

    @Bean
    public Queue deadLetterQueueStep7() {
        return new Queue(DLQ);
    }

    @Bean
    public Binding orderCompletedBidingStep7() {
        return BindingBuilder.bind(orderQueueStep7()).to(orderExchangeStep7()).with("order.completed.#");
    }

    @Bean
    public Binding deadLetterBindingStep7() {
        return BindingBuilder.bind(deadLetterQueueStep7()).to(deadLetterExchangeStep7()).with(DLQ);
    }
}
