package com.example.rabbitmq.step8;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.resilience.annotation.EnableResilientMethods;
import org.springframework.core.retry.RetryPolicy;
import org.springframework.core.retry.RetryTemplate;
import java.time.Duration;

@Configuration
@EnableResilientMethods
public class RetryConfig {

    @Bean
    public RetryTemplate retryTemplate() {
        // Spring Boot 4 (Spring Framework 7) builder pattern
        // maxRetries(2) means 1 initial + 2 retries = 3 total attempts
        RetryPolicy retryPolicy = RetryPolicy.builder()
                .maxRetries(2)
                .delay(Duration.ofMillis(1000))
                .build();

        RetryTemplate retryTemplate = new RetryTemplate();
        retryTemplate.setRetryPolicy(retryPolicy);

        return retryTemplate;
    }
}
