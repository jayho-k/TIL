package com.example.rabbitmq.step10;

import com.example.rabbitmq.entity.StockEntity;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/message")
public class TransactionController2 {

    private final MessageProducer2 messageProducer;

    public TransactionController2(MessageProducer2 messageProducer) {
        this.messageProducer = messageProducer;
    }

    @PostMapping
    public ResponseEntity<String> publishMessage(@RequestBody StockEntity stockEntity, @RequestParam boolean testCase) {
        System.out.println("Publisher Confirms Send message : " + stockEntity);

        try {
            messageProducer.sendMessage(stockEntity, testCase);
            return ResponseEntity.ok("Publisher Confirms sent successfully");
        } catch (RuntimeException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Publisher Confirms 트랜잭션 실패 : " + e.getMessage());
        }
    }
}