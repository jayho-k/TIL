package com.example.rabbitmq.step9;

import com.example.rabbitmq.entity.StockEntity;
import com.example.rabbitmq.entity.StockRepository;
import jakarta.transaction.Transactional;
import org.springframework.amqp.rabbit.core.RabbitTemplate;

import java.time.LocalDateTime;

public class MessageProducer {
    private final StockRepository stockRepository;
    private final RabbitTemplate rabbitTemplate;


    public MessageProducer(StockRepository stockRepository, RabbitTemplate rabbitTemplate) {
        this.stockRepository = stockRepository;
        this.rabbitTemplate = rabbitTemplate;
    }

    @Transactional
    public void sendMessage(StockEntity stockEntity, String testCase) {
        rabbitTemplate.execute(channel -> {
            try {
                channel.txSelect(); // transaction start
                stockEntity.setProcessed(false);
                stockEntity.getCreatedAt(LocalDateTime.now());
                StockEntity savedStockEntity = stockRepository.save(stockEntity);

                // message publish
                rabbitTemplate.convertAndSend("transactionQueue", savedStockEntity); // 원래는 Dto 생성

                if ("fail".equalsIgnoreCase(testCase)) {
                    throw new RuntimeException("transaction error");
                }
                channel.txCommit();
                System.out.println("transaction complete");
            } catch (Exception e) {
                System.out.println("transaction fail");
                channel.txRollback();
                throw new RuntimeException("transaction rollback complete", e);
            } finally {
                if (channel != null) {
                    try {
                        channel.close();
                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                }
            }
            return null;
        });
    }


}
