# MAP.md — 노트 전체 지도

> 이 파일은 Claude가 노트를 빠르게 찾기 위한 네비게이션 맵입니다.
> 새 노트를 추가할 때마다 여기에도 등록해주세요.

---

## AI/

### Matplotlib (`AI/Matplotlib/`)
- `01` ~ `17` — 그래프 기초, 축/범례/스타일, 저장, 바 그래프, 파이 차트, 산점도, 다중 그래프 (Jupyter)

### Pandas (`AI/pandas/`)
- `Pandas.md` — Pandas 기본 사용법

### Deep Learning (`AI/deep_learning/`)

**CNN** (`CNN/`)
- `AlexNet.md`, `VGGNet.md`, `ResNet.md`, `DenseNet.md`
- `Batch_Normalization.md`, `1x1Conv.md`, `VoVNet.md`, `ELAN.md`, `CSPNet.md`

**ObjectDetection** (`ObjectDetection/`)
- `01` Object Detection 개요 → `02` OpenCV 데이터셋
- `03` R-CNN → `04` SPPNet → `05` Fast RCNN → `06` Faster RCNN
- `07` OpenCV 실습 → `08~09` Faster RCNN 실습
- `10` SSD → `11~12` YOLO / 실습 → `13` RetinaNet → `14` EfficientDet
- `15` Segmentation(Mask RCNN)
- `YOLOv7.md`, `yolact.md`
- `socar1~8.md` — socar 실전 프로젝트 시리즈
- `99_` — 비교/정리 노트 (1x1conv vs FC, Separable Conv, 모델 비교)

**ActionDetection** (`ActionDetection/`)
- `SlowFast.md`, `deepSORT.md`

**Paper** (`deep_learning/paper/`)
- `Faster_R-CNN.md`, `Object Detection_Review.md`, `Terms for DL.md`

### Transformer (`AI/transformer/text/`)
- `01_RNN.md` → `02_Transformer.md` → `03_Encoder.md` → `04_Decoder.md`
- `05_hf.md` → `06_hf_tokenizer.md` — HuggingFace
- `11_ViT.md` — Vision Transformer

### vLLM (`AI/vllm/`)
- `KVcache.md` — KV Cache 원리
- `02_vLLM 고성능 원리.md` — PagedAttention 등
- `03_MQA_GQA.md` — Multi Query / Group Query Attention
- `04_OpenAICompatible.md` — OpenAI 호환 서버
- `05_vLLM Monitoring.md`
- `06_Multimodel load.md`

### Gemma (`AI/gemma/`)
- `gemma.md`

### Mem0 (`AI/mem0/`)
- `text/01_Mem0_기반_에이전트_메모리_아키텍처.md` — Mem0·Qdrant·PostgreSQL·MinIO·DeepAgents·LangGraph의 역할 경계
- `text/02_Mem0_동작원리_및_운영상_제약.md` — V3 ADD-only, Qdrant retrieval, SQLite history, server mode 제약
- `text/03_PoC와_내부코드_분석_가이드.md` — PoC 단계, 통과 기준, 내부 소스 분석 순서
- `text/04_고급_메타데이터_필터링.md` — filter 연산자, Qdrant indexing, 논리 조합과 검증 방법
- `text/05_리랭커_강화_검색.md` — Python·TypeScript reranker, provider별 설정, 성능·비용·fallback
- `text/06_비동기_메모리.md` — AsyncMemory API, 동시성·재시도·FastAPI·운영 계측
- `text/07_멀티모달_지원.md` — vision 설정, URL/base64 image 입력, privacy·용량·오류 처리
- `text/08_사용자_지침.md` — custom instruction, few-shot fact 추출, schema·version 관리
- `text/09_V3_메모리_알고리즘_마이그레이션.md` — V3 ADD-only, hybrid retrieval, entity linking, SDK migration
- `text/code_analize/` — Python OSS library mode source code 분석 노트
- `text/code_analize/09_PostgreSQL_State_Store_대체_설계.md` — SQLite history/recent-message를 PostgreSQL로 대체하는 wrapper·schema·동시성·업그레이드 상세 설계
- `code/` — Mem0 연동 및 검증 실험 코드

---

## CS/

### 자료구조 (`CS/data_structure/`)
- `01` 자료구조 개요 → `02` 시간복잡도 → `03` 배열/리스트
- `04` Stack → `05` Queue → `06` LinkedList → `07` HashTable
- `08` Tree → `09` Binary Tree → `10` Balanced Binary Tree → `11` Trie
- `cs_01_set.md`

