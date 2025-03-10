package kube.board.common.outboxmessagerelay;

import jakarta.annotation.PreDestroy;
import lombok.RequiredArgsConstructor;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.connection.StringRedisConnection;
import org.springframework.data.redis.core.RedisCallback;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

@Component
@RequiredArgsConstructor
public class MessageRelayCoordinator {

    private final StringRedisTemplate redisTemplate;

    @Value("${spring.application.name}")
    private String applicationName;

    private final String APP_ID = UUID.randomUUID().toString();

    private final int PING_INTERVAL_SECONDS = 3;
    private final int PING_FAILURE_THRESHOLD = 3;

    public AssignedShard assignedShard(){
        return AssignedShard.of(APP_ID, findAppIds(), MessageRelayConstants.SHARD_BOUND);
    }

    private List<String> findAppIds(){
        return redisTemplate.opsForZSet().reverseRange(generateKey(), 0, -1).stream()
                .sorted() // 살아있는 app를 동일한 순서로 보장하기 위함 [아래 함수로 인해 정렬이 계속 바뀌기 때문 ]
                .toList();
    }

    @Scheduled(fixedDelay = PING_INTERVAL_SECONDS)
    public void ping(){
        redisTemplate.executePipelined((RedisCallback<?>) action -> {
            StringRedisConnection conn = (StringRedisConnection) action;
            String key = generateKey();
            conn.zAdd(key, Instant.now().toEpochMilli(), APP_ID);
            conn.zRemRangeByScore(
                    key,
                    Double.NEGATIVE_INFINITY,
                    Instant.now().minusSeconds(PING_INTERVAL_SECONDS * PING_FAILURE_THRESHOLD).toEpochMilli()
            );
            return null;
        });
    }

    // app이 죽었을 때 바로 죽었다고 알릴 수 있기 때문에
    @PreDestroy
    public void leave(){
        redisTemplate.opsForZSet().remove(generateKey(), APP_ID);
    }


    // 각 서비스가 name 을 가지고 있고, 고유하게 설정 [ex_large-scale-system-article 등등]
    private String generateKey(){
        return "message-replay-coordinator::app-list::%s".formatted(applicationName);
    }

}
