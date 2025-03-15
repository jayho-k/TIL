package kube.board.articleread.repository;

import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Range;
import org.springframework.data.redis.connection.Limit;
import org.springframework.data.redis.connection.RedisZSetCommands;
import org.springframework.data.redis.connection.StringRedisConnection;
import org.springframework.data.redis.core.RedisCallback;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
@RequiredArgsConstructor
public class ArticleIdListRepository {

    private final StringRedisTemplate redisTemplate;

    private static final String KEY_FORMAT = "article-read::board::%%s::article-list";

    public void add(Long boardId, Long articleId, Long limit){
        redisTemplate.executePipelined((RedisCallback<?>) action -> {
            StringRedisConnection conn = (StringRedisConnection) action;
            String key = generateKey(boardId);
            conn.zAdd(key, 0, toPaddedString(articleId)); // score가 double값이라서 데이터가 꼬일수 있음
            conn.zRemRange(key, 0, -limit - 1);
            return null;
        });
    }

    public void delete(Long boardId, Long articleId) {
        redisTemplate.opsForZSet().remove(generateKey(boardId), toPaddedString(articleId));
    }

    public List<Long> readAll(Long boardId, Long offset, Long limit){
        return redisTemplate.opsForZSet()
                .reverseRange(generateKey(boardId), offset, offset + limit - 1)
                .stream().map(Long::valueOf).toList();
    }


    /*
    *  limit : 3
    *  만약 lastArticleId가 null이면?
    *  이유 :
    *  6 5 4 3 2 1 => limit가 3이기 때문에 6 5 4를 가져올 거임
    *  만약  lastArticleId가 4이면?
    *  exclusive(toPaddedString(lastArticleId)) : lastArticleId은 제외하고 3개 가져오라는 뜻
    *  따라서 3 2 1만 출력되게 된다.
    *
    */
    public List<Long> readAllInfiniteScroll(Long boardId, Long lastArticleId, Long limit) {
        return redisTemplate.opsForZSet().reverseRangeByLex( // 문자열로 정렬된 상태로 있을 것임
                generateKey(boardId),
                lastArticleId == null ?
                        Range.unbounded() :
                        Range.leftUnbounded(Range.Bound.exclusive(toPaddedString(lastArticleId))),
                Limit.limit().count(limit.intValue())
        ).stream().map(Long::valueOf).toList();
    }

    private String toPaddedString(Long articleId){
        return "%019d".formatted(articleId);
        // 1234 -> 00000000000001234 : 고정된 자릿수로 저장하기 위함
    }

    private String generateKey(Long boardId){
        return KEY_FORMAT.formatted(boardId);
    }


}
