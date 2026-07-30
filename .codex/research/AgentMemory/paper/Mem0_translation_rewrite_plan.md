# Mem0 Translation Rewrite Plan

> **For agentic workers:** 작업은 원문 대조와 구조 검증을 순서대로 수행한다.

**Goal:** Mem0 논문 전체를 원문 정보 손실 없이, 깨지지 않은 한국어 Markdown으로 재작성한다.

**Architecture:** PDF 원문을 기준 텍스트로 삼고, 기존 번역 파일 하나만 교체한다. 설계·계획 문서는 조사 기록으로 `.codex/research/AgentMemory/paper/`에 보존한다.

**Tech Stack:** Markdown, Poppler `pdftotext`/`pdfinfo`, PowerShell 정규식 검사.

---

### Task 1: 원문 구조와 번역 범위 확정

**Files:**
- Read: `.codex/research/AgentMemory/paper/2504.19413v1.pdf`
- Read: `.codex/research/AgentMemory/paper/Mem0_Building_Production_Ready_AI_Agents_with_Scalable_Long_Term_Memory_ko_translation.md`

- [x] 원문에서 초록, 본문 1~6절, 부록 A~C, 그림 1~4, 표 1~2를 식별한다.
- [x] 수식·알고리즘·프롬프트·표 수치를 보존 대상으로 기록한다.

### Task 2: 한국어 Markdown 전체 재작성

**Files:**
- Modify: `.codex/research/AgentMemory/paper/Mem0_Building_Production_Ready_AI_Agents_with_Scalable_Long_Term_Memory_ko_translation.md`

- [x] 제목과 메타데이터를 정리하고, 초록을 문장 단위로 번역한다.
- [x] 1~6절을 원문 순서대로 번역하고 그림 캡션을 해당 문맥에 배치한다.
- [x] 표 1~2를 열·행·각주가 식별되는 Markdown 표로 변환한다.
- [x] 참고문헌과 부록 A~C를 보존하고, 프롬프트·알고리즘은 코드 블록으로 분리한다.

### Task 3: 구조·잔재 검사

**Files:**
- Verify: `.codex/research/AgentMemory/paper/Mem0_Building_Production_Ready_AI_Agents_with_Scalable_Long_Term_Memory_ko_translation.md`

- [x] 절/그림/표/부록 개수를 원문과 대조한다.
- [x] PDF 페이지 머리글, 단독 대괄호, 잘린 하이픈 단어, 비정상 Markdown 제목을 검사한다.
- [x] 발견한 구조 오류를 수정한 뒤 검사 결과를 보고한다.
