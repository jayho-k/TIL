# Qdrant 저장과 인덱스 구조 — 공개 설계 사례 기반

> 학습 단계: 2 / 9  
> 조사 기준일: 2026-07-24  
> 목적: Qdrant의 write·검색·최적화가 서로 다른 단계로 진행되는 이유를 이해하고, 사용자별 subagent memory에서 index·storage 옵션을 어떤 검증 질문으로 선택해야 하는지 정리한다.

## 이 노트의 출처와 한계

| 출처 유형 | 사용한 자료 | 해석 원칙 |
| --- | --- | --- |
| 1차 기술 문서 | Qdrant 공식 Storage, Indexing, Optimizer, Search, Quantization 문서 | 기능 정의·제약·설정 의미의 근거로 사용 |
| 공개 고객 사례 | Dust, Fieldy AI 사례 | 실제 선택과 문제를 볼 수 있음. 성능·비용 결과는 Qdrant가 발행한 고객 사례이므로 독립 검증으로 취급하지 않음 |

---

## 1. Segment와 전체 흐름: Point는 저장 직후와 최적화 이후에 서로 다른 상태를 거친다

### 1.1 Segment란 무엇인가?

**Segment는 Collection 안의 Point들을 실제로 나누어 보관하고 검색하는 물리 저장 단위**다. Collection은 개발자가 이름을 붙여 만든 논리적인 검색 공간이고, Segment는 Qdrant가 그 Collection을 내부에서 여러 묶음으로 나누어 관리하는 단위다.

Qdrant 공식 Storage 문서에 따르면, Collection의 data는 여러 Segment로 나뉘며 **각 Segment는 독립적인 vector storage, payload storage, vector index, payload index, 그리고 내부 ID와 외부 Point ID를 연결하는 ID mapper**를 가진다. 즉 HNSW도 “Collection 전체에 단 하나”로만 존재한다고 이해하기보다, 최적화된 Segment가 각자 vector index를 갖고 Collection 검색 결과가 합쳐진다고 이해하는 편이 정확하다.

```text
Collection: technical_docs

  Segment A (최적화됨)
    ├─ Point P1, P2, P3 ...
    ├─ vector storage
    ├─ payload storage
    └─ HNSW / payload index

  Segment B (최적화됨)
    ├─ Point P4, P5 ...
    └─ HNSW / payload index

  Segment C (방금 쓰기 반영, 아직 최적화 중일 수 있음)
    ├─ 새 Point P6, P7 ...
    └─ 검색은 가능하지만 HNSW가 아직 없거나 완성 전일 수 있음
```

여기서 **Segment는 문서·사용자·하루치 batch를 뜻하지 않는다.** 예를 들어 PDF 한 파일의 모든 chunk가 같은 Segment에 반드시 들어가는 것도 아니고, 하루 batch의 Point만 하나의 Segment에 고정되는 것도 아니다. Segment는 Qdrant가 write·검색·최적화 효율을 위해 내부적으로 관리하는 저장 묶음이다.

| 구분 | 사람이 설계하는가? | 무엇을 나타내는가? | 이 노트에서 연결되는 역할 |
| --- | --- | --- | --- |
| Collection | 예 | 같은 vector schema와 검색·운영 설정을 공유하는 논리 공간 | `technical_docs`, `agent_memory` 같은 검색 경계 |
| Point | 예 | 검색할 최소 레코드 | 문서 chunk 하나 또는 memory fact 하나 |
| Segment | 아니오. Qdrant가 관리 | 여러 Point를 담는 내부 물리 저장·index 단위 | 새 write, HNSW build, merge가 일어나는 단위 |
| HNSW | Collection 설정과 optimizer가 관리 | Segment 안 vector의 근사 최근접 탐색 graph | 많은 Point에서 가까운 vector를 빠르게 찾음 |

### 1.2 Segment는 왜 필요한가?

Segment가 없다면 Point 하나가 새로 들어올 때마다 Collection 전체의 vector storage와 HNSW graph를 다시 정리해야 한다. 이는 일일 문서 batch나 agent memory의 지속 write에서 지나치게 비싸다. Qdrant는 새 data를 먼저 쓰기 가능한 Segment에 넣고, 이전 data가 있는 Segment는 계속 검색에 사용하게 하므로 **write와 search를 동시에 진행하면서도 전체 Collection을 매번 다시 만들지 않을 수 있다.**

```text
새 문서의 chunk 100개 upsert
  → 기존 HNSW Segment를 즉시 폐기하지 않음
  → 새 Point는 쓰기 가능한 Segment에 반영
  → 검색은 기존 Segment와 새 Segment에서 후보를 찾음
  → optimizer가 background에서 작은 Segment를 병합·정리하고 index를 구축
```

사용자 query가 들어오면 Qdrant는 관련 Segment들을 검색한 뒤 후보를 합쳐 최종 Top-K Point를 반환한다. 같은 Point가 서로 다른 Segment에 잠시 존재하더라도 Qdrant에는 중복 제거 과정이 있으므로, 애플리케이션이 Segment를 직접 선택하거나 결과를 합칠 필요는 없다.

### 1.3 쓰기 가능한 Segment와 최적화된 Segment의 차이

공식 문서에서 Segment는 추가 write가 가능한 **appendable** 상태일 수도 있고, 읽기·삭제 중심의 **non-appendable** 상태일 수도 있다. Collection에는 적어도 하나의 appendable Segment가 있어 새 Point를 받을 수 있다. 학습 단계에서는 이 상태 이름을 외우는 것보다 다음 차이를 이해하는 것이 중요하다.

| 상태를 단순화한 표현 | Point를 추가할 수 있는가? | 검색 방식의 특징 | 운영에서 보이는 현상 |
| --- | --- | --- | --- |
| 새/쓰기 중심 Segment | 가능 | HNSW가 아직 없거나 최적화가 덜 된 상태일 수 있음 | write 직후 검색은 되지만 지연 특성이 달라질 수 있음 |
| 최적화된 검색 중심 Segment | 일반적으로 새 Point 추가 대상이 아님 | HNSW·payload index를 활용해 빠르게 후보 탐색 | 안정적인 검색 경로의 주된 부분 |

