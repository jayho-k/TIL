package com.example.rabbitmq.step7;

import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/order")
@RequiredArgsConstructor
public class OrderControllerStep7 {

    private final OrderProducerStep7 orderProducer;

    @GetMapping
    public ResponseEntity<String> sendOrderMessageStep7(@RequestParam String message) {
        orderProducer.sendShpping(message);
        return ResponseEntity.ok("Order Completed Message sent: " + message);
    }
}