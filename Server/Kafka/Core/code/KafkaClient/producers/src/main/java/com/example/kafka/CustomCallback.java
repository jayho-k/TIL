package com.example.kafka;

import org.apache.kafka.clients.producer.Callback;
import org.apache.kafka.clients.producer.RecordMetadata;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class CustomCallback implements Callback {

    public static final Logger logger = LoggerFactory.getLogger(CustomCallback.class.getName());

    private int seq;
    public CustomCallback(int seq) {
        this.seq = seq;
    }

    @Override
    public void onCompletion(RecordMetadata recordMetadata, Exception e) {

        if (e == null) {
            logger.info("seq:{} partition:{} offset:{}",this.seq, recordMetadata.partition(), recordMetadata.offset());
        } else {
            logger.error("exception error from broker : {}", e.getMessage());
        }
    }
}