이 표는 내부 구현의 모든 상태 전이를 단순화한 학습용 설명이다. 실제 Segment 구성과 최적화 시점은 `indexing_threshold`, storage 설정, workload에 따라 달라지며 Qdrant optimizer가 결정한다. Dust·Fieldy 같은 공개 고객 사례는 각자의 Segment 수나 전이 설정을 공개하지 않았으므로, 이 내부 구조는 Qdrant 공식 Storage·Optimizer 문서를 근거로 이해해야 한다.

### 1.4 Segment를 알면 일일 batch를 어떻게 읽어야 하는가?

하루에 문서를 적재할 때 “HNSW를 껐다가 다시 만들어야 하나?”라는 질문은 다음처럼 바뀐다.

```text
잘못된 생각
새 문서 batch → Collection 전체 HNSW를 다시 생성해야 함

Segment 관점
새 문서 batch → 새 Point가 쓰기 가능한 Segment에 들어감
             → 기존 최적화 Segment는 계속 검색에 사용됨
             → optimizer가 새 data가 담긴 Segment를 차례로 최적화함
```

따라서 소규모·중간 규모의 일일 증분 적재에서는 HNSW를 끈 뒤 매번 전체 index를 재구축하지 않는다. 다음 절의 optimizer backlog, unoptimized Segment, p95/p99는 바로 **새 Segment를 optimizer가 다음 batch 전까지 얼마나 잘 정리하는지**를 관찰하는 지표다.

### 1.5 Point 저장의 전체 흐름

Qdrant에서 write 요청은 한 번에 “영속화·검색 가능·HNSW 색인 완료”가 되지 않는다. 공식 low-latency search 문서가 설명하는 흐름은 다음과 같다.

```text
write request
  → WAL 기록: 영속화됨, 아직 검색 불가
  → update queue
  → unoptimized segment 반영: 검색 가능, 아직 vector index 없음
  → indexing optimizer
  → HNSW index 생성: 검색 성능이 최적 상태
```

### 개념

- **WAL(Write-Ahead Log)**: 변경을 먼저 순서대로 기록하는 로그다. WAL에 기록된 변경은 비정상 종료나 전원 손실 후에도 복구할 수 있다.
- **Segment**: shard 안에서 Point의 vector, payload, index 같은 자료구조를 보관하는 부분 저장 단위다.
- **Unoptimized segment**: update가 반영되어 검색은 가능하지만 HNSW가 아직 만들어지지 않았거나 최적화되지 않은 segment다.
- **Indexing optimizer**: 일정 크기·조건에 도달한 segment에 vector index를 만들고, 필요하면 merge·vacuum·storage 최적화를 수행하는 백그라운드 작업이다.

### 왜 중요한가

애플리케이션의 “저장 성공”은 최소한 WAL 영속화와 이후 반영을 의미하지만, 즉시 HNSW 성능으로 검색된다는 뜻은 아니다. 대량 write 또는 재색인 직후에는 검색 가능하더라도 unoptimized segment 때문에 지연 시간이 달라질 수 있다.

이것은 subagent memory에서 다음 질문으로 이어진다.

- memory write API가 성공을 반환한 뒤, 즉시 recall해야 하는가?
- 즉시 recall이 필요하다면 read-after-write를 어떤 기준으로 검증할 것인가?
- background ingestion이 밀릴 때 update queue와 optimizer가 search latency에 주는 영향을 어떻게 관찰할 것인가?

### 공개 사례와 연결

**Fieldy AI**는 **기존 데이터를 Qdrant로 옮길 때 bulk import 동안 indexing을 비활성화하고, 적재가 끝난 뒤 다시 활성화했다.** 이는 대량 적재 중마다 HNSW를 계속 재구축하는 비용을 피하고, serving-ready index는 적재 완료 후 한 번 구축하는 선택이다. 이는 online memory write가 지속되는 시스템과 초기 migration의 설정이 같을 필요 없다는 실제 사례다.

### 여기서 반드시 구분할 것 — Agent 장기기억과 문서 ingestion은 다르게 읽는다

#### 1) Agent의 장기기억을 저장하는 경우 — 지속적인 작은 write

Fieldy의 사례를 “새 Point 하나를 넣을 때마다 index를 끄고, 넣은 뒤 다시 켠다”로 이해하면 안 된다. **일반적인 agent 장기 memory의 지속 write에서는 HNSW를 켠 채 Point를 upsert한다.** Qdrant는 새 Point를 WAL과 unoptimized segment에 반영하고, background optimizer가 segment 병합과 HNSW 구축을 처리한다. 즉 새 memory는 다음처럼 들어간다.

```text
새 memory 발생
  → embedding 생성
  → vector + payload를 Qdrant에 upsert
  → 즉시 또는 segment 반영 뒤 검색 가능
  → optimizer가 background에서 index/segment 작업 수행
```

평소에는 index를 끄지 않는다. write가 짧게 몰리면 적절한 batch로 upsert하고, update queue·optimizer backlog·unoptimized segment가 search latency에 주는 영향을 관찰한다. Qdrant 공식 Bulk Upload 문서도 지속 bulk write 중에는 optimizer가 HNSW build, segment merge, quantization을 처리하며 search와 CPU·memory bandwidth·I/O를 경쟁한다고 설명한다.

agent memory도 **초기 migration, 대규모 backfill, 장기간 중단 뒤 누적된 대량 적재**처럼 한 번에 많은 Point를 넣는 예외 상황에서는 vector index 구축을 잠시 미뤘다가 적재 후 한 번 구축하는 방식을 검토할 수 있다. 운영 Collection을 검색 중이라면 index를 껐다 켜는 대신, 새 Collection을 별도로 bulk build하고 검증 뒤 alias를 교체하는 방식도 후보가 된다.

### `indexing`도 두 종류를 분리해서 본다

```text
Payload index
  → tenant_id, status, scope처럼 filter에 쓰는 field의 index
  → Collection 생성 직후, Point ingest 전에 만든 뒤 계속 유지

Dense HNSW vector index
  → vector 유사도 검색을 빠르게 하는 graph
  → 일반 online write에서는 켜 둠
  → 대량 일괄 적재 때만 일시 중지·적재 후 rebuild를 검토
```

Payload index를 대량 import 때 함께 껐다가 다시 만드는 것이 아니다. Qdrant 공식 문서는 filterable HNSW의 추가 edge가 payload index를 만든 뒤 HNSW를 구축할 때 생성되므로, 실제 filter field의 payload index는 **Point ingest 전에** 만들 것을 권장한다. 새 filter field를 나중에 추가하면 field index를 만든 뒤 HNSW rebuild가 필요할 수 있다.

