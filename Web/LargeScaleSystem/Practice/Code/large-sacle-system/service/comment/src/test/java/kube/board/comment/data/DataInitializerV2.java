package kube.board.comment.data;

import jakarta.persistence.EntityManager;
import jakarta.persistence.PersistenceContext;
import kube.board.comment.entity.Comment;
import kube.board.comment.entity.CommentPath;
import kube.board.comment.entity.CommentV2;
import kube.board.common.snowflake.Snowflake;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.transaction.support.TransactionTemplate;

import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

@SpringBootTest
public class DataInitializerV2 {
    @PersistenceContext
    EntityManager entityManager;
    @Autowired
    TransactionTemplate transactionTemplate;
    Snowflake snowflake = new Snowflake();
    CountDownLatch latch = new CountDownLatch(6000);
    static final int BULK_INSERT_SIZE = 2000;
    static final int EXECUTE_COUNT = 6000;


    @Test
    void initialize() throws InterruptedException {
        ExecutorService executorService = Executors.newFixedThreadPool(10);
        for (int i = 0; i< EXECUTE_COUNT; i++){
            int start = i * BULK_INSERT_SIZE;
            int end = (i+1) * BULK_INSERT_SIZE;
            executorService.submit(() -> {
                insert(start, end);
                latch.countDown();
                System.out.println("latch.getCount() = " + latch.getCount());
            });
        }
        latch.await();
        executorService.shutdown();
    }



    // 이렇게 start end로 구분해서 insert 하는 이유
    // path 는 unique 해야한다. 하지만 multi thread 환경이기 떄문에 해당 범위를 나눠준 것
    // 범위 중복이 안되겠끔
    void insert(int start, int end){
        transactionTemplate.executeWithoutResult(status -> {
            for(int i = start; i< end; i++){
                CommentV2 comment = CommentV2.create(
                        snowflake.nextId(),
                        "comment",
                        1L,
                        1L,
                        toPath(i)
                );
                entityManager.persist(comment);
            }
        });
    }

    private static final String CHARSET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";
    private static final int DEPTH_CHUNK_SIZE = 5;
    CommentPath toPath(int value){

        String path = "";
        for (int i=0; i<DEPTH_CHUNK_SIZE; i++){
            // value % charsetLength => 해당 char의 위치
            path = CHARSET.charAt(value % CHARSET.length()) + path;
            value /= CHARSET.length();
        }
        return CommentPath.create(path);
    }


}
