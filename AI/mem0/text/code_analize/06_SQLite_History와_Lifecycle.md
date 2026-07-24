# SQLite History와 Memory Lifecycle

> 분석 대상: `mem0/memory/storage.py`, `mem0/memory/main.py`의 CRUD·history·reset 경로  
> 기준 snapshot: 로컬 `mem0ai 2.0.12`; 2026-07-18에 upstream `main`도 SQLite 고정 wiring 여부를 재확인

## 결론

**SQLite는 Mem0의 기억 알고리즘에 필수인 데이터베이스가 아니다.** 다만 현재 Python OSS library mode의 `Memory`/`AsyncMemory` 구현이 `SQLiteManager`를 직접 생성하므로, 코드를 수정하지 않고 stock SDK를 쓰는 경우에는 구현상 필수로 따라온다. SQLite의 목적은 주 메모리 본문 저장이 아니라 다음 두 가지다.

1. 메모리 ADD/UPDATE/DELETE 변경 이력
2. 다음 사실 추출에 쓸 scope별 최근 대화 메시지 최대 10개

우리 구성에서는 이 두 역할도 PostgreSQL이 수행할 수 있으며, 운영에서는 그렇게 통합하는 편이 낫다. 단, `vector_store.provider`를 Qdrant나 pgvector로 바꾸는 설정과 이 내부 DB를 바꾸는 것은 별개다. 현재 공개 설정은 SQLite 파일 경로만 바꿀 수 있고 PostgreSQL history/message provider를 선택하는 기능은 없으므로, 작은 storage adapter/fork가 필요하다.

## 1. SQLite 초기화와 기본 경로

`SQLiteManager(db_path)`는 `sqlite3.connect(db_path, check_same_thread=False)`로 연결을 열고 thread lock을 둔다. 생성 시 다음을 실행한다.

```text
기존 history schema migration
→ history table 생성 보장
→ messages table 생성 보장
```

`MemoryConfig.history_db_path` 기본값은 `~/.mem0/history.db`다. 로컬 라이브러리 실험에는 편하지만, 여러 worker/pod가 있는 서비스에서 각 프로세스가 이 기본 경로를 쓰면 history와 최근 문맥이 인스턴스별로 분리된다.

### 1.1 설정만으로 PostgreSQL로 바꿀 수 있는가?

현재 snapshot과 확인한 upstream `main`에서는 **바꿀 수 없다**.

| 확인 지점 | 실제 구현 | 의미 |
| --- | --- | --- |
| `MemoryConfig` | `history_db_path: str`만 존재 | SQLite 파일 경로만 지정 가능 |
| `Memory.__init__()` | `self.db = SQLiteManager(self.config.history_db_path)` | provider factory나 생성자 주입점 없음 |
| `AsyncMemory.__init__()` | 동일하게 `SQLiteManager(...)` 직접 생성 | async 전용 PostgreSQL store도 없음 |
| sync/async `reset()` | 기존 DB를 닫은 뒤 다시 `SQLiteManager(...)` 생성 | 실행 중 `memory.db`만 바꾸는 monkey patch도 reset 후 깨짐 |

Mem0의 `vector_store`에는 Qdrant, pgvector 같은 provider 선택 구조가 있지만, `history`/`messages` 저장소에는 같은 추상화가 없다. 따라서 “Mem0가 PostgreSQL을 지원한다”는 설명을 곧바로 이 SQLite의 대체 가능성으로 읽으면 안 된다. `vector_store="pgvector"`로 설정해도 `self.db`는 별도로 SQLite를 연다.

`history_db_path=":memory:"`를 주면 디스크 파일은 없앨 수 있지만 여전히 SQLite이고, 프로세스가 종료되면 history와 최근 메시지가 사라진다. 로컬 PoC에는 쓸 수 있어도 다중 worker 운영의 해결책은 아니다.

SQLite를 선택한 이유는 외부 DB 없이 `pip install` 후 바로 동작하게 하는 library-mode 기본값으로 보는 것이 타당하다. 파일 하나로 history와 짧은 최근 문맥을 처리하기 쉽기 때문이다. 이는 편의상 구현 선택이지, 사실 추출·임베딩·hybrid retrieval에 SQLite 고유 기능이 필요해서가 아니다.

## 2. 두 테이블

### `history`

```sql
history(
  id, memory_id,
  old_memory, new_memory, event,
  created_at, updated_at, is_deleted,
  actor_id, role
)
```

`history(memory_id)`는 `created_at ASC, DATETIME(updated_at) ASC`로 이 row들을 반환한다. 이는 특정 memory ID의 변경 흔적을 보는 내부 audit 보조 기능이지, 중앙화된 compliance audit log는 아니다.

