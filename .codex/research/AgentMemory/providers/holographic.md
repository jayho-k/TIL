# Holographic 조사

조사일: 2026-07-11

## 공식/준공식 자료

- Hermes provider README: https://github.com/NousResearch/hermes-agent/tree/main/plugins/memory/holographic
- Raw README: https://raw.githubusercontent.com/NousResearch/hermes-agent/main/plugins/memory/holographic/README.md

주의:

- 독립 제품/공식 문서는 확인하지 못했다.
- 현재 확인 가능한 정보는 Hermes memory plugin README가 전부에 가깝다.

## 정확한 역할

Holographic은 Hermes plugin 기준 **local SQLite fact store**다. FTS5 search, trust scoring, entity resolution, HRR-based compositional retrieval을 제공한다.

HRR은 Holographic Reduced Representations 계열로 보이며, compositional retrieval을 위한 vector algebra 성격의 기능으로 추정된다.

## 무엇을 어디에 저장하는가

README 기준:

- 기본 DB path: `$HERMES_HOME/memory_store.db`
- storage: SQLite
- search: SQLite FTS5
- optional: NumPy for HRR algebra
- config:
  - `db_path`
  - `auto_extract`
  - `default_trust`
  - `hrr_dim`

## 저장만 하는가, 더 많은 기능이 있는가

저장 이상이다.

Tools:

- `fact_store`
  - add
  - search
  - probe
  - related
  - reason
  - contradict
  - update
  - remove
  - list
- `fact_feedback`
  - helpful/unhelpful rating
  - trust score 학습

기능:

- local fact store
- FTS5 search
- trust scoring
- entity resolution
- contradiction handling
- feedback-based trust update
- optional auto_extract at session end

## Qdrant / Postgres / MinIO와 결합 가능성

### Qdrant

직접 결합성 낮음. SQLite/FTS5 중심 구조다. Qdrant를 쓰려면 Holographic의 search/storage를 재구현해야 한다.

### Postgres

직접 결합성 낮음. SQLite 전용 plugin으로 보인다. Postgres로 옮기려면 fact schema, FTS, trust score, relation/HRR 구조를 직접 재설계해야 한다.

### MinIO

해당 없음에 가깝다. fact store이지 object/document store가 아니다.

## Chat Portal에 적합한 사용처

적합한 경우:

- 로컬 단일 사용자 Hermes 환경
- 가벼운 fact store
- SQLite 기반 proof-of-concept
- trust scoring / contradiction / feedback 실험

부적합:

- Chat Portal처럼 중앙 RDB/Postgres/Qdrant/MinIO 기반 서비스
- multi-tenant production
- cloud DB / object storage 통합

## Chat Portal 적용 판단

우선순위 낮음.

아이디어는 참고할 수 있다.

- fact trust score
- contradiction action
- feedback으로 memory 품질 조정

하지만 인프라 관점에서는 로컬 SQLite 전제라 현재 서비스 요구와 맞지 않는다.

