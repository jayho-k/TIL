package kube.board.hotarticle.repository;

import lombok.RequiredArgsConstructor;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Repository;

import java.time.Duration;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneOffset;

@Repository
@RequiredArgsConstructor
public class ArticleCreatedTimeRepository {

    // 오늘 생성된 글인지 확인을 하기 위해서 게시글 서비스에 조회가 필요
    // 게시글 생성 시간을 저장하고 있으면, 오늘 게시글인지 서비스에 안찍어봐도 알 수 있기 때문에 Date를 관리

    private final StringRedisTemplate redisTemplate;

    // hot-article::article::{articleId}::created-time
    private static final String KEY_FORMAT = "hot-article::article::%s::created-time";

    public void createOrUpdate(Long articleId, LocalDateTime createdAt, Duration ttl) {
        redisTemplate.opsForValue().set(
                generateKey(articleId),
                String.valueOf(createdAt.toInstant(ZoneOffset.UTC).toEpochMilli()), // LocalDateTime을 String으로 바꾸는 방법
                ttl
        );
    }

    public void delete(Long articleId) {
        redisTemplate.delete(generateKey(articleId));
    }

    public LocalDateTime read(Long articleId) {
        // LocalDateTime으로 조회를 해야함
        String result = redisTemplate.opsForValue().get(generateKey(articleId));
        if (result == null) {
            return null;
        }
        // String => Long => LocalDateTime
        return LocalDateTime.ofInstant(
                Instant.ofEpochMilli(Long.valueOf(result)), ZoneOffset.UTC
        );
    }

    private String generateKey(Long articleId) {
        return KEY_FORMAT.formatted(articleId);
    }

}
