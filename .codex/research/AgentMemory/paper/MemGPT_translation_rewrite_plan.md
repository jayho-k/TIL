# MemGPT Translation Rewrite Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 영어 원문을 기준으로 MemGPT 논문의 모든 텍스트 요소를 빠짐없이 자연스러운 한국어로 다시 번역한다.

**Architecture:** 원문 Markdown을 유일한 기준으로 삼아 제목·저자·초록부터 부록까지 순서대로 번역문을 재구축한다. 이미지 파일은 추가하지 않고, 원문에 있는 그림·표·코드·프롬프트의 순서와 내용을 Markdown으로 보존한다. 재작성 후 원문과 번역문의 섹션·그림·표·코드 요소를 다시 대조한다.

**Tech Stack:** UTF-8 Markdown, PowerShell 읽기·검수 명령

---

## File Structure

- Modify: `.codex/research/AgentMemory/paper/MemGPT_Towards_LLMs_as_Operating_Systems_ko_translation.md` — 완전한 한국어 번역문
- Reference: `.codex/research/AgentMemory/paper/2310.08560v2.pdf` — 번역 대조용 영어 원문 PDF
- Context only: `.codex/research/AgentMemory/paper/MemGPT_Towards_LLMs_as_Operating_Systems.md` — 기존 메모 파일(원문 전체가 아님)
- Reference: `.codex/research/AgentMemory/paper/MemGPT_Towards_LLMs_as_Operating_Systems_analysis.md` — 번역과 분리된 해석·비평 노트
- Reference: `.codex/research/AgentMemory/paper/Generative_Agents_Interactive_Simulacra_of_Human_Behavior_ko_translation.md` — 제목 메타데이터·캡션·Markdown 구성의 참고 형식

### Task 1: 원문 구조와 보존 대상 목록화

**Files:**
- Read: `.codex/research/AgentMemory/paper/2310.08560v2.pdf`

- [x] **Step 1: 원문의 제목 계층과 부록 항목을 추출한다.**

Run:

```powershell
pdftotext.exe -layout '.codex\research\AgentMemory\paper\2310.08560v2.pdf' "$env:TEMP\memgpt_2310.08560v2_layout.txt"
Select-String -LiteralPath "$env:TEMP\memgpt_2310.08560v2_layout.txt" -Pattern '^(\s{0,5}(Abstract|[1-5]\. |References|A\.))'
```

Expected: 제목, 1~5장, 참고문헌, 부록 및 모든 하위 항목이 원문 순서대로 출력된다.

- [x] **Step 2: 그림·표·코드·프롬프트·함수 호출의 위치를 기록한다.**

Run:

```powershell
Select-String -LiteralPath "$env:TEMP\memgpt_2310.08560v2_layout.txt" -Pattern '(Figure [0-9]+\.|Table [0-9]+\.|[A-Za-z_]+\()'
```

Expected: 번역문에서 생략하면 안 되는 비서술 요소의 위치를 확인할 수 있다.

### Task 2: 제목·초록·1~2장 번역 재구성

**Files:**
- Modify: `.codex/research/AgentMemory/paper/MemGPT_Towards_LLMs_as_Operating_Systems_ko_translation.md`
- Read: `.codex/research/AgentMemory/paper/2310.08560v2.pdf`

- [x] **Step 1: 문서 메타데이터를 기준 노트 형식으로 작성한다.**

번역문 상단에 한국어 제목, 원문 서지 정보, 전체 번역임을 밝히는 범위 설명, 저자 목록을 넣는다. 분석·비평을 추가하지 않는다.

- [x] **Step 2: 초록과 1장을 단락 순서대로 완전 번역한다.**

컨텍스트 창의 한계, 가상 메모리 비유, 함수 호출, MemGPT의 기여를 원문 단락 순서로 옮긴다. 그림 1~2의 캡션과 본문 참조도 보존한다.

- [x] **Step 3: 2장의 메모리 계층과 제어 흐름을 완전 번역한다.**

주 컨텍스트, 외부 컨텍스트, Queue Manager, function executor, function chaining을 원문 순서대로 번역한다. `working_context`, `recall_storage`, 함수 호출 예시 등 코드 식별자는 영어 표기를 그대로 둔다.

### Task 3: 3~5장 및 참고문헌 번역 재구성

**Files:**
- Modify: `.codex/research/AgentMemory/paper/MemGPT_Towards_LLMs_as_Operating_Systems_ko_translation.md`
- Read: `.codex/research/AgentMemory/paper/2310.08560v2.pdf`

- [x] **Step 1: 3장의 대화·문서 분석 실험을 완전 번역한다.**

DMR, Opener, 다중 문서 질의응답, 중첩 key-value 검색의 과제 설정·비교 기준·정량 결과·표 캡션을 모두 보존한다. 수치, 모델명, 데이터셋명과 인용 키는 원문 표기와 일치시킨다.

- [x] **Step 2: 4장 관련 연구와 5장 결론을 완전 번역한다.**

각 문단의 주장과 인용을 보존하고, 번역자의 요약이나 최신 기술 비교를 더하지 않는다.

- [x] **Step 3: 참고문헌을 원문 순서로 보존한다.**

서지 표기는 원문의 영문 표기를 유지하며, 본문 인용 키와 대응되도록 누락 없이 넣는다.

### Task 4: 부록의 지시문·프롬프트 전문 번역

**Files:**
- Modify: `.codex/research/AgentMemory/paper/MemGPT_Towards_LLMs_as_Operating_Systems_ko_translation.md`
- Read: `.codex/research/AgentMemory/paper/2310.08560v2.pdf`

- [x] **Step 1: 부록의 하위 섹션 체계를 원문과 동일하게 만든다.**

`6.1.1`부터 마지막 부록 항목까지 원문에 있는 제목과 순서를 번역문에 동일하게 둔다.

- [x] **Step 2: 모든 시스템 지시문과 사용자 프롬프트를 전문으로 옮긴다.**

명령문, 예시 입력·출력, XML/JSON/함수 형식, 자리표시자, 특수 토큰을 생략하거나 축약하지 않는다. 코드 블록 내부의 문구는 의미를 번역하되 형식과 식별자는 유지한다.

### Task 5: 구조·내용 충실도 검수

**Files:**
- Verify: `.codex/research/AgentMemory/paper/MemGPT_Towards_LLMs_as_Operating_Systems_ko_translation.md`
- Compare: `.codex/research/AgentMemory/paper/2310.08560v2.pdf`

- [x] **Step 1: 제목 계층을 원문과 대조한다.**

Run:

```powershell
Select-String -LiteralPath '.codex\research\AgentMemory\paper\MemGPT_Towards_LLMs_as_Operating_Systems_ko_translation.md' -Pattern '^(#{1,6})\s'
```

Expected: 원문의 장·절·부록 계층이 모두 존재하며 순서가 같다.

- [x] **Step 2: 잔여 추출 오류와 번역 누락을 검사한다.**

Run:

```powershell
Select-String -LiteralPath '.codex\research\AgentMemory\paper\MemGPT_Towards_LLMs_as_Operating_Systems_ko_translation.md' -Pattern 'tiguous|Ki-|아들 외|나이\)|계속 “|\[cs\.AI\]'
```

Expected: 출력이 없다. 발견되면 원문을 재대조해 해당 문단을 바로잡는다.

- [x] **Step 3: 그림·표·코드 블록·프롬프트를 원문과 대조한다.**

원문과 번역문을 나란히 읽고 모든 그림·표 캡션, 실험 수치, 코드 블록, 함수 호출, 부록 프롬프트가 대응하는지 확인한다.
