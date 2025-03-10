package kube.board.common.outboxmessagerelay;

import jakarta.persistence.*;
import kube.board.common.event.EventType;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.ToString;

import java.time.LocalDateTime;

@Table(name = "outbox")
@Getter
@Entity
@ToString
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Outbox {
    @Id
    private Long outboxId;
    @Enumerated(EnumType.STRING)
    private EventType eventType;
    private String payload;
    private Long shardKey;
    private LocalDateTime createdAt;
    public static Outbox create(Long outboxId, EventType eventType, String payload, Long shardKey) {
        Outbox outBox = new Outbox();
        outBox.outboxId = outboxId;
        outBox.eventType = eventType;
        outBox.payload = payload;
        outBox.shardKey = shardKey;
        outBox.createdAt = LocalDateTime.now();
        return outBox;
    }



}

