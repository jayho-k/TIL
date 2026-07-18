# Mem0 PostgreSQL State Store 대체 설계

> 대상: Mem0 OSS Python library mode의 `SQLiteManager` 대체
> 기준 소스: `AI/mem0/code/mem0_code_analize/mem0`, package version `mem0ai 2.0.12`
> 작성일: 2026-07-18
> 상태: 설계 검토 대기
> 관련 문서: [01_전체_아키텍처.md](01_전체_아키텍처.md), [02_V3_쓰기_파이프라인.md](02_V3_쓰기_파이프라인.md), [06_SQLite_History와_Lifecycle.md](06_SQLite_History와_Lifecycle.md), [07_강점_제약과_우리_아키텍처.md](07_강점_제약과_우리_아키텍처.md)

## 0. 문서 목적

이 문서는 Mem0 Python OSS library mode가 로컬 SQLite에 저장하는 다음 두 상태를 PostgreSQL로 대체하기 위한 상세 설계를 정의한다.

1. scope별 최근 대화 메시지: 다음 `Memory.add(infer=True)`의 fact extraction prompt에 들어가는 최근 문맥
2. memory lifecycle history: `ADD`, `UPDATE`, `DELETE` 변경 이력

이 설계의 목표는 Mem0의 전체 memory pipeline을 다시 만드는 것이 아니다. Mem0의 LLM fact extraction, embedding, Qdrant 저장, entity linking, hybrid retrieval은 그대로 사용하고, `SQLiteManager`가 담당하는 범위만 PostgreSQL adapter로 교체한다.

```text
유지하는 Mem0 기능
  - 대화에서 fact 추출
  - embedding과 Qdrant 저장
  - entity linking
  - hybrid retrieval와 reranker

교체하는 기능
  - SQLite history
  - SQLite recent messages

별도 서비스가 담당하는 기능
  - research artifact와 원문
  - canonical memory와 현재 버전
  - tenant/ACL
  - outbox, retry, reconciliation
  - Qdrant write 결과 검증
  - 업무 감사와 개인정보 lifecycle
```

이 경계를 고정하는 이유는 adapter에 서비스 기능을 계속 추가하면 Mem0의 비공개 내부 API와 우리 도메인이 강하게 결합되고, 오픈소스 업데이트를 따라가기 어려워지기 때문이다.

---

## 1. 결론 요약

최종 선택은 **외부 `PostgresMem0StateStore` + composition wrapper인 `Mem0Facade`**다.

```text
Application / MemoryService
          │
          ▼
      Mem0Facade
          │
          ├── Mem0 Memory 또는 AsyncMemory
          │      ├── LLM
          │      ├── Embedder
          │      └── Qdrant
          │
          └── PostgresMem0StateStore
                 ├── mem0_aux.memory_history
                 └── mem0_aux.session_context
```

Mem0 패키지는 수정하지 않는다. 초기화 시 `history_db_path=":memory:"`로 임시 SQLite를 만들고 즉시 닫은 뒤 `memory.db`를 PostgreSQL store로 교체한다. 따라서 운영 요청에서는 SQLite 파일, SQLite query, SQLite file lock이 발생하지 않는다.

```python
effective_config = config.model_copy(
    update={"history_db_path": ":memory:"}
)
memory = AsyncMemory(config=effective_config)
memory.db.close()
memory.db = postgres_state_store
facade = Mem0Facade(memory)
```

초기화 순간의 SQLite 객체 생성도 허용할 수 없게 되면 별도 provider 전체를 fork하지 않고, 생성자에 `state_store`를 받을 수 있게 하는 최소 dependency-injection patch로 전환한다. 이 patch는 예비 선택지이며 첫 구현 범위에는 포함하지 않는다.

---

## 2. 왜 이 결과가 나왔는가

### 2.1 SQLite는 기억 알고리즘의 필수 구성 요소가 아니다

Mem0에서 실제 memory fact와 embedding은 vector store에 저장된다. 우리 구성에서는 Qdrant다. Entity memory도 `{collection}_entities` Qdrant collection에 저장된다.

SQLite는 다음 두 보조 상태만 저장한다.

```text
history table
  → memory lifecycle 변경 기록

messages table
  → 다음 fact extraction에 사용할 최근 10개 메시지
```

Fact extraction, embedding, semantic search, BM25, entity boost는 SQLite 고유 기능을 사용하지 않는다. 따라서 같은 method contract를 제공하는 PostgreSQL 구현체로 교체해도 memory 알고리즘의 핵심 동작은 유지된다.

### 2.2 현재 Python OSS에는 history-store provider가 없다

`MemoryConfig`에는 `vector_store`, `llm`, `embedder`, `reranker` provider 설정이 있지만 history 저장소에는 `history_db_path`만 있다.

```python
history_db_path: str
```

동기와 비동기 생성자는 모두 다음 객체를 직접 만든다.

```python
self.db = SQLiteManager(self.config.history_db_path)
```

Qdrant를 vector store로 설정하거나 PostgreSQL을 애플리케이션 DB로 사용해도 이 SQLite는 자동으로 교체되지 않는다.

### 2.3 실제 저장소 method contract는 작고 SQL도 한 파일에 모여 있다

현재 Mem0 core가 `self.db`에 요구하는 실질적인 method는 일곱 개다.

```text
get_last_messages
save_messages
add_history
batch_add_history
get_history
reset
close
```

SQL 문자열도 대부분 `mem0/memory/storage.py`의 `SQLiteManager`에 모여 있다. 따라서 Mem0의 모든 query를 추적해 각각 수정할 필요는 없다. 이 일곱 method를 동일한 입출력 계약으로 구현하고 `self.db`에 주입하면 된다.

### 2.4 SQLite 유지가 운영 요구와 맞지 않는다

현재 `SQLiteManager`는 하나의 connection과 하나의 `threading.Lock`을 사용한다. 동일한 manager 인스턴스에서는 사용자와 scope가 달라도 모든 읽기와 쓰기가 직렬화된다.

다중 프로세스가 같은 SQLite 파일을 사용하면 각 프로세스의 Python lock은 서로를 조정하지 못하고 SQLite file lock에 의존한다. 여러 Pod가 각자의 로컬 파일을 사용하면 lock 문제는 줄지만 최근 문맥과 history가 Pod마다 분리된다.

우리 환경은 수만 명의 사용자, 다중 worker/pod, 중앙 백업과 관측을 전제로 하므로 로컬 SQLite는 적절한 공유 상태 저장소가 아니다.

### 2.5 Mem0 전체를 직접 구현하는 것은 현재 요구보다 범위가 크다

SQLite를 없애기 위해 Mem0 전체를 다시 구현하면 다음 기능도 우리가 소유해야 한다.

- fact extraction prompt와 JSON parsing
- existing memory retrieval과 extraction context 조립
- MD5 exact dedup
- dense/BM25/entity score 결합
- entity collection과 link 관리
- reranker 연동
- sync/async SDK parity
- LLM·embedder·vector-store provider 변화 대응

현재 요구는 이 기능들을 대체하는 것이 아니라 SQLite의 두 역할을 PostgreSQL로 옮기는 것이다. 따라서 전체 재구현은 과도하다.

### 2.6 Mem0 내부에 PostgreSQL provider를 직접 추가하는 것도 첫 선택으로 과하다

