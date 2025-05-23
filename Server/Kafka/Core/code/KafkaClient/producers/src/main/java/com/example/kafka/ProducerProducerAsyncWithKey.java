package com.example.kafka;

import org.apache.kafka.clients.producer.*;
import org.apache.kafka.common.serialization.StringSerializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Properties;

public class ProducerProducerAsyncWithKey {

    public static final Logger logger = LoggerFactory.getLogger(ProducerProducerAsyncWithKey.class.getName());
    public static void main(String[] args)  {

        String topicName = "multipart-topic";

        //KafkaProducer config
        Properties props = new Properties();

        // bootstrap.servers, key.serializer.class, value.serializer.class
        props.setProperty(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "192.168.56.101:9092");
        props.setProperty(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        props.setProperty(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());

        // KafkaProducer
        KafkaProducer<String, String> kafkaProducer = new KafkaProducer<>(props);

        // ProducerRecord
        for (int seq = 0; seq < 20; seq++) {
            ProducerRecord<String, String> producerRecord = new ProducerRecord<>(topicName, String.valueOf(seq), "hello world "+seq);

            // send
            kafkaProducer.send(producerRecord, (recordMetadata, e) -> {
                if (e == null) {
                    logger.info("########record meta data ####### \npartition : {}\n offset : {}", recordMetadata.partition(), recordMetadata.offset());
                } else {
                    logger.error("exception error from broker : {}", e.getMessage());
                }
            });
        }



        try {
            Thread.sleep(3000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }

        kafkaProducer.close();
    }
}
