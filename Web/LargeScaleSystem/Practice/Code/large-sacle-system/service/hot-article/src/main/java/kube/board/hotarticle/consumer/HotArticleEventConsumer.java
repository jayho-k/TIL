package kube.board.hotarticle.consumer;

import kube.board.common.event.Event;
import kube.board.common.event.EventPayload;
import kube.board.common.event.EventType;
import kube.board.hotarticle.service.HotArticleService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.support.Acknowledgment;
import org.springframework.stereotype.Component;
import org.springframework.web.bind.annotation.RequestParam;

import static kube.board.common.event.Event.*;

@Slf4j
@Component
@RequiredArgsConstructor
public class HotArticleEventConsumer {

    private final HotArticleService hotArticleService;

    @KafkaListener(topics = {
            EventType.Topic.LARGE_SCALE_SYSTEM_ARTICLE,
            EventType.Topic.LARGE_SCALE_SYSTEM_COMMENT,
            EventType.Topic.LARGE_SCALE_SYSTEM_LIKE,
            EventType.Topic.LARGE_SCALE_SYSTEM_VIEW
    })
    public void listen(String message, Acknowledgment ack){
        log.info("[HotArticleEventConsumer.listen] received message={}", message);
        Event<EventPayload> event = fromJson(message);
        if (event != null) {
            hotArticleService.handleEvent(event);
        }
        ack.acknowledge();
    }


}
