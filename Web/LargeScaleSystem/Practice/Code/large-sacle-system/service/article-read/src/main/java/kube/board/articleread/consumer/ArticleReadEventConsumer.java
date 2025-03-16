package kube.board.articleread.consumer;

import kube.board.articleread.service.ArticleReadService;
import kube.board.common.event.Event;
import kube.board.common.event.EventPayload;
import kube.board.common.event.EventType;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.support.Acknowledgment;
import org.springframework.stereotype.Component;

@Slf4j
@Component
@RequiredArgsConstructor
public class ArticleReadEventConsumer {

    private final ArticleReadService articleReadService;

    @KafkaListener(topics = {
            EventType.Topic.LARGE_SCALE_SYSTEM_ARTICLE,
            EventType.Topic.LARGE_SCALE_SYSTEM_COMMENT,
            EventType.Topic.LARGE_SCALE_SYSTEM_LIKE
    })
    public void listen(String message, Acknowledgment ack){
        log.info("[ArticleReadEventConsumer.listen] message={}", message);
        Event<EventPayload> event = Event.fromJson(message);
        if (event != null){
            articleReadService.handleEvent(event);
        }
        ack.acknowledge();
    }
}
