package com.example.rabbitmq.step8;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/step8/order")
public class OrderControllerStep8 {

    private final OrderProducerStep8 orderProducer;

    public OrderControllerStep8(OrderProducerStep8 orderProducer) {
        this.orderProducer = orderProducer;
    }

    @GetMapping
    public ResponseEntity<String> sendOrderMessageStep8(@RequestParam String message) {

        orderProducer.sendShipping(message);
        return ResponseEntity.ok("Order Completed Message sent: " + message);
    }
}