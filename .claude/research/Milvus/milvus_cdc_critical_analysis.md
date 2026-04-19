# Milvus CDC 이중화 — Critical 분석 초안

> 원문: https://milvus.io/blog/milvus-cdc-standby-cluster-high-availability.md  
> 분석 목적: 글에서 주장하는 내용을 실제 운영 관점에서 비판적으로 검토

---

## 1. 아키텍처 요약 (학습 기반)

```
[Primary Cluster]
  └─ WAL (Woodpecker) ──► [CDC Node] ──► [Standby Cluster]
                                              └─ WAL replay
```

- CDC Node가 Primary의 WAL을 읽어서 Standby에 replay
- Standby는 읽기는 가능, 쓰기는 불가
- 3계층 HA 전략: Node-level(multi-replica) → Cluster-level(CDC) → Safety-net(Backup)

---

## 2. Critical Points — 글에서 숨기거나 축소한 문제들

### 2-1. CDC Node 자체가 SPOF (Single Point of Failure)

> 글의 주장: `replicas: 1` 설정으로 CDC 배포  
> 문제: CDC Node가 1개밖에 없음. CDC Node가 죽으면 replication이 멈춤.

- HA를 구축하기 위한 컴포넌트(CDC Node) 자체에 HA가 없다.
- 글도 솔직하게 인정함: *"Single CDC replica — Distributed CDC is planned for a future release"*
- **실제 운영 영향**: CDC Node가 재시작되는 동안(예: K8s pod eviction, OOM) replication lag이 누적됨.
  WAL 보존 기간 내에 복구되면 괜찮지만, 보존 기간이 얼마인지 글에 **명시 없음**.

### 2-2. "Seconds behind"는 Normal 조건에서만 성립

> 글의 주장: *"The standby stays seconds behind the primary under normal conditions"*  
> 문제: "Normal conditions"가 무엇인지 정의 없음.

- 대규모 insert 배치, index 빌드 중, 네트워크 congestion 상황에서 lag이 얼마나 커질 수 있는지 **벤치마크 없음**
- PostgreSQL의 경우 Streaming Replication에서 heavy write 시 수십 초~분 단위 lag도 발생함
- RPO(Recovery Point Objective)를 "seconds"로 보장한다는 SLA 수준의 근거가 없음
- **실제 운영 영향**: 장애 직전에 대용량 write가 있었다면, standby가 얼마나 뒤처져 있는지 알 수 없음.

### 2-3. BulkInsert 미지원 = 실제 AI 운영 시나리오와 충돌

> 글의 주장: *"BulkInsert is not supported while CDC is enabled"*  
> 문제: 벡터 DB의 가장 흔한 사용 패턴이 대규모 초기 로딩 또는 주기적 bulk 재색인임.

- RAG 파이프라인: 문서 업데이트 시 수백만 개 embedding을 재색인 → BulkInsert 의존
- 추천 시스템: 일별/주별 전체 아이템 벡터 갱신 → BulkInsert
- **실제 운영 영향**: CDC를 켜면 BulkInsert를 못 쓰고, BulkInsert를 쓰려면 CDC를 꺼야 함.
  CDC를 껐다 켜는 동안의 gap은 어떻게 처리? 글에서 언급 없음.
  
  [메모] : 그럼 다른 DB들은 어떻게 진행하는데? 분명 다른 실제 프로덕션을 운영하는 회사들에서도 milvus를 사용하거나 다른 vector db를 사용할텐데 고가용성 운영을 위해서 이중화 작업을 할거야. 다른 곳들은 어떻게 하길래 잘 운영하고 있는거지? 자체적으로 개발을 하는걸까? 

### 2-4. WAL 보존 기간 무언급 → 복구 가능 윈도우 불명확

- CDC 체크포인트 기반 복구는 WAL이 보존되어 있는 기간 내에서만 가능
- Woodpecker WAL의 기본 보존 기간이 얼마인지 글에 없음
- CDC Node가 몇 시간 다운되면 WAL이 이미 삭제된 시점까지 밀릴 수 있음
- **실제 운영 영향**: "CDC resumes from where it left off" 주장은 WAL 보존 기간 이내일 때만 성립

### 2-5. Split-brain 시나리오 미언급

- 네트워크 파티션 발생 시: Primary는 살아있는데 CDC Node가 Primary에 접근 불가
- 이 경우 Standby로 failover를 잘못 트리거하면 두 클러스터 모두 write를 받는 split-brain 발생
- 글은 *"Part 3: Managing failover"*를 아직 작성 안 했고, 이 부분이 가장 중요함

  [메모] : 아직 글이 없는지 확인해줘. 있으면 찾아서 분석해줘.
