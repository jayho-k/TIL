# DeepAgent EventSourceResponse 스트리밍

DeepAgent/LangGraph `astream()`을 FastAPI의 `EventSourceResponse`로 제공한다.
기존 `StreamingResponseAdapter`는 학습·비교 코드로 보존하며 운영 라우팅에서는 사용하지 않는다.

## 사전 조건

- CPython 3.12
- 외부 PostgreSQL (`POSTGRES_DSN`)
- Redis Stack (`REDIS_URL`, 기본 `redis://localhost:6379`)
- OpenAI 호환 Ollama endpoint

실제 secret은 `.env`에만 둔다. PostgreSQL과 Redis Docker Compose는 이 프로젝트에서 제공하지 않는다.

## 실행

```powershell
uv sync
uv run alembic upgrade head
uv run uvicorn app.api.main:app --host 0.0.0.0 --port 8000
```

```http
POST /v1/chat/stream
Content-Type: application/json

{"thread_id":"conversation-1","message":"안녕"}
```

같은 `thread_id`를 후속 요청에 사용하면 Redis checkpoint의 대화 state가 이어진다.
기존 `/v1/chat/event-source-response`와 `/v1/chat/streaming-response`도 같은 구현으로 연결된다.
후자는 deprecated 호환 URL이며, 이름과 달리 실제 transport와 로그 값은 `event_source_response`다.
POST 응답이 SSE이므로 브라우저에서는 `fetch` 기반 SSE 소비기를 사용한다.

## 운영 정책

- heartbeat 15초, send timeout 30초, Agent timeout 10분
- 기본 제한: process별 SSE 30개, Agent 10개. 1 RPS는 시험 목표이며 rate limiter가 아니다.
- SSE/Agent 슬롯 확보와 초기 DB commit을 HTTP 응답 시작 전에 수행한다.
  시작 실패는 `503` 및 `Retry-After: 5`로 응답한다.
- 최종 DB commit 성공 후에만 `stream.completed`를 전송한다.
  저장 실패는 `PERSISTENCE_ERROR`, Agent 실패는 `AGENT_ERROR`, 실행 초과는 `AGENT_TIMEOUT`이다.
  실패 로그를 저장하지 못해도 `stream.error` 전송을 시도한다.
- DB 작업별 제한은 기본 10초(`ChatStreamService.persistence_timeout_seconds`)다.
- disconnect 시 Agent를 취소하며 PostgreSQL `RUNNING` 로그는 그대로 둔다.
- Response 종료 시 시작한 generator와 source task를 닫고 연결/실행 슬롯을 반환한다.
- source는 하나의 task가 소비하며 application queue 크기는 1이다.
  배칭은 첫 토큰 도착부터 최대 20ms 또는 128문자를 기준으로 flush한다.
  event-loop 스케줄링·OS 타이머·전송 대기 때문에 실제 도착시간이 20ms를 초과할 수 있다.
- 공개 토큰은 v2 root namespace(`ns=()`)의 `model` 노드로 제한한다.
  subagent·다른 노드·`nostream`/`private` 태그를 제외하고 text block만 노출한다.
  다른 graph에 삽입할 때는 `StreamEventProjector(public_nodes=...)`를 명시적으로 설정한다.
- PostgreSQL session은 시작/완료/실패 기록 구간에서만 짧게 사용한다.
- checkpoint는 SSE replay log가 아니다.

## 검증

```powershell
uv run ruff check app tests load_tests
uv run pytest -q
uv run pytest tests/integration -q
```

실제 인프라 및 모델 검증은 관련 `RUN_*_TESTS=1` 환경변수가 있을 때만 실행한다.
부하 테스트 명령과 해석 범위는 `docs/reports/load-test-report.md`를 참고한다.

로컬 회귀 테스트는 commit 실패, 실패 로그 저장 오류, 초기화 실패, permit 고갈,
header/body send timeout, disconnect, preflight 취소, Agent timeout, 내부 출력 차단,
배칭 deadline과 실제 DeepAgent + 가짜 모델의 v2 이벤트 형식을 검증한다.

## 운영 시스템에 삽입할 때

- 인증된 사용자/tenant와 `thread_id` 소유권을 응답 초기화 전에 확인해야 한다.
- 동일 thread의 동시 turn은 별도 거부/직렬화 정책이 필요하다. 다중 worker라면 분산 제어가 필요하다.
- `RUNNING` 로그만으로 현재 실행 여부를 판단할 수 없다. 중단/프로세스 장애의 만료 판정이 필요하다.
- 현재 readiness는 시작 시 DB/Redis 연결 성공 여부에 기반한다. 실행 중 장애의 주기적 탐지는 별도다.
- 프록시 buffering/idle timeout, 실제 DB/Redis/모델 장애, 장시간 부하는 배포 환경에서 검증해야 한다.
- 사용자 정의 tool/source는 취소에 협조하고 외부 I/O timeout을 가져야 한다.
  application queue 제한이 LangGraph 내부 queue나 provider buffer까지 제한하지는 않는다.

이번 수정의 로컬 테스트 통과는 위 통합 조건이나 실제 운영 용량에 대한 보증이 아니다.
