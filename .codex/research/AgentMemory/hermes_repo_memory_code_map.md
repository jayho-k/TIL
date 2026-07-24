# Hermes Agent Memory 코드 위치 맵

조사일: 2026-07-11

## 출처

- Repository: https://github.com/NousResearch/hermes-agent/tree/main
- 확인 기준: GitHub main branch, 2026-07-11 접근

## 결론

`agent/memory_manager.py`는 memory 저장 구현체가 아니라 provider orchestration layer다. Hermes memory 구조를 코드로 보려면 다음 파일들을 함께 봐야 한다.

## 핵심 파일

### 1. Durable facts: built-in memory tool

- GitHub: https://github.com/NousResearch/hermes-agent/blob/main/tools/memory_tool.py
- Raw: https://raw.githubusercontent.com/NousResearch/hermes-agent/main/tools/memory_tool.py

역할:

- file-backed durable memory 구현
- `MEMORY.md`: agent notes, environment facts, project conventions, tool quirks, lessons
- `USER.md`: user preferences, communication style, expectations, workflow habits
- 저장 위치: profile-scoped `HERMES_HOME/memories/`
- tool action: `add`, `replace`, `remove`
- batch operation 지원
- char limit 기반 bounded memory
- session 시작 시 frozen snapshot을 system prompt에 주입
- mid-session write는 disk에는 즉시 반영하지만 현재 session system prompt는 바꾸지 않음

중요 포인트:

- durable memory의 실제 built-in 저장 구조는 이 파일에 있다.
- Hermes 블로그의 Layer 1 durable facts를 보려면 이 파일이 우선이다.

### 2. Memory provider interface

- GitHub: https://github.com/NousResearch/hermes-agent/blob/main/agent/memory_provider.py
- Raw: https://raw.githubusercontent.com/NousResearch/hermes-agent/main/agent/memory_provider.py

역할:

- 외부 memory provider가 구현해야 하는 ABC
- `initialize`
- `system_prompt_block`
- `prefetch`
- `queue_prefetch`
- `sync_turn`
- `get_tool_schemas`
- `handle_tool_call`
- `on_session_end`
- `on_session_switch`
- `on_pre_compress`
- `on_memory_write`
- `on_delegation`
- `backup_paths`

중요 포인트:

- Hermes가 memory backend를 어떻게 추상화하는지 보려면 이 파일이 기준이다.
- `MemoryManager`는 이 interface를 호출하는 orchestrator다.

### 3. Provider orchestration

- GitHub: https://github.com/NousResearch/hermes-agent/blob/main/agent/memory_manager.py
- 현재 로컬 복사본: `.codex/research/AgentMemory/hermes_memory_manager.py`

역할:

- built-in provider + external provider를 agent runtime에 연결
- provider tool schema 주입
- prefetch/retrieval context 수집
- turn sync background 처리
- session boundary hook 전달
- built-in memory write를 external provider에 mirror
- memory context fencing/scrubbing

중요 포인트:

- 저장소 자체가 아니라 integration boundary다.
- durable facts 구조를 분석하려면 `tools/memory_tool.py`를 봐야 한다.

### 4. Session search

- GitHub: https://github.com/NousResearch/hermes-agent/blob/main/tools/session_search_tool.py
- Raw: https://raw.githubusercontent.com/NousResearch/hermes-agent/main/tools/session_search_tool.py

역할:

- long-term conversation recall
- SQLite session DB + FTS5 index 기반 검색
- 세 가지 모드:
  - discovery: `query`로 FTS5 검색
  - scroll: `session_id + around_message_id`로 특정 메시지 주변 탐색
  - browse: 최근 session 목록
- raw messages를 반환하며 LLM call은 하지 않음

중요 포인트:

- Hermes 블로그의 Layer 3 session search를 보려면 이 파일이 우선이다.
- 실제 DB primitive는 `hermes_state.py`의 `SessionDB` 쪽도 추가로 봐야 한다.

