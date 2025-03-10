# 07_PopularArticle

> - Kafka Cluster 

### 모르는 것들

@EnableAsync

@TransactionalEventListener()

@EventListener(), @Async 등 





## 용어 정리

### Producer

- Kafka로 데이터를 보내는 클라이언트
- 데이터를 생산 및 전송
- Topic 단위로 데이터 전송\

### Consumer 

- Kafka에서 데이터를 읽는 클라이언트
- 데이터를 소비 및 처리
- Topic 단위로 구독하여 데이터를 처리한다.

### Broker

- Kafka에서 데이터를 중개 및 처리해주는 애플리케이션 실행 단위
- Producer와 Concumer 사이에엇 데이터를 주고 받는 역할

### Kafka Cluster

- 여러 개의 Broker가 모여서 하나의 분산형 시스템을 구성한 것
- 데이터의 복제, 분산 처리, 장애 복구 등 여러 대규모 데이터에 대한 기능을 지원한다.
  - 고성능, 안전성, 고가용성 등

### Topic

- 데이터가 구분되는 논리적 단위
  - article-topic, comment-topic, like-topic 등등

### Partition

- Topic이 분산되는 단위
- 각 Topic은 여러개의 Partition으로 분산 저장 및 병렬 처리된다.
- 각 Partition 내에서 데이터가 순차적으로 기록되고 순서가 보장된다.
- 각 Partition 끼리는 순서가 보장 되지 않는다.
- Partition은 여러 Broker에 분산되어 Cluster의 확장성을 높인다.

### Offset

- 각 데이터에 대해 고유한 위치
  - 데이터는 각 Topic의 Partition 단위로 순차적으로 기록, 기록된 데이터는 offset을 가진다.

### Consumer Group

- 각 Topic의 Partition 단위로 Offset을 관리한다.
  - 인기글을 위한 Consumer Group
  - 조회 최적화 서비스를 위한 Consumer Group
- Consumer Group 내의 Consumer 들은 데이터를 중복해서 읽지 않을 수 있다.
- Consumer Group 별로 데이터를 병렬로 처리할 수 있다.



## 인기글 설계

> - 요구사항
> - 배치 처리 방법
> - 스트림 처리 방법

### 요구사항

- 일 단위로 상위 10건 인기글 성정
- 매일 오전 1시 업데이트
- 최근 7일 인기글 내역 조회



### 배치 처리 방법

- 처리해야 할 게시글의 개수 = 대규모

- **배치 처리는 시간이 오래걸릴 수 있음**

  - 병렬 처리가 가능하나 구현 복잡도가 올라가게 된다.

    

- **인기글 작업으로 인해 타 서비스에 영향이 갈 수 있음**

  - 1시간 동안에 무수히 많은 Query가 필요하다.
  - 1시간 동안 인기글 서비스에 의해 타 서비스의 부하가 폭발적으로 증가할 수 있다.



### 스트림 처리 방법

> - **스트림 (Stream)**
>
>   - 연속적인 데이터 흐름
>
>   - 실시간으로 발생하는 로그, 센서 감지, 주식 거래 데이터 등과 같이 연속적으로 들어오는 데이터
>
>     
>
> - **스트림 처리 (Stream Processing)**
>
>   - 스트림을 처리하는 것
>   - 연속적으로 들어오는 실시간 데이터를 처리하는 방식

#### 설계

<img src="./07_PopularArticle.assets/image-20250308165719633.png" alt="image-20250308165719633" style="zoom:67%;" />

1. **인기글 선정에 필요한 이벤트(ex_게시글 CRUD, 댓글 생성, 좋아요 등)를 스트림으로 받는다.**
   - 조회수 이벤트의 경우 트래픽이 많을 수 있으므로 백업 시점 (100개 단위)에만 생산해본다.
   
2. **실시간으로 각 게시글의 점수를 계산한다.**
   - 이벤트를 받을 때마다 점수를 계산한다.
   
3. **실시간으로 상위 10건의 인기글 목록을 만든다.**
   - 이러한 처리결과를 Redis에 TTL 기능을 활용하여 저장한다.
   - Sorted Set 자료 구조를 활용하여 정렬된 집합 데이터로 관리한다.
     즉, 상위 점수 10건의 게시글을 정렬 상태로 유지할 수 있다.
4. **Client는 인기글 목록을 조회한다.**



#### API vs Message Broker

##### API

<img src="./07_PopularArticle.assets/image-20250308170129528.png" alt="image-20250308170129528" style="zoom:67%;" />

