package com.pratice.kafka.event;

import com.pratice.kafka.producer.FileProducer;
import org.apache.kafka.clients.producer.Callback;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.clients.producer.RecordMetadata;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.concurrent.ExecutionException;



public class FileEventHandler implements EventHandler{

    public static final Logger logger = LoggerFactory.getLogger(FileEventHandler.class.getName());

    private KafkaProducer<String, String> kafkaProducer;
    private String topicName;
    private boolean sync;

    public FileEventHandler(KafkaProducer<String, String> kafkaProducer, String topicName, boolean sync) {
        this.kafkaProducer = kafkaProducer;
        this.topicName = topicName;
        this.sync = sync;
    }

    @Override
    public void onMessage(MessageEvent messageEvent) throws InterruptedException, ExecutionException {
        ProducerRecord<String, String> producerRecord = new ProducerRecord<>(topicName, messageEvent.key, messageEvent.value);
        if (this.sync) {
            RecordMetadata recordMetadata = this.kafkaProducer.send(producerRecord).get();
            logger.info("########record meta data ####### \n"
                    + "partition : " + recordMetadata.partition() + "\n offset : " + recordMetadata.offset());
        } else {
            kafkaProducer.send(producerRecord, (recordMetadata, e) -> {
                if (e == null) {
                    logger.info("########record meta data ####### \npartition : {}\n offset : {}", recordMetadata.partition(), recordMetadata.offset());
                } else {
                    logger.error("exception error from broker : {}", e.getMessage());
                }
            });
        }
    }
}
