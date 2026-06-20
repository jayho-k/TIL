# Airflow 조사 규칙

Airflow 관련 내용을 조사하거나 노트를 작성할 때 따르는 규칙.

---

## 버전 명시 원칙

- 조사한 내용이 어느 Airflow 버전에서 유효한지 항상 명시
- 특히 2.x ↔ 3.x 간 동작 차이가 크므로 버전 구분 필수
- Provider 패키지도 버전 별도 명시 (ex. `apache-airflow-providers-amazon >= 8.0`)

## 조사 우선순위 (출처 신뢰도 순서)

1. Apache Airflow 공식 문서 (airflow.apache.org)
2. Provider 공식 문서 (AWS, GCP, Azure 등)
3. Astronomer 공식 블로그/문서 (astronomer.io)
4. AIP (Airflow Improvement Proposal) 원문
5. 커뮤니티 아티클 (Medium, 블로그 등) — 날짜 반드시 확인

## 노트 구성 기준

- **개념**: 왜 만들어졌는지 (배경/문제) 먼저, 그 다음 원리
- **비교**: 유사 기능이 있으면 반드시 비교표 포함 (ex. Poke vs Reschedule vs Deferrable)
- **코드**: 최소 동작하는 예제 포함. provider import 경로까지 명시
- **운영**: 설정값, HA 구성, 모니터링 포인트 포함

## Executor/Component 관련 주의

- Executor 종류(Sequential, Local, Celery, Kubernetes)에 따라 동작이 달라지는 기능은 별도 표기
- Triggerer가 필요한 기능(Deferrable Operators)은 Triggerer 설치/HA 여부를 전제 조건으로 명시

## 이관 기준 (research → 본 저장소)

- `Server/Airflow/text/` 아래에 시리즈 파일로 추가
- 기존 `01_Airflow.md`와 주제 겹치면 해당 파일에 섹션 추가
- 새 주제(ex. Deferrable, Executor, Sensor 등)는 새 파일 생성 후 MAP.md 등록
- research 파일은 이관 후에도 `.claude/research/`에 유지 (삭제하지 않음)
