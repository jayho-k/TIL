# 01_Spring Batch

> - spring 4.xx 기준이다. 즉 5버전부터는 다르니 확인이 필요

## 핵심 패턴

- Read : 데이터베이스, 파일, 큐에서 다량의 데이터를 조회한다.
- Process : 특정 방법으로 데이터를 가공한다.
- Write : 데이터를 수정된 양식으로 다시 저장한다.

- ETL 과 동일하다고 보면 된다.
  - Extract, Transform, Load => read, process, write



## 배치 시나리오

- 배치 프로세스를 주기적으로 커밋
  - commit 전략이 중요하다. 여러 데이터를 한번에 commit을 시도하게 되면 부하가 걸리기 떄문이다.
- 동시 다발적인 Job의 배치 처리, **대용량 병렬 처리 필요**
- 수동 or 스케줄링에 의한 재시작 필요
- 반복, 재시도, Skip 처리 필요
  - 잠깐에 네트워크 발생했을 경우 그부분만 재시도 가능하도록 하도록 진행



## 스프링 배치 아키텍처

![image-20240802213034643](./Spring Batch.assets/image-20240802213034643.png)

- **Application**
  - 업무로직의 구현에만 집중하고 공통적인 기반 기술 담당!
- **Batch Core**
  - Job을 실행, 모니터링, 관리하는 API로 구성되어있다.
  - JobLauncher, Job, Stop, Flow 등이 여기 속함
- **Batch Infrasturecture**
  - Application, Core 모두 공통 Infra위에서 빌드한다.
  - Job 실행의 흐름과 처리를 위한 틀을 제공한다.
  - Reader, Processor, Writer, Skip, Retry 등이 속한다.



## Spring Batch 시작

### @EnableBatchProcessing

- **총 4개의 설정 클래스**를 실행시키며 **스프링 배치의 모든 초기화 및 실행 구성**이 이루어진다.

- 자동 설정 클래스가 실행됨

  - 빈으로 등록된 모든 Job을 검색 => 초기화와 동시에 Job을 수행하도록 구성

  

### 4개의 초기화 설정 클래스

![image-20240802220421037](./01_Spring Batch.assets/image-20240802220421037.png)

1. **BatchAutoConfiguration**
   - 스프링 배치가 초기화 될 때 자동으로 실행되는 설정 클래스
   - Job을 수행하는 JobLauncherApplicationRunner 빈을 생성
2. **SimpleBatchConfiguration**
   - JobBuilderFactory와 StepBuilderFactory 생성
   - 스프링 배치의 주요 구성 요소 생성 - 프록시 객체로 생성된다.
3. **BatchConfigurerConfiguration**
   - BasicBatchConfigurer
     - SimpleBatchConfiguration 에서 생성한 프록시 객체의 실제 대상 객체 (target)을 생성하는 설정 클래스
   - JpaBatchConfigurer
     - JPA 관련 객체를 생성하는 설정 클래스



## Spring Batch 시작

![image-20240802223152415](./01_Spring Batch.assets/image-20240802223152415.png)

```java
@Configuration // Job을 정의 : 각각의 내용들을 설정하고 구성한다는 뜻
@RequiredArgsConstructor
public class HelloJobConfiguration {

    private final JobBuilderFactory jobBuilderFactory; // Job을 쉽게 생성하기 위함
    private final StepBuilderFactory stepBuilderFactory; // Step을 쉽게 생성하기 위함

    @Bean
    public Job helloJob(){
        return jobBuilderFactory.get("helloJob") // Job을 생성하는 부분
                .start(helloStep())
                .build(); // build하게 되면 Job의 구현체의 객체가 생성되게 된다.
    }
    
    // Step에서는 기본적으로 Tasklet을 무한반복시킨다.
    // RepeatStatus.FINISHED; 으로 한번만 실행하게끔 한다.
    @Bean
    public Step helloStep(){
        return stepBuilderFactory.get("helloStep") // Step을 생성하는 부분
                .tasklet(((stepContribution, chunkContext) -> { // Step안에서 단일 태스크로 수행
                    System.out.println("Hello Spring Batch");
                    return RepeatStatus.FINISHED;
                }))
                .build();
    }
}
```

