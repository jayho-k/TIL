package kube.board.view.repository;

import lombok.RequiredArgsConstructor;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Repository;

@Repository
@RequiredArgsConstructor
public class ArticleViewCountRepository {

    private final StringRedisTemplate redisTemplate;

    // view::article::{article_id}::view_count => 여기로 저장할 것
    private static final String KEY_FORMAT = "view::article::%s::view_count";

    public Long read(Long articleId ){
        String result = redisTemplate.opsForValue().get(generateKey(articleId));
        return result == null ? 0L : Long.valueOf(result);
    }

    // Redis Documentation: INCRBY : 숫자형 string을 특정 숫자만큼 더할때 사용된다.
    public Long increase(Long articleId){
        return redisTemplate.opsForValue().increment(generateKey(articleId));
    }

    private String generateKey(Long articleId){
        return KEY_FORMAT.formatted(articleId);
    }


}
