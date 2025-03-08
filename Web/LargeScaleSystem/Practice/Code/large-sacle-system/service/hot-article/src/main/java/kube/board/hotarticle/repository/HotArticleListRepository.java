package kube.board.hotarticle.repository;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.connection.StringRedisConnection;
import org.springframework.data.redis.core.RedisCallback;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.data.redis.core.ZSetOperations;
import org.springframework.stereotype.Repository;

import java.time.Duration;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.stream.Collectors;

@Slf4j
@Repository
@RequiredArgsConstructor
public class HotArticleListRepository {

    private final StringRedisTemplate redisTemplate;

    // hot-article::list::{yyyyMMdd}
    private static final String KEY_FORMAT = "hot-article::list::%s";

    private static final DateTimeFormatter TIME_FORMATTER = DateTimeFormatter.ofPattern("yyyyMMdd");

    public void add(Long articleId, LocalDateTime time, Long score, Long limit, Duration ttl){
        // pipeline : redis 와 연결 한번으로 여러개를 한번에 계산하기 위함
        redisTemplate.executePipelined((RedisCallback<?>) action -> {
            StringRedisConnection conn = (StringRedisConnection) action;
            String key = generateKey(time);
            conn.zAdd(key, score, String.valueOf(articleId));
            conn.zRemRange(key, 0, -limit - 1); // 상위 limit 만큼의 데이터만 남길 수 있음
            conn.expire(key, ttl.toSeconds());
            return null;
        });
    }

    public void remove(Long articleId, LocalDateTime time){
        redisTemplate.opsForZSet().remove(generateKey(time), String.valueOf(articleId));
    }

    public List<Long> readAll(String dateStr){
        return redisTemplate.opsForZSet()
                .reverseRangeWithScores(generateKey(dateStr), 0, -1).stream()
                .peek(tuple -> log.info("[HotArticleListRepository.readAll] articleId={}, score={}", tuple.getValue(), tuple.getScore()))
                .map(ZSetOperations.TypedTuple::getValue)
                .map(Long::valueOf)
                .toList();
    }

    private String generateKey(LocalDateTime time){
        return generateKey(TIME_FORMATTER.format(time));
    }

    private String generateKey(String dateStr){
        return KEY_FORMAT.formatted(dateStr);
    }

}