#### 2) 문서를 저장하는 경우 — chunk를 지속적으로 추가하는 write

##### 일반 문서 검색에서 HNSW가 실제로 하는 일

문서를 chunk로 나눈다는 말보다 먼저 이해할 것은 **HNSW가 무엇을 인덱싱하는가**다. HNSW는 PDF·Word 파일이나 “문서 A”라는 논리 단위를 인덱싱하지 않는다. **각 Point의 dense vector를 graph의 node로 인덱싱하고, 의미가 가까운 vector끼리 edge로 연결해 둔다.**

문서 검색에서 chunk를 쓰는 이유는 HNSW가 chunk를 요구해서가 아니다. “질문과 관련 있는 문서 전체”보다 “질문에 답할 수 있는 작은 문맥”을 결과로 찾아 LLM에 넘기는 편이 보통 더 정확하고 token 비용도 작기 때문에, 애플리케이션이 문서를 검색 단위로 나누는 것이다. 각 검색 단위에 vector를 붙여 Point로 만들면, 그 Point가 HNSW graph의 node가 된다.

```text
문서 A
 ├─ chunk A-1 → Point P1 → dense vector v1 → HNSW graph의 node
 ├─ chunk A-2 → Point P2 → dense vector v2 → HNSW graph의 node
 └─ chunk A-3 → Point P3 → dense vector v3 → HNSW graph의 node

문서 B
 ├─ chunk B-1 → Point P4 → dense vector v4 → HNSW graph의 node
 └─ chunk B-2 → Point P5 → dense vector v5 → HNSW graph의 node
```

**보조 예시**로 사용자가 “환불 승인 기준은 무엇인가?”라고 묻는다고 하자. 질의 텍스트도 같은 embedding 모델로 dense vector가 된다. HNSW는 모든 문서를 처음부터 끝까지 읽지 않고, graph를 따라 질의 vector와 가까운 `P2`, `P5` 같은 chunk Point를 찾아 Top-K로 반환한다.

```text
사용자 query
  → query dense vector 생성
  → HNSW가 가까운 chunk node를 graph에서 탐색
  → Top-K Point ID와 score 반환
  → payload의 document_id / chunk_index 확인
  → 관련 chunk와 필요한 주변 문맥을 context로 조립
```

여기서 HNSW가 직접 하는 일은 **가까운 vector를 가진 Point를 빠르게 찾는 것**까지다. “P2가 어느 문서의 몇 번째 조각인지”, “앞뒤 문단도 함께 보여 줄지”, “어떤 형식의 답변으로 만들지”는 HNSW가 알지 못한다. 애플리케이션이 `document_id`, `chunk_index`, `source` 같은 payload로 원문 위치를 복원해 context를 조립한다. 즉 chunk는 HNSW의 핵심을 흐리는 별도 주제가 아니라, HNSW가 반환한 Point를 사람이 읽을 수 있는 문서 문맥으로 되돌리는 연결고리다.

##### 새 문서가 들어오면 HNSW는 어떻게 유지되는가?

일반적인 신규 문서 추가에서 HNSW를 끄거나, collection 전체 graph를 수동으로 다시 만들지 않는다. 새 문서의 chunk Point를 upsert하면 Qdrant는 먼저 쓰기를 받아 segment에 반영한다. 이후 background optimizer가 조건에 맞는 segment를 최적화하면서 HNSW index를 생성·병합한다. 아직 최적화되지 않은 segment도 검색 경로에서 처리할 수 있으므로, 새 문서를 넣기 위해 기존 검색을 멈출 필요가 없다.

```text
새 문서
  → chunk별 dense vector 생성
  → Point upsert
  → 새/미최적화 segment에 반영
  → 검색은 기존 HNSW segment와 새 data를 함께 고려
  → background optimizer가 segment를 최적화하고 HNSW index를 생성·병합
```

따라서 운영자가 매 문서마다 관리하는 대상은 “HNSW graph를 껐다 켜기”가 아니라 **collection의 HNSW 설정과 optimizer가 적재량을 따라가는지**다. 문서가 지속적으로 아주 많이 들어오면 optimizer의 HNSW build·segment merge가 검색과 CPU, memory bandwidth, I/O를 경쟁할 수 있다. 이때는 batch 크기와 적재 속도를 조절하고 optimizer backlog를 관찰한다. 반대로 최초 수백만 건처럼 한 번에 큰 corpus를 옮기는 경우에만, Fieldy 사례처럼 vector indexing을 일시 중지한 bulk import 후 재활성화를 검토한다.

| 문서 적재 상황 | HNSW 관점의 기본 처리 |
| --- | --- |
| 문서 1건 또는 작은 batch를 계속 추가 | HNSW를 켠 채 Point를 upsert하고 optimizer에 맡긴다. |
| 지속적인 대량 ingestion | HNSW는 유지하되 batch·속도를 조절하고 optimizer backlog를 관찰한다. |
| 최초 대규모 corpus migration/backfill | indexing 일시 중지 후 bulk 적재·재활성화를 별도로 검토한다. |

##### 일일 배치에서 HNSW를 계속 켤지 판단하는 운영 지표

“하루 한 번 적재하니 indexing을 꺼야 하는가?”는 Point 수만으로 바로 답할 수 없다. **이번 배치가 끝난 뒤 Qdrant가 index 작업을 따라잡는지와, 그 시간의 실제 검색 품질이 서비스 기준을 지키는지**를 함께 본다. 아래 네 항목은 그 판단을 위한 관찰 지표다. Qdrant가 이 네 항목에 공통된 단일 임계값을 제공하는 것은 아니므로, 서비스의 허용 지연 시간과 서버 자원에 맞춰 기준을 정한다.

