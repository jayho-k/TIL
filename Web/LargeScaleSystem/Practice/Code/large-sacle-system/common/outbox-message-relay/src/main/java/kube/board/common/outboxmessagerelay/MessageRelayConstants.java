package kube.board.common.outboxmessagerelay;

import lombok.AccessLevel;
import lombok.NoArgsConstructor;

@NoArgsConstructor(access = AccessLevel.PRIVATE)
public class MessageRelayConstants {
    public static final int SHARD_BOUND = 4;
}