- 데이터 변경이 생기면 인기글 서비스로 API를 이용한 이벤트 전송
- **장점**
  - 구현이 간단하다.
  
- **단점** 
  - 타 서비스에 직접적 의존, 시스템 간 결합도 증가
  - 서버 부하가 전파 될 수 있음 => 장애 전파, 유실등의 위험이 높음
    - 데이터를 실시간으로 push를 받는 것



##### Message Broker

<img src="./07_PopularArticle.assets/image-20250308170442405.png" alt="image-20250308170442405" style="zoom: 80%;" />

- 동작
  - 게시글/ 좋아요 등 서비스의 데이터 변경되면 메시지 브로커로 이벤트 전송
  - 인기글 서비스는 이벤트를 가져와서 처리한다.

- 장점
  - 메시지 브로커에서 적절하게 이벤트를 가져와서 작업이 가능하다.
  - 게시글/ 좋아요/ 조회수/ 댓글 은 메시지 브로커로 이벤트만 전송하면 된다.
    즉 인기글에 대해서 신경쓰지 않아도 된다.
  - 장애 전파, 유실 등의 위험이 낮다.
  
- 단점
  - 구현이 복잡한다.



### Stream Processing을 활용한 인기글 설계

<img src="./07_PopularArticle.assets/image-20250308172202987.png" alt="image-20250308172202987" style="zoom:80%;" />

- Redis => Sorted Set에 저장된 인기글의 key를 날짜로 지정한다.
- 하루가 지나면 새로운 Key를 생성한다.
- 오전 1시가 될 때 (약속된 시간) Client는 해당 Key만 바라본다.
- 그렇게 반복되며, 데이터는 7일간 보존한다.



#### 점수 계산

- 게시글, 댓글 등의 이벤트는 개별적으로 받는다.
  즉 댓글 이벤트를 수신했을 때 좋아요 수, 조회수 같은 이벤트는 포함되어있디 않다.

- 점수 계산에 댓글의 유니크 작성자 수가 필요하다면?

  - 이러한 데이터는 댓글 서비스에서 가지고 제공할 이유도 없다.

  - 즉 인기글 서비스에서 관리해야하는 데이터들이 존재

    

- **인기글 서비그가 자체적인 데이터를 가지도록 해야하는 것이 포인트다**



## Producer

> - 게시글/ 댓글/ 좋아요/조회수 서비스 같은 것들이 인기글에게는 Producer 역할을 한다.
> - 이벤트를 전달하는 역할
> - Transactional Messaing
>   - Two Phase Commit
>   - Transactional Outbox
>   - Transaction Log Tailing

### Transactional Messaging

**장애 발생**

<img src="./07_PopularArticle.assets/image-20250309165328233.png" alt="image-20250309165328233" style="zoom:67%;" />

- Producer는 Kafka에 데이터 전송실패와 무관하게 비즈니스로직이 수행되어야한다.
- 이렇게 되면 데이터 일관성이 깨지게 된다.
- 해결 방안  **[Eventually Consistency]**
  - 비즈니스 로직 수행과 이벤트 전송이 모두 일어나거나, 모두 일어나지 않거나 해야한다.
  - 꼭 실시간으로 처리될 필요 없음
  - 즉 비즈니스 로직 우선 처리 => Kafka 전송 나중에 완료

**Bad Case**

1. Transction start
2. 비즈니스 로직 수행
3. publishEvent() [Kafka로 전송]
4. commit or rollback

- 위 방법은 Kafka와 MySQL이 서로 다른 시스템이기 때문에 정상적으로 진행되지 않는다.
- 만약 위 과정이 완료 되기 위해선 publishEvent가 완료될 때까지 기다렸다가 수행할 수 있음
  - 하지만 위 방법은 Kafka에 의존하게 되는 것 => 즉 Kafka에서 답을 3초 지연돼서 줬으면 3초가 지연되는 구조임  
- 비동기 처리?  => 그럼 3번 진행이 rollback 되어야하는지 안되는지 모름



#### Two Phase Commit

<img src="./07_PopularArticle.assets/image-20250309171103266.png" alt="image-20250309171103266" style="zoom: 50%;" />

- **정의**
  - 모든 시스템이 성공적으로 완료 : Commit
  - 하나의 시스템이라도 실패 : Rollback

- **Prepare phase (준비 단계)**
  - Coordinator는 각 참여자에게 트랜잭션을 commit할 준비가 되었는지 물어본다.
  - 각 참여자는 준비가 되었는지 응답한다
