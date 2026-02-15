package com.example.rabbitmq.step3;

import org.springframework.messaging.handler.annotation.MessageMapping;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Controller;

@Controller
public class StompController {

    private final SimpMessagingTemplate messagingTemplate;

    public StompController(SimpMessagingTemplate messagingTemplate) {
        this.messagingTemplate = messagingTemplate;
    }

    @MessageMapping("/send")
    public void sendMessage(NotificationMessage notificationMessage) {
        // 수신된 메시지를 브로드캐스팅
        String message = notificationMessage.getMessage();

        System.out.println("[#] message = " + message);
        // 클라이언트에 메시지 브로드캐스트
        messagingTemplate.convertAndSend("/topic/notifications", message);
    }
}