### 5. External memory providers

Directory:

- GitHub: https://github.com/NousResearch/hermes-agent/tree/main/plugins/memory

현재 확인된 provider:

- `plugins/memory/hindsight/`
- `plugins/memory/openviking/`
- `plugins/memory/mem0/`
- `plugins/memory/honcho/`
- `plugins/memory/byterover/`
- `plugins/memory/holographic/`
- `plugins/memory/retaindb/`
- `plugins/memory/supermemory/`

각 provider는 대체로 `__init__.py`에서 `MemoryProvider` 구현체를 정의한다.

#### Hindsight

- GitHub: https://github.com/NousResearch/hermes-agent/tree/main/plugins/memory/hindsight
- Raw: https://raw.githubusercontent.com/NousResearch/hermes-agent/main/plugins/memory/hindsight/__init__.py

특징:

- knowledge graph
- entity resolution
- multi-strategy retrieval
- cloud / local embedded / local external mode
- tools: `hindsight_retain`, `hindsight_recall`, `hindsight_reflect`
- auto recall / auto retain
- memory bank, tags, recall budget 설정

#### OpenViking

- GitHub: https://github.com/NousResearch/hermes-agent/tree/main/plugins/memory/openviking
- Raw: https://raw.githubusercontent.com/NousResearch/hermes-agent/main/plugins/memory/openviking/__init__.py

특징:

- `viking://` URI 기반 filesystem hierarchy
- tiered context loading
- automatic memory extraction
- session management
- semantic search + hierarchical directory retrieval
- resource ingestion
- built-in memory write를 OpenViking subdirectory로 mirror

#### Mem0

- GitHub: https://github.com/NousResearch/hermes-agent/tree/main/plugins/memory/mem0
- Raw: https://raw.githubusercontent.com/NousResearch/hermes-agent/main/plugins/memory/mem0/__init__.py

특징:

- Mem0 Platform API 또는 self-hosted OSS
- server-side LLM fact extraction
- semantic search
- automatic deduplication
- tools: `mem0_search`, `mem0_add`, `mem0_update`, `mem0_delete`

#### Honcho

- GitHub: https://github.com/NousResearch/hermes-agent/tree/main/plugins/memory/honcho
- Raw: https://raw.githubusercontent.com/NousResearch/hermes-agent/main/plugins/memory/honcho/__init__.py

특징:

- cross-session user modeling
- dialectic Q&A
- semantic search
- peer cards
- persistent conclusions
- tools: `honcho_profile`, `honcho_search`, `honcho_reasoning`, `honcho_context`, `honcho_conclude`

## Hermes 3-layer blog와 코드 매핑

| 블로그 계층 | 코드 위치 | 비고 |
| --- | --- | --- |
| Durable facts | `tools/memory_tool.py` | `MEMORY.md`, `USER.md` file-backed store |
| Procedural skills | `skills/`, `tools/skill_*`, `agent/skill_commands.py` | skill 저장/로드 구조는 별도 조사 필요 |
| Session search | `tools/session_search_tool.py`, `hermes_state.py` | SQLite + FTS5 session DB |
| Provider orchestration | `agent/memory_manager.py`, `agent/memory_provider.py` | backend 연결/동기화/라이프사이클 |
| External long-term memory | `plugins/memory/*/__init__.py` | Hindsight, OpenViking, Mem0, Honcho 등 |

## 다음에 가져와서 분석할 우선순위

1. `tools/memory_tool.py`
   - built-in durable memory 핵심
2. `tools/session_search_tool.py`
   - session search 핵심
3. `hermes_state.py`
   - SQLite session DB / FTS5 구현
4. `agent/memory_provider.py`
   - provider interface 계약
5. `plugins/memory/openviking/__init__.py`
   - OpenViking provider 구현
6. `plugins/memory/hindsight/__init__.py`
   - 가장 고급 long-term memory provider로 보임