- **실제 운영 영향**: failover가 manual이면, 새벽 3시 장애 시 사람이 판단해야 함. 잘못된 판단 = 데이터 불일치

### 2-6. pchannel 수 하드코딩 문제

```python
pchannel_num = 16
```

- 왜 16인지 설명 없음
- Milvus 클러스터 설정(`rootcoord.dmlChannelNum`)에 따라 다를 수 있음
- 실제 클러스터의 pchannel 수와 다르게 설정하면 일부 채널의 데이터가 복제 안 될 수 있음
- **실제 운영 영향**: 검증 없이 따라 하면 silent data loss 발생 가능

### 2-7. Woodpecker WAL의 프로덕션 성숙도 미검증

- Woodpecker는 Milvus 2.6에서 도입된 신규 컴포넌트 (Kafka/Pulsar 대체)
- CDC도 v2.6.6에서 처음 지원
- 둘 다 동시에 신규 기능 → 충분한 프로덕션 검증 사례가 아직 없음
- **비교**: MySQL binlog replication은 20년 이상의 프로덕션 검증, PostgreSQL WAL shipping은 15년 이상
- 글이 이 기술들을 언급하며 동등하게 비교하는 건 misleading

---

## 3. 글에서 잘한 점 (공정한 평가)

- 3계층 HA 프레임워크(Node / Cluster / Backup)는 개념적으로 올바르고 명확함
- CDC Node가 Primary의 read/write path에 영향 없다는 점 (비동기 WAL 읽기) → 타당
- BulkInsert 미지원, Single replica 제약을 숨기지 않고 명시한 점은 정직함
- Standby를 read scaling에 활용하는 아이디어는 실용적

---

## 4. 타 DB와 비교 — "First major vector DB with WAL-based CDC" 주장 검증

| DB | 클러스터 레벨 복제 | 방식 | 성숙도 |
|----|------------------|------|--------|
| PostgreSQL | WAL Streaming Replication | WAL shipping | 15년+ |
| MySQL | Binlog Replication | Binlog | 20년+ |
| MongoDB | Replica Set | Oplog | 15년+ |
| Elasticsearch | Cross-Cluster Replication (CCR) | Soft-delete + checkpoint | 5년+ |
| Qdrant | 없음 (노드 레벨만) | - | - |
| Weaviate | 없음 (노드 레벨만) | - | - |
| Milvus CDC | WAL (Woodpecker) | WAL replay | 2026년~ (신생) |

→ 벡터 DB 중에서는 사실상 최초. 하지만 "proven technique"으로 포지셔닝하기엔 아직 이름.  
→ Elasticsearch CCR과 유사한 포지션이지만, ES CCR도 초기엔 버그가 많았음.

---

## 5. 실제 운영에서 고려해야 할 체크리스트

```
[ ] WAL 보존 기간 확인 및 설정
[ ] CDC Node 모니터링 및 알람 구성 (pod 재시작, lag 급증)
[ ] replication lag 메트릭 수집 (Prometheus 등)
[ ] pchannel 수를 실제 클러스터 설정에서 확인 (rootcoord.dmlChannelNum)
[ ] BulkInsert 대안 프로세스 설계 (CDC 일시 중단 → Bulk → CDC 재개 절차)
[ ] 정기 Failover 드릴 스케줄 수립 (글 권장)
[ ] Split-brain 방지 펜싱(fencing) 전략 수립 (Part 3 나오기 전까지 직접 설계 필요)
[ ] Standby를 read로 활용할 경우 lag-aware 라우팅 로직 필요
```

---

## 6. 질문해볼 만한 것들

1. Woodpecker WAL의 기본 보존 기간(retention)은 얼마이고, 어디서 설정하는가?
2. pchannel 수를 실제 클러스터에서 확인하는 방법은?
3. CDC가 활성화된 상태에서 Primary를 업그레이드하면 어떻게 되는가?
4. BulkInsert가 필요한 경우 CDC를 일시 중단하고 재개하는 공식 절차가 있는가?
5. replication lag을 모니터링하는 공식 메트릭 이름은?



## 7. 질문

- 다른 AI 서비스를 제공하는 회사에서 vector db를 사용하는 사례가 있는지.
- vector db를 사용하면 운영을 어떻게 하는지에 대한 reference가 있는지 추천 필요
- 해당 블로그를 읽어보고 싶음. 
- 그리고 지금 현재 상황에서 vector db HA를 유지해야하는데 여러 다양한 방법 조사 필요