- **Commit phase (커밋 단계)**
  - 모든 참여자가 준비가 완료되면 참여자들에게 트랜잭션 커밋을 요청한다.
  - 모든 참여자는 트랜잭션을 커밋한다.

- **문제점**
  - 모든 참여자의 응답을 기다려야한다. 지연이 길어질 수 있음
  - 참여가 하나가 장애가 발생하면 다른 참여자들은 이유를 모르고 대기해야한다.
  - 트랜잭션 복구 처리가 복잡해질 수 있다.





#### Transactional Outbox

- Transactional Outbox란?
  - 이벤트 전송 정보를 데이터 데이터베이스 트랜잭션에 포함하여 기록할 수 있음
  - 트랜잭션을 지원하는 DB에 Outbox 테이브를 생성
    - [서비스 로직 수행 + Outbox 테이블 이벤트 메시지 기록] : 하나의 트랙잭션으로 묶는다.

- **동작 방식**
  1. **비즈니스 로직 수행 및 Outbox 테이블 이벤트 기록**
     - Transaction start
     - 비즈니스 로직 수행
     - Outbox 테이블에 전송 할 이벤트 데이터 기록
     - commit or abort
     
  2. **Outbox 테이블을 이용한 이벤트 전송 처리**
     - Outbox 테이블 미전송 이벤트 조회
     - 이벤트 전송
     - Outbox 테이블 전송 완료 처리



#### Transaction Log Tailing

- DB의 트랜잭션 로그를 추적 및 분석하는 방법
  - DB는 각 트랜잭션의 변경 사항을 로그로 기록하는데 그것을 읽어서 Message Broker에 이벤트를 전송하는 방법이다.
- CDC(Change Data Capture) 기술을 활용하면 데이터의 변경 사항을 다른 시스템에 전송할 수 있음

- **동작방식**

<img src="./07_PopularArticle.assets/image-20250309174158200.png" alt="image-20250309174158200" style="zoom:67%;" />

1. Data Table 변경
2. DB에 Transaction Log가 찍힘
3. Transaction Log Miner 가 Transaction Log를 조회해서 변경사항을 check하게 된다.
4. 변경 사항을 Event 전송하여 Message Broker에 보내게 된다.

- 장점
  - 이벤트 전송작업을 직접 개발하지 않을 수 있다.
  
- 필요점
  - 올바르게 활용하려면 새로운 기술에 대한 학습 및 운영비용이 발생한다. 



### Transactional Outbox  설계

<img src="./07_PopularArticle.assets/image-20250309174610398.png" alt="image-20250309174610398" style="zoom:67%;" />

- Shard Key
  - Outbox Table에 이벤트 데이터 기록과 비즈니스 로직에 의한 상태 변경이 동일한 트랜잭션으로 처리될 수 있도록 한다.



<img src="./07_PopularArticle.assets/image-20250309175452919.png" alt="image-20250309175452919" style="zoom: 67%;" />

1. **게시글 생성 / 수정 / 삭제 API**
2. **Article Table 값, Outbox Table 변경**
   - 추가로 게시글 서비스에서 트랜잭션이 commit이 되면 Message Relay에 이벤트 전달
   
3. **Message Relay는 10초 간격으로 Outbox Table 조회**
   - 해당 부분은 2번 과정에서 이벤트 전달이 실패한 이벤트만 조회하도록 한다.
   - 즉 장애 상황에만 발생했을 것이기 때문에 생성된지 10초가 지난 이벤트만 pooling하게 된다.
   - **여전히 이벤트 중복 처리가 될 수 있기 때문에 Consumer 측에서 멱등성을 고려한 개발이 필요**
4. **전송이 완료된 이벤트 처리**
   - 삭제하는 방법, Event Sourcing (추적 방법)등 여러방법이 있음
   - 정책에 따라서 판단해주면 된다.

5. **Shard 처리를 위해서 Redis (중앙 저장소) 에서 Application이 실행되고 있는지 확인해준다.**

   - ping 시간을 정렬된 상태로 저장하는 Sorted Set을 이용하여 저장한다.

   - 3초 간격으로 ping을 보낸다.

   - ping을 받은지 9초가 지났으면 애플리케이션이 종료되었다고 판단하고 삭제한다.
   - 4개의 샤드가 있다고 가정하고 4개의 샤드를 범위 기반으로 할당한다.
     - ex_ 0~1 / 2~3 번 샤드를 각각 polling















