package com.pratice.kafka.event;

public class MessageEvent {

    String key;
    String value;

    public MessageEvent(String key, String value) {
        this.key = key;
        this.value = value;
    }



}
