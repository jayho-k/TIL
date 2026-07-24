# Mem0 PoC와 내부 코드 분석 가이드

> 목표: Mem0 도입 여부와 필요한 보강 범위를 측정 가능한 결과로 판단한다.  
> 실험 코드 위치: [`../code/`](../code/README.md)

## PoC의 원칙

- document RAG 개선과 personal durable memory 개선은 다른 문제다. 이번 PoC는 Mem0의 personal memory 효과를 독립적으로 검증한다.
- Control은 기존 conversation/RAG, Treatment는 strict scope filter를 적용한 top-N Mem0 fact recall이다.
- golden set, prompt, 모델, max context token, authorization fixture를 고정한다.
- raw Mem0 API를 browser/client에 직접 공개하지 않는다.

## 단계별 검증

### P0. V3 ADD-only와 correction

1. 같은 사실을 표현만 바꿔 두 번 입력한다.
2. exact hash 외 중복이 누적되는지 확인한다.
3. explicit `update()`/`delete()` 후 Qdrant, entity collection, SQLite history를 함께 확인한다.
4. PostgreSQL의 supersede 정책이 stale fact를 active context에서 제외하는지 확인한다.

**통과 기준:** superseded/deleted fact가 active prompt에 0회 주입된다.

### P1. Qdrant schema와 retrieval

1. `chat_portal_mem0`, `chat_portal_mem0_entities` 전용 collection을 만든다.
2. `tenant_id`, `project_id`, `memory_tier`, `status` payload index를 직접 provision한다.
3. semantic-only, semantic+BM25, entity boost의 precision·latency를 비교한다.
4. 한국어 fact set에서 expected default action accuracy를 측정한다.

**통과 기준:** baseline 이상 품질이며, token/p95 latency 증가가 사전에 정한 예산 안에 든다.

### P2. SQLite history와 실행 모델

1. 실제 `history_db_path`와 생성 테이블을 기록한다.
2. container/pod restart와 multi-worker에서 recent message context가 유지되는지 검증한다.
3. ephemeral/read-only SQLite가 extraction과 history API에 주는 영향을 측정한다.
4. PostgreSQL history adapter fork의 변경 범위와 운영 비용을 추정한다.

**통과 기준:** production의 local persistence·HA 요구와 충돌하지 않는 운영안을 선택할 수 있다.

### P3. 테넌트 권한

1. 같은 API key 환경에서도 다른 tenant의 search 결과가 0건인지 확인한다.
2. memory id만 아는 요청이 다른 tenant의 get/update/delete에 실패하는지 검증한다.
3. 필수 filter 누락 요청을 MemoryService가 거부하는지 확인한다.

**통과 기준:** cross-tenant negative test에서 누출 0건이다.

### P4. DeepAgents·LangGraph life cycle

1. L3 → L2 → L1 순서의 filtered recall을 context file로 materialize한다.
2. 각 항목에 memory id, path, evidence id, score를 기록한다.
3. agent/subagent candidate를 즉시 durable write하지 않고 outbox/review 노드로 보낸다.
4. recall outage, stale recall, promotion 실패 시 LangGraph의 retry/fallback을 확인한다.

**통과 기준:** memory 장애가 일반 대화 전체 장애로 전파되지 않고, agent가 사용한 memory의 provenance를 추적할 수 있다.

## 내부 코드 분석 순서

| 우선순위 | 확인 대상 | 확인할 질문 |
| --- | --- | --- |
| 1 | `mem0/configs/base.py` | history provider가 아닌 `history_db_path`만 있는가? |
| 2 | `mem0/memory/main.py` | V3 `add`가 언제 retrieval/extraction/batch insert를 수행하는가? |
| 3 | `mem0/memory/storage.py` | history/messages SQLite schema와 recent context 조회 방식은 무엇인가? |
| 4 | `mem0/vector_stores/qdrant.py` | collection, BM25, entity, filter, payload index는 어떻게 구성되는가? |
| 5 | `server/main.py`, `server/server_state.py` | REST server의 auth/config persistence가 tenant authorization을 보장하는가? |

코드 분석 결과는 “관찰한 commit/version”, “호출 경로”, “우리 아키텍처에 미치는 영향”, “후속 실험” 네 항목으로 `text/`에 남긴다. 추정과 실제 소스 관찰을 섞지 않는다.

## 실험 기록 템플릿

```markdown
## 실험: <이름>

- 날짜 / Mem0 commit / Docker image
- 가설
- Control과 Treatment
- 입력 데이터와 tenant fixture
- 측정 지표: quality, token, p95, error, leak count
- 결과
- 판정: 통과 / 보류 / 실패
- 후속 조치
```

## 참고 자료

- [Mem0 동작 원리와 제약](02_Mem0_동작원리_및_운영상_제약.md)
- [Agent Memory Provider 최종 리포트](../../../.codex/research/AgentMemory/agent_memory_provider_final_report.md)
- [Mem0 vs OpenViking 비교](../../../.codex/research/AgentMemory/mem0_openviking_chatportal_comparison.md)