| 관찰 항목 | 무엇을 뜻하는가 | 왜 HNSW 유지 판단에 필요한가 | 문제가 계속될 때 먼저 할 일 |
| --- | --- | --- | --- |
| optimizer backlog | write 뒤 남아 있는 segment 최적화, HNSW build, segment merge 작업의 밀림 | optimizer가 다음 배치 전까지 일을 끝내지 못하면 새 write가 누적되어 index 작업이 계속 뒤처진다. | batch 크기·속도를 낮추거나 저부하 시간대로 옮긴다. |
| 검색 p95/p99 지연 | 정렬한 검색 요청 중 각각 95%, 99%가 그 시간 안에 끝난다는 지연 시간 | 평균 지연은 일부 느린 검색을 숨긴다. 배치 중 늦어지는 사용자의 실제 경험을 본다. | batch 속도를 낮추고, 검색과 적재의 자원 경쟁 여부를 확인한다. |
| unoptimized segment의 지속 누적 | 새 Point가 들어온 뒤 HNSW/segment 최적화가 아직 끝나지 않은 segment가 계속 남는 상태 | 일시적인 미최적화는 정상이다. 그러나 계속 늘면 optimizer 처리량보다 write량이 크다는 신호다. | 적재량을 분할하고 optimizer가 회복할 시간을 준다. |
| write와 search의 자원 경쟁 | ingestion과 HNSW build가 CPU·memory bandwidth·disk I/O를 사용해 검색 요청과 같은 자원을 쓰는 상태 | HNSW를 켠 online ingestion의 비용은 이 경쟁으로 나타난다. | batch를 throttling하고, 필요하면 적재 시간대·자원을 분리한다. |

**1) optimizer backlog는 무엇인가?**

Point를 upsert했다고 곧바로 모든 Point가 최적화된 HNSW segment에 들어가는 것은 아니다. optimizer는 background에서 작은 segment를 병합하고, 조건에 맞으면 HNSW index를 만든다. 여기서 backlog는 그 background 작업이 처리하지 못하고 남아 있는 양 또는 시간으로 이해하면 된다.

```text
01:00 일일 batch 시작
  → 새 chunk Point가 segment에 들어감
  → optimizer가 HNSW build·segment merge 수행
  → 02:00 이전에 작업이 안정화됨
  → 다음 날 batch 전까지 backlog 없음: HNSW 유지 운영이 가능한 신호

반대 경우
  → 01:00 batch의 최적화가 다음 날 01:00에도 남아 있음
  → 다음 batch가 기존 작업 위에 다시 쌓임
  → 지속적으로 처리량이 부족하다는 신호
```

여기서 중요한 것은 “backlog가 잠깐 생겼는가”가 아니라 **일일 적재 주기 안에 다시 안정 상태로 돌아오는가**다. 일시적인 backlog만으로 index를 끌 이유는 없다. 여러 배치 동안 누적될 때 batch 속도 조절, 인프라 확장, 또는 재구축 작업의 별도 collection 전환을 검토한다.

**2) 검색 p95/p99 지연은 무엇인가?**

검색 요청 100개를 빠른 순서로 정렬했을 때, 95번째 요청의 시간이 p95이고 99번째 요청의 시간이 p99이다. 예를 들어 p95가 250ms라면 검색 100개 중 95개는 250ms 이내에 끝났다는 뜻이다. 평균이 80ms여도 일부 요청이 수 초 걸리면 사용자에게는 느린 서비스가 될 수 있으므로, 배치 전·중·후의 p95/p99를 비교한다.

```text
배치 전:  p95 180ms, p99 320ms
배치 중:  p95 210ms, p99 380ms  → 서비스 기준 안이면 HNSW 유지 가능
배치 중:  p95 900ms, p99 4s    → 적재와 index 작업이 검색을 압박하는지 조사
```

위 수치는 원리 설명용 보조 예시이며, 허용 지연 시간은 제품의 요청 경로와 SLA/SLO가 결정한다. Qdrant만의 보편적인 p95/p99 기준은 없다.

**3) unoptimized segment가 계속 누적된다는 것은 무엇인가?**

새 Point가 들어온 직후 unoptimized segment가 존재하는 것은 정상이다. Qdrant는 이 data도 검색할 수 있도록 처리하지만, 최적화된 HNSW segment만으로 검색할 때와 같은 비용·지연 특성을 항상 보장하지는 않는다. 따라서 일일 batch가 끝난 뒤 unoptimized segment가 줄어드는지, 또는 날이 갈수록 남은 작업이 늘어나는지를 본다.

```text
정상:   batch 직후 증가 → optimizer 실행 → 다음 batch 전 감소 또는 안정화
경고:   batch 직후 증가 → 충분한 시간이 지나도 유지 → 다음 batch에서 다시 증가
```

후자라면 “HNSW가 문제라서 즉시 꺼야 한다”가 아니라, 현재 write 속도와 index 작업량이 서버의 처리량을 초과한다는 뜻이다. 우선 ingestion을 작은 batch로 쪼개거나 간격을 두고, 검색 트래픽이 적은 시간에 실행한다.

**4) write와 search가 경쟁한다는 것은 무엇인가?**

문서 batch는 embedding 생성 이후에도 Qdrant에 Point를 쓰고, optimizer는 HNSW graph build·segment merge를 수행한다. 이 작업들은 CPU, memory bandwidth, disk I/O를 쓴다. 동시에 들어온 검색은 vector 탐색과 payload filter를 위해 같은 자원을 사용한다. 따라서 batch 시간에 CPU·I/O 사용량과 함께 p95/p99가 올라간다면, 두 작업의 자원 경쟁이 검색 지연으로 나타나는 것이다.

```text
batch write 증가
  → optimizer의 HNSW build·merge 증가
  → CPU / memory bandwidth / disk I/O 사용 증가
  → 동시 search의 대기 또는 처리 시간 증가
  → p95/p99 상승
```

이 네 항목을 관찰한 뒤의 판단 순서는 다음과 같다. **일일 배치가 끝난 뒤 backlog와 unoptimized segment가 회복되고, 배치 중 p95/p99가 서비스 기준 안이면 HNSW는 계속 켜 둔다.** 반대로 여러 일 동안 회복되지 않거나 검색 기준을 반복해서 넘으면, 먼저 batch throttling·시간대 조정·자원 확장을 검토한다. 전체 재색인처럼 큰 작업일 때만 indexing을 일시 중지하거나 별도 collection을 구축해 alias를 바꾸는 선택으로 넘어간다.

`document_id`, `source`, `created_at` 같은 payload index는 HNSW와 역할이 다르다. HNSW는 **의미가 가까운 chunk vector를 찾는 graph index**이고, payload index는 예를 들어 `tenant_id = A` 또는 `source = policy`처럼 **검색 대상을 먼저 제한하는 filter index**다. 두 종류를 함께 쓰면 “A 테넌트의 정책 문서 범위에서 의미가 가까운 chunk”를 찾는다.

##### 문서를 넣을 때 MultiVector를 기본으로 쓰는가?

