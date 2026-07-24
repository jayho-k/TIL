# Hindsight 조사

조사일: 2026-07-11

## 공식 자료

- 공식 사이트: https://hindsight.vectorize.io/
- Storage docs: https://hindsight.vectorize.io/developer/storage
- Hermes provider README: https://github.com/NousResearch/hermes-agent/tree/main/plugins/memory/hindsight
- Hermes provider raw README: https://raw.githubusercontent.com/NousResearch/hermes-agent/main/plugins/memory/hindsight/README.md

## 정확한 역할

Hindsight는 Vectorize의 long-term memory provider다. Hermes README 기준으로 knowledge graph, entity resolution, multi-strategy retrieval을 제공한다.

운영 모드:

- Cloud: Hindsight Cloud API
- Local Embedded: Hermes가 local Hindsight daemon을 띄움. PostgreSQL 내장
- Local External: 기존 Hindsight instance에 HTTP로 연결

## 무엇을 어디에 저장하는가

Hermes README 기준:

- memory bank 단위로 저장
- `bank_id` 또는 `bank_id_template`으로 profile/workspace/platform/user/session 기반 격리 가능
- retain path:
  - conversation turns를 retain
  - entity extraction
  - tags/source/metadata 부여
- recall path:
  - observation
  - world
  - experience

README는 observation을 raw facts 위에 구축되는 consolidated knowledge layer로 설명한다. observation은 deduplicated beliefs, evidence, proof counts, freshness signals를 가진다.

Local embedded는 built-in PostgreSQL을 사용한다고 설명한다.

## 저장만 하는가, 더 많은 기능이 있는가

저장 이상이다.

기능:

- knowledge graph
- entity resolution
- auto retain
- auto recall
- recall budget
- recall type filtering
- tags filtering
- Hindsight reflect: cross-memory LLM synthesis
- observations: raw fact를 consolidation한 지식 계층
- cloud/local embedded/local external 선택

Hermes tools:

- `hindsight_retain`: 정보 저장 + entity extraction
- `hindsight_recall`: semantic + entity graph search
- `hindsight_reflect`: LLM-powered cross-memory synthesis

## Qdrant / Postgres / MinIO와 결합 가능성

### Postgres

좋다. Local Embedded가 built-in PostgreSQL을 사용한다. 다만 기존 Chat Portal Postgres를 직접 backend로 쓸 수 있는지, 또는 Hindsight 전용 Postgres를 띄워야 하는지는 추가 확인 필요.

### Qdrant

README 기준 Qdrant backend 지원은 확인되지 않았다. Hindsight가 자체 embedding/reranking/search stack을 갖는 것으로 보인다.

### MinIO

직접 object storage 역할은 아니다. conversation/memory graph 중심이다. MinIO와 엮으려면 원본 파일은 MinIO에 두고, Hindsight에는 extracted text, URL, object key, metadata를 retain해야 한다.

## Chat Portal에 적합한 사용처

적합한 경우:

- entity graph 기반 agent memory가 필요할 때
- raw fact보다 consolidated observation을 선호할 때
- local embedded/self-hosted 옵션이 필요할 때
- profile/workspace/user/session 기반 bank isolation이 필요할 때
- recall뿐 아니라 reflect/synthesis까지 맡기고 싶을 때

주의:

- Hindsight의 내부 schema와 기존 Postgres 통합 가능성은 추가 확인 필요
- Qdrant를 중심 vector store로 쓰고 싶다면 중복 인프라가 될 수 있다.
- LLM 기반 retain/reflect 비용과 latency를 평가해야 한다.

## Chat Portal 적용 판단

우선순위 중간~높음.

Hindsight는 단순 memory store보다 "entity-aware memory graph + observation layer"에 가까워 Chat Portal의 장기 사용자/프로젝트 memory에 유용하다. 기존 Postgres와는 맞을 가능성이 있지만, Qdrant/MinIO 중심 구조와 직접 결합하려면 adapter 설계가 필요하다.

