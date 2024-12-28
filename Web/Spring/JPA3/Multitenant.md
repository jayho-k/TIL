# Multitenant



## 스키마 분리를 통한 Multitenat 구현

> - 구현 필요
> - 

- CurrentTenantIdentifierResolver
  - tenatId를 제공하는 인터페이스다. 그래서 Entity에 tenantId를 넣어야한다.
  - 이 구현은 DB 연결을 위한 현재 tenantId를 결정한다.
  - 정작 보면 컬럼에 값이 있던데..? 
- MultiTenantConnectionProvider 
  - 각각의 tenant는 다른 스키마나 데이터베이스를 가질 수 있다.
  - 역할
    - 현재 tenant에 맞는 DB 연결을 제공. 즉 각각의 DB나 schema를 사용할 수 있도록 tenatId에 맞는 DB 연결을 동적으로 반환한다.
    - 각 tanent의 데이터는 다른 스키마를 저장한다. MultiTenantConnectionProvider는 쿼리 시 해당 스키마를 자동으로 분리하여 실행한다.
    - 즉 tenant Id 대신 MultiTenantConnectionProvider 를 작성하여 tenant 를 구분한다고 보면 될 듯 하다.



- 문제
  - 이전에 저장되어있는 db schema 값으로 들어가게 된다.
  - 그래서 찾아야하는 부분 : 
    - db schema가 바뀌는 타이밍 + 바뀐 schema를 언제 사용하는지

- 순서 (1에 넣고 싶지만 2에 넣어진 상황)
  - 요청이 왔음
  - resolveCurrentTenantIdentifier : multitenant2 인 상황
    - 용도 파악
  - getConnection을 하네 => multitenant2 인상황 
    - => 근데 얘는 어떤 용도로 쓰이는거지?
  - 그리고 setting을 시작하네 **맨 처음에 setting을 해야하는데 그게 안돼서 지금 이 문제가 발생하는 것**
    - setting에서는 multitenant1라고 뜨긴함 즉 set은 됐음 multitenant1
    - 이 set한 애를 언제 쓰는지가 모르겠네
  - save가 들어감
  - getConnection을 다시 하는데 이때 아직 multitenant2 임
  - save 완료 된 시점도 multitenant2 임
  - 실제 insert들어감 **save가 완료되고 나서 insert가 들어가는 것이 아님**

- 순서 (제대로 들어간 상황)

  - 요청이 왔음

  - setting 시작 multitenant2 

  - setting 완료 multitenant2 

  - resolveCurrentTenantIdentifier multitenant2  

  - getConection 스키마도 multitenant2

  - save 관련으로 넘어가서 save 시작

  - update seq 하고 releaseConnection multitenant2

  - insert 까지 하고 multitenant2

  - save 완료

    

- 문제 상황

  - transaction이 시작하기 전에 중간에 set이 안되는게 문제였음
    - 중간에 set이 안된다기보단 이미 setting이 multitenant1 로 잡혀있었음
    - 중간에 set이 안된다는 건 당연한 이야기임 왜냐하면 transaction을 물었다는 건 이미 connection을 얻었다는 것임 따라서 중간에 set을 바꾼다고 한다 하더라도 이미 schema가 정해진 상태라는 것임
    - 따라서 open-view 를 true로 해두면 controller가 시작하자마자 connection 시도를 하게 됨 그리고 영속성 컨텍스트가 살아있음 그러므로 set을 해도 shcema가 이미 connection을 물고 있는 상태이므로 작동이 안되는 거임
    - set은 했기 때문에 다음의 요청이 들어올 때 그때 connection을 가져가는 것임 따라서 타이밍에 따라서 multitenant1로 설정 해두고 multitenant2로 요청 했을때 처음에는 multitenant1 로 값을 주고 2번째는 multitenant2로 connection이 됐던 것임. 이러고 그담에 multitenant1 로 요청하면 multitenant2로 먹힘 (이전에 1값이라서)

  - 그리고 open-view 때문에 끝까지 transaction을 잡고 있어서 처음 시작할때 setting을 해도 안먹힌거임
    - transaction이 끝났는데도 반납을 안한거임 그래서 문제가 생긴거

- 일단 해결

  - open-view를 false로 뒀음 => 이거 원리 파악해야함
  - setting하는 부분을 transaction 시작하기 전에 진행했음





확인

- JpaTransactionManager 에서 doGetTransaction 함수
  - TransactionSynchronizationManager에서 toGetResource함수로 multitenant1 값을 얻네 (근데 )
  - 여기서 setEntityManagerHolder를 위에서 얻은 resource로 진행한다.



Controller에서 set을 해주면 어떻게 될까?

