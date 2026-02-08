package com.example.rabbitmq.step2;

import org.springframework.stereotype.Component;

@Component
public class WorkQueueConsumer {

    public void workQueueTask(String message) {
        String[] messageParts = message.split("\\|");
        String originMessage = messageParts[0];

        int duration = Integer.parseInt(messageParts[1]);

        System.out.println(originMessage + " | " + duration);

        try {
            System.out.println(duration);
            Thread.sleep(duration);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }

        System.out.println("Complete : " + originMessage);
    }
}
