package com.example.rabbitmq.step5;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
public class CustomExceptionHandler {
    private final LogPublisher logPublisher;

    // error log
    public void handleException(Exception e) {
        String message = e.getMessage();
        String routingKey;
        if (e instanceof NullPointerException) {
            routingKey = "log.error";
        } else if (e instanceof IllegalAccessException) {
            routingKey = "log.warn";
        } else {
            routingKey = "log.error";
        }
        logPublisher.publish(routingKey, "Exception 발생" + message);
    }

    // message
    public void handleMessage(String message) {
        String routingKey = "log.info";
        logPublisher.publish(routingKey, "Info Log : " + message);
    }

}