| 이벤트 | 생성 시점 | 주요 값 |
| --- | --- | --- |
| `ADD` | V3 add / raw create / procedural create | `new_memory`, 생성 시각 |
| `UPDATE` | 공개 `update()` | 이전·새 text, 갱신 시각 |
| `DELETE` | 공개 `delete()` 또는 `delete_all()` | 이전 text, `new_memory=None`, `is_deleted=1` |

### `messages`

```sql
messages(
  id, session_scope,
  role, content, name, created_at
)
```

`save_messages()`는 새 메시지를 저장한 뒤 동일 `session_scope`에서 최대 10개만 남긴다. `get_last_messages()`도 N개를 고른 뒤 시간 오름차순으로 재정렬한다.

하지만 한 `save_messages()` 호출의 모든 row에는 동일한 `created_at`을 넣고, 두 SQL 모두 tie-breaker 없이 `created_at`만 정렬한다. 그래서 한 번에 10개를 넘겨 저장한 경우 마지막 10개·원래 순서는 보장되지 않는다. 이 snapshot에서 `m0`~`m11`을 한 호출로 저장한 직접 검증 결과는 `m0`~`m9`였다. bulk transcript import에는 message sequence column/정렬 수정 또는 우리 쪽 사전 chunking이 필요하다.

즉 Mem0가 유지하는 최근 대화 문맥은 대화 로그 전체가 아니라 **최대 10개짜리 작은 window**다. 동률 timestamp에서는 엄밀한 sliding window도 아니며, extraction prompt에서는 각 과거 content가 다시 300자로 잘린다. 장기 세션 transcript나 사용자의 삭제 요청 범위를 SQLite 메시지 테이블에 의존하면 안 된다.

## 3. 메모리 lifecycle 실제 흐름

### 생성

V3 `add(infer=True)`는 Qdrant batch insert 뒤 `db.batch_add_history()`를 쓴다. raw path의 `_create_memory()`와 procedural path도 Qdrant insert 후 `db.add_history(..., "ADD")`를 실행한다.

### 명시적 수정

`Memory.update(memory_id, text, metadata, ...)`는 다음 순서다.

```text
기존 Qdrant memory 조회
→ 새 text 임베딩 + hash/text_lemmatized/updated_at 갱신
→ vector_store.update(dense vector + payload)
→ SQLite UPDATE history 추가
→ text 변경 시 entity link 제거 후 새 text로 다시 연결
```

V3 자동 add 경로는 update를 선택하지 않지만, 이 공개 API로 수정하면 같은 memory ID를 유지할 수 있다. 따라서 “최신 값 한 개만 유지”가 필요한 도메인은 새로운 ADD에만 의존하지 말고, PostgreSQL의 현재성 판단 후 명시적 `update()`를 호출해야 한다.

metadata만 바꾸는 `update()`도 기존 text를 다시 lemmatize하고 dense embedding한 뒤 전체 vector/payload를 update한다. 기능상 문제는 아니지만 잦은 metadata patch에는 불필요한 embedding 비용이 생길 수 있다. `actor_id`는 생성 후 immutable하게 기존 payload 값을 유지한다.

### 삭제

`delete(memory_id)`는 Qdrant에서 point를 물리 삭제하고, SQLite에 DELETE history row를 남긴 뒤 entity collection의 `linked_memory_ids`에서 해당 ID를 지운다.

`delete_all(user_id/agent_id/run_id)`는 적어도 하나의 scope가 필수다. 해당 scope의 main memories를 list한 다음 하나씩 `_delete_memory()`를 호출한다. 그러나 Qdrant adapter의 기본 `list()`는 한 번에 최대 100개만 scroll하고 pagination하지 않으므로 **100개를 넘는 scope의 전체 삭제를 보장하지 않는다**.

또한 `delete()`/`delete_all()`은 다음 데이터를 의도적으로 또는 구현상 남긴다.

- SQLite `history`에는 삭제된 memory의 이전 text가 `DELETE` record로 남는다.
- SQLite `messages`는 memory 삭제 API가 지우지 않는다.
- 두 테이블을 모두 지우는 것은 collection 전체를 초기화하는 `reset()`뿐이며, scope별 SQLite 삭제 API는 없다.

따라서 개인정보 삭제·보존 정책 관점에서 vector point 삭제만으로 완전 삭제라고 응답하면 안 된다. 우리 서비스는 transcript/history의 별도 보존·삭제 설계를 가져야 한다.

### reset

`reset()`은 history/messages 테이블을 drop한 후 다시 만들고, vector store도 reset한다. 실험 환경용 전체 초기화이며 운영 데이터에 사용하면 안 된다.

## 4. 원자성·일관성 한계

Mem0의 한 lifecycle 작업은 Qdrant와 SQLite를 가로지르지만 분산 트랜잭션이 아니다.

```text
Qdrant write 성공 → SQLite history 실패
SQLite history 성공 → 이후 entity cleanup 실패
```