정식 provider/factory를 Mem0 내부에 추가하면 구조는 깨끗하지만 다음 파일과 경로를 지속해서 fork해야 한다.

- `MemoryConfig`
- `Memory.__init__()`
- `AsyncMemory.__init__()`
- sync/async `reset()`
- provider factory
- packaging과 optional dependency
- upstream unit test

Mem0의 주요 알고리즘 변경이 `memory/main.py`에 집중되어 있어 업그레이드 충돌 가능성도 높다. 우리 목적은 오픈소스 업데이트를 쉽게 따라가는 것이므로, PostgreSQL 구현은 애플리케이션 repository에 두고 Mem0와의 접점만 작은 compatibility layer로 제한하는 편이 낫다.

### 2.7 서비스 정합성은 adapter의 책임이 아니다

SQLite를 PostgreSQL로 바꿔도 Qdrant와 PostgreSQL이 하나의 ACID transaction이 되는 것은 아니다. Mem0 V3 pipeline에는 Qdrant write, history write, entity write, recent-message write가 순차적으로 존재한다.

하지만 우리는 research artifact, canonical memory, outbox, 처리 상태를 별도 서비스에서 직접 구현하기로 했다. 따라서 이 adapter의 history는 업무 원장이 아니며 recent messages는 extraction 보조 문맥이다.

이 책임 분리가 wrapper 방식을 선택할 수 있게 한다. Mem0 내부의 부분 실패를 adapter가 모두 해결할 필요가 없기 때문이다.

### 2.8 결론을 뒷받침하는 source 지점

| 확인 내용 | Source 지점 | 설계에 미친 영향 |
| --- | --- | --- |
| 동기 생성자가 SQLite를 직접 생성 | `mem0/memory/main.py`의 `Memory.__init__()`, `self.db = SQLiteManager(...)` | config만으로 PostgreSQL 선택 불가능 |
| 비동기 생성자도 동일 | 같은 파일의 `AsyncMemory.__init__()` | 동기 store contract 하나를 주입하는 방향 선택 |
| 최근 문맥 조회 | `_add_to_vector_store()` Phase 0의 `get_last_messages(..., 10)` | recent context가 fact extraction 결과에 영향을 줌 |
| 최근 문맥 저장 | fact가 없을 때, record가 없을 때, Phase 8의 `save_messages()` | 조기 return 경로까지 contract test 필요 |
| batch history | Qdrant persist 뒤 `batch_add_history()` | history는 vector write 이후의 보조 기록 |
| public history API | `history(memory_id)`의 `get_history()` | 기존 response shape 유지 필요 |
| update/delete history | Qdrant update/delete 뒤 `add_history()` | adapter는 기존 호출 순서를 바꾸지 않음 |
| reset의 SQLite 재생성 | sync/async `reset()`의 `self.db = SQLiteManager(...)` | facade에서 reset을 차단해야 함 |
| 실제 SQL과 lock | `mem0/memory/storage.py`의 `SQLiteManager` | SQL은 중앙화되어 있고 store contract가 작음 |

재현 대상 source는 `AI/mem0/code/mem0_code_analize/mem0`에 보관되어 있다. 신규 Mem0 version을 평가할 때 같은 지점을 다시 확인한다.

---

## 3. 목표와 비목표

### 3.1 목표

#### 기능 목표

1. stock `SQLiteManager`가 제공하는 일곱 method의 입출력 shape를 유지한다.
2. scope별 최근 메시지를 최대 10개 유지한다.
3. 같은 scope의 동시 저장에서도 메시지 순서와 최대 개수를 보장한다.
4. memory history를 시간 순서가 안정적으로 결정되도록 저장하고 조회한다.
5. `Memory`와 `AsyncMemory`에서 같은 adapter를 사용할 수 있게 한다.
6. 여러 process와 Pod가 같은 PostgreSQL 상태를 공유하게 한다.
7. Mem0 패키지 소스를 수정하지 않고 사용할 수 있게 한다.
8. Mem0 신규 버전의 내부 DB contract 변경을 CI에서 감지한다.

#### 운영 목표

1. PostgreSQL connection pool을 사용해 thread-safe하게 동작한다.
2. 동일 scope만 직렬화하고 서로 다른 scope는 병렬 처리한다.
3. runtime DB role은 DDL 권한 없이 필요한 DML만 수행한다.
4. query latency, error, pool 대기, scope lock 대기를 관측할 수 있게 한다.
5. 운영 환경에서 전체 `reset()`을 실행할 수 없게 한다.

### 3.2 비목표

이 설계는 다음 문제를 해결하지 않는다.

- Qdrant와 PostgreSQL 사이의 분산 트랜잭션
- V3 Qdrant batch insert의 부분 성공 추적
- ADD-only memory의 모순·최신성 판단
- memory promotion 정책
- research artifact와 memory provenance
- 서비스 tenant 인증·인가
- 공식 업무 audit log
- outbox, retry, dead-letter, reconciliation
- `delete_all()`의 Qdrant pagination 문제
- 한국어 BM25/entity 품질
- Gemma 4 31B fact extraction 품질

이 항목은 `MemoryService`와 research workflow의 책임이다. `PostgresMem0StateStore`에 포함하지 않는다.

---

## 4. 대안 비교와 결정

### 대안 A: stock SQLite 유지

```text
장점
  - 코드 변경 없음
  - 설치 직후 동작

단점
  - process-local global lock
  - 다중 Pod에서 상태 분리
  - 중앙 백업·삭제·관측 어려움
  - local file lifecycle 관리 필요
```

결정: 단일 프로세스 개발 실험 외에는 사용하지 않는다.

### 대안 B: SQLite와 PostgreSQL 이중 기록

```text
장점
  - Mem0 stock 동작 유지
  - PostgreSQL에도 보조 복사본 생성

단점
  - 어느 저장소가 기준인지 불명확
  - 이중 쓰기 실패와 삭제 불일치 추가
  - SQLite lock과 Pod 분리 문제는 그대로 존재
  - 운영 복잡도만 증가
```

결정: 사용하지 않는다.

### 대안 C: Mem0 전체 memory pipeline 직접 구현

```text
장점
  - 모든 저장 순서와 정책 통제
  - 내부 API 의존 없음

단점
  - 현재 요구보다 구현 범위가 큼
  - extraction/retrieval/entity/rerank 품질을 직접 유지
  - Mem0를 도입하는 이점이 사라짐
```

결정: 현재 단계에서는 선택하지 않는다. 향후 Mem0 core를 계속 수정해야 하는 요구가 누적될 때 다시 평가한다.

### 대안 D: Mem0 내부에 PostgreSQL provider/factory 추가

```text
장점
  - 구조적으로 가장 명확한 provider 선택
  - SQLite 객체도 생성하지 않음
  - reset/lifecycle을 정식으로 처리 가능

단점
  - Mem0 fork 유지
  - upstream main.py/config 충돌 가능성
  - 패키징과 배포 책임 증가
```

결정: 첫 구현으로 선택하지 않는다. upstream에 공식 extension point가 생기거나 wrapper 유지 비용이 커지면 전환한다.

### 대안 E: 외부 wrapper에서 PostgreSQL store 주입

