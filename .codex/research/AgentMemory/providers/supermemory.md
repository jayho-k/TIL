# Supermemory 조사

조사일: 2026-07-11

## 공식 자료

- 공식 GitHub: https://github.com/supermemoryai/supermemory
- 공식 문서: https://supermemory.ai/docs
- Hermes provider README: https://github.com/NousResearch/hermes-agent/tree/main/plugins/memory/supermemory
- Raw README: https://raw.githubusercontent.com/NousResearch/hermes-agent/main/plugins/memory/supermemory/README.md

## 정확한 역할

Supermemory는 memory + RAG + user profile + connectors + file processing을 하나로 제공하는 context engine이다. 공식 README는 "memory and context layer for AI"라고 설명한다.

기능 범위가 넓다.

- Memory Engine
- User Profiles
- Hybrid Search
- Connectors
- File Processing
- MCP / plugins
- local self-host

## 무엇을 어디에 저장하는가

공식 README 기준:

- conversation에서 fact 추출
- user profile 자동 유지
  - static facts
  - dynamic recent context
- documents/files 업로드
  - PDF
  - images
  - videos
  - code
- connector data
  - Google Drive
  - Gmail
  - Notion
  - OneDrive
  - GitHub
  - Web Crawler

Hermes provider 기준:

- `container_tag`로 profile/project scope 분리
- full session conversation ingest
- automatic turn capture
- profile recall
- semantic search
- explicit memory tools
- session end에 conversations endpoint로 full session 1회 ingest

Supermemory local:

- `supermemory-server`가 `http://localhost:6767`에서 full Memory API 제공
- embedded graph engine
- local embeddings
- data는 `./.supermemory` directory에 저장

## 저장만 하는가, 더 많은 기능이 있는가

저장 이상이다.

기능:

- fact extraction
- temporal changes 처리
- contradiction resolution
- automatic forgetting
- user profile static/dynamic 분리
- hybrid search: RAG + memory
- connector auto-sync
- file processing
- multimodal extractor
- MCP server
- local mode
- framework integrations: LangChain, LangGraph, OpenAI Agents SDK 등

Hermes tools:

- `supermemory-save`
- `supermemory-search`
- `supermemory-forget`
- `supermemory-profile`

## Qdrant / Postgres / MinIO와 결합 가능성

### Qdrant

직접 결합성은 낮아 보인다. Supermemory는 "No vector DB config, no embedding pipelines"를 장점으로 내세운다. 즉 자체 context stack을 제공한다.

### Postgres

GitHub topics에 Postgres/Drizzle ORM이 보이고, repo가 오픈소스이므로 내부적으로 Postgres를 사용할 가능성이 있다. 하지만 공식 README 레벨에서는 사용자가 기존 Postgres를 backend로 지정하는 구조인지 확인되지 않았다.

### MinIO

file processing과 document upload를 제공하지만, MinIO/S3-compatible object storage를 backend로 지정 가능한지는 확인되지 않았다.

권장 구조:

- Supermemory를 별도 context engine으로 사용하거나
- 원본 파일은 MinIO에 유지하고, Supermemory에는 file/document를 별도 ingest
- 기존 Qdrant/Postgres와 통합하려면 self-host 내부 구조를 코드로 분석해야 한다.

## Chat Portal에 적합한 사용처

적합한 경우:

- memory + RAG + user profile + documents를 한 번에 맡기고 싶을 때
- connector 기반 company/personal brain이 필요할 때
- user profile을 자동 유지하고 싶을 때
- local self-host와 hosted platform을 모두 검토하고 싶을 때
- LangGraph/agent framework integration이 필요한 경우

주의:

- 기존 Qdrant/Postgres/MinIO를 중심으로 직접 제어하려는 구조와는 겹칠 수 있다.
- Supermemory가 제공하는 전체 context stack을 도입할지, 일부만 쓸지 결정해야 한다.
- local mode는 `./.supermemory` directory storage라 production infra에 맞추려면 내부 커스터마이징 확인 필요.

## Chat Portal 적용 판단

우선순위 중간~높음.

제품 기능은 강하지만, "기존 Qdrant/Postgres/MinIO를 활용한다"는 조건에서는 Mem0/Honcho보다 직접 결합성이 낮을 수 있다. 다만 user profile, contradiction handling, automatic forgetting, hybrid RAG+memory는 Chat Portal 설계에 참고 가치가 크다.

