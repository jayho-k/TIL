# RetainDB 조사

조사일: 2026-07-11

## 공식 자료

- 공식 사이트: https://www.retaindb.com/
- Hermes provider README: https://github.com/NousResearch/hermes-agent/tree/main/plugins/memory/retaindb
- Raw README: https://raw.githubusercontent.com/NousResearch/hermes-agent/main/plugins/memory/retaindb/README.md
- GitHub: 공식 사이트 footer에서 GitHub 링크가 있으나 이 조사 단계에서는 repo 세부 확인 전

## 정확한 역할

RetainDB는 AI agent용 persistent memory / company brain / agent filesystem을 제공하는 managed memory layer다.

공식 사이트는 세 가지 축을 강조한다.

- Agent Memory: user preference, correction, decision, history
- Company Brain: Slack, GitHub, docs, tickets, files 등 company knowledge
- Agent Filesystem: memory/document/decision을 agent가 path처럼 읽을 수 있는 context로 노출

Hermes provider README 기준으로는 cloud memory API이며 hybrid search(Vector + BM25 + Reranking)와 7 memory types를 제공한다.

## 무엇을 어디에 저장하는가

RetainDB 서비스 내부에 저장한다.

공식 사이트 예시:

- after each agent turn: `db.user("usr_01").remember(userMessage)`
- before response: `db.user("usr_01").getContext(userQuery)`
- automatic: `runTurn(...)`으로 retrieve-generate-store를 묶음

Hermes provider config:

- `RETAINDB_API_KEY`
- `RETAINDB_BASE_URL`
- `RETAINDB_PROJECT`

Hermes tools:

- `retaindb_profile`: user stable profile
- `retaindb_search`: semantic search
- `retaindb_context`: task-relevant context
- `retaindb_remember`: fact store with type + importance
- `retaindb_forget`: delete memory by ID

## 저장만 하는가, 더 많은 기능이 있는가

저장 이상이다.

기능:

- per-user isolated memory
- preference/correction/history 저장
- context injection before response
- hybrid retrieval
- BM25 + vector + reranking
- SDK / MCP / Memory Router
- company brain connectors
- agent-readable filesystem
- self-hosted option 언급
- retention/deletion control
- encryption at rest/in transit

공식 사이트는 self-hosted option을 "your Cloudflare account, your Postgres instance"로 설명한다.

## Qdrant / Postgres / MinIO와 결합 가능성

### Postgres

가능성 높음. 공식 사이트가 self-hosted option에서 "your Postgres instance"를 언급한다. 다만 실제 self-host 문서와 schema/adapter 공개 수준은 추가 확인 필요.

### Qdrant

직접 지원 여부 확인 안 됨. RetainDB는 hybrid search를 자체 제공하는 managed layer로 보는 편이 안전하다. 기존 Qdrant와 병행하면 중복 search layer가 된다.

### MinIO

Company Brain / filesystem / files를 강조하지만 MinIO backend 직접 지정 가능 여부는 확인되지 않았다.

권장 구조:

- 원본 파일은 MinIO
- RetainDB에는 문서 URL, extracted text, object key, source metadata 저장
- company brain connector가 MinIO/S3 compatible을 지원하는지 추가 확인

## Chat Portal에 적합한 사용처

적합한 경우:

- 빠른 managed memory 도입
- per-user product memory
- SDK/MCP/Router로 기존 agent에 쉽게 붙이고 싶을 때
- memory + company brain + agent filesystem을 단일 제품으로 쓰고 싶을 때
- self-hosted Postgres option이 실제로 충분히 열려 있을 때

주의:

- managed API 의존도가 높다.
- Qdrant를 직접 쓰기 어렵다면 기존 vector DB 전략과 충돌한다.
- self-host 문서와 커스텀 storage backend를 반드시 확인해야 한다.

## Chat Portal 적용 판단

우선순위 중간.

RetainDB는 product integration 속도는 빠르지만, 이미 Qdrant/Postgres/MinIO가 있는 Chat Portal 입장에서는 "내부 인프라와 결합 가능한가"가 핵심이다. 공식 사이트의 Postgres self-host 가능성은 긍정적이나, Qdrant/MinIO 활용은 불확실하다.