아니다. **“문서”라는 데이터 타입이 MultiVector를 결정하지는 않는다.** 일반 문서/RAG ingestion의 기본은 문서를 적절한 chunk로 나누고, 각 chunk를 Point 하나와 dense vector 하나로 저장하는 방식이다. 새 문서가 추가되면 해당 chunk Point들을 upsert하면 되고, 매번 HNSW를 풀고 다시 만들지 않는다.

```text
일반 문서 추가
문서 → chunk 1, chunk 2, ...
     → dense embedding 각각 생성
     → Point 각각 upsert (HNSW는 유지)
```

MultiVector는 ColBERT·ColPali·ColQwen처럼 **한 문서/페이지에서 token 또는 patch별 vector 행렬을 출력하는 late-interaction 모델을 채택했을 때** 고려한다. 이때도 “MultiVector니까 HNSW를 무조건 건다”가 정답은 아니다. Qdrant 공식 가이드는 MultiVector가 보통 dense 1차 retrieval 뒤의 reranking에 쓰이므로, token-level MultiVector field에는 HNSW를 끄고(`m=0`) dense field로 후보를 먼저 찾은 뒤 MultiVector `max_sim`으로 재정렬하는 구성을 권장한다. 한 문서가 수백 token vector를 만들 수 있어 그 모든 vector를 HNSW에 넣으면 RAM·insert 시간·compute 비용이 크게 늘기 때문이다.

```text
late-interaction 문서 검색의 흔한 2단계
dense field + HNSW         → 빠르게 후보 100개 검색
ColBERT MultiVector field  → 후보 100개만 정밀 rerank
```

따라서 판단 순서는 다음과 같다.

| 상황 | 일반적인 시작 선택 | 새 문서가 들어올 때 |
| --- | --- | --- |
| 짧은 agent memory, 일반 텍스트 문서 | dense vector 1개 + HNSW | Point/chunk를 그냥 upsert |
| 고유 ID·코드·이름 recall도 중요 | dense + sparse hybrid 평가 | 두 vector representation을 함께 upsert |
| ColBERT/ColPali 같은 late-interaction 모델을 실제 채택 | dense 1차 retrieval + MultiVector rerank 평가 | dense와 MultiVector를 저장, MultiVector HNSW는 보통 끔 |
| 초기 migration/대규모 backfill | payload index 선생성, 필요 시 vector indexing 일시 중지 | 대량 적재 후 index build/rebuild 및 품질 검증 |

이 표는 Qdrant 기능과 공개 권고를 우리 문서/agent memory 문제에 연결한 설계 보조 자료다. 실제 batch 크기, HNSW parameter, online write 허용량은 vector 차원·payload 크기·hardware·QPS에 따라 benchmark로 결정해야 한다.

---

## 2. HNSW와 Exact Search

### 2.1 HNSW란 무엇인가

Qdrant의 dense vector index는 현재 HNSW(Hierarchical Navigable Small World)다. HNSW는 vector를 다층 그래프로 구성한다. 상위 계층은 성긴 탐색 경로를 제공하고, 아래 계층으로 내려갈수록 더 가까운 이웃을 탐색해 전체 vector를 모두 비교하지 않고 근접 후보를 찾는다.

```text
상위의 성긴 graph
  → 질의와 가까운 영역을 빠르게 찾음
  → 더 조밀한 하위 graph로 이동
  → Top-K 후보 반환
```

HNSW의 핵심 trade-off는 다음과 같다.

| 파라미터 | 뜻 | 값을 높일 때의 일반적 효과 |
| --- | --- | --- |
| `m` | graph에서 node당 최대 연결 수 | recall과 index 메모리 증가 |
| `ef_construct` | index 생성 중 고려하는 이웃 후보 수 | index build 시간·품질 증가 |
| `hnsw_ef` | query 때 유지하는 후보 집합 크기 | query latency·recall 증가 |

HNSW는 근사 최근접 이웃 검색이다. 즉 빠른 대신 모든 상황에서 전수 비교와 완전히 같은 순서·결과를 보장하지는 않는다.

### 2.2 Exact Search와 full scan

**Exact Search**는 HNSW를 우회하고 모든 후보 vector를 비교하는 방식이다. 검색 결과를 안정된 순서로 받아 offset pagination을 해야 하거나, 작은 Collection에서 정확한 비교 기준이 필요할 때 쓸 수 있다. 대신 데이터가 커질수록 지연 시간이 증가하므로 일반적인 대규모 online recall의 기본값은 아니다.

Qdrant query planner는 조건이 만족하는 Point 수가 작다고 추정하면 HNSW보다 full scan을 선택할 수 있다. 따라서 “HNSW를 만들었으니 모든 질의가 HNSW를 탄다”는 가정은 틀릴 수 있다.

### 실제 사례와 연결

**Fieldy AI**는 현재 architecture에서 HNSW를 dense vector similarity에 사용한다고 공개했다. 이는 장기간 축적되는 transcript memory에서 online recall 지연 시간을 우선한 선택이다. 반면 Fieldy가 Exact Search를 사용하는지, `m`·`ef_construct`·`hnsw_ef` 값을 어떻게 조정하는지는 공개되지 않았다.

### subagent memory에 남는 질문

- memory recall은 approximate result를 허용하는가, 아니면 정확한 감사·페이지 조회와 분리해야 하는가?
- 높은 recall을 위해 `hnsw_ef`를 올릴 때 실제 QPS와 P95/P99 latency는 어떻게 변하는가?
- 짧은 private scope처럼 후보 수가 적은 질의는 planner의 full scan이 더 합리적인가?

---

## 3. Payload index와 filterable HNSW

### 3.1 Payload index란 무엇인가

Payload index는 JSON payload field에 만드는 인덱스다. 일반 document database의 secondary index와 비슷하게 filter를 빠르게 처리한다.

```text
vector query
  + payload filter (예: group_id = tenant-A)
  → 해당 범위에서 가까운 vector 검색
```

Qdrant 공식 문서는 filtered query를 최적화할 때 HNSW 파라미터보다, 실제 filter에 사용하는 payload field의 index가 더 큰 효과를 내는 경우가 많다고 설명한다.

### 3.2 filterable HNSW가 필요한 이유

filter가 거의 없는 경우에는 HNSW graph를 그대로 탐색할 수 있다. filter가 매우 강하면 payload index로 후보를 좁힌 뒤 전수 비교할 수 있다. 하지만 중간 정도로 선택적인 filter에서는 둘 다 비효율적일 수 있다. Qdrant는 indexed payload 값에 기반한 추가 edge를 HNSW graph에 넣어 filter 조건을 만족하면서도 graph 탐색을 계속할 수 있게 한다.