```text
장점
  - 공식 mem0ai package 수정 없음
  - adapter를 우리 repository에서 독립적으로 테스트 가능
  - 문제 발생 시 rollback이 쉬움
  - Mem0 업데이트 시 compatibility layer만 수정

단점
  - 비공개 속성 memory.db에 의존
  - 생성 시 임시 SQLite 객체가 잠깐 생성됨
  - core reset을 호출하면 SQLite로 복귀
```

결정: **선택한다.** 비공개 속성 의존 위험은 버전 고정, contract test, startup guard, reset 차단으로 통제한다.

---

## 5. 전체 구성 요소

### 5.1 `Mem0StateStore` Protocol

우리 코드 안에 Mem0가 요구하는 저장소 계약을 명시적으로 선언한다.

```python
from typing import Any, Protocol


class Mem0StateStore(Protocol):
    def add_history(
        self,
        memory_id: str,
        old_memory: str | None,
        new_memory: str | None,
        event: str,
        *,
        created_at: str | None = None,
        updated_at: str | None = None,
        is_deleted: int = 0,
        actor_id: str | None = None,
        role: str | None = None,
    ) -> None: ...

    def batch_add_history(self, records: list[dict[str, Any]]) -> None: ...

    def get_history(self, memory_id: str) -> list[dict[str, Any]]: ...

    def save_messages(
        self,
        messages: list[dict[str, Any]],
        session_scope: str,
    ) -> None: ...

    def get_last_messages(
        self,
        session_scope: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]: ...

    def reset(self) -> None: ...

    def close(self) -> None: ...
```

이 Protocol은 Mem0 upstream의 공식 interface가 아니라 우리 compatibility contract다. Mem0 version을 올릴 때 실제 `self.db.*` 호출 목록과 비교한다.

### 5.2 `PostgresMem0StateStore`

이 클래스는 위 Protocol의 PostgreSQL 구현이다.

책임은 다음과 같다.

- pool에서 connection을 checkout
- method 단위 transaction 실행
- PostgreSQL row를 Mem0가 기대하는 Python dictionary로 변환
- scope별 recent-message window 보장
- query metric과 error metric 기록
- 외부 pool 소유권 존중

다음 책임은 갖지 않는다.

- Mem0 object 생성
- tenant authorization
- business retry
- Qdrant write
- outbox 상태 변경

### 5.3 `Mem0CompatibilityLayer`

Mem0 object 생성과 PostgreSQL store 주입을 담당한다.

```python
def build_mem0_memory(
    *,
    mem0_config: MemoryConfig,
    state_store: Mem0StateStore,
    async_mode: bool,
):
    effective_config = mem0_config.model_copy(
        update={"history_db_path": ":memory:"}
    )

    core = (
        AsyncMemory(effective_config)
        if async_mode
        else Memory(effective_config)
    )
    core.db.close()
    core.db = state_store

    verify_mem0_storage_binding(core, state_store)
    return core
```

애플리케이션의 다른 module은 `memory.db`에 직접 접근하지 않는다.

### 5.4 `Mem0Facade`

우리 서비스가 Mem0를 호출하는 유일한 표면이다. 필요한 API만 명시적으로 노출한다.

```text
허용 후보
  - add
  - search
  - get
  - get_all
  - update
  - delete
  - delete_all
  - history
  - close

금지
  - reset
  - 내부 self.db 접근
  - vector_store 직접 접근
```

`__getattr__`로 모든 Mem0 API를 자동 위임하지 않는다. 그렇게 하면 `reset()`과 향후 추가되는 위험한 API도 자동 노출되기 때문이다.

---

## 6. PostgreSQL schema

### 6.1 schema namespace

애플리케이션 업무 테이블과 Mem0 보조 테이블의 migration·권한·보존 정책을 분리하기 위해 별도 schema를 사용한다.

```sql
CREATE SCHEMA mem0_aux;
```

권한 모델은 다음과 같다.

```text
migration role
  - CREATE/ALTER/DROP on mem0_aux

runtime role
  - USAGE on mem0_aux
  - SELECT/INSERT/UPDATE/DELETE on 필요한 테이블
  - DDL 권한 없음
```

Schema revision은 애플리케이션의 migration 도구가 기록한 revision을 기준으로 한다. Alembic을 사용한다면 기존 `alembic_version`의 기대 revision을 compatibility manifest에 기록한다. 별도 migration 도구를 사용한다면 동일한 의미의 단일 revision 값을 사용한다. Adapter 생성자가 table을 만들거나 자동 migration을 실행하지 않는다.

### 6.2 `memory_history`

```sql
CREATE TABLE mem0_aux.memory_history (
    id          UUID PRIMARY KEY,
    sequence    BIGINT GENERATED ALWAYS AS IDENTITY UNIQUE,
    memory_id   TEXT,
    old_memory  TEXT,
    new_memory  TEXT,
    event       TEXT,
    created_at  TIMESTAMPTZ,
    updated_at  TIMESTAMPTZ,
    is_deleted  BOOLEAN NOT NULL DEFAULT FALSE,
    actor_id    TEXT,
    role        TEXT,

    CONSTRAINT ck_mem0_history_event
        CHECK (event IS NULL OR event IN ('ADD', 'UPDATE', 'DELETE'))
);

CREATE INDEX ix_mem0_history_memory_sequence
    ON mem0_aux.memory_history (memory_id, sequence);
```

#### 설계 이유

- `memory_id`는 현재 UUID 문자열이지만 Mem0의 미래 vector ID 타입 변경을 덜 제한하기 위해 `TEXT`로 둔다.
- `id`는 현재 SQLite처럼 event row 자체의 UUID다. Python에서 `uuid.uuid4()`로 만든다.
- `sequence`는 동일 timestamp와 `NULL` timestamp에서도 안정적인 정렬을 보장한다.
- `created_at`, `updated_at`은 입력에서 누락될 수 있으므로 nullable이다.
- `old_memory`, `new_memory`는 삭제와 최초 추가에서 각각 `NULL`일 수 있다.
- Qdrant는 외부 저장소이므로 DB foreign key를 만들지 않는다.

`get_history()` 반환 시 UUID와 timestamp는 현재 Mem0 response shape와 맞게 문자열로 변환한다.

```python
{
    "id": str(row.id),
    "memory_id": row.memory_id,
    "old_memory": row.old_memory,
    "new_memory": row.new_memory,
    "event": row.event,
    "created_at": to_iso_or_none(row.created_at),
    "updated_at": to_iso_or_none(row.updated_at),
    "is_deleted": bool(row.is_deleted),
    "actor_id": row.actor_id,
    "role": row.role,
}
```

### 6.3 `session_context`

```sql
CREATE TABLE mem0_aux.session_context (
    session_scope TEXT PRIMARY KEY,
    messages      JSONB NOT NULL DEFAULT '[]'::jsonb,
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT ck_mem0_context_messages_array
        CHECK (jsonb_typeof(messages) = 'array'),
    CONSTRAINT ck_mem0_context_message_limit
        CHECK (jsonb_array_length(messages) <= 10)
);

CREATE INDEX ix_mem0_context_updated_at
    ON mem0_aux.session_context (updated_at);
```

#### SQLite처럼 메시지별 row를 만들지 않는 이유

Mem0는 messages table에서 다음 동작만 한다.

1. scope의 최근 메시지 N개를 전부 읽는다.
2. 신규 메시지를 붙인다.
3. 마지막 10개만 남긴다.