1. @Configuration
   - 하나의 배치 Job을 정의하고 빈 설정
2. JobBuilderFactory
   - Job을 생성하는 빌더 팩토리
3. StepBuilderFactory
   - Stop을 생성하는 빌더 팩토리
4. Job
   - helloJob 이름으로 Job 생성
5. Step
   - hellpStep 이름으로 Step 생성
6. tasklet
   - Step 안에서 단일 태스크로 수행되는 로직 구현
7. Job => Step => Tasklet



![image-20240802223211582](./01_Spring Batch.assets/image-20240802223211582.png)

1. Job
   - 하나의 일의 단위 
2. Step
   - 하나의 일에서 무엇을 해야하는지에 대한 단계
   - Step에서는 기본적으로 Tasklet을 무한반복시킨다.
   - 
3. Tasklet
   - 실제 작업 내용
     - 즉 실제 비즈니스로직이 들어가야한다.



## DB 스키마 생성 및 이해

### Overview

1. 스프링 배치 메터 데이터
   - 여러 도메인들 (Job, Step, JobParameters)의 정보들을 업데이트, 조회할 수 있는 스키마 제공
   - 과거, 현재의 실행에 대한 정보, 실행에 대한 성공 여부 등을 관리해준다. => Log 찍어줌
   - DB와 연동할 경우 필수적으로 메타 테이블 생성
2. DB 스키마 제공
   - 파일 위치 : /org/springframework/batch/core/schema*.sql
   - DB 유형별로 제공
3. 스키마 생성 설정
   - 수동 생성
   - 자동 생성
     - spring.batch.jdbc.initialize-schema
       - ALWAYS : 
         - 스크립트 항상 실행
         - RDBMS 설정이 되어 있을 경우 내장 DB 보다 우선적으로 실행
       - EMBEDED
         - 내장 DB일 때만 실행되며 스키마가 자동 생성, [DEFAULT]
       - NEVER
         - 스크립트 항상 실행 안함
         - 내장 DB 일 경우 스크립트가 생성이 안되기 떄문에 오류 발생
         - 운영에서 수동으로 스크립트 생성 후 설정하는 것을 권장
           - **운영에서는 always로 하는 것은 위험하다.**



### DB 테이블 구성

- Meta Data를 저장한다.

![image-20240802232506323](./01_Spring Batch.assets/image-20240802232506323.png)

- **Job 관련 테이블**

  - **BATCH_JOB_INSTANCE**

    - Job이 실행될 때 JobInstance 정보가 저장
    - Job_name, job_key를 키로 하여 하나의 데이터가 저장
    - 동일한 job_name, job_key로 중복 저장될 수 없음

  - **BATCH_JOB_EXECUTION**

    - job의 실행 저보가 저장
    -  job 생성, 시작, 종료시간, 실행 상태, 메시지 등을  관리

  - **BATCH_JOB_EXECUTION_CONTEXT**

    - Job과 함께 실행되는 JobParameter 정보를 저장

  - **BATCH_JOB_EXECUTION_PARAMS**

    - Job의 실행동안 여러가지 상태정보, 공유 데이터를 직렬화 (Json)해서 저장
    - Step간 거로 공유가 가능하다

    

- **Step 관련 테이블**

  - **BATCH_STEP_EXECUTION**
    - Step의 실행정보가 저장
  - **BATCH_STEP_EXECUTION_CONTEXT**
    - Step 별로 저장되며 Step간 서로 공유할 수 없음
    - Step의 실행동안 여러가지 상태 정보, 공유데이터를 직렬화해서 저장



### DB Table Columns

#### **BATCH_JOB_INSTANCE**

