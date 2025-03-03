# 07_PopularArticle

> - Kafka Cluster 



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