메시지 하나를 독립적으로 조회·수정·삭제하는 API는 없다. 따라서 scope 하나의 bounded state로 모델링하는 편이 실제 access pattern과 더 잘 맞는다.

장점은 다음과 같다.

- scope당 row 하나
- 최근 10개 유지가 명시적
- 같은 batch 메시지의 list 순서 보존
- `INSERT 여러 번 + DELETE` write amplification 감소
- 동일 scope row lock으로 경쟁 범위 제한

JSONB 안의 각 메시지는 다음 shape를 사용한다.

```json
{
  "role": "user",
  "content": "Qdrant를 사용하기로 결정했다.",
  "name": null,
  "created_at": "2026-07-18T10:00:00.000000+00:00"
}
```

SQLite의 `id`는 recent-message API 응답에 노출되지 않고 retention 용도로만 쓰인다. JSONB 구조에서는 list 위치가 순서를 제공하므로 별도 message UUID는 필요하지 않다.

### 6.4 tenant key에 대한 전제

현재 Mem0가 store에 전달하는 `session_scope`에는 tenant ID가 별도 필드로 들어오지 않는다.

```text
agent_id=...&run_id=...&user_id=...
```

이 store는 서비스의 tenant 보안 경계가 아니다. 서비스는 Mem0에 전달하는 entity ID를 전역적으로 namespace해야 한다.

```text
user_id  = tenant:{tenant_id}:user:{user_id}
agent_id = tenant:{tenant_id}:agent:{agent_id}
run_id   = tenant:{tenant_id}:run:{run_id}
```

또한 `&`, `=`가 scope 조합 구분자로 쓰이므로 원래 ID를 base64url 또는 percent encoding한 뒤 조합한다. 애플리케이션은 raw 외부 ID를 그대로 Mem0에 전달하지 않는다.

```text
외부 user ID
  → canonical ID encoder
  → Mem0 user_id
  → Mem0 session_scope
```

---

## 7. method별 상세 동작

### 7.1 `add_history()`

#### transaction

```text
pool에서 connection checkout
  → transaction 시작
  → history row 한 건 INSERT
  → commit
  → connection 반환
```

#### 입력 처리

- `id`: Python `uuid.uuid4()`
- `is_deleted`: `0/1`, `False/True`를 `bool`로 정규화
- timestamp: ISO 8601 string이면 UTC-aware datetime으로 변환
- 잘못된 timestamp는 임의 문자열로 저장하지 않고 명시적 validation error 발생
- `event`는 `ADD`, `UPDATE`, `DELETE` 또는 현재 호환을 위한 `None`만 허용

#### 반환과 오류

- 성공 시 `None`
- SQL 오류를 삼키지 않고 호출자에게 전달
- memory text는 error log와 metric label에 기록하지 않음

#### 멱등성

stock SQLite contract에는 operation ID가 없으므로 이 adapter도 exactly-once history를 보장하지 않는다. 임의의 unique constraint로 합법적인 반복 update를 제거하지 않는다.

업무상 멱등성은 별도 서비스 outbox가 담당한다. Mem0 history는 보조 이력이다.

### 7.2 `batch_add_history()`

#### transaction

모든 row를 하나의 transaction으로 저장한다.

```text
records가 비어 있음
  → 즉시 return

records가 존재
  → transaction
  → UUID와 timestamp 정규화
  → executemany/pipeline INSERT
  → commit
```

하나라도 validation 또는 INSERT에 실패하면 전체 batch를 rollback한다. 이는 SQLite `BEGIN` + `executemany` 의미와 같다.

Mem0 core가 batch 실패 후 단건 fallback을 수행하므로 adapter 내부에서 다시 같은 fallback을 구현하지 않는다. 이중 fallback은 중복과 오류 은폐를 늘린다.

### 7.3 `get_history()`

```sql
SELECT
    id, memory_id, old_memory, new_memory, event,
    created_at, updated_at, is_deleted, actor_id, role
FROM mem0_aux.memory_history
WHERE memory_id = %s
ORDER BY
    created_at ASC NULLS FIRST,
    updated_at ASC NULLS FIRST,
    sequence ASC;
```

#### 정렬 결정

SQLite 구현은 `created_at`, `DATETIME(updated_at)`을 사용하지만 같은 시각과 `NULL`에서 안정적인 tie-breaker가 없다. PostgreSQL 구현은 원래 의도인 시간 순서를 유지하면서 `sequence`로 결과를 결정적으로 만든다.

#### 반환

- 조회 결과가 없으면 `[]`
- 모든 row는 stock `SQLiteManager.get_history()`와 같은 key를 가진 dictionary
- `is_deleted`는 Python `bool`
- timestamp는 ISO 8601 string 또는 `None`

#### 보안 경계

`get_history(memory_id)`에는 tenant filter가 없다. 따라서 facade의 `history()`는 서비스가 memory ownership을 확인한 뒤에만 호출해야 한다. 이 adapter를 외부 API에서 직접 호출하지 않는다.

### 7.4 `save_messages()`

#### 입력 검증

- 빈 list면 DB에 접근하지 않고 return
- `session_scope`는 빈 문자열을 허용하지 않음
- 각 항목은 dictionary
- `role`, `content`, `name`은 `str | None`
- 현재 fact-extraction 경로에서 vision input은 저장 전에 text로 정규화된다는 전제를 사용
- JSON 직렬화가 불가능한 값은 문자열로 강제 변환하지 않고 오류 발생

#### 저장 algorithm

```text
now = UTC ISO timestamp
incoming = 입력 순서대로 role/content/name/created_at 정규화

transaction 시작
  → scope row가 없으면 빈 배열로 INSERT, conflict면 무시
  → SELECT messages ... FOR UPDATE
  → merged = existing + incoming
  → retained = merged[-10:]
  → UPDATE messages=retained, updated_at=now
  → commit
```

개념 SQL은 다음과 같다.

```sql
INSERT INTO mem0_aux.session_context (
    session_scope,
    messages,
    updated_at
)
VALUES (%s, '[]'::jsonb, now())
ON CONFLICT (session_scope) DO NOTHING;

SELECT messages
FROM mem0_aux.session_context
WHERE session_scope = %s
FOR UPDATE;

UPDATE mem0_aux.session_context
SET messages = %s::jsonb,
    updated_at = now()
WHERE session_scope = %s;
```

#### 동시성

동일 scope의 transaction은 row-level lock에서 직렬화된다. 서로 다른 scope는 다른 row를 잠그므로 병렬 처리된다.

scope row가 아직 없는 상태에서 두 transaction이 동시에 진입하면 `INSERT ... ON CONFLICT`가 한 row 생성만 허용한다. 이후 `SELECT ... FOR UPDATE`가 순서를 정한다.

#### stock SQLite와 의도적으로 다른 점

SQLite는 한 batch의 모든 메시지에 같은 timestamp를 넣고 timestamp만으로 최신 10개를 고르므로 입력 순서가 불안정할 수 있다. 이 구현은 JSON array 순서를 사용해 실제 입력 순서를 보장한다.

이는 bug-for-bug 복제가 아니라 `save_messages()`의 의도인 “마지막 10개”를 정확하게 구현하는 차이다.

### 7.5 `get_last_messages()`

```sql
SELECT messages
FROM mem0_aux.session_context
WHERE session_scope = %s;
```

#### 동작

