package com.example.rabbitmq.step4;

import org.springframework.amqp.core.Binding;
import org.springframework.amqp.core.BindingBuilder;
import org.springframework.amqp.core.FanoutExchange;
import org.springframework.amqp.core.Queue;
import org.springframework.amqp.rabbit.connection.ConnectionFactory;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class NewsRabbitMQConfig {

    public static final String FANOUT_EXCHANGE_FOR_NEWS = "newsExchange";

    public static final String JAVA_QUEUE = "javaQueue";
    public static final String SPRING_QUEUE = "springQueue";
    public static final String VUE_QUEUE = "vueQueue";

    @Bean("newsRabbitTemplate")
    public RabbitTemplate newsRabbitTemplate(ConnectionFactory connectionFactory) {
        return new RabbitTemplate(connectionFactory);
    }

    @Bean("javaQueue")
    public Queue javaQueue() {
        return new Queue(JAVA_QUEUE, false);
    }

    @Bean("springQueue")
    public Queue springQueue() {
        return new Queue(SPRING_QUEUE, false);
    }

    @Bean("vueQueue")
    public Queue vueQueue() {
        return new Queue(VUE_QUEUE, false);
    }

    @Bean("newsFanoutExchange")
    public FanoutExchange fanoutExchange() {
        // 메시지를 수신하면 연결된 모든 큐로 브로드캐스트
        return new FanoutExchange(FANOUT_EXCHANGE_FOR_NEWS);
    }

    @Bean("javaBinding")
    public Binding javaBinding(Queue javaQueue, FanoutExchange fanoutExchange) {
        return BindingBuilder.bind(javaQueue).to(fanoutExchange);
    }

    @Bean("SpringBinding")
    public Binding springBinding(Queue springQueue, FanoutExchange fanoutExchange) {
        return BindingBuilder.bind(springQueue).to(fanoutExchange);
    }

    @Bean("vueBinding")
    public Binding vueBinding(Queue vueQueue, FanoutExchange fanoutExchange) {
        return BindingBuilder.bind(vueQueue).to(fanoutExchange);
    }

}
