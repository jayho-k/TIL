# ByteRover 조사

조사일: 2026-07-11

## 공식 자료

- 공식 사이트: https://www.byterover.dev/
- 공식 문서: https://docs.byterover.dev/
- Hermes provider README: https://github.com/NousResearch/hermes-agent/tree/main/plugins/memory/byterover
- Raw README: https://raw.githubusercontent.com/NousResearch/hermes-agent/main/plugins/memory/byterover/README.md
- 관련 논문: ByteRover: Agent-Native Memory Through LLM-Curated Hierarchical Context, arXiv 2604.01599

## 정확한 역할

ByteRover는 agent/team 간 project memory를 공유하는 **local-first hierarchical context memory**다. 공식 사이트는 "share the right context across your agents and team"을 강조한다.

Hermes provider 기준:

- `brv` CLI를 통한 persistent memory
- hierarchical knowledge tree
- tiered retrieval
- fuzzy text -> LLM-driven search

## 무엇을 어디에 저장하는가

Hermes provider README 기준:

- local-first
- working directory: `$HERMES_HOME/byterover/`
- cloud sync는 optional `BRV_API_KEY`
- knowledge tree에 facts, decisions, patterns 저장

공식 사이트 기준:

- memory는 context files로 저장된다.
- agent가 recall할 때 source links를 붙인다.
- cloud sync option이 있으며, memory files/folders를 선택적으로 share 가능하다.

관련 논문 기준:

- hierarchical Context Tree
- Domain / Topic / Subtopic / Entry 구조
- 각 entry는 relation, provenance, lifecycle metadata를 가진다.
- 외부 vector DB/graph DB/embedding service 없이 markdown files에 저장하는 방향을 제안한다.

## 저장만 하는가, 더 많은 기능이 있는가

저장 이상이다.

기능:

- context tree
- local-first memory files
- selective cloud sync
- team/agent access control
- source attribution
- fuzzy text search
- LLM-driven search escalation
- decisions/bug fixes/rules 저장
- agent/team shared memory

Hermes tools:

- `brv_query`: knowledge tree search
- `brv_curate`: facts, decisions, patterns 저장
- `brv_status`: CLI version, tree stats, sync state

## Qdrant / Postgres / MinIO와 결합 가능성

### Qdrant

낮음. ByteRover의 핵심은 "no vector DB"와 file-based context tree다. Qdrant를 사용하는 기존 구조와는 철학이 다르다.

### Postgres

낮음. Postgres 기반 memory service가 아니라 local context files + optional sync 중심이다.

### MinIO

간접 가능성은 있다. context files를 MinIO에 저장/동기화하도록 별도 sync layer를 만들 수는 있지만, 공식 경로는 local files/cloud sync다.

Chat Portal에서는 다음처럼 변환해야 한다.

- context tree를 Postgres table로 모델링하거나
- context files를 MinIO object로 저장하고 metadata를 Postgres에 저장하거나
- ByteRover를 그대로 쓰지 않고 hierarchy/provenance/source attribution 아이디어만 차용

## Chat Portal에 적합한 사용처

적합한 경우:

- agent coding workflow에서 decisions/rules/bug fixes를 파일 기반으로 남기고 싶을 때
- team이 memory files를 읽고 편집해야 할 때
- source attribution과 selective sharing이 중요할 때
- local-first coding assistant memory

부적합:

- 중앙 서비스형 Chat Portal
- 기존 Qdrant/Postgres/MinIO를 core storage로 쓰려는 경우
- multi-tenant SaaS memory backend를 직접 RDB에 넣고 싶은 경우

## Chat Portal 적용 판단

우선순위 낮음~중간.

제품 자체를 그대로 도입하기보다는 아이디어를 차용하는 쪽이 현실적이다.

차용할 아이디어:

- hierarchy: domain/topic/subtopic/entry
- provenance visible source
- team/agent selective sharing
- human-readable memory artifact
- local-first 파일 모델을 MinIO object + Postgres metadata 모델로 재해석

