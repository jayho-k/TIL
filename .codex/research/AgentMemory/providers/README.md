# Agent Memory Provider 조사 인덱스

조사일: 2026-07-11

## 목적

Chat Portal은 이미 다음 인프라를 사용한다.

- Vector DB: Qdrant
- RDB: PostgreSQL
- Object Storage: MinIO

따라서 memory provider를 볼 때 핵심 질문은 "좋아 보이는가"가 아니라 다음이다.

1. 정확히 어떤 역할을 하는가?
2. 무엇을 어디에 저장하는가?
3. 저장만 하는가, extraction/reasoning/profile/search까지 하는가?
4. Qdrant/Postgres/MinIO와 결합 가능한가?
5. local file 저장 전제라면 service backend로 커스텀 가능한가?

## 개별 조사 파일

- [Honcho](./honcho.md)
- [Honcho 심화](./honcho_deep_dive.md)
- [Mem0 통합본](./mem0.md)
- [OpenViking](./openviking.md)
- [Hindsight](./hindsight.md)
- [Hindsight 심화](./hindsight_deep_dive.md)
- [Holographic](./holographic.md)
- [RetainDB](./retaindb.md)
- [ByteRover](./byterover.md)
- [Supermemory](./supermemory.md)

## 빠른 비교

| SW | 주 역할 | 저장 모델 | Qdrant | Postgres | MinIO | Chat Portal 적합도 |
| --- | --- | --- | --- | --- | --- | --- |
| Honcho | reasoning-first stateful memory | Postgres + vector collections | 미확인 | 높음 | 간접 | 높음 |
| Mem0 | self-improving memory layer | Qdrant/SQLite 또는 Postgres+pgvector | 높음 | 높음 | 간접 | 높음 |
| OpenViking | URI 기반 context filesystem | viking:// hierarchy + 자체 context DB | 낮음/미확인 | 낮음/미확인 | URL ingest 간접 | 중간 |
| Hindsight | entity graph + observation memory | cloud/local Hindsight, local embedded Postgres | 미확인 | 중간~높음 | 간접 | 중간~높음 |
| Holographic | local SQLite fact store | SQLite + FTS5 | 낮음 | 낮음 | 낮음 | 낮음 |
| RetainDB | managed memory/company brain/filesystem | managed API, self-host Postgres 가능성 | 미확인 | 중간~높음 | 간접 | 중간 |
| ByteRover | local-first hierarchical context tree | local context files + optional cloud sync | 낮음 | 낮음 | 커스텀 필요 | 낮음~중간 |
| Supermemory | memory + RAG + profile + connectors | managed/local context engine | 낮음/미확인 | 미확인 | 미확인 | 중간~높음 |

## 현재 기준 추천 순위

### 1순위: Mem0

이유:

- Qdrant와 Postgres 양쪽 모두 공식 경로가 보인다.
- OSS/self-host 선택지가 있다.
- LangChain/LangGraph integration이 공식 문서에 있다.
- Chat Portal의 기존 인프라와 가장 직접적으로 맞는다.

확인할 것:

- 기존 Qdrant endpoint 연결 가능성
- Postgres와 history/metadata 분리 방식
- extraction prompt customization
- tenant/workspace/project namespace

### 2순위: Honcho

이유:

- Postgres 기반 data model이 명확하다.
- workspace/peer/session/message 모델이 Chat Portal과 잘 맞는다.
- 단순 retrieval보다 representation/reasoning 계층이 있다.
- DeepAgents sub-agent를 peer로 모델링할 가능성이 있다.

확인할 것:

- vector backend가 Qdrant로 교체 가능한지
- file upload storage와 MinIO 연동 가능성
- AGPL-3.0 라이선스 영향

### 3순위였으나 재평가 필요: Hindsight

이유:

- entity graph, observations, freshness/proof count 개념이 강하다.
- PostgreSQL/pgvector를 primary storage로 쓴다.
- MIT 라이선스다.
- LangGraph/LangChain integration이 tools, nodes, BaseStore adapter까지 직접 제공된다.
- reflect/synthesis까지 제공한다.

확인할 것:

- 기존 Chat Portal Postgres와 같은 cluster에 둘지 별도 cluster로 둘지
- Qdrant를 쓰지 않고 Postgres/pgvector 중심으로 memory를 분리해도 되는지
- DeepAgents graph에 recall/retain nodes를 붙일 수 있는지
- HindsightStore limitations가 Chat Portal 요구와 충돌하지 않는지

심화 조사 후 판단:

- "기존 Qdrant를 memory backend로 적극 활용"하려면 Mem0가 여전히 유리하다.
- "Postgres 기반 memory engine을 별도로 운영"해도 된다면 Hindsight는 Mem0와 1~2위를 다툴 수 있다.
- "multi-agent peer modeling"이 핵심이면 Honcho가 독특한 강점을 가진다.

### 개념 참고: OpenViking / ByteRover

둘 다 직접 도입보다는 설계 아이디어가 중요하다.

- OpenViking: `viking://` URI, abstract/overview/full tier, directory-recursive retrieval
- ByteRover: human-readable context tree, provenance, selective sharing

Chat Portal에서 직접 설계한다면:

```text
Postgres
├─ memory_nodes
├─ memory_edges
├─ memory_versions
├─ memory_profiles
└─ memory_permissions

Qdrant
└─ memory vectors with namespace/path metadata

MinIO
└─ raw artifacts, transcripts, source documents, snapshots
```

### 낮은 우선순위: Holographic

SQLite local plugin이라 현재 서비스 인프라와 맞지 않는다. trust score, contradiction, feedback 아이디어만 참고한다.

### 조건부 검토: RetainDB / Supermemory

둘 다 제품성은 강하지만 자체 managed/context stack 색이 강하다. 기존 Qdrant/Postgres/MinIO를 중심에 두고 싶다면 내부 커스터마이징 가능성을 더 확인해야 한다.