```text
row가 없음
  → []

row가 있음
  → JSON array의 마지막 limit개
  → 원래 시간 순서로 반환
```

호환성을 우선해 `limit <= 0`일 때 `[]`를 반환한다. 정상 Mem0 경로에서는 `limit=10`이므로 이 분기는 방어적 처리다.

반환 dictionary는 다음 key만 가진다.

```text
role
content
name
created_at
```

### 7.6 `reset()`

운영에서는 금지한다.

```python
def reset(self) -> None:
    if not self._allow_reset:
        raise ResetDisabledError(
            "Mem0 PostgreSQL state reset is disabled"
        )
```

테스트 전용 store는 `allow_reset=True`로 생성할 수 있다. 테스트 reset도 `DROP TABLE`이 아니라 transaction 안의 `TRUNCATE` 또는 테스트 schema 삭제로 구현한다.

중요하게도 stock `Memory.reset()`은 injected store의 `reset()`과 `close()`를 실행한 뒤 다시 `SQLiteManager`를 생성한다. 따라서 facade에서는 core `reset()`을 노출하지 않는다. adapter의 테스트용 `reset()`과 Mem0 core의 `reset()`은 별개다.

### 7.7 `close()`

store는 pool 소유 여부를 명시한다.

```python
PostgresMem0StateStore(
    pool=shared_pool,
    owns_pool=False,
)
```

- `owns_pool=False`: `close()`는 store를 closed 상태로만 표시하고 shared pool은 닫지 않음
- `owns_pool=True`: `close()`가 pool을 닫음
- 두 번 호출해도 오류가 없는 idempotent close
- close 후 operation을 호출하면 명시적인 `StateStoreClosedError`

운영 기본값은 `owns_pool=False`다. 애플리케이션 startup/shutdown lifecycle이 pool을 생성하고 닫는다.

여러 `Memory`/`AsyncMemory` 객체가 필요하다면 각 core 객체마다 별도 store 인스턴스를 만들고 connection pool만 공유한다. 하나의 store 인스턴스를 여러 core 객체가 공유하면 한 core의 `close()`가 다른 core에서 사용하는 store까지 closed 상태로 만들 수 있기 때문이다.

---

## 8. 동기·비동기 실행 모델

### 8.1 동기 `Memory`

동기 Memory는 store method를 같은 요청 thread에서 호출한다. 매 operation은 pool에서 독립 connection을 빌린다.

```text
request thread
  → store method
  → pool checkout
  → SQL
  → pool return
```

### 8.2 `AsyncMemory`

현재 `AsyncMemory`는 store method를 `asyncio.to_thread()`로 실행한다.

```text
event loop
  → asyncio.to_thread(store method)
  → worker thread
  → psycopg pool checkout
  → SQL
```

따라서 첫 구현은 native async PostgreSQL adapter가 아니라 동기 `psycopg_pool.ConnectionPool` adapter를 사용한다.

이 결정을 한 이유는 다음과 같다.

- `Memory`와 `AsyncMemory`가 같은 store contract를 공유할 수 있음
- Mem0 core 호출부 수정이 필요 없음
- 현재 package에도 psycopg/psycopg-pool 의존과 사용 사례가 존재
- native async adapter를 넣으려면 sync/async store interface를 이중화해야 함

### 8.3 pool 크기

총 connection 수는 다음 계산을 넘지 않게 한다.

```text
총 connection 수
  = Pod 수 × process worker 수 × process별 pool max_size
```

초기값은 부하 테스트로 정한다. LLM/Qdrant 호출이 SQLite/PG query보다 훨씬 길 수 있으므로 HTTP 동시 요청 수와 같은 크기의 DB pool은 필요하지 않다.

pool wait time을 측정하고 PostgreSQL max connection에 여유를 둔다. Pod와 worker 수가 많으면 PgBouncer 도입을 검토한다.

---

## 9. transaction, timeout, retry

### 9.1 transaction 경계

| Method | Transaction |
| --- | --- |
| `add_history` | 단일 INSERT transaction |
| `batch_add_history` | batch 전체가 하나의 transaction |
| `get_history` | read-only statement |
| `save_messages` | row 생성·lock·merge·update가 하나의 transaction |
| `get_last_messages` | read-only statement |
| `reset` | 운영 금지 |

### 9.2 isolation level

기본 `READ COMMITTED`를 사용한다.

- history는 append-only이므로 더 강한 isolation이 필요하지 않다.
- session context는 `SELECT ... FOR UPDATE`가 같은 scope 경쟁을 제어한다.
- 전체 테이블 수준 lock은 사용하지 않는다.

### 9.3 timeout

connection과 statement가 무기한 대기하지 않게 다음 값을 설정 가능하게 한다.

```text
pool checkout timeout
statement_timeout
lock_timeout
connect_timeout
```

정확한 값은 운영 SLA와 부하 테스트로 정하며 코드에 상수로 하드코딩하지 않는다.

### 9.4 retry

adapter가 모든 PostgreSQL 오류를 자동 재시도하지 않는다.

안전하게 재시도할 수 있는 후보는 transaction이 commit되지 않았음이 명확한 다음 오류다.

```text
serialization failure
deadlock detected
connection 획득 전 일시 실패
```

commit 성공 여부가 불명확한 connection 오류는 history 중복 가능성이 있으므로 adapter 안에서 무조건 재시도하지 않는다. 이 history는 보조 기능이고 서비스 operation retry는 상위 outbox가 담당한다.

`save_messages()`는 마지막 10개 bounded state이므로 같은 입력 재시도가 중복 문맥을 만들 수 있다. exactly-once가 필요해지면 `request_id + message ordinal`을 Mem0 core 또는 context propagation으로 전달하는 별도 설계가 필요하다. 첫 범위에는 포함하지 않는다.

---

## 10. 오류 처리 계약

### 10.1 원칙

1. adapter는 SQL 오류를 조용히 무시하지 않는다.
2. memory text와 message content를 로그에 남기지 않는다.
3. connection, timeout, validation, closed-store 오류를 구분한다.
4. Mem0 core가 오류를 삼키는 경로는 별도 metric으로 감지한다.

### 10.2 오류 분류

```text
Mem0StateStoreError
  ├── StateStoreUnavailableError
  ├── StateStoreTimeoutError
  ├── StateStoreValidationError
  ├── StateStoreClosedError
  ├── StateStoreSchemaMismatchError
  └── ResetDisabledError
```

PostgreSQL exception을 위 분류로 변환하되 원래 exception을 `raise ... from exc`로 보존한다.

### 10.3 Mem0 pipeline에서의 의미

| 호출 지점 | Store 오류의 외부 의미 |
| --- | --- |
| add 시작의 `get_last_messages` | fact extraction 전에 add 실패 |
| fact가 없을 때 `save_messages` | memory write는 없지만 add 실패 |
| batch history | Mem0 core가 단건 fallback 후에도 실패를 로그만 남길 수 있음 |
| add 마지막 `save_messages` | Qdrant write 후 add 전체가 실패로 보일 수 있음 |
| explicit update history | Qdrant update 후 실패 가능 |
| explicit delete history | Qdrant delete 후 실패 가능 |

이 표의 부분 실패는 adapter가 해결하지 않는다. 대신 metric과 상위 서비스 operation 상태로 관측한다. 서비스는 Mem0의 반환값만으로 업무 성공을 확정하지 않는다.

