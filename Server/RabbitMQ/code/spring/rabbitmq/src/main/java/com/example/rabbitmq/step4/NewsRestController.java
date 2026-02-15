package com.example.rabbitmq.step4;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/news/api")
public class NewsRestController {
    private final NewsPublisher newsPublisher;

    public NewsRestController(NewsPublisher newsPublisher) {
        this.newsPublisher = newsPublisher;
    }

    @PostMapping("/publish")
    public ResponseEntity<String> publishNews(@RequestParam String newsType) {
        String result = newsPublisher.publishAPI(newsType);
        return ResponseEntity.ok("# Message published to RabbitMQ: " + result);
    }
}

