package com.example.rabbitmq.step9;

import com.example.rabbitmq.entity.StockEntity;
import com.example.rabbitmq.entity.StockRepository;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;

@Component
public class MessageConsumer {
    private final StockRepository stockRepository;

    public MessageConsumer(StockRepository stockRepository) {
        this.stockRepository = stockRepository;
    }

    @RabbitListener(queues = "transactionQueue")
    public void receiveTransaction(StockEntity stockEntity) {
        System.out.println("receive message");
        try {
            stockEntity.setProcessed(true);
            stockEntity.setUpdatedAt(LocalDateTime.now());
            stockRepository.save(stockEntity);
            System.out.println("save complete");
        } catch (Exception e) {
            System.out.println("error");
            throw e; // 원래는 여기에 DLQ 로직이 들어가게 되어야함
        }
    }
}
