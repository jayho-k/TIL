package kube.board.common.outboxmessagerelay;

import kube.board.common.event.Event;
import kube.board.common.event.EventPayload;
import kube.board.common.event.EventType;
import kube.board.common.snowflake.Snowflake;
import lombok.RequiredArgsConstructor;
import org.springframework.context.ApplicationEventPublisher;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
public class OutboxEventPublisher {

    private final Snowflake outboxIdSnowFlake = new Snowflake();
    private final Snowflake eventIdSnowFlake = new Snowflake();

    // 발행하기 위함
    private final ApplicationEventPublisher applicationEventPublisher;

    public void publish(EventType type, EventPayload payload, Long sharKey){
        // 물리적 샤드가 들어가 있는 부분을 찾기 위함
        // article id==10, sharKey==articleId
        // 10 % 4 = 2
        Outbox outbox = Outbox.create(
                outboxIdSnowFlake.nextId(),
                type,
                Event.of(
                        eventIdSnowFlake.nextId(), type, payload
                ).toJson(),
                sharKey % MessageRelayConstants.SHARD_BOUND
        );
        applicationEventPublisher.publishEvent(OutboxEvent.of(outbox));
    }


}
