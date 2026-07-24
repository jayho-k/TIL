# Honcho 조사

조사일: 2026-07-11

## 공식 자료

- 공식 문서: https://honcho.dev/docs/v3/documentation/introduction/overview
- Architecture: https://honcho.dev/docs/v3/documentation/core-concepts/architecture
- GitHub: https://github.com/plastic-labs/honcho
- Hermes provider: https://github.com/NousResearch/hermes-agent/tree/main/plugins/memory/honcho
- 라이선스: GitHub 기준 AGPL-3.0

## 정확한 역할

Honcho는 단순 vector memory가 아니라 **stateful agent를 위한 reasoning-first memory infrastructure**다. 핵심은 대화/이벤트를 저장한 뒤, background reasoning으로 peer별 representation을 계속 갱신하는 것이다.

공식 문서 기준 핵심 primitive:

- Workspace: top-level namespace, application/environment/customer 분리
- Peer: 시간이 지나며 변하는 entity. user, agent, group, project, idea 등을 표현
- Session: peers 사이의 interaction thread
- Message: session 안에 들어가는 원자 데이터. 대화, 이벤트, 문서, 파일, activity 등

## 무엇을 어디에 저장하는가

공식 architecture 문서 기준:

- messages는 즉시 PostgreSQL에 저장된다.
- background queue에 reasoning task가 들어간다.
- worker가 logic, summary, insight, peer representation을 생성한다.
- conclusions/insights는 vector collection에 저장되어 retrieval된다.
- message는 JSONB metadata/structured data를 지원한다.

즉 저장 모델은 다음과 같다.

```text
PostgreSQL
├─ workspace
├─ peer
├─ session
├─ message
└─ queue / metadata

Vector collections
└─ reasoned conclusions / peer representations
```

GitHub README에는 내부적으로 peer 관련 observations를 vector-embedded document collection에 저장하며, collection은 `(observer, observed)` peer pair로 keying된다고 설명한다.

## 저장만 하는가, 더 많은 기능이 있는가

저장만 하는 도구가 아니다.

주요 기능:

- background reasoning
- peer representation 생성
- session context 생성
- peer card / compact identity summary
- hybrid search
- peer-to-peer perspective modeling
- session summary
- natural-language insight query
- MCP / SDK / Hermes integration

Honcho의 차별점은 raw transcript retrieval보다 "reasoned conclusion"을 만든다는 점이다.

## Qdrant / Postgres / MinIO와 결합 가능성

### Postgres

강하게 맞는다. 공식 architecture가 PostgreSQL write path를 전제로 한다. 이미 Postgres를 쓰는 Chat Portal과 구조적으로 가장 잘 맞는 편이다.

다만 self-host 시 Honcho가 자체 schema/server를 운영하므로, 기존 Postgres에 같은 DB로 넣을지 별도 DB/schema로 둘지 검토해야 한다.

### Qdrant

공식 문서에서는 "vector collections"라고 표현하지만 Qdrant를 직접 backend로 설정할 수 있는지는 이 조사 단계에서 확인되지 않았다. GitHub repo를 더 파서 vector store abstraction이 있는지 확인해야 한다.

현실적 선택:

- Honcho self-host의 기본 vector backend를 그대로 쓴다.
- 또는 Chat Portal의 Qdrant와 별도 vector store로 둔다.
- Qdrant 통합이 필요하면 Honcho 내부 vector collection 구현 교체 가능성을 코드로 확인한다.

### MinIO

문서에서는 messages가 documents/files도 받을 수 있다고 하며 `session.upload_file(...)` 기능이 보인다. 하지만 object storage backend를 MinIO로 바꿀 수 있는지 공식 문서만으로는 확인되지 않았다.

Chat Portal에서 MinIO를 쓰려면:

- 원본 파일은 MinIO에 저장
- Honcho에는 파일 URL, metadata, extracted text, summary를 message로 ingest
- Honcho를 원본 object store로 쓰지 않는 구조가 안전하다.

## Chat Portal에 적합한 사용처

적합한 경우:

- 사용자/agent/project를 peer로 모델링하고 싶을 때
- 단순 memory retrieval보다 "사용자에 대한 결론"이 필요할 때
- multi-agent, group chat, support ticket처럼 여러 참여자가 있는 경우
- 시간이 지나며 변화하는 user state를 관리해야 할 때
- Postgres 기반 self-host memory infrastructure가 필요할 때

부적합하거나 주의할 경우:

- Qdrant를 반드시 단일 vector backend로 써야 한다면 내부 교체 가능성 확인 필요
- AGPL-3.0 라이선스 영향 검토 필요
- reasoning-first라 write 이후 representation 반영이 async다. 즉시 일관성이 필요한 workflow는 별도 barrier가 필요하다.

## Chat Portal 적용 판단

우선순위 높음.

이유:

- Postgres와 자연스럽게 맞는다.
- 단순 memory API보다 data model이 명확하다.
- workspace/peer/session/message 모델은 Chat Portal의 user/workspace/project/session 구조와 잘 대응된다.
- DeepAgents의 sub-agent를 peer로 모델링할 수 있다.

추가 검증:

- self-host 구성에서 vector backend가 무엇인지
- Qdrant adapter 가능 여부
- file upload storage backend와 MinIO 연계 가능 여부
- AGPL 사용 가능성
- background reasoning 비용과 latency