- JOB_INSTANCE_ID : 고유하게 식별할 수 있는 기본 키
- VERSION : 업데이트 될 때 마다 1씩 증가
- JOB_NAME : JOB을 구정할 떄 부여하는 이름 (잡을 생성할 떄 string으로 지정해준다.)
- JOB_KEY : Job_name과 jobParameter를 합쳐 해싱한 값을 저장



#### **BATCH_JOB_EXECUTION**

- JOB_EXECUTION_ID : 기본키, JOB_INSTANCE와 일대 다 관계
- VERSION : 업데이트 될 때마다 1씩 증가
- JOB_INSTANCE_ID : JOB_INSTANCE의 키 저장
- CREATE_TIME : 생성 시점
- START_TIME : 시작 시점
- END_TIME : 종료 시점 / **Job 실행 중 오류 시 값이 저장되지 않을 수 있음 (NULL)**
- STATUS : 실행 상태를 저장 (COMPLETED, FAILED, STOPPED)
- EXIT_CODE : 실행 종료 코드
- EXIT_MESSAGE : 실패일 경우 원인
- LAST_UPDATED : 마지막 실행 시점



#### **BATCH_JOB_EXECUTION_PARAMS**

- JOB_EXECUTION_ID : 식별 키, JOB_EXECUTION과 일대다
- TYPE_CD : STRING, LONG, DATE, DOUBLE 타입 정보
- KEY_NAME : 파라미터 키 값
- STRING_VAL 
- DATE_VAL
- LONG_VAL
- DOUBLE_VAL
- IDENTIFYING : 식별 여부 (TRUE, FALSE) => 식별할지말지 



**BATCH_JOB_EXECUTION_CONTEXT**

- JOB_EXECUTION_ID
- SHORT_CONTEXT : JOB의 실행 상태정보, 공유데이터등의 정보를 문자열로 저장
- SERIALIZED_CONTEXT : 직렬화된 전체 ㅓㄴ텍스트



**BATCH_STEP_EXECUTION**

- STEP_EXECUTION_ID : Step 의 실행정보를 고유하게 식별할 수 있는 기본 키 
- VERSION : 업데이트 될 때마다 1씩 증가 
- STEP_NAME : Step 을 구성할 때 부여하는 Step 이름 
- JOB_EXECUTION_ID : JobExecution 기본키, JobExecution 과는 일대 다 관계 
- START_TIME : 실행(Execution)이 시작된 시점을 TimeStamp 형식으로 기록 
- END_TIME : 실행이 종료된 시점을 TimeStamp 으로 기록하며 Job 실행 도중 오류가 발생해서 Job 이 중단된 경우 값이 저장되지 않을 수 있음 
- STATUS : 실행 상태 (BatchStatus)를 저장 (COMPLETED, FAILED, STOPPED…) 
- COMMIT_COUNT : 트랜잭션 당 커밋되는 수를 기록 
- READ_COUNT : 실행시점에 Read한 Item 수를 기록 
- FILTER_COUNT : 실행도중 필터링된 Item 수를 기록 
- WRITE_COUNT : 실행도중 저장되고 커밋된 Item 수를 기록 
- READ_SKIP_COUNT :  실행도중 Read가 Skip 된 Item 수를 기록 
- WRITE_SKIP_COUNT : 실행도중 write가 Skip된 Item 수를 기록 
- PROCESS_SKIP_COUNT : 실행도중 Process가 Skip 된 Item 수를 기록 
- ROLLBACK_COUNT : 실행도중 rollback이 일어난 수를 기록 EXIT_CODE 실행 종료코드(ExitStatus) 를 저장 (COMPLETED, FAILED…) 
- EXIT_MESSAGE : Status가 실패일 경우 실패 원인 등의 내용을 저장 
- LAST_UPDATED : 마지막 실행(Execution) 시점을 TimeStamp 형식으로 기록



**BATCH_STEP_EXECUTION_CONTEXT**

- STEP_EXECITION_ID
- SHORT_CONTEXT
- SERIALIZED_CONTEXT





















