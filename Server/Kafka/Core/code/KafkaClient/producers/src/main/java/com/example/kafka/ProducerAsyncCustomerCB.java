package com.example.kafka;

import org.apache.kafka.clients.producer.Callback;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.common.serialization.IntegerSerializer;
import org.apache.kafka.common.serialization.StringSerializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Properties;

public class ProducerAsyncCustomerCB {

    public static final Logger logger = LoggerFactory.getLogger(ProducerAsyncCustomerCB.class.getName());
    public static void main(String[] args)  {

        String topicName = "multipart-topic";

        //KafkaProducer config
        Properties props = new Properties();

        // bootstrap.servers, key.serializer.class, value.serializer.class
        props.setProperty(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "192.168.56.101:9092");
        props.setProperty(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, IntegerSerializer.class.getName());
        props.setProperty(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());

        // KafkaProducer
        KafkaProducer<Integer, String> kafkaProducer = new KafkaProducer<>(props);

        // ProducerRecord
        for (int seq = 0; seq < 20; seq++) {
            ProducerRecord<Integer, String> producerRecord = new ProducerRecord<>(topicName, seq, "hello world "+seq);

            // send
            kafkaProducer.send(producerRecord, new CustomCallback(seq));
        }

        try {
            Thread.sleep(3000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }

        kafkaProducer.close();
    }
}
