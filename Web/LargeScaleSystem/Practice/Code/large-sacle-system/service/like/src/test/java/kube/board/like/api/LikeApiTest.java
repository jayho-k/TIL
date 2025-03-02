package kube.board.like.api;

import kube.board.like.service.response.ArticleLikeResponse;
import org.junit.jupiter.api.Test;
import org.springframework.web.client.RestClient;

import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class LikeApiTest {

    RestClient restClient = RestClient.create("http://localhost:9002");

    @Test
    void likeAndUnlikeTest() {
        Long articleId = 9999L;

        like(articleId, 1L, "pessimistic-lock-1");
        like(articleId, 2L, "pessimistic-lock-1");
        like(articleId, 3L, "pessimistic-lock-1");

        ArticleLikeResponse response1 = read(articleId, 1L);
        ArticleLikeResponse response2 = read(articleId, 2L);
        ArticleLikeResponse response3 = read(articleId, 3L);
        System.out.println("response1 = " + response1);
        System.out.println("response2 = " + response2);
        System.out.println("response3 = " + response3);

        unlike(articleId, 1L, "pessimistic-lock-1");
        unlike(articleId, 2L, "pessimistic-lock-1");
        unlike(articleId, 3L, "pessimistic-lock-1");

        /*
        *
        * response1 = ArticleLikeResponse(articleLikeId=154172510213623808, articleId=9999, userId=1, createdAt=2025-03-01T19:26:31)
            response2 = ArticleLikeResponse(articleLikeId=154172510557556736, articleId=9999, userId=2, createdAt=2025-03-01T19:26:31)
            response3 = ArticleLikeResponse(articleLikeId=154172510620471296, articleId=9999, userId=3, createdAt=2025-03-01T19:26:31)
        * */
    }


    void like(Long articleId, Long userId, String lockType) {
        restClient.post()
                .uri("/v1/article-likes/articles/{articleId}/users/{userId}/"+lockType, articleId, userId)
                .retrieve();
    }

    void unlike(Long articleId, Long userId, String lockType) {
        restClient.delete()
                .uri("/v1/article-likes/articles/{articleId}/users/{userId}/" + lockType, articleId, userId)
                .retrieve();
    }

    ArticleLikeResponse read(Long articleId, Long userId) {
        return restClient.get()
                .uri("/v1/article-likes/articles/{articleId}/users/{userId}", articleId, userId)
                .retrieve()
                .body(ArticleLikeResponse.class);
    }

    @Test
    void likePerformanceTest() throws InterruptedException {
        ExecutorService es = Executors.newFixedThreadPool(100);
        likePerformanceTest(es, 1111L, "pessimistic-lock-1");
        likePerformanceTest(es, 1111L, "pessimistic-lock-2");
        likePerformanceTest(es, 1111L, "optimistic-lock");
    }

    void likePerformanceTest(ExecutorService es, Long articleId, String lockType) throws InterruptedException {
        CountDownLatch latch = new CountDownLatch(3000);
        System.out.println(lockType + " start");
        like(articleId, 1L, lockType);

        long start = System.nanoTime();
        for (int i=0; i< 3000; i++){
            long userId = i + 2;
            es.submit(() -> {
                like(articleId, userId, lockType);
                latch.countDown();
            });
        }
        latch.await();
        long end = System.nanoTime();
        System.out.println("lockType = " + lockType + ", time = " + (end-start) / 1000000 + "ms");

        Long count = restClient.get()
                .uri("/v1/article-likes/articles/{articleId}/count", articleId)
                .retrieve()
                .body(Long.class);

        System.out.println("count = " + count);
    }






}
