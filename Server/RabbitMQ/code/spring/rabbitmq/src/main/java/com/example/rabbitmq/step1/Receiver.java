package com.example.rabbitmq.step1;

import org.springframework.stereotype.Component;

@Component
public class Receiver {
    public void receiveMessage(String message) {
        System.out.println(message);
    }

}
