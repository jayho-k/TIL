package com.example.rabbitmq.step9;


import com.example.rabbitmq.entity.StockEntity;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/message")
public class TransactionController {
    private final MessageProducer messageProducer;

    public TransactionController(MessageProducer messageProducer) {
        this.messageProducer = messageProducer;
    }

    @PostMapping()
    public ResponseEntity<String> sendMessage(@RequestBody StockEntity stockEntity,
                                              @RequestParam(required = false, defaultValue = "success") String testCase) {
        // do something
        System.out.println("Send message : " + stockEntity);
        try {
            messageProducer.sendMessage(stockEntity, testCase);
            return ResponseEntity.ok("Message sent successfully");
        } catch (RuntimeException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("MQ 트랜잭션 실패 : " + e.getMessage());
        }
    }
}