---

## 11. Facade와 lifecycle 설계

### 11.1 생성

```text
Application startup
  → PostgreSQL pool 생성
  → migration schema revision 확인
  → PostgresMem0StateStore 생성
  → Mem0 config의 history_db_path를 :memory:로 설정
  → Memory/AsyncMemory 생성
  → 임시 SQLite close
  → memory.db에 PostgreSQL store 주입
  → binding과 contract startup guard 실행
  → Mem0Facade 등록
```

### 11.2 startup guard

```python
REQUIRED_STORE_METHODS = {
    "add_history",
    "batch_add_history",
    "get_history",
    "save_messages",
    "get_last_messages",
    "reset",
    "close",
}
```

다음을 확인한다.

- injected `memory.db is state_store`
- 모든 required method가 callable
- 지원하는 Mem0 version인지
- DB migration revision이 adapter가 요구하는 revision과 맞는지
- 운영에서 `allow_reset=False`인지

### 11.3 종료

```text
Application shutdown
  → 신규 요청 중단
  → 진행 중 요청 drain
  → Memory/AsyncMemory.close()
  → facade close
  → shared PostgreSQL pool close
```

`Memory.close()`가 store의 `close()`를 호출하더라도 `owns_pool=False`이므로 pool은 애플리케이션 shutdown까지 유지된다.

### 11.4 reset 차단

Facade는 reset method를 제공하지 않거나 명시적으로 거부한다.

```python
def reset(self):
    raise ResetDisabledError(
        "Use an isolated test database for reset"
    )
```

운영 code path에서 `_memory.reset()`에 직접 접근할 수 없게 core object를 외부에 노출하지 않는다.

---

## 12. 오픈소스 업데이트 전략

### 12.1 의존성 고정

운영 배포는 정확한 version을 고정한다.

```text
mem0ai==2.0.12
```

floating version과 무조건적인 자동 merge는 사용하지 않는다.

### 12.2 compatibility module 집중

Mem0 import와 내부 `db` 주입은 한 module에만 존재해야 한다.

```text
memory/
  contracts.py
  postgres_state_store.py
  mem0_compat.py
  facade.py
```

다른 business module이 Mem0 class, `memory.db`, `SQLiteManager`를 직접 import하지 않는다.

### 12.3 신규 version 검증 workflow

```text
dependency update PR 생성
  → candidate Mem0 설치
  → internal db-call surface scan
  → SQLite/PostgreSQL differential contract test
  → sync Memory integration test
  → AsyncMemory integration test
  → PostgreSQL/Qdrant real-container test
  → concurrency test
  → 기존 memory evaluation regression
  → canary
  → 수동 승인 후 merge
```

### 12.4 `self.db.*` 호출 감지

AST 또는 제한된 source scan으로 `Memory`와 `AsyncMemory`가 사용하는 DB method 목록을 수집한다.

기대값은 다음과 같다.

```text
add_history
batch_add_history
get_history
get_last_messages
save_messages
reset
close
```

신규 method가 발견되면 CI를 실패시킨다. 테스트가 우연히 해당 code path를 실행하지 않아도 contract 변경을 감지하기 위한 장치다.

### 12.5 version별 compatibility manifest

```python
SUPPORTED_MEM0_STORAGE_CONTRACTS = {
    "2.0.12": {
        "methods": {...},
        "reset_rebinds_sqlite": True,
        "async_store_calls_via_to_thread": True,
    },
}
```

지원하지 않는 version에서는 경고만 내고 실행하지 않는다. startup에서 fail-fast한다.

### 12.6 최소 patch로 전환하는 조건

다음 중 하나가 발생하면 외부 injection에서 최소 source patch로 전환한다.

1. `memory.db`가 제거되거나 읽기 전용이 됨
2. 생성자에서 SQLite query가 memory operation에 영향을 주기 시작함
3. `reset()` 외의 경로가 `SQLiteManager`를 다시 생성함
4. 하나의 `self.db` contract가 여러 store로 분리됨
5. 초기 SQLite 객체 생성 자체가 보안·패키징 정책상 금지됨

최소 patch는 PostgreSQL query를 Mem0 내부에 넣지 않는다. 다음 injection point만 추가한다.

```python
Memory(config, state_store=None)
AsyncMemory(config, state_store=None)
```

이렇게 하면 PostgreSQL 구현과 test는 계속 우리 repository에 남고 upstream diff는 작게 유지된다.

---

## 13. Migration과 배포

### 13.1 신규 환경

```text
1. mem0_aux schema migration
2. runtime role 권한 부여
3. PostgreSQL store contract test
4. facade feature flag 활성화
5. canary worker에서 add/search/history 검증
6. 전체 worker 활성화
```

### 13.2 기존 SQLite 데이터가 없는 경우

별도 데이터 migration은 필요 없다. 신규 PostgreSQL 상태를 빈 상태로 시작한다.

recent messages는 extraction 보조 문맥이므로 시작 직후 첫 몇 번의 add에서는 과거 문맥이 없을 수 있다. 서비스 canonical data에는 영향이 없어야 한다.

### 13.3 기존 SQLite 데이터를 보존해야 하는 경우

선택적 one-time migration을 수행한다.

```text
write 중단
  → SQLite history/messages export
  → timestamp와 bool 정규화
  → history import
  → session_scope별 created_at 순서 정렬
  → 마지막 10개를 JSONB array로 import
  → row count와 sample 비교
  → PostgreSQL adapter 활성화
```

SQLite messages의 같은 timestamp 순서는 원래 불명확하므로 rowid 또는 export 순서를 tie-breaker로 사용하고, 이 한계를 migration report에 기록한다.

### 13.4 feature flag

개발·검증을 위해 생성 factory에서 backend를 선택할 수 있게 한다.

```text
MEM0_STATE_STORE=sqlite
MEM0_STATE_STORE=postgres
```

운영 기본값은 `postgres`다. `sqlite`는 로컬 단일 프로세스 테스트에만 허용한다.

### 13.5 rollback

PostgreSQL adapter 장애 시 서비스의 canonical memory와 outbox는 별도로 유지된다. 따라서 다음 rollback이 가능하다.

```text
신규 Mem0 write 일시 중단
  → 이전 application image로 rollback
  → PostgreSQL state store 장애 원인 수정
  → recent context/history 필요 시 재구성
```

운영에서 SQLite로 즉시 되돌려 여러 Pod가 각자 상태를 가지게 하는 것은 정상 rollback으로 보지 않는다. 긴급 진단용 단일 worker에만 제한한다.

---

## 14. 테스트 설계

### 14.1 SQLite differential contract test

동일한 scenario를 stock `SQLiteManager`와 `PostgresMem0StateStore`에 실행하고 외부 observable result를 비교한다.

```text
동일 입력
  ├── SQLiteManager
  └── PostgresMem0StateStore

비교 대상
  - history field와 bool 변환
  - history chronological order
  - 없는 memory의 []
  - batch 저장 결과
  - 최근 메시지 shape
  - 최근 limit 처리
  - close의 idempotency
```

의도적으로 고친 동률 메시지 순서는 별도 expected behavior로 기록하고 SQLite 결과와 동일함을 요구하지 않는다.

### 14.2 store unit test

#### History

