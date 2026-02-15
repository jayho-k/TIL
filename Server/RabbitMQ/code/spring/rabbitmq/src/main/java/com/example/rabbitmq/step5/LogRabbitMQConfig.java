package com.example.rabbitmq.step5;

import org.springframework.amqp.core.Binding;
import org.springframework.amqp.core.BindingBuilder;
import org.springframework.amqp.core.DirectExchange;
import org.springframework.amqp.core.Queue;
import org.springframework.amqp.rabbit.connection.ConnectionFactory;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class LogRabbitMQConfig {

    public static final String ERROR_QUEUE = "error_queue";
    public static final String WARN_QUEUE = "warn_queue";
    public static final String INFO_QUEUE = "info_queue";

    public static final String ALL_LOG_QUEUE = "all_log_queue";

    public static final String TOPIC_EXCHANGE = "topic_exchange";

    public static final String DIRECT_EXCHANGE = "direct_exchange";

    @Bean("logRabbitTemplate")
    public RabbitTemplate logRabbitTemplate(ConnectionFactory connectionFactory) {
        return new RabbitTemplate(connectionFactory);
    }

    @Bean("logDirectExchange")
    public DirectExchange logDirectExchange() {
        return new DirectExchange(DIRECT_EXCHANGE);
    }

    @Bean("logTopicExchange")
    public DirectExchange logTopicExchange() {
        return new DirectExchange(TOPIC_EXCHANGE);
    }

    @Bean("errorQueue")
    public Queue errorQueue() {
        return new Queue(ERROR_QUEUE, false);
    }

    @Bean("warnQueue")
    public Queue warnQueue() {
        return new Queue(WARN_QUEUE, false);
    }

    @Bean("infoQueue")
    public Queue infoQueue() {
        return new Queue(INFO_QUEUE, false);
    }

    @Bean("allLogQueue")
    public Queue allLogQueue() {
        return new Queue(ALL_LOG_QUEUE, false);
    }

    @Bean("errorBinding")
    public Binding errorBinding() {
        return BindingBuilder.bind(errorQueue())
//                .to(logDirectExchange())
                .to(logTopicExchange())
                .with("log.error"); // prefix 값
    }

    @Bean("warnBinding")
    public Binding warnBinding() {
        return BindingBuilder.bind(warnQueue())
//                .to(logDirectExchange())
                .to(logTopicExchange())
                .with("log.warn"); // prefix 값
    }

    @Bean("infoBinding")
    public Binding infoBinding() {
        return BindingBuilder.bind(infoQueue())
//                .to(logDirectExchange())
                .to(logTopicExchange())
                .with("log.info"); // prefix 값
    }

    @Bean("allLogBinding")
    public Binding allLogBinding() {
        return BindingBuilder.bind(allLogQueue())
                .to(logTopicExchange())
                .with("log.*"); // prefix 값
    }
}
