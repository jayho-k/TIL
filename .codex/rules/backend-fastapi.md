# Backend FastAPI Rules

FastAPI 또는 Python backend 코드를 작성, 테스트, 실행할 때는 아래 규칙을 따른다.

## Python Environment

- 전역 Python 환경에 dependency를 설치하지 않는다.
- `pip install ...`을 직접 실행하기 전에 반드시 프로젝트 또는 작업 폴더에 `.venv`가 있는지 확인한다.
- `.venv`가 없으면 먼저 생성한다.

Windows PowerShell 기준:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -r requirements.txt
```

이후 Python, pytest, uvicorn, pip는 항상 `.venv`의 실행 파일을 사용한다.

```powershell
.\.venv\Scripts\python -m pytest
.\.venv\Scripts\python -m uvicorn app.main:app --reload
.\.venv\Scripts\python -m pip install <package>
```

## Dependency Changes

- 새 dependency가 필요하면 먼저 `requirements.txt` 또는 해당 프로젝트의 dependency 파일에 기록한다.
- dependency 설치는 `.venv` 내부에서만 수행한다.
- 전역 설치가 이미 발생한 경우, 임의로 계속 사용하지 말고 사용자에게 알리고 `.venv` 기준으로 다시 검증한다.

## Test and Run

- 테스트 명령은 `pytest` 단독 호출보다 `.venv` Python을 통한 호출을 우선한다.
- FastAPI 서버 실행도 `.venv` Python을 통해 실행한다.
- 테스트 결과를 보고할 때 사용한 Python executable이 `.venv`인지 함께 확인한다.