즉 transaction이 시작하기 전에 setting이 되어야함

- 해결
  - open - view -in : false로 바꾸고 모든 값은 트랜잭션 안에서 이뤄지도록 해야한다.
  - 트랜잭션 안에서 모든 값을 다 로딩해두거나 fetch join을 써서 사용한다.

- 쿼리용 서비스?
  - 서비스 부분인데 repository로 긁어오거나 하는 부분만 사용하는것이다
  - 즉 repository를 controller까지 가져오지 않으면 될듯 하다
    - 화면이나 API에 맞춘 서비스 - 주로 읽기 전용 트랜잭션을 사용



```java
```



- domain이 member, order 이렇게 되어있으면 그쪽 안에다가 query용 서비스를 넣는게 더 나을듯



## ThreadLocal  공부 필요

- thread local은 각각의 스레드 마다 독립적인 변수를 가지기 위해서 존재하는 기술이다.
- 확인해야할 것
  - 메모리 누수
    - thread.remove() 를 직접 해줘야한다.
    - 안그러면 메모리 누수가 일어날 수 있음

https://digitalbourgeois.tistory.com/177#:~:text=ThreadLocal%EC%9D%80%20%EC%9E%90%EB%B0%94%EC%97%90%EC%84%9C%20%EB%A9%80%ED%8B%B0,%EB%8A%94%20%EB%8F%99%EA%B8%B0%ED%99%94%EA%B0%80%20%ED%95%84%EC%9A%94%ED%95%A9%EB%8B%88%EB%8B%A4.



```java
// 얘네 어떻게 쓰이는건지 확인
@UnknownKeyFor @Nullable @Initialized

```



## **2. remove() 동작 원리**

1. **현재 쓰레드 확인**
   - `Thread.currentThread()`를 통해 **현재 실행 중인 쓰레드**를 가져옵니다.
2. **ThreadLocalMap 접근**
   - `Thread.currentThread().threadLocals`로 해당 쓰레드의 `ThreadLocalMap`에 접근합니다.
3. **키(ThreadLocal)로 항목 검색**
   - `ThreadLocalMap`에서 **현재 `ThreadLocal` 객체**를 키로 사용하여 항목을 찾습니다.
4. **항목 제거**
   - 항목이 존재하면 해당 항목을 `null`로 설정하여 GC(Garbage Collection) 대상이 되도록 합니다.





- 해야할거
  - multi tenant 정리
  - JPA getTransaction 관련 정리 (On/ OFF 비교)
  - JAVA





```

job에서 run을 돌리는 순간 thread가 진행되고 거기서 runInThread에서 진행읋 한다.

[jobLauncher.run(partitionJob, jobParameters);]
1. lastExecution으로 각 step별로 어떤 상황인지 확인 (실패한게 있는지 등)
2. validate(jobParameters); 확인
3. jobRepository.createJobExecution 으로 JobExecution 생성
4. taskExecutor.execute 실행
	- run 함수 overide
	*- job.execute(jobExecution); 실행
5. jobRepository.update(jobExecution); 해줌


[job.execute(jobExecution); 실행]
1. JobSynchronizationManager.register(execution);로 자기 스레드에 변수값 저장
2. BatchStatus.STARTED 업데이트
3. before 리스터
*4. doExecute 실행
5. 후처리
6. after 리스너


[doExecute 실행!!!]
이때 step을 하나씩 실행시켜준다.
- handleStep(step 하나씩 실제 실행시키는 부분)
	1. lastStepExecution과 비교
	2. status을 update => starting
	3. createStepExecution 생성
	4. 현재 step setExecutionContext 해줌
	5. jobRepository.add(currentStepExecution) jobRepositoru에 현재 
	*6. step.execute(currentStepExecution); 실제 실행시키는 구간
	7. 후처리


[[TaskletStep]에서 doExecute 시작!!!!]
- iterate를 진행
	1. RepeatStatus.CONTINUABLE 상태 변경
	2. executeInternal
        - completionPolicy
        - while(running) : doInIteration 반복
        - StepSynchronizationManager에 stepExecution 등록(ThreadLocal에 등록하는 것)
        - doInChunkContext()
        - doInChunkContext 반복
            1. stepExecution 뽑고
            2. interrupPolicy 확인
            3. 여기서 new TransactionTemplate(tManager, tAttribute).execute 진행한다.
            4. Listener after 실행
            5. interruptionPolicy.checkInterrupted(stepExecution);
            6. 끝


[new TransactionTemplate(tManager, tAttribute).execute(new ChunkTransactionCallback(chunkContext, semaphore)) 진행!!!!!]
이때 transaction을 가져온다 하지만 tm은 언제 set이 되는거지??
1. tm.getTransaction(this)을 진행함
	- 이 함수에서 doGetTracaction으로 진짜 transaction 가져오기
	- 해당 transaction은 JpaTransaction을 가져오게 된다.
		- 현재 스레드에 대한 resource(EntityManagerHolder)를 가져오게 됨 
2. doInTrasaction()을 진행함, 즉 Transaction안에서  new ChunkTransactionCallback(chunkContext, semaphore)을 실행시키는 것
	- RepeatStatus.CONTINUABLE
	- beforeChunk 리스너 실행
	- StepExecution 미리 저장해놓음 => commit fail 날 때 용도
	- tasklet.execute(contribution, chunkContext); 실행
		- 언제까지? result가 null이 될 때까지 tasklet 반복
		-  result가 null일 때 RepeatStatus.FINISHED; 변경 후 종료
	- finally
		- semaphore 얻고 lock 걸고 sync에서 여러 count 값들 갱신
		- 여러 후처리들 해주고



[tasklet.execute(contribution, chunkContext); 실행!!!]
1. chunkProcessor.provide
	- iterate로 read를 진행
	- beforeRead 리스너 진행
	- read를 진행
	- afterRead 리스너
2. chunkProcessor.process(contribution, inputs);
	- do write 진행
	- listener.beforeWrite(items); 
	- writeItems(items) => 여러 커스텀 또는 구현체 사용해서 진행
3. chunkProvider.postProcess(contribution, inputs);
	- FaultTolerantChunkProvider 같은 것들 실행 없으면 아무것도 안함
4. chunkContext.removeAttribute(INPUTS_KEY);
5. chunkContext.setComplete();
6. if (아직 실행 중 => return Continue)
	아니면 RepeatStatus.continueIf(!inputs.isEnd());
```