- 단건 ADD
- UPDATE와 old/new memory
- DELETE와 `is_deleted=True`
- nullable timestamp
- timezone 포함 timestamp
- 잘못된 timestamp 거부
- 한 memory의 여러 history 순서
- 빈 batch
- 1,000건 batch
- batch 중 한 row validation 실패 시 전체 rollback
- 존재하지 않는 memory 조회
- Unicode와 한국어 text

#### Session context

- scope가 없을 때 빈 list
- 메시지 1개 저장
- 여러 메시지 입력 순서
- 10개 이하 유지
- 10개 초과 시 정확한 마지막 10개
- 여러 호출 누적 후 마지막 10개
- `limit=3`
- 같은 timestamp에서도 순서 보장
- 빈 messages no-op
- 빈 scope 거부
- 직렬화 불가능 content 거부
- close 후 호출 거부

### 14.3 concurrency test

#### 동일 scope

여러 thread가 같은 scope에 동시에 메시지를 저장한다.

검증:

- 최종 JSON array 길이 10 이하
- JSON 손상 없음
- transaction 오류 없음
- row-level lock이 동일 scope에서만 발생

동시 요청의 전체 대화 순서는 서비스에서 정의한 도착 순서와 다를 수 있다. 이 test는 commit/lock 순서가 일관되고 데이터가 유실·손상되지 않는지를 검증한다. 강한 대화 causal order가 필요하면 상위 서비스가 scope별 sequence를 부여해야 한다.

#### 서로 다른 scope

여러 scope에 병렬 저장한다.

검증:

- scope 간 불필요한 blocking 없음
- SQLite식 global serialization이 없음
- pool 크기 내에서 throughput 증가

### 14.4 Mem0 integration test

#### Sync

```text
Memory 생성
  → PostgreSQL store 주입
  → add(infer=True)
  → context row 생성 확인
  → history row 생성 확인
  → history(memory_id) response 확인
```

#### Async

```text
AsyncMemory 생성
  → PostgreSQL store 주입
  → concurrent add
  → event loop blocking과 thread pool 대기 측정
  → context/history 검증
```

LLM과 embedder는 deterministic fake를 우선 사용하고, 별도 end-to-end test에서 실제 Gemma와 Qdrant를 사용한다.

### 14.5 lifecycle test

- 임시 SQLite connection이 주입 직후 닫혔는지
- injected `memory.db`가 PostgreSQL store인지
- facade가 reset을 차단하는지
- `Memory.close()`가 shared pool을 닫지 않는지
- application shutdown이 pool을 닫는지
- 두 번 close해도 안전한지

### 14.6 upgrade test

- 지원 version manifest 확인
- `self.db.*` 신규 method 없음
- `Memory.__init__`, `AsyncMemory.__init__`에서 injection 가능
- `reset()` 이외 SQLite 재생성 경로 없음
- method positional/keyword argument 형태 동일
- return shape 동일
- 전체 regression test 통과

### 14.7 부하 테스트

최소 다음 scenario를 분리한다.

```text
1. 다수 사용자, 각기 다른 scope
2. 하나의 hot scope에 높은 동시성
3. history batch write
4. recent-context read 중심
5. PostgreSQL pool saturation
6. PostgreSQL restart/failover
```

측정값:

- p50/p95/p99 store latency
- pool checkout wait
- row lock wait
- transaction rollback
- connection error
- context JSONB 평균/최대 byte
- PostgreSQL WAL과 autovacuum 영향
- AsyncMemory thread pool saturation

---

## 15. 관측성과 운영

### 15.1 Metric

```text
mem0_state_store_operation_duration_seconds{operation,status}
mem0_state_store_operation_total{operation,status}
mem0_state_store_pool_wait_seconds
mem0_state_store_scope_lock_wait_seconds
mem0_state_store_history_batch_size
mem0_state_store_context_message_count
mem0_state_store_context_bytes
mem0_state_store_schema_mismatch_total
mem0_state_store_reset_blocked_total
```

operation label은 고정된 method 이름만 사용한다. `memory_id`, `session_scope`, user ID를 metric label로 사용하지 않는다. cardinality와 개인정보 노출을 막기 위해서다.

### 15.2 Log

로그에 허용하는 값:

- operation
- duration
- retry count
- SQLSTATE
- pool 상태
- context message count
- batch size
- 필요 시 salt가 있는 scope hash

로그에 금지하는 값:

- old/new memory 원문
- message content
- raw user/agent/run ID
- DB password와 DSN

### 15.3 Alert

- store error rate 임계 초과
- p99 latency 임계 초과
- pool wait 증가
- schema mismatch
- reset 시도
- context row check constraint 실패
- 동일 scope lock wait 장기화

Mem0 core가 batch history 오류를 로그만 남기고 진행할 수 있으므로 adapter error metric은 API success metric과 별도로 감시해야 한다.

### 15.4 보존과 정리

SQLite parity만 요구하므로 첫 구현에서 자동 TTL을 필수로 넣지 않는다. 다만 PostgreSQL table이 무한히 자라지 않게 운영 정책은 별도로 정한다.

```text
session_context
  - scope당 한 row, updated_at 기준 유휴 scope 정리 가능

memory_history
  - 보조 이력 보존 기간 적용 가능
  - 개인정보 삭제 시 canonical service 정책에 따라 삭제/익명화
```

정리 job은 adapter request path가 아니라 별도 maintenance job에서 실행한다.

---

## 16. 보안과 개인정보

### 16.1 이 store는 authorization boundary가 아니다

Mem0의 `history(memory_id)`와 내부 store method에는 tenant filter가 없다. 외부 요청을 store에 직접 연결하지 않는다.

```text
API authorization
  → canonical memory ownership 확인
  → Mem0Facade 호출
```

### 16.2 최소 권한

- runtime 계정은 `mem0_aux` DML만 허용
- public schema 권한 제거 검토
- migration 계정 분리
- DSN은 secret manager에서 주입
- TLS 연결 사용
- backup과 storage encryption 적용

### 16.3 민감 정보

history에는 삭제 전 memory text가 남을 수 있다. recent context에는 사용자 대화가 들어간다. 따라서 이 데이터를 단순 캐시라고 가정해서 보호 수준을 낮추지 않는다.

- 개인정보 분류
- 접근 로그
- 보존 기간
- 삭제 요청 반영
- backup 만료

를 서비스 정책과 일치시킨다.

---

## 17. 성능 특성 예상

### 17.1 SQLite 대비 개선

```text
SQLiteManager
  - manager 하나의 global threading.Lock
  - 동일 process의 모든 scope가 직렬화
  - 다중 process는 file lock 경쟁

PostgresMem0StateStore
  - connection pool
  - history append 병렬 처리
  - session context는 동일 scope row만 lock
  - 여러 Pod가 같은 상태 공유
```

### 17.2 hot scope

동일 session scope에 요청이 집중되면 해당 row는 직렬화된다. 이것은 결함이 아니라 최근 메시지 순서를 보존하기 위한 의도적인 경계다.

하나의 scope에 동시에 매우 많은 add가 들어오는 사용 사례가 있다면 상위 서비스가 scope별 queue나 causal sequence를 제공해야 한다. DB가 임의 순서의 동시 대화를 의미 있는 한 대화 순서로 복원할 수는 없다.

### 17.3 JSONB update 비용

