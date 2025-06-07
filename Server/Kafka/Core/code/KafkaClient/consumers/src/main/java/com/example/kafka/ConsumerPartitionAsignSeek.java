package com.example.kafka;

import org.apache.kafka.clients.consumer.*;
import org.apache.kafka.common.TopicPartition;
import org.apache.kafka.common.errors.WakeupException;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.Duration;
import java.util.Arrays;
import java.util.Map;
import java.util.Properties;

public class ConsumerPartitionAsignSeek {

    public static final Logger logger = LoggerFactory.getLogger(ConsumerPartitionAsignSeek.class.getName());

    public static void main(String[] args) {

        String topicName = "pizza-topic";

        Properties props = new Properties();
        props.setProperty(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "192.168.56.101:9092");
        props.setProperty(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        props.setProperty(ConsumerConfig.GROUP_ID_CONFIG, "group_pizza_assign_seek_v001"); // group 이름을 바꿔야한다. 같은 그룹의 offset을 건들게 되면 offset 변화가 생기기 떄문이다.
        props.setProperty(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, "false");


        // consumer static member를 설정
        // 각 consumer 마다 값을 바꿔줘야한다.
        props.setProperty(ConsumerConfig.GROUP_INSTANCE_ID_CONFIG, "1");


        KafkaConsumer<String, String> kafkaConsumer = new KafkaConsumer<>(props);
        TopicPartition topicPartition = new TopicPartition(topicName, 0);

        //kafkaConsumer.subscribe(List.of(topicName));
        kafkaConsumer.assign(Arrays.asList(topicPartition)); // 특정 파티션만 읽기
        kafkaConsumer.seek(topicPartition, 10L); // 특정 파티션의 offset부터 읽기

        Thread mainThread = Thread.currentThread();

        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            logger.info("main program starts to exit by calling wakeup");
            kafkaConsumer.wakeup();
            try{
                // main thread 안죽고 기다리게 하기 위함
                mainThread.join();
            }catch (InterruptedException e) {
                e.printStackTrace();
            }
        }));

//        pollAutoCommit(kafkaConsumer);
        pollCommitSync(kafkaConsumer);
//        pollCommitAsync(kafkaConsumer);
        pollNoCommit(kafkaConsumer);


    }

    private static void pollNoCommit(KafkaConsumer<String, String> kafkaConsumer) {

        try {
            int loopCnt = 0;
            while (true) {
                ConsumerRecords<String, String> consumerRecords = kafkaConsumer.poll(Duration.ofMillis(1000));

                logger.info(" ############ loopCnt : {} ConsumerRecord : {} ", loopCnt++, ConsumerRecords.class);

                for (ConsumerRecord record : consumerRecords) {
                    logger.info("key : {}, val : {}, partition : {}", record.key(), record.value(), record.partition());
                }

            }
        } catch (WakeupException e) {
            logger.error("wakeup exception has been called");
        }
    }

    private static void pollCommitAsync(KafkaConsumer<String, String> kafkaConsumer) {
        try {
            int loopCnt = 0;
            while (true) {
                ConsumerRecords<String, String> consumerRecords = kafkaConsumer.poll(Duration.ofMillis(1000));

                logger.info(" ############ loopCnt : {} ConsumerRecord : {} ", loopCnt++, ConsumerRecords.class);

                for (ConsumerRecord record : consumerRecords) {
                    logger.info("key : {}, val : {}, partition : {}", record.key(), record.value(), record.partition());
                }

                kafkaConsumer.commitAsync(new OffsetCommitCallback() {
                    @Override
                    public void onComplete(Map<TopicPartition, OffsetAndMetadata> offsets, Exception exception) {
                        if (exception != null) {
                            logger.error("offset {} is not completed. error : {}", offsets, exception);
                        }
                    }
                });
            }

        } catch (WakeupException e) {
            logger.error("wakeup exception has been called");
        }finally {
            try {
                kafkaConsumer.commitSync();
            } catch (CommitFailedException e) {
            }
            finally {
                logger.info("finally conumer is closing");
                kafkaConsumer.close();
            }
        }
    }

    private static void pollCommitSync(KafkaConsumer<String, String> kafkaConsumer) {
        try {
            int loopCnt = 0;
            while (true) {
                ConsumerRecords<String, String> consumerRecords = kafkaConsumer.poll(Duration.ofMillis(1000));

                logger.info(" ############ loopCnt : {} ConsumerRecord : {} ", loopCnt++, ConsumerRecords.class);

                for (ConsumerRecord record : consumerRecords) {
                    logger.info("key : {}, val : {}, partition : {}", record.key(), record.value(), record.partition());
                }

                // poll이 batch 단위로 수행되기 때문에 여기서 commit을 찍어야한다.
                try {
                    if (consumerRecords.count() > 0) {
                        kafkaConsumer.commitSync();
                        logger.info("commit sync has been called");
                    }
                } catch (CommitFailedException e) {
                    logger.error(e.getMessage());
                }
            }

        } catch (WakeupException e) {
            logger.error("wakeup exception has been called");
        }finally {
            kafkaConsumer.close();
        }
    }

    private static void pollAutoCommit(KafkaConsumer<String, String> kafkaConsumer) {
        try {
            int loopCnt = 0;
            while (true) {
                ConsumerRecords<String, String> consumerRecords = kafkaConsumer.poll(Duration.ofMillis(1000));

                logger.info(" ############ loopCnt : {} ConsumerRecord : {} ", loopCnt++, ConsumerRecords.class);

                for (ConsumerRecord record : consumerRecords) {
                    logger.info("key : {}, val : {}, partition : {}", record.key(), record.value(), record.partition());
                    // poll로 Data를 가져와서 저장등을 수행하는 시간이 오래걸리는 작업 = Main Thread
                }
                try {
                    Thread.sleep(10000);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }

        } catch (WakeupException e) {
            logger.error("wakeup exception has been called");
        }finally {
            kafkaConsumer.close();
        }
    }

}