```

buildEntityManager -> 
SessionBuilderImpl을 생성자가 생성할 때 
tenantIdentifier = currentTenantIdentifierResolver.resolveCurrentTenantIdentifier(); 생성
따라서 db와 connection하기 전에 schema update 하고 connection 시작한다.


```



**JPA 연결 과정:**

- `EntityManagerFactory` → `EntityManager` → `Transaction` → `SQL 실행` → `트랜잭션 종료`

# 🏢 **2. TenantIdentifier 변경 시점**

멀티테넌시는 **Hibernate**의 `CurrentTenantIdentifierResolver`와 `MultiTenantConnectionProvider`를 통해 테넌트를 분리합니다.

## **2.1. TenantIdentifier 변경 시점**

### **① EntityManagerFactory가 생성될 때**

- `CurrentTenantIdentifierResolver`는 `EntityManagerFactory`가 초기화될 때 설정됩니다.

### **② 커넥션 풀에서 커넥션을 가져올 때**

- `MultiTenantConnectionProvider#getConnection(String tenantIdentifier)`가 호출됩니다.
- 이 단계에서 `tenantIdentifier`를 사용하여 올바른 데이터베이스 스키마나 데이터베이스로 라우팅됩니다.

### **③ EntityManager가 생성될 때**

- `EntityManager`가 특정 테넌트를 위한 커넥션을 사용하기 위해 `tenantIdentifier`를 확인합니다.

### **④ 트랜잭션이 시작될 때**

- `EntityManager`가 트랜잭션을 시작할 때 `CurrentTenantIdentifierResolver`를 통해 현재 테넌트를 확인합니다.
- 일반적으로 `ThreadLocal`이나 `HttpRequest`에서 `tenantIdentifier`를 추출합니다.





## **1.1. EntityManagerFactory 생성**

- JPA 애플리케이션이 시작되면 `EntityManagerFactory`가 생성됩니다.
- 이 단계에서는 `persistence.xml`이나 `application.properties`에 정의된 **데이터베이스 연결 정보**(JDBC URL, username, password, 드라이버 등)를 기반으로 데이터베이스 연결이 설정됩니다.
- Hibernate를 사용할 경우, Hibernate는 데이터베이스 Dialect, 스키마 검증, 테이블 생성 등을 처리합니다.

```
java


Copy code
EntityManagerFactory emf = Persistence.createEntityManagerFactory("my-persistence-unit");
```

------

## **1.2. EntityManager 생성**

- `EntityManagerFactory`를 통해 `EntityManager`가 생성됩니다.
- `EntityManager`는 하나의 트랜잭션 범위 내에서 데이터베이스와 상호작용합니다.

```
java


Copy code
EntityManager em = emf.createEntityManager();
```

------

## **1.3. 트랜잭션 시작**

