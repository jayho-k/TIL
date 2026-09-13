# DeepAgent File Translation HITL PoC

TXT 파일을 DeepAgent의 중첩 SubAgent들이 분석, 추출, 번역, 검증한 뒤 사람의 선택을 기다렸다가 결과 파일을 만드는 실습 프로젝트입니다.

## 구성

```text
Document DeepAgent
└─ File Translation DeepAgent
   ├─ File Analyzer SubAgent
   ├─ File Extractor SubAgent
   ├─ File Translator SubAgent
   ├─ File Validation SubAgent
   ├─ TranslationReviewGateMiddleware → interrupt()
   └─ replace_file Tool
```

단계 호출은 LLM의 자율적인 Tool 선택에 맡기지 않습니다. `before_model` Middleware가 다음 `task` ToolCall을 생성해 DeepAgent의 정상적인 tools 노드로 보냅니다. Validation이 끝난 다음 Middleware가 `interrupt()`를 실행하며, RedisSaver가 실행 상태를 보존합니다.

## 준비

- Python 3.11 이상
- `localhost:6379`에서 실행 중인 Redis
- OpenAI 호환 Chat Completions API

현재 설정은 기존 Docker Redis와 사용자가 제공한 Ollama endpoint를 사용합니다. 비밀값을 저장소에 올리지 않도록 `.env`는 Git에서 제외됩니다.

```powershell
cd C:\Users\jayho\Developer\practice\AI\agent_hitl
$env:UV_CACHE_DIR='.uv-cache'
uv sync
Copy-Item .env.example .env  # .env가 없을 때만 실행
```

## 실행

터미널 1에서 FastAPI 서버를 실행합니다.

```powershell
$env:UV_CACHE_DIR='.uv-cache'
uv run uvicorn app.api.main:app --reload --port 8000
```

터미널 2에서 Streamlit을 실행합니다.

```powershell
$env:UV_CACHE_DIR='.uv-cache'
uv run streamlit run streamlit_app/main.py
```

브라우저에서 TXT 파일을 올리면 첫 번째 SSE 요청은 `hitl.required`를 반환하고 종료됩니다. 사용자가 segment별로 1차 번역, 검증 번역, 직접 수정을 선택하면 두 번째 `/resume` 요청이 같은 Redis 체크포인트를 이어 실행하고 결과 TXT를 제공합니다.

## API

- `POST /runs`: UTF-8 TXT 업로드 및 실행 시작, SSE 반환
- `GET /runs/{run_id}`: 실행 상태와 현재 검수 요청 조회
- `POST /runs/{run_id}/resume`: 사람의 결정을 제출하고 실행 재개, SSE 반환
- `GET /runs/{run_id}/download`: 완료된 TXT 다운로드
- `GET /health`: 서버 상태 확인

## 검증

```powershell
$env:UV_CACHE_DIR='.uv-cache'
uv run ruff check app tests
uv run pytest tests/unit -q
```

실제 endpoint와 Redis를 사용하는 통합 확인은 다음 스크립트로 수행합니다.

```powershell
uv run python scripts/live_smoke.py
uv run python scripts/live_resume.py <run_id>
```

상세 설계는 [설계 문서](docs/specs/2026-09-13-deepagent-hitl-poc-design.md), 구현 순서는 [구현 계획](docs/plans/2026-09-13-deepagent-hitl-poc-implementation.md)을 참고하세요.
