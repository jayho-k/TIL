package com.pratice.kafka.producer;

import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.common.serialization.StringSerializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.Properties;

public class FileProducer {

    public static final Logger logger = LoggerFactory.getLogger(FileProducer.class.getName());
    public static void main(String[] args)  {

        String topicName = "file-topic";

        //KafkaProducer config
        Properties props = new Properties();

        // bootstrap.servers, key.serializer.class, value.serializer.class
        props.setProperty(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "192.168.56.101:9092");
        props.setProperty(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        props.setProperty(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());

        // KafkaProducer -> Record -> send() 비동기 방식 -> close
        KafkaProducer<String, String> kafkaProducer = new KafkaProducer<>(props);
        String filePath = "C:\\Users\\jayho\\Developer\\practice\\Server\\Kafka\\Core\\code\\KafkaClient\\practice\\src\\main\\resources\\pizza_sample.txt";

        sendFileMessages(kafkaProducer, topicName, filePath);

        kafkaProducer.close();
    }

    private static void sendFileMessages(KafkaProducer<String, String> kafkaProducer, String topicName, String filePath) {
        String line = "";
        final String DELIMITER = ",";
        try {
            FileReader fileReader = new FileReader(filePath);
            BufferedReader bufferedReader = new BufferedReader(fileReader);

            while ((line = bufferedReader.readLine()) != null) {
                String[] tokens = line.split(DELIMITER);
                String key = tokens[0];
                StringBuffer value = new StringBuffer();

                for (int i = 0; i < tokens.length; i++) {
                    if (i != (tokens.length - 1)) {
                        value.append(tokens[i])
                             .append(",");
                    } else {
                        value.append(tokens[i]);
                    }
                }
                sendMessage(kafkaProducer, topicName, key, value.toString());
            }
        } catch (IOException e) {
            throw new RuntimeException(e);
        }

    }

    private static void sendMessage(KafkaProducer<String, String> kafkaProducer, String topicName, String key, String value) {
        // ProducerRecord
        ProducerRecord<String, String> producerRecord = new ProducerRecord<>(topicName, key, value);

        // send
        kafkaProducer.send(producerRecord, (recordMetadata, e) -> {
            if (e == null) {
                logger.info("########record meta data ####### \npartition : {}\n offset : {}", recordMetadata.partition(), recordMetadata.offset());
            } else {
                logger.error("exception error from broker : {}", e.getMessage());
            }
        });

    }

}