### 알고리즘 (`CS/Algorithm/`)
- `01_Arr.md`, `02_List.md`, `03_String.md`, `04_Stack.md`, `05_Queue.md`
- `06_Tree.md`, `07_graph.md`
- `TwoPointer(tech).md`
- `0218_problem_solution.md` — 문제 풀이 모음

### 운영체제 (`CS/operating_system/`)
- `01` OS 개요 → `02` 컴퓨터 구조 → `03` 프로세스 관리 → `04` CPU 스케줄링
- `05` 프로세스 동기화 → `06` Deadlock → `07` 메모리 관리
- `08` 가상 메모리 → `09` 파일 시스템 → `10` 디스크 관리
- `Thread정리.md`
- **cs 시리즈**: `cs_01` Thread → `cs_02` IPC → `cs_03` 프로세스 주소공간
  → `cs_04` 시스템콜 → `cs_05` 인터럽트 → `cs_06` CPU 스케줄링
  → `cs_07` 페이징 → `cs_08` 페이지 교체 알고리즘 → `cs_09` 파일시스템
  → `cs_10` 동기/비동기 → `cs_11` blocking/nonblocking → `cs_12` Deadlock

### 네트워크 (`CS/network/`)
- **교재 시리즈**: `1장_2장` 네트워크/모델 → `3장` 데이터통신 → `4장` IP
  → `5장` ARP → `6장` IPv4/ICMP → `7-9장` → `10장` → `11장`
- **cs 시리즈**: `cs_01` OSI 7계층 → `cs_02` 3-way handshake → `cs_03` HTTP/HTTPS
  → `cs_04` (기타) → `cs_05` 흐름제어/혼잡제어 → `cs_06` 로드밸런싱
  → `cs_07` blocking/nonblocking
- `WebRTC.md`, `session_token_cookie.md`

### 데이터베이스 (`CS/Database/`)
- `cs_01` DB 언어 → `cs_02` 이상현상 → `cs_03` 정규화 → `cs_04` 트랜잭션
- `cs_05` SQL vs NoSQL → `cs_07` Stored Procedure → `cs_08` Redis
- `cs_09` ORM → `cs_10` SQL 문법
- `Query 관련.md`

### 컴퓨터 구조 (`CS/computer_architecture/`)
- `Principle_of_cpu/Principle_of_cpu.md`
- `muticoreCPU/muticoreCPU.md`

### 디자인 패턴 (`CS/design pattern/`)
- `01` 디자인 패턴 개요 → `02` AbstractFactory → `03` Factory Method
- `04` Singleton → `05` Composite → `06` Decorator → `07` State
- `08` Strategy → `09` Command → `10` Template Method

### 언어 (`CS/language/`)

**Python**
- 기초: `기본메소드연습/Python_grammer/01~07` (기초, 함수, 모듈, 자료구조, 예외, OOP)
- `GC.md`, `Multi_Processing/`, `Threading/`
- 내부 구조: `List 내부구조.md`, `sort 내부구조.md`, `heapq.md`
- `배열.md`

**Java**
- 기초: `Study/basic/basic.md`
- Advanced: `01~14` (Process/Thread, 동기화, volatile, synchronized, Lock, 생산자소비자, BlockingQueue, Atomic, Collection, ThreadPool, Future)
- Advanced2: `01~06` (인코딩, 네트워크, 리소스, HTTP, 리플렉션, 어노테이션)
- Advanced3: `01` 람다
- 이론: `HashMap.md`, `예외처리.md`, `overloading.md`, `객체지향.md`
- From_pjt: `int_Integer.md`

**JavaScript**
- `01_intro.md` → `02_JS.md` → `03_axios.md` → `04_vue_js.md`

**JVM**
- `jvm.md`, `g1gc.md`

**C**
- `01_C_basic.md`, `02_C_basic2.md`

**Common**
- `floating point.md`

---

## Server/

### Docker (`Server/Docker/text/`)
- `01` Docker 개요 → `02` 명령어 → `03` 이미지 → `04` Node.js와 Docker
- `05` Docker Compose → `06~07` 배포 → `08` 멀티 컨테이너

### Kafka (`Server/Kafka/Core/text/`)
- `01_Kafka.md` → `02_Client.md` → `03_Consumer.md` → `04_Cluster.md`

### Redis (`Server/Redis/`)
- `01` Redis 개요 → `02` 데이터 타입 → `03` 특수 명령어 → `04` 예제 → `05` 주의사항