같은 부분 성공이 가능하다. 코드에는 여러 batch→항목별 fallback이 있으나, 보상 트랜잭션/outbox/reconciliation job은 없다.

V3 batch add에는 더 구체적인 false-success 가능성도 있다. 개별 Qdrant fallback insert 실패 ID를 제거하지 않은 채 history/entity/반환값을 만든다. 반대로 마지막 SQLite message 저장이 실패하면 Qdrant 쓰기가 끝났어도 호출 전체가 예외로 보인다. 반환된 ID의 존재 확인과 idempotency key가 필요한 이유다.

이 때문에 우리 시스템에서 다음은 PostgreSQL이 책임져야 한다.

| PostgreSQL 책임 | 이유 |
| --- | --- |
| 조사 job 상태와 결과의 current version | SQLite history는 메모리 변경 log일 뿐 업무 상태가 아님 |
| MinIO object와 요약/메모리의 source mapping | Mem0 history에는 source artifact 모델이 없음 |
| ACL, 삭제 요청, 보존 기간 | Qdrant filter와 local SQLite만으로 중앙 정책을 보장할 수 없음 |
| 재시도/idempotency/outbox | Qdrant·Mem0 호출 실패를 업무 트랜잭션과 묶어야 함 |

## 5. 운영 선택지와 권장안

| 선택지 | 장점 | 한계 | 판단 |
| --- | --- | --- | --- |
| stock SQLite 파일 유지 | 코드 변경 없음, 로컬 PoC가 빠름 | worker별 상태 분리, 중앙 백업·삭제·관측 어려움 | 단일 프로세스 PoC에만 적합 |
| stock SQLite `:memory:` + PostgreSQL 업무 원장 | SQLite 파일은 남지 않음 | 최근 문맥/내부 history가 재시작 때 유실되고 여전히 이중 구현 | 짧은 실험용 |
| SQLite 유지 + 같은 내용을 PostgreSQL에도 기록 | upstream SDK를 그대로 사용 | 중복 저장·삭제·정합성 문제가 늘어남 | 운영 기본안으로 권장하지 않음 |
| **PostgreSQL storage adapter로 SQLite 대체** | 다중 worker 공유, 중앙 백업·보존·삭제·관측 가능 | Mem0에 작은 fork/주입 패치 필요 | **우리 운영 권장안** |

따라서 앞서 적었던 “SQLite는 내부 보조로 남겨 둔다”는 구성은 stock SDK를 고치지 않을 때의 타협안일 뿐이다. 이미 PostgreSQL을 운영한다면 중복 SQLite를 필수로 유지할 이유가 없다.

### 5.1 수정해야 하는 코드 경계

현재 `SQLiteManager`를 직접 참조하는 부분을 다음과 같은 storage contract로 바꾸면 된다. Mem0에는 이 interface가 선언돼 있지 않지만, `self.db` 호출부가 요구하는 실질 계약은 작다.

```python
class MemoryHistoryStore(Protocol):
    def add_history(self, memory_id, old_memory, new_memory, event, **kwargs): ...
    def batch_add_history(self, records): ...
    def get_history(self, memory_id): ...
    def save_messages(self, messages, session_scope): ...
    def get_last_messages(self, session_scope, limit=10): ...
    def reset(self): ...
    def close(self): ...
```

최소 fork는 다음 네 곳을 바꾼다.

1. `MemoryConfig`에 `history_store` 설정 또는 생성자 주입 필드를 추가한다.
2. `Memory`와 `AsyncMemory` 생성자의 `SQLiteManager(...)` 직접 생성을 factory/injected store로 바꾼다.
3. sync/async `reset()`도 같은 factory를 통해 재생성하거나, 운영에서는 전체 `reset()`을 금지한다.
4. `PostgresMemoryHistoryStore`가 위 7개 메서드와 기존 반환 shape를 구현한다.

`AsyncMemory`도 DB 메서드를 `asyncio.to_thread()`로 호출하므로, 최소 변경안에서는 동기 PostgreSQL connection pool 기반 adapter로도 계약을 맞출 수 있다. 완전한 native async adapter를 넣으려면 `AsyncMemory`의 호출부까지 별도 추상화해야 한다.

객체 생성 후 다음처럼 `memory.db`를 바꾸는 방식도 실험상 가능하지만 권장하지 않는다.

```python
memory = Memory.from_config(config)  # 이 시점에 이미 SQLite를 연다.
memory.db.close()
memory.db = PostgresMemoryHistoryStore(pool)
```

이 방식은 비공개 내부 필드에 의존하고 `reset()`이 다시 SQLite를 생성하므로 안정적인 확장 지점이 아니다.

### 5.2 PostgreSQL 테이블 설계 시 보완할 점

