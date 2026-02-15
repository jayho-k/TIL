package com.example.rabbitmq.step4;

import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.messaging.handler.annotation.Header;
import org.springframework.messaging.handler.annotation.MessageMapping;
import org.springframework.stereotype.Controller;

@Controller
@RequiredArgsConstructor
public class NewsController {

    private final NewsPublisher newsPublisher;

    // /app/subscribe
    @MessageMapping("/subscribe") // web socket을 사용할 떄 사용하는 Mapping 어노테이션
    public void handleSubscribe(@Header("newsType") String newsType) {
        System.out.println("[#] newsType: " + newsType);

        String newsMessage = newsPublisher.publish(newsType);
        System.out.println("# newsMessage: " + newsMessage);
    }
}