### RabbitMQ (`Server/RabbitMQ/text/`)
- `01` 개요 → `02` Consumer → `03` PubSub → `04` Routing → `05` DeadLetterQueue
- `06` Transaction → `07` TCC

### Oracle (`Server/Oracle/`)
- `00` 설치 → `01` 아키텍처 → `02` 기초 → `03` SGA → `04` PGA
- `05` DataDictionary → `06` Wait Event → `07` AWR
- `파티션.md`, `CTAS.md`, `인덱스재생성.md`, `RAC튜닝.md`, `오라클setup.md`

### Prometheus (`Server/Prometheus/`)
- `01` Prometheus 개요 → `02` PromQL → `03` 함수 설정 → `04` 모니터링

### Airflow (`Server/Airflow/text/`)
- `01_Airflow.md` — DAG, Task Instance, XCom 기초
- `02_Deferrable_Operators.md` — Deferrable Mode 원리, Trigger 구현, 언제 쓸지
- `03_Dynamic_Task_Mapping.md` — expand(), trigger_rule, Pool, AirflowRescheduleException, 실전 파이프라인 패턴

### Celery (`Server/Celery/`)
- `01_Celery.md`, `02_Task(Retry, Exception).md`

### Flink (`Server/Flink/text/`)
- `01_flink란.md`

### StreamingDataLake (`Server/StreamingDataLake/`)
- `DataLake/DataLake.md`
- `Spark/RealTimeDataLake/spark.md`

### 기타 (`Server/etc/`)
- `Jenkins.md`

---

## Web/

### Spring

**Spring 기초** (`Web/Spring/Spring/`)
- `01` DI/IoC → `02` Bean → `03` 의존성 주입 → `04` Lombok

**Spring 심화** (`Web/Spring/Spring2/`)
- `01` SOLID → `02` DI/IoC 심화 → `03` Bean → `04` Singleton/Configuration
- `05` ComponentScan → `06` Autowired → `07` Bean 생명주기 → `08` Bean 스코프

**JPA** (`Web/Spring/JPA/`)
- `01` JPA 장점 → `02` Dialect → `03` JPA 기초 → `04` 영속성 컨텍스트
- `05` Entity Mapping → `06` 실습 → `07~08` 연관관계 매핑 → `09` 상속/MappedSuperclass
- `10` 프록시/EntityManager → `11` 타입

**JPA 활용** (`Web/Spring/JPA2/`)
- `01` DTO → `02` LazyLoading → `03` 컬렉션 → `04` OSIV

**JPQL** (`Web/Spring/JPQL/`)
- `01~03` JPQL 문법

**QueryDSL** (`Web/Spring/QueryDSL/`)
- `01` 기본 문법 → `02` 중급 문법 → `03` 동적 쿼리 → `04` 실전 적용

**SpringMVC** (`Web/Spring/SpringMVC/`)
- `01` 웹 애플리케이션 → `02` 서블릿 → `03` MVC 패턴 → `04` MVC 프레임워크

**SpringBatch** (`Web/Spring/SpringBatch/`)
- `01` Spring Batch 개요 → `02` Domain → `03` Job
- `Reader.md`, `Processor.md`, `Writer.md`, `Chunk Process.md`, `MultiThread.md`

**financialLedger** (프로젝트 중 정리) (`Web/Spring/financialLedger/`)
- Controller/Service/Repository, Entity/EntityListener, HttpEntity
- @RestControllerAdvice, Optional, SpringSession+Redis
- SuperBuilder, Builder, TestCode, Generic, int vs Integer

### Django (`Web/Django/`)
- `01` Django 개요 → `02` CRUD → `03` SQL → `04` Form → `05` 인증
- `DB.md`, `DjangoAndAI.md`, `REST API.md`, `fixrues.md`

### Vue (`Web/Vue/`)
- `Vue_Component.md`, `Vuex.md`, `Vuex정리.md`
- `JavaScript 정리.md`, `Vue2 와 3의 차이점.md`

### 대규모 시스템 (`Web/LargeScaleSystem/Practice/Text/`)
- `01` 대규모 시스템 설계 → `02` 분산 RDB → `03` Article API
- `04` Comment → `05` Like → `06` 조회수 → `07` 인기글 → `08` CQRS

### Gradle (`Web/Gradle/`)
- `Gradle.md`

---

## PS/ (Problem Solving)

| 폴더 | 플랫폼 |
|------|--------|
| `PS/Back_jun/` | 백준 |
| `PS/programmers/` | 프로그래머스 |
| `PS/swea/` | SWEA (삼성) |
| `PS/test/` | 기타 테스트 |
