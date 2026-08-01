# AGENTS.md - TIL Study Project

이 저장소는 jayho가 공부한 내용을 정리하는 TIL(Today I Learned) 노트 저장소이다.
코드 프로젝트가 아니라 학습 노트 중심이므로, 모든 작업은 노트 작성과 정리 흐름에 맞춘다.

## 프로젝트 성격

- 공부한 개념을 Markdown으로 정리한 저장소이다.
- 주제별 폴더로 분류한다: `AI/`, `CS/`, `Server/`, `Web/`, `PS/`.
- 노트에는 이미지(`*.assets/` 폴더), Jupyter 노트북(`.ipynb`), 코드 예제가 포함될 수 있다.
- 새 노트는 기존 폴더 구조를 따른다. 상세 매핑은 `.codex/MAP.md`를 참고한다.

## 학습 워크플로우

공부와 노트 정리는 2단계로 진행한다.

### 1단계 - `.codex/`에서 초안 작성

| 작업 유형 | 저장 위치 | 설명 |
| --- | --- | --- |
| 학습 초안 / 정리 중인 노트 | `.codex/임시파일명.md` | 자유롭게 작성하는 작업 공간 |
| 조사 / 분석 자료 | `.codex/research/주제명/파일명.md` | 외부 자료 분석, critical review 등 |

예시:

```text
.codex/
  draft_kafka_consumer.md
  research/
    Milvus/
      cdc_critical_analysis.md
    Kafka/
      kafka_replication_review.md
```

### 2단계 - 본 저장소로 이관

초안이 완성되면 아래 기준으로 본 저장소에 합친다.

| 상황 | 처리 방법 |
| --- | --- |
| 기존 파일과 같은 주제 | 기존 파일을 읽고, 적절한 위치에 내용을 끼워넣기 |
| 새로운 주제 | `.codex/MAP.md`를 참고해 올바른 폴더에 새 파일 생성 |
| 기존 파일을 대체할 수준 | 기존 파일과 병합 |

이관 후에는 `.codex/MAP.md`에 새 노트를 등록한다.

파일 삭제 기준:

- `.codex/` 루트의 임시 초안 파일(`draft_*.md` 등)은 이관 후 삭제한다.
- `.codex/research/` 폴더의 조사 자료는 삭제하지 않고 원본 참고 자료로 보존한다.

## 사용자와 공부하는 방식

- 새 개념을 정리할 때는 주제를 확인하고 적절한 폴더 경로를 제안한다.
- 먼저 `.codex/`에 초안을 작성하고, 완성되면 본 저장소로 이관한다.
- 기존 노트를 찾을 때는 `.codex/MAP.md`와 저장소 파일을 기준으로 검색한다.
- 개념 질문에는 기존 노트 내용을 우선 기반으로 답한다.
- 노트가 없는 내용은 새로 정리할 수 있다.
- 노트 보강 요청에는 기존 노트를 읽고 빠진 내용이나 더 깊은 내용을 추가 제안한다.

## 파일 규칙

```text
폴더/
  01_주제명.md
  개념명.md
  주제명.assets/
```

- 노트 파일은 `.md`를 사용한다.
- 실습 코드는 `code/` 서브폴더에 둔다.
- 이미지는 `파일명.assets/` 폴더를 사용한다. Typora 스타일을 따른다.
- Jupyter 실습은 `.ipynb`를 사용한다.

## 전체 구조 요약

| 폴더 | 내용 |
| --- | --- |
| `AI/` | 딥러닝, Transformer, vLLM, Pandas, Matplotlib |
| `CS/` | 자료구조, 알고리즘, OS, 네트워크, DB, 언어, 디자인패턴 |
| `Server/` | Docker, Kafka, Redis, Airflow, Oracle, Prometheus 등 인프라 |
| `Web/` | Spring, JPA, Django, Vue, 대규모 시스템 |
| `PS/` | 백준, 프로그래머스, SWEA 풀이 |

## 주제별 추가 규칙

- Airflow 관련 조사나 노트 작성 시 `.codex/rules/airflow.md`를 먼저 읽고 따른다.
- 외부 자료를 참고한 경우 버전, 날짜, 출처 신뢰도를 명확히 남긴다.

## Git 작업 금지

- 사용자가 명시적으로 요청하기 전에는 Git 상태를 변경하지 않는다.
- `git add`, `git commit`, `git reset`, `git checkout`, `git restore`, `git rebase`, `git merge`, `git push`, `git pull`을 실행하지 않는다.
- Git 상태 확인(`git status`, `git diff`, `git log`)만 필요할 때 읽기 전용으로 사용한다.
- 이미 만들어진 커밋을 되돌리거나 수정하는 작업도 사용자의 명시적 지시가 있을 때만 수행한다.