중요한 운영 제약은 다음과 같다.

1. payload index는 가능한 한 **data ingest 전에** 만든다.
2. 이미 적재한 뒤 payload index를 만들면, 기존 HNSW graph가 그 index를 이용하는 extra edge를 갖도록 HNSW rebuild가 필요하다.
3. 모든 payload field를 index하지 않는다. 메모리 한계가 있다면 결과를 가장 많이 좁히는 field를 먼저 고른다.

### 공개 설계와 연결

Qdrant의 공식 멀티테넌시 설계는 `group_id`에 keyword payload index를 만들고, `is_tenant=true`로 tenant별 vector를 함께 배치한다. 이는 tenant filter가 모든 query에 붙는 워크로드에서 filter를 단순한 사후 조건이 아니라 storage·HNSW 구성의 일부로 취급한 예다.

**Dust**는 shared multi-tenant Collection으로 통합하면서 payload filtering과 sharding을 사용했다고 공개했다. 정확한 index field 목록은 비공개지만, data source별 Collection을 없앤 뒤에는 payload 기반 범위 제한이 검색 경로의 핵심이 됐다고 해석할 수 있다.

### subagent memory에 남는 질문

- 모든 read에 반드시 붙는 scope field는 무엇인가?
- `tenant_id`만 index할지, `project_id`·`status`·`memory_scope`까지 index할지 실제 filter 선택도와 query 빈도로 판단했는가?
- filter field를 적재 후에 추가했다면 HNSW rebuild와 검색 품질·지연을 검증했는가?

---

## 4. Segment와 optimizer

### 개념

shard는 여러 Segment로 구성된다. Segment는 shard Point 일부의 vector·payload·index 자료구조를 보관한다. Segment 수에는 trade-off가 있다.

| Segment 구성 | 장점 | 비용 |
| --- | --- | --- |
| 더 적고 큰 Segment | 큰 HNSW graph를 적게 탐색하므로 search throughput에 유리 | build·rebuild가 오래 걸려 write와 optimization이 느려질 수 있음 |
| 더 많고 작은 Segment | indexing과 update 처리에 유리 | query가 더 많은 Segment를 조사해 search 성능이 낮아질 수 있음 |

Qdrant optimizer는 이 trade-off를 백그라운드에서 조정한다.

- **Vacuum optimizer**: 물리적으로 즉시 제거하지 않고 soft-delete된 Point가 쌓이면 segment를 재구축해 정리한다.
- **Merge optimizer**: 작은 segment가 너무 많아지면 병합한다.
- **Indexing optimizer**: 일정 vector 크기 이상이 되면 HNSW와 memmap 같은 storage/index 구성을 적용한다.

최적화 중에도 기존 segment는 읽을 수 있다. Qdrant는 copy-on-write segment를 사용해 변경을 처리한다. 다만 continuous write와 query가 CPU·memory·I/O를 두고 경쟁할 수 있으므로, optimizer가 있다는 사실이 write cost를 없애 주지는 않는다.

### 실제 사례와 연결

**Fieldy AI**의 bulk import 중 indexing 비활성화는 optimizer와 index build의 비용을 한 번에 통제한 사례다. 반대로 지속적으로 memory를 추가하는 서비스라면 index를 계속 껐다 켜는 방식보다, write rate·optimizer 지연·unoptimized segment 검색 시간을 계측해야 한다.

**Dust**는 수천 data source와 대량 upsert/delete에서 memory-mapped vector가 disk로 밀려날 때 search가 느려졌다고 설명한다. 이 사례는 Segment 내부 vector storage와 optimizer 정책이 Collection 수만큼이나 검색 성능에 영향을 준다는 점을 보여 준다.

---

## 5. RAM, on-disk storage, quantization

### 5.1 on-disk payload와 vector storage

Qdrant는 payload를 RAM에 두는 InMemory 방식과 disk에 두는 OnDisk 방식을 제공한다. 큰 원문·이미지처럼 payload가 클 경우 on-disk payload는 RAM 사용량을 줄일 수 있지만, filter가 disk payload를 매번 읽으면 지연 시간이 늘어난다. 이 때문에 공식 문서는 filter에 쓰는 field에는 payload index를 만들라고 권장한다. index된 field 값은 on-disk payload를 사용해도 RAM에 유지된다.

#### payload 저장 위치와 payload index는 다른 설정이다

`on_disk_payload`는 **payload 전체의 기본 저장 위치**를 정하는 Collection 설정이다. 반면 payload index는 “이 field를 filter 조건에 사용하겠다”는 선언이다. 두 설정은 함께 쓰이지만 같은 기능이 아니다.

```text
on_disk_payload = true
  → raw text를 포함한 payload의 기본 보관 장소는 disk

tenant_id payload index 생성
  → tenant_id의 값과 filter용 index 구조는 RAM에 유지
  → filter할 때 원본 payload를 disk에서 하나씩 읽지 않아도 됨
```

**보조 예시**로, 기술문서 chunk Point가 아래와 같다고 하자.

```json
{
  "tenant_id": "acme",
  "product": "payment-api",
  "version": "2.4",
  "status": "active",
  "document_id": "payment-guide-01",
  "chunk_index": 42,
  "heading": "Timeout and Retry",
  "raw_chunk_text": "길고 상세한 원문 chunk ..."
}
```

여기서 `raw_chunk_text`는 수백~수천 글자가 될 수 있지만, `tenant_id`, `product`, `version`, `status`는 짧은 값이다. 모든 payload를 RAM에 올리면 원문이 누적될수록 RAM을 많이 쓰므로 `on_disk_payload=true`로 원문을 disk에 둘 수 있다. 그러나 다음 검색에는 작은 field를 빠르게 확인해야 한다.

```text
"timeout 설정 방법" 검색
  + tenant_id = acme
  + product = payment-api
  + version = 2.4
  + status = active
```

index가 없다면 Qdrant는 HNSW가 탐색한 여러 후보 Point가 위 조건에 맞는지 확인하려고 각 Point의 payload를 disk에서 읽을 수 있다. 반대로 각 filter field에 payload index가 있으면, Qdrant는 RAM의 index를 이용해 먼저 조건에 맞는 Point 범위를 빠르게 판단한다.