- 데이터베이스와의 상호작용을 위해 `EntityTransaction`이 시작됩니다.
- JPA는 트랜잭션 단위로 데이터베이스와 커넥션을 관리합니다.

```
javaCopy codeEntityTransaction tx = em.getTransaction();
tx.begin();
```

------

## **1.4. SQL 실행 및 데이터베이스와 통신**

- `EntityManager`는 SQL 쿼리를 실행하고 결과를 반환받습니다.
- 데이터베이스 커넥션 풀(Connection Pool)에서 커넥션을 가져와서 통신을 진행합니다.

------

## **1.5. 트랜잭션 종료 및 커넥션 반환**

- 트랜잭션이 종료되면 데이터베이스 커넥션이 반환됩니다.
- `EntityManager`가 종료되면 JPA는 커넥션을 반환하고, 필요한 경우 영속성 컨텍스트를 정리합니다.

```
javaCopy codetx.commit();
em.close();
```









active는 뭐지?



체인(chain)에서 **다음 인터셉터(interceptor)**로 진행합니다.

이 메서드의 **구현 및 의미(semantics)**는 **실제 조인포인트(joinpoint)의 유형**에 따라 달라집니다 (**자식 인터페이스**를 참조하세요).

**반환값:**

- 반환값은 **자식 인터페이스**의 `proceed` 정의를 참조하세요.

**예외:**

- **Throwable:** 조인포인트에서 **예외가 발생한 경우** 던져집니다.



- createJobExecution

- 주어진 `Job`과 `JobParameters`에 대해 `JobExecution`을 생성합니다. 만약 일치하는 `JobInstance`가 이미 존재한다면, 해당 Job은 재시작 가능해야 하며, 마지막 `JobExecution`이 완료되지 않은 상태여야 합니다. 만약 일치하는 `JobInstance`가 아직 존재하지 않는다면, 새로운 `JobInstance`가 생성됩니다.

  이 메서드가 `Isolation.REPEATABLE_READ` 이상의 격리 수준에서 트랜잭션 내에서 실행되는 경우(일반적으로 그렇듯이), 동일한 `JobParameters` 및 `Job` 이름에 대해 다른 트랜잭션이 이미 실행 중이라면 이 메서드는 차단됩니다. 이 시나리오에서 첫 번째로 완료된 트랜잭션이 유효한 `JobExecution`을 획득하며, 다른 트랜잭션들은 `JobExecutionAlreadyRunningException`을 발생시키거나 타임아웃됩니다. `JobInstanceDao`와 `JobExecutionDao`가 트랜잭션 격리 수준을 준수하지 않는 경우(예: 비관계형 데이터 저장소 사용 시 또는 플랫폼이 높은 격리 수준을 지원하지 않는 경우) 이러한 보장은 제공되지 않습니다.

  **매개변수:**

  - **jobName:** 실행할 Job의 이름
  - **jobParameters:** Job 실행 시 사용할 런타임 매개변수

  **반환값:**
  제공된 인자에 대해 유효한 `JobExecution`

  **예외:**

  - **JobExecutionAlreadyRunningException:** 제공된 Job 및 매개변수로 이미 실행 중인 `JobExecution`이 존재하는 경우
  - **JobRestartException:** 동일한 매개변수로 기존 `JobInstance`가 하나 이상 발견되었지만 `Job.isRestartable()`이 `false`인 경우
  - **JobInstanceAlreadyCompleteException:** 해당 `JobInstance`가 이미 성공적으로 완료된 경우





Spring AOP 프레임워크에서 **JDK 동적 프록시(JDK Dynamic Proxy)**를 기반으로 하는 **JDK 기반 AopProxy 구현체**입니다.

이 구현체는 **AopProxy가 노출하는 인터페이스**를 구현하는 **동적 프록시**를 생성합니다. 그러나 동적 프록시는 **클래스에 정의된 메서드**를 프록시할 수 없으며, **인터페이스에 정의된 메서드만 프록시할 수 있습니다.**

이 유형의 객체는 **AdvisedSupport** 클래스로 구성된 **프록시 팩토리(proxy factories)**를 통해 획득해야 합니다. 이 클래스는 Spring AOP 프레임워크의 **내부 클래스**이며, 클라이언트 코드에서 직접 사용할 필요는 없습니다.

이 클래스를 사용하여 생성된 프록시는 **기본(target) 클래스가 스레드 안전(Thread-safe)**하다면 프록시도 스레드 안전합니다.

또한, 모든 **Advisor**(Advice 및 Pointcut 포함)와 **TargetSource**가 **Serializable**하다면, 이 프록시도 **Serializable**합니다.













**디자인 패턴 중 전략 패턴**