매 `save_messages()`마다 context row의 새 tuple version이 생긴다. 그러나 array가 최대 10개로 제한되고 메시지 window 전체를 항상 읽는 access pattern이므로 normalized row의 반복 insert/delete보다 단순하다.

다음 값은 부하 테스트로 확인한다.

- 평균 context JSONB 크기
- TOAST 사용 여부
- table/index bloat
- autovacuum 주기

메시지 크기가 예상보다 크면 content를 일정 byte/token 이하로 제한하거나 최근 문맥에는 요약과 참조 ID만 저장한다.

---

## 18. 알려진 한계와 수용 기준

### 18.1 수용하는 한계

1. 초기화 시 `:memory:` SQLite 객체가 잠깐 생성된다.
2. `memory.db`라는 비공개 attribute에 의존한다.
3. recent-message exactly-once를 보장하지 않는다.
4. Mem0 history는 업무 원장이 아니다.
5. Qdrant와 PostgreSQL write는 원자적이지 않다.
6. 동일 scope 동시 요청의 의미적 대화 순서는 상위 서비스가 정의해야 한다.

### 18.2 수용하지 않는 상태

1. 운영 요청이 SQLite query를 실행함
2. SQLite 파일이 Pod에 생성됨
3. PostgreSQL store가 전체 사용자 global lock을 사용함
4. session context가 10개를 초과함
5. 운영 reset이 history/context를 삭제함
6. Mem0 지원하지 않는 version으로 무검증 기동함
7. store가 raw memory/message를 로그나 metric label에 노출함

### 18.3 구현 완료 기준

- 일곱 method contract 구현
- SQLite differential test 통과
- sync/async integration test 통과
- 동일 scope concurrency test 통과
- 서로 다른 scope 병렬성 확인
- reset 차단 확인
- shared pool lifecycle 확인
- schema migration과 runtime 권한 분리
- observability metric 제공
- 지원 Mem0 version startup guard 제공
- upgrade CI 제공

### 18.4 위험 등록부

| ID | 위험 | 가능성 | 영향 | 방어책 | 잔여 판단 |
| --- | --- | --- | --- | --- | --- |
| R1 | Mem0가 `memory.db`를 변경·제거 | 중간 | 높음 | version pin, AST surface scan, integration test | 변경 시 최소 injection patch로 전환 |
| R2 | core `reset()` 호출로 SQLite 복귀 | 낮음 | 치명적 | core 비노출, facade reset 차단, reset metric | 운영에서 수용하지 않음 |
| R3 | 신규 `self.db` method 추가 | 중간 | 높음 | expected method set와 CI 비교 | upgrade merge 차단 |
| R4 | PostgreSQL 장애로 extraction context 조회 실패 | 중간 | 높음 | timeout, health check, 상위 retry | Mem0 write 일시 실패 허용 |
| R5 | 동일 scope hot-row lock 대기 | 낮음~중간 | 중간 | lock metric, 상위 scope queue 검토 | 순서 보장을 위한 의도적 직렬화 |
| R6 | ambiguous retry로 recent message 중복 | 낮음 | 중간 | 상위 operation ID, context 관측 | 첫 버전에서는 수용 |
| R7 | history/context의 민감 정보 노출 | 중간 | 높음 | 최소 권한, TLS, 암호화, 로그 금지, retention | 서비스 privacy 정책 적용 |
| R8 | DB migration과 adapter schema 불일치 | 낮음 | 높음 | migration revision startup guard | fail-fast |
| R9 | Pod·worker 증가로 pool connection 폭증 | 중간 | 높음 | 총 connection 계산, pool metric, PgBouncer | 배포 전 capacity 검증 |
| R10 | 임시 SQLite 객체 생성이 정책 위반 | 낮음 | 중간 | `:memory:` + 즉시 close | 정책 변경 시 injection patch |
| R11 | JSONB context가 큰 메시지로 비대해짐 | 중간 | 중간 | byte/token metric, 입력 제한, 요약/참조 | 부하 시험 결과로 제한값 결정 |
| R12 | `history(memory_id)`가 tenant authorization 없이 호출됨 | 낮음 | 치명적 | facade 전 ownership 검사, core 직접 노출 금지 | 서비스 보안 테스트 필수 |

---

## 19. 구현 단위 제안

실제 구현 계획은 별도 문서로 작성하되, 설계상 단위는 다음처럼 분리한다.

```text
memory_state/
  contracts.py
    - Mem0StateStore Protocol
    - error hierarchy

  postgres_store.py
    - 일곱 method 구현
    - timestamp/row mapping

  migrations/
    - mem0_aux schema
    - memory_history
    - session_context

  mem0_compat.py
    - version manifest
    - Memory/AsyncMemory 생성과 주입
    - startup guard

  facade.py
    - 허용 Mem0 API만 노출
    - reset 차단

  metrics.py
    - store metric과 안전한 logging

tests/
  unit/
  contract/
  integration/
  concurrency/
  upgrade/
```

각 단위의 경계를 지키면 PostgreSQL query 변경, Mem0 version 대응, business memory policy를 서로 독립적으로 수정할 수 있다.

---

## 20. 최종 결정 기록

### 결정

Mem0 Python OSS library mode의 SQLite를 운영에서 사용하지 않는다. 외부 `PostgresMem0StateStore`가 history와 recent-message method contract를 구현하고 `Mem0CompatibilityLayer`가 `Memory`/`AsyncMemory.db`에 주입한다. 애플리케이션은 `Mem0Facade`만 사용한다.

### 결정 이유

1. SQLite는 memory 알고리즘의 필수 저장소가 아니라 두 보조 상태의 기본 구현이다.
2. 현재 SQLite의 process-local global lock과 local file은 다중 worker/pod 운영에 맞지 않는다.
3. 실제 DB contract가 일곱 method로 작고 SQL이 `storage.py`에 집중되어 있어 adapter 대체 범위가 제한적이다.
4. Mem0 전체 재구현은 현재 요구보다 범위가 크다.
5. 내부 PostgreSQL provider fork는 upstream update 비용이 크다.
6. 서비스 원장·outbox·tenant·정합성은 별도 구현하므로 adapter가 Mem0 pipeline의 모든 한계를 해결할 필요가 없다.
7. 외부 wrapper는 버전 고정과 contract test를 전제로 가장 작은 변경으로 중앙 PostgreSQL 상태를 제공한다.

### 결과

- Mem0의 extraction/retrieval 기능은 유지한다.
- SQLite file과 global lock을 운영 경로에서 제거한다.
- history와 recent context를 여러 worker/pod가 공유한다.
- PostgreSQL adapter와 Mem0 오픈소스 업데이트를 분리한다.
- 서비스 업무 정합성과 Mem0 내부 보조 상태를 명확히 구분한다.

### 재검토 조건

다음 상황에서는 이 결정을 다시 검토한다.

- Mem0가 공식 history-store provider 또는 constructor injection을 제공
- upstream이 `self.db` contract를 크게 변경
- 최근 문맥이 10개 window보다 복잡한 conversation store로 확장
- Mem0 core 부분 실패를 수정해야 하는 patch가 계속 누적
- 우리 memory policy가 Mem0 extraction/retrieval보다 더 큰 비중을 차지
- 초기 SQLite 객체 생성 자체가 허용되지 않음

이 조건이 발생하기 전까지는 외부 PostgreSQL adapter + facade를 기본 설계로 유지한다.
