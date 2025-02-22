# 03_ArticleAPI



- 모르는 거 확인

  - @NoArgsConstructor(access = AccessLevel.PROTECTED) //

  - 

  - // factory method란

  - 잘 사용할 수 있을 방법

    ```java
        // factory method
        public static Article create(Long articleId, String title, String content, Long boardId, Long writerId, LocalDateTime createAt, LocalDateTime modifiedAt){
            Article article = new Article();
            article.articleId = articleId;
            article.title = title;
            article.content = content;
            article.boardId = boardId;
            article.writerId = writerId;
            article.createAt = createAt;
            article.modifiedAt = modifiedAt;
            return article;
        }
    
        public void update(String title, String content){
            this.title = title;
            this.content = content;
            modifiedAt = LocalDateTime.now();
        }
    
    ```

- @SpringBootTest : 공부



```java
package kube.board.article.data;

import jakarta.persistence.EntityManager;
import jakarta.persistence.PersistenceContext;
import kube.board.article.entity.Article;
import kube.board.common.snowflake.Snowflake;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.transaction.support.TransactionTemplate;

import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

@SpringBootTest
public class DataInitializer {
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
            executorService.submit(() -> {
                insert();
                latch.countDown();
                System.out.println("latch.getCount() = " + latch.getCount());
            });
        }
        latch.await();
        executorService.shutdown();
    }

    void insert(){
        transactionTemplate.executeWithoutResult(status -> {
            for(int i=0; i< BULK_INSERT_SIZE; i++){
                Article article = Article.create(
                        snowflake.nextId(),
                        "title" + i,
                        "content" + i,
                        1L,
                        1L
                );
                entityManager.persist(article);
            }
        });
    }

}

```

- @PersistenceContext 이란?
  - EntityManager가 Thread-Safe하지 않는다. 
  - 따라서 PersistenceContext을 통해 Spring으로 EntityManager를 관리하는 역할을 한다.
  - @PersistenceContext를 사용해서 EntityManager를 주입 받으면 Spring에서 EntityManager를 Proxy로 감싼 EntityManager를 사용해서 Thread-Safe를 보장한다.\
  - Proxy로 생성하고 호출 시 마다 새로운 객체를 생성해주기 때문에 Thread safe 한 것
- CountDownLatch 이란?
  - 하나 이상의 스레드가 다른 스레드에서 수행 중인 작업이 완료될 때까지 대기할 수 있는 동기화 보조 기능이라고 생각하시면 됩니다.

```java
CountDownLatch latch = new CountDownLatch(6000);

latch.countDown(); // 이 함수 1번 실행 하면 1씩 감소한다.

latch.await(); // CountDownLatch 가 0이 될때까지 대기한다. 즉 6000번 호출될 때 까지 대기

```

- ex
  - 1개의 카운트로 초기화된 CountDownLatch는 on/off latch 또는 게이트 역할을 해준다.
  - 호출되는 모든 스레드는 countDown()을 스레드에 의해 열릴떄 까지 대기한다.



- transactionTemplate.executeWithoutResult(status -> {})

  - Transaction을 관리해주는 class이다.

  - 하기 2가지 단점을 가지고 있어 이럴 때 사용하면 좋음

  - @Transaction을 사용하면 되지만 단점을 가지고 있음

    - 메서드 레벨에 AOP 가 적용되기 때문에 트랜잭션 단위도 메서드 레벨로 적용
      (메서드 내에서 지정 불가능)

    - self invocation 에서 트랜잭션 적용 불가

    - ```java
      public Proxy {
      	public void externalMethod(){
          	internalMethod(); // 자기 호출(Self Invocation) 발생
          }
          public void internalMethod(){
          }
      }
      ```

    - 이렇게 생성된 프록시 객체에서 내부(Internal) 호출을 할 경우, 다시 말해 같은 클래스 내 메소드 호출인 **자기 호출**(Self-Invocation)을 이용하면 AOP 기능이 수행되지 않아 여러 블로그 글들에서 **트랜잭션 기능이 동작하지 않는다**고 설명하고 있습니다.



## 페이징 조회

### 페이징을 처리하는 방법은?

- DB에서 특정 페이지의 데이터만 바로 추출하는 방법이 필요

### 1 - 페이지 번호 방식

- N번 페이지에서 M개의 게시글
- 게시글의 개수
  - 즉 페이지당 30개의 게시글을 보여주고, 총 94개의 게시글이 있다면 4번 페이지까지 이동할 수 있다는 것을 알 수 있어야한다. 

```sql
# 게시판 별 게시글 목록
# shard key = board id : 단일 샤드에서 조회 가능

select * from article
	where board_id = {baord_id}
		order by created_at desc
        limit {limit} offset {offset}; # N번 페이지에서 M개
```

- **4초 걸린다 : 굉장히 느림!!!**





30 rows in set (0.02 sec)







1. 무한 스크롤

