```text
payload index가 없을 때
HNSW 후보 탐색
  → 후보마다 tenant_id / product / version 값을 disk에서 확인
  → disk I/O가 반복됨

payload index가 있을 때
RAM의 tenant_id / product / version index로 조건 확인
  → 조건을 만족하는 Point만 vector 검색 후보로 다룸
  → 최종 Top-K가 정해진 뒤에만 raw_chunk_text를 disk에서 읽어 반환
```

따라서 OnDisk payload의 목적은 “모든 payload를 느리게 만든다”가 아니다. **자주 filter하는 작고 구조적인 값은 RAM index에 남기고, 크지만 filter하지 않는 원문은 disk에 두는 역할 분리**다. 최종 결과 5~10개의 원문을 disk에서 읽는 비용은, filter 후보 수백·수천 개의 payload를 disk에서 반복 확인하는 비용과 다르다.

| payload field 예시 | 기본 판단 | 이유 |
| --- | --- | --- |
| `tenant_id` | keyword payload index | 모든 검색에서 테넌트 범위를 제한하는 filter이기 때문 |
| `product`, `version`, `status` | 실제 filter에 쓴다면 keyword payload index | 제품·버전·활성 상태 범위를 빠르게 좁힘 |
| `document_id` | 문서 단위 조회·삭제·재처리에 filter로 쓴다면 keyword payload index | 특정 원본 문서의 chunk만 찾거나 갱신할 때 필요 |
| `updated_at` | 기간 filter를 쓴다면 datetime payload index | 최신 문서, 특정 시점 이후 문서를 제한할 때 필요 |
| `chunk_index`, `heading` | 보통 index하지 않음 | 최종 결과의 위치·표시용 metadata이고 filter 조건이 아니라면 RAM index가 불필요 |
| `raw_chunk_text` | 보통 index하지 않고 OnDisk payload로 보관 | 긴 원문은 filter field가 아니며 index를 만들면 RAM 절약 목적이 사라짐 |
| 이미지 binary | Qdrant payload에 직접 보관하지 않는 것을 우선 검토 | object storage의 URL·checksum을 payload에 두는 편이 크기·전송·수명주기 관리에 유리 |

#### 코드는 무엇을 직접 설정하고, 무엇을 Qdrant가 처리하는가?

애플리케이션은 **Collection 생성 시 payload 저장 방식**과 **filter에 사용할 field index**를 한 번 설정한다. 이후 문서를 upsert할 때마다 RAM/disk 위치를 고르거나, 검색 때 index를 직접 호출하지 않는다. Qdrant가 설정된 storage와 index를 사용한다.

```python
from qdrant_client import QdrantClient, models

client = QdrantClient(url="http://localhost:6333")
collection = "technical_docs"

# 1. 큰 원문 payload의 기본 저장 위치를 disk로 설정한다.
client.create_collection(
    collection_name=collection,
    vectors_config=models.VectorParams(
        size=1024,  # 실제 embedding 모델의 차원으로 교체
        distance=models.Distance.COSINE,
    ),
    on_disk_payload=True,
)

# 2. 실제 filter 조건에 쓰는 field만 payload index로 선언한다.
for field_name in ("tenant_id", "product", "version", "status"):
    client.create_payload_index(
        collection_name=collection,
        field_name=field_name,
        field_schema=models.PayloadSchemaType.KEYWORD,
    )
```

문서를 넣을 때는 평소처럼 vector와 payload를 함께 upsert한다. `raw_chunk_text`에 별도의 “disk 저장” 코드를 붙일 필요는 없다. 위 Collection 설정이 적용된다.

```python
client.upsert(
    collection_name=collection,
    points=[
        models.PointStruct(
            id="payment-guide-01:chunk:42",
            vector=chunk_embedding,
            payload={
                "tenant_id": "acme",
                "product": "payment-api",
                "version": "2.4",
                "status": "active",
                "document_id": "payment-guide-01",
                "chunk_index": 42,
                "heading": "Timeout and Retry",
                "raw_chunk_text": long_chunk_text,
            },
        )
    ],
)
```

검색에서도 애플리케이션은 filter를 표현할 뿐이다. Qdrant는 해당 field의 payload index가 있으면 이를 자동으로 검색 계획에 사용한다.

```python
result = client.query_points(
    collection_name=collection,
    query=query_embedding,
    query_filter=models.Filter(
        must=[
            models.FieldCondition(
                key="tenant_id",
                match=models.MatchValue(value="acme"),
            ),
            models.FieldCondition(
                key="product",
                match=models.MatchValue(value="payment-api"),
            ),
            models.FieldCondition(
                key="version",
                match=models.MatchValue(value="2.4"),
            ),
        ]
    ),
    limit=5,
    with_payload=True,
)
```

payload index도 모두 같은 방식으로 둘 필요는 없다. Qdrant는 payload index 자체를 disk에 두는 옵션도 제공하지만, 이는 hot filter보다 크기가 크거나 드물게 쓰는 filter index에 맞는 선택이다. `tenant_id`처럼 모든 검색에서 쓰는 filter는 기본 RAM index로 두는 편이 지연 시간에 유리하다. 또한 index는 RAM과 disk 공간을 추가로 쓰므로, **“언젠가 filter할 수도 있는 모든 field”가 아니라 실제 query에 쓰고 결과를 많이 제한하는 field만** index로 만든다.

vector도 on-disk로 둘 수 있고, memory-mapped file을 사용한다. 이는 대량 vector를 다루는 데 도움이 되지만 disk I/O가 병목이 되면 latency가 커질 수 있다. persistent storage에는 Qdrant가 요구하는 POSIX 호환 block storage를 사용해야 하며, on-disk vector에는 SSD/NVMe가 권장된다.

### 5.2 Quantization

**Quantization**은 원본 vector를 더 작은 표현으로 압축해 RAM·storage 사용량과 검색 비용을 줄이는 기법이다. Qdrant는 scalar, binary, product, TurboQuant 등을 지원한다. 압축률이 높을수록 일반적으로 memory 사용량은 낮아지지만 검색 품질 손실 또는 rescoring 비용 가능성이 생긴다.

가장 단순한 예인 scalar quantization은 `float32 → uint8`로 각 component를 줄여 vector 메모리 사용량을 약 4분의 1로 만든다. 하지만 이 비율과 recall 손실은 embedding distribution과 parameter에 의존하므로, 공식 문서도 실제 data에서 test한 뒤 채택하라고 권고한다.