SQLite schema를 그대로 복제하기보다 확인된 순서·삭제 문제를 함께 고치는 편이 낫다.

```text
mem0_memory_history
  - event_id, memory_id, event, old_memory, new_memory
  - actor_id, role, created_at, updated_at, is_deleted
  - source_id, tenant_id, request_id/idempotency_key

mem0_recent_message
  - message_id, session_scope, sequence
  - role, content, name, created_at
  - tenant_id, expires_at
```

- `sequence` 또는 단조 증가 ID를 정렬 기준에 포함해 같은 batch의 메시지 순서를 보장한다.
- 최근 문맥 보존 개수와 조회 개수를 각각 설정 가능하게 한다. 현재 하드코딩된 10개를 그대로 복제할 필요는 없다.
- scope별 삭제, 보존 기간, tenant 조건을 모든 query에 포함한다.
- `request_id`/idempotency key로 worker 재시도 시 history/message 중복을 막는다.

### 5.3 수정된 권장 운영 패턴

```text
PostgreSQL transaction
  → research artifact/version/status 기록
  → outbox: memory promotion event 생성

worker
  → outbox event 소비
  → PostgreSQL history store에서 scope 최근 문맥 조회
  → Mem0.add/update/delete 실행
       ├─ Qdrant: memory + entity vector 저장
       └─ PostgreSQL adapter: history + recent messages 저장
  → 성공한 memory_id/source mapping/처리 결과를 PostgreSQL에 기록
  → 실패 시 retry / dead-letter / 운영 알림
```

이 구조에서는 SQLite를 사용하지 않는다. 하나의 PostgreSQL 안에서도 업무 테이블과 Mem0 보조 테이블은 schema를 분리해 소유권·migration·보존 정책을 명확히 하는 것이 좋다.

다만 SQLite를 PostgreSQL로 바꿔도 Qdrant와 PostgreSQL 사이의 원자성이 자동으로 생기지는 않는다. Mem0는 Qdrant write 뒤 history를 쓰는 순차 dual-write 구조이므로, outbox는 여전히 필요하다. worker는 idempotency key, read-after-write, 처리 상태, reconciliation으로 부분 성공을 복구해야 한다. 같은 PostgreSQL을 쓴다는 사실만으로 외부 Qdrant write까지 하나의 ACID transaction이 되는 것은 아니다.

## 6. AsyncMemory의 의미

stock `AsyncMemory`는 동일한 SQLite schema와 같은 vector store/LLM 구성을 사용한다. 대부분의 SQLite·동기 adapter·LLM/embedding 호출은 `asyncio.to_thread()`로 넘긴다. PostgreSQL adapter를 적용한 뒤에도 동기 store contract를 유지한다면 같은 방식으로 실행된다.

예외가 있다. `AsyncMemory.add()`는 vision parsing을 `parse_vision_messages()`로 직접 호출하며, vision이 활성화되면 그 안의 동기 `llm.generate_response()`가 event loop를 막을 수 있다. 멀티모달 async 경로는 별도 부하 테스트 또는 wrapper offload가 필요하다.

async `delete_all()`은 개별 삭제를 `gather(return_exceptions=True)`로 실행하고 실패를 로그만 남긴 뒤 성공 message를 반환한다. 그 후 entity store가 초기화돼 있었다면 scope의 entity link를 bulk clear한다. 일부 main 삭제가 실패해 memory가 남아도 그 memory의 entity link는 지워질 수 있다. sync/async 모두 삭제 후 잔존 검증이 필요하다.

장기 실행 worker는 종료 시 `close()`를 호출해 history-store connection/pool과 provider client/reranker 자원을 정리한다.

## 7. 판단 요약

- **SQLite가 반드시 필요한가?** 알고리즘상 아니다.
- **현재 SDK 설정만으로 PostgreSQL로 바꿀 수 있는가?** 아니다. `history_db_path`는 SQLite 경로 설정일 뿐이다.
- **PostgreSQL이 두 역할을 모두 맡을 수 있는가?** 가능하며, 우리 다중 worker 운영에는 더 적합하다.
- **어느 정도 수정이 필요한가?** `self.db`의 7개 메서드를 만족하는 adapter와 생성자/reset의 주입 지점이 필요하다.
- **그러면 outbox가 불필요한가?** 아니다. PostgreSQL과 Qdrant의 dual-write 정합성 문제는 그대로 남는다.

## 참고한 upstream 소스

- [Memory/AsyncMemory가 SQLiteManager를 직접 생성하는 `main.py`](https://github.com/mem0ai/mem0/blob/main/mem0/memory/main.py)
- [`history_db_path`만 제공하는 `MemoryConfig`](https://github.com/mem0ai/mem0/blob/main/mem0/configs/base.py)
- [SQLite의 history/messages 구현](https://github.com/mem0ai/mem0/blob/main/mem0/memory/storage.py)