```text
원본 vector: disk에 보관
quantized vector: RAM에 보관
  → 빠른 1차 후보 탐색
  → 필요하면 원본 vector로 rescore
```

### 실제 사례와 연결

**Dust**는 scalar quantization을 사용해 vector storage 크기를 4분의 1로 줄이고, quantized vector는 RAM에, 원본 vector는 disk에 두는 방식으로 memory와 latency의 균형을 잡았다고 공개했다. 또 다른 Dust 공개 사례에서는 MMAP threshold와 scalar quantization을 함께 조정해 RAM footprint를 줄였다고 설명한다.

이 사례는 “on-disk가 항상 저렴하고 느리다” 또는 “모든 vector를 RAM에 둬야 한다”의 이분법보다, 원본·압축 vector의 배치와 rescoring을 함께 설계한다는 관점을 보여 준다. 다만 Dust의 data size·embedding·hardware가 공개되지 않았으므로 그대로 수치를 재현할 수는 없다.

---

## 6. WAL은 원장이나 분산 트랜잭션이 아니다

WAL은 Qdrant 내부에서 update를 안전하게 순서대로 기록하고 장애 후 복구하기 위한 장치다. WAL에 기록된 뒤에는 해당 변경을 잃지 않도록 설계되어 있지만, 이것만으로 애플리케이션의 다른 저장소와 원자적 transaction이 되는 것은 아니다.

예를 들어 memory system이 Qdrant 외에 PostgreSQL의 현재 상태·감사 로그와 object storage의 원문 근거를 함께 쓴다면 다음 부분 성공은 여전히 가능하다.

```text
PostgreSQL 상태 저장 성공
  → Qdrant write 성공
  → 원문 evidence 저장 실패
```

또는 반대 순서의 실패도 가능하다. Qdrant WAL은 Qdrant 내부 복구를 돕지만 여러 시스템을 묶는 outbox, idempotency, reconciliation 설계를 대신하지 않는다. 이 책임 분리는 7단계 생명주기·운영에서 다시 다룬다.

---

## 7. 사례 비교

| 사례 | 공개된 선택 | 해결하려던 문제 | 이 단계에서 얻는 교훈 | 한계 |
| --- | --- | --- | --- | --- |
| Qdrant 공식 멀티테넌시 | payload index를 ingest 전에 만들고 tenant index 사용 | filter가 붙는 대규모 tenant query | filter field는 data model과 HNSW 구성의 일부 | 실제 user/subagent scope schema는 제공하지 않음 |
| Fieldy AI | bulk import 중 indexing 비활성화 후 재활성화, HNSW + BM25 | 대량 migration throughput과 memory recall | migration mode와 online serving mode의 index 정책을 분리 | index parameter와 tenant 설계는 비공개 |
| Dust | scalar quantization, MMAP/storage tuning, shared Collection | RAM 압박과 disk spill로 인한 latency | storage·compression은 Collection topology와 함께 봐야 함 | 비용·latency 수치는 벤더 고객 사례라 독립 검증 아님 |

---

## 8. 이 단계에서 확정한 학습 결론

1. Qdrant write는 WAL 영속화, segment 반영, HNSW index 완료라는 서로 다른 시점을 가진다.
2. HNSW는 빠른 근사 검색이고 Exact Search는 작은 범위 또는 정확한 순서가 필요한 별도 도구다.
3. filtered recall의 첫 최적화 대상은 자주 쓰고 선택도가 높은 payload field의 index다. HNSW 파라미터 조정보다 먼저 검토한다.
4. payload index 생성 시점은 중요하다. filterable HNSW 효과를 내려면 ingest 전에 만들거나 이후 HNSW rebuild를 계획해야 한다.
5. Segment optimizer는 delete·merge·index 작업을 백그라운드로 처리하지만, 지속 write와 검색의 자원 경쟁은 남는다.
6. on-disk, quantization, rescoring은 각각 독립적인 “빠름/느림” 스위치가 아니라 memory·disk I/O·recall의 trade-off다.
7. WAL은 Qdrant 내부 내구성 장치이며 다른 DB·object storage와의 분산 transaction을 제공하지 않는다.

## 9. 아직 결정하지 않는 항목

- `tenant_id`, `user_id`, `agent_id`, `project_id`, `memory_scope`, `status` 중 실제 payload index 대상
- subagent memory write의 일관성 수준과 read-after-write 요구
- memory의 예상 Point 수, write QPS, query QPS, latency SLO
- vector를 RAM·disk·quantized RAM 중 어디에 둘지
- HNSW `m`, `ef_construct`, query `hnsw_ef` 값
- Exact Search와 indexed-only query를 언제 사용할지

이 항목은 다음 3단계에서 tenant와 Collection topology를 확정한 뒤, 실제 workload의 filter pattern과 benchmark로 결정한다.

## 출처

### 공식 1차 출처

- Qdrant, [Indexing](https://qdrant.tech/documentation/manage-data/indexing/) — 접근일 2026-07-24
- Qdrant, [Storage](https://qdrant.tech/documentation/manage-data/storage/) — 접근일 2026-07-24
- Qdrant, [Optimizer](https://qdrant.tech/documentation/operations/optimizer/) — 접근일 2026-07-24
- Qdrant, [Search](https://qdrant.tech/documentation/search/) — 접근일 2026-07-24
- Qdrant, [Low-Latency Search](https://qdrant.tech/documentation/search/low-latency-search/) — 접근일 2026-07-24
- Qdrant, [Quantization](https://qdrant.tech/documentation/quantization/) — 접근일 2026-07-24
- Qdrant, [Database Optimization FAQ](https://qdrant.tech/documentation/faq/database-optimization/) — 접근일 2026-07-24

### 공개 고객 사례

- Qdrant, [How Dust Scaled to 5,000+ Data Sources with Qdrant](https://qdrant.tech/blog/case-study-dust-v2/) — 2025-04-29, Qdrant 발행 고객 사례
- Qdrant, [Dust and Qdrant: Using AI to Unlock Company Knowledge](https://qdrant.tech/blog/dust-and-qdrant/) — Qdrant 발행 고객 사례
- Qdrant, [How Fieldy AI Achieved Reliable AI Memory with Qdrant](https://qdrant.tech/blog/case-study-fieldy/) — 2025-09-04, Qdrant 발행 고객 사례
