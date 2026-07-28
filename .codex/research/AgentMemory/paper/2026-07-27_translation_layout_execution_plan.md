# 논문 완역본 가독성 재편집 실행 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 세 논문 완역본을 원문 누락 없이 문단·제목·그림/표 중심의 읽기용 Markdown으로 재구성한다.

**Architecture:** 각 PDF의 UTF-8 raw 추출본을 원문 기준으로 사용한다. 기존 자동 번역은 참고만 하고, 원문 섹션별로 자연스러운 한국어 문단을 다시 작성한 뒤 Markdown 구조와 캡션·표·부록을 복원한다. 분석 노트는 변경하지 않는다.

**Tech Stack:** Poppler `pdftotext`, PowerShell 읽기 전용 검증, Markdown, `apply_patch`.

---

### Task 1: 원문 구조·검증 기준 고정

**Files:**
- Read: `.codex/research/AgentMemory/paper/2304.03442v2.pdf`
- Read: `.codex/research/AgentMemory/paper/2504.19413v1.pdf`
- Read: `.codex/research/AgentMemory/paper/2310.08560v2.pdf`
- Read: `%TEMP%/arxiv_2304_03442v2_raw.txt`
- Read: `%TEMP%/arxiv_2504_19413v1_raw.txt`
- Read: `%TEMP%/arxiv_2310_08560v2_raw.txt`

- [ ] **Step 1: PDF 쪽수와 raw 추출본 존재를 확인한다.**

Run:

```powershell
pdfinfo .codex/research/AgentMemory/paper/2304.03442v2.pdf
pdfinfo .codex/research/AgentMemory/paper/2504.19413v1.pdf
pdfinfo .codex/research/AgentMemory/paper/2310.08560v2.pdf
```

Expected: 각각 22쪽, 23쪽, 13쪽이며 raw 추출본을 재생성할 수 있다.

- [ ] **Step 2: 섹션·그림·표·부록을 원문에서 목록화한다.**

Run:

```powershell
Select-String -Path $raw -Pattern '^Figure|^Table|^References$|^Appendix|^[0-9]+\.'
```

Expected: 각 완역본의 섹션 계층과 그림·표 검증 기준을 확보한다.

### Task 2: Generative Agents 완역본 재구성

**Files:**
- Modify: `.codex/research/AgentMemory/paper/Generative_Agents_Interactive_Simulacra_of_Human_Behavior_ko_translation.md`
- Read: `%TEMP%/arxiv_2304_03442v2_raw.txt`

- [ ] **Step 1: 서지·초록·서론을 저자 정보, 독립 그림 캡션, 자연스러운 문단으로 재작성한다.**

Include: 저작권 안내, CCS concepts, keywords, ACM citation, 각주 링크를 보존한다.

- [ ] **Step 2: 관련 연구부터 아키텍처·Smallville·평가·논의·결론까지 절별 문단을 복원한다.**

Include: retrieval 점수식, reflection threshold 150, 각 그림/표 캡션, 평가 수치, 22쪽 원문의 각주를 보존한다.

- [ ] **Step 3: 참고문헌과 부록 A/B를 문단 및 번호 목록으로 재구성한다.**

Include: 부록의 prompt와 25개 interview question을 빠뜨리지 않는다.

- [ ] **Step 4: 원문과 대조한다.**

Run:

```powershell
Select-String -Path .codex/research/AgentMemory/paper/Generative_Agents_Interactive_Simulacra_of_Human_Behavior_ko_translation.md -Pattern '^## 1\.|^## 참고문헌|^## 부록 A|^## 부록 B|ZZSECTION|TODO|TBD'
```

Expected: 모든 주요 섹션·부록이 존재하고 임시 표식은 0개다.

### Task 3: Mem0 완역본 재구성

**Files:**
- Modify: `.codex/research/AgentMemory/paper/Mem0_Building_Production_Ready_AI_Agents_with_Scalable_Long_Term_Memory_ko_translation.md`
- Read: `%TEMP%/arxiv_2504_19413v1_raw.txt`

- [ ] **Step 1: 초록과 제안 방법을 extraction/update 및 Mem0g graph의 독립 문단·수식·그림 캡션으로 재작성한다.**

Include: ADD/UPDATE/DELETE/NOOP, `m=10`, `s=10`, GPT-4o-mini 설정을 보존한다.

- [ ] **Step 2: LOCOMO 실험 설정과 결과를 표·문단으로 재구성한다.**

Include: Table 1의 범주별 F1/BLEU-1/J, Table 2의 latency·token·Overall J, Fig. 4~5 캡션을 보존한다.

- [ ] **Step 3: 결론, 참고문헌, Appendix A/B/C의 프롬프트·알고리즘·baseline 설명을 재구성한다.**

- [ ] **Step 4: 원문과 대조한다.**

Run:

```powershell
Select-String -Path .codex/research/AgentMemory/paper/Mem0_Building_Production_Ready_AI_Agents_with_Scalable_Long_Term_Memory_ko_translation.md -Pattern '^## 1\.|^## 2\.|^## 3\.|^## 4\.|^## 5\.|^## 참고문헌|^## 부록|ZZSECTION|TODO|TBD'
```

Expected: 모든 주요 섹션·부록이 존재하고 임시 표식은 0개다.

### Task 4: MemGPT 완역본 재구성

**Files:**
- Modify: `.codex/research/AgentMemory/paper/MemGPT_Towards_LLMs_as_Operating_Systems_ko_translation.md`
- Read: `%TEMP%/arxiv_2310_08560v2_raw.txt`

- [ ] **Step 1: 초록·서론·메모리 계층을 문단과 독립 그림 캡션으로 재작성한다.**

Include: main context의 system instructions/working context/FIFO queue, recall/archival storage의 차이를 보존한다.

- [ ] **Step 2: queue manager, function executor, event/control flow와 대화·문서 실험을 재구성한다.**

Include: DMR Table 2, conversation opener Table 3, document QA와 nested KV 결과, 그림 캡션을 보존한다.

- [ ] **Step 3: 관련 연구·결론·참고문헌·Appendix 6.1의 모든 지시문을 재구성한다.**

- [ ] **Step 4: 원문과 대조한다.**

Run:

```powershell
Select-String -Path .codex/research/AgentMemory/paper/MemGPT_Towards_LLMs_as_Operating_Systems_ko_translation.md -Pattern '^## 1\.|^## 2\.|^## 3\.|^## 4\.|^## 5\.|^## 참고문헌|^## 6\. 부록|ZZSECTION|TODO|TBD'
```

Expected: 모든 주요 섹션·부록이 존재하고 임시 표식은 0개다.

### Task 5: 공통 완결성 검증

**Files:**
- Read: 완역본 3개
- Read: 원문 PDF 3개

- [ ] **Step 1: 각 PDF의 쪽수와 최상위 섹션·그림·표·부록을 완역본과 재대조한다.**

Run:

```powershell
pdfinfo <pdf>
Select-String -Path <translation> -Pattern '^## |^### |^그림 [0-9]+[:.]|^표 [0-9]+[:.]'
```

Expected: 22쪽, 23쪽, 13쪽의 원문 구조가 각각의 완역본에 반영된다.

- [ ] **Step 2: 읽기 방해 요소를 검사한다.**

Run:

```powershell
Select-String -Path <translation> -Pattern 'ZZSECTION|TODO|TBD|^UIST|^arXiv:|^Mem0: Building|^MemGPT: Towards'
```

Expected: 임시 표식과 반복 페이지 머리말은 0개다. 제목은 문서의 단일 Markdown 제목에서만 허용한다.

- [ ] **Step 3: 분석 노트의 번역본 상대 링크를 확인한다.**

Run:

```powershell
Select-String -Path .codex/research/AgentMemory/paper/*_analysis.md -Pattern '번역본:'
```

Expected: 세 분석 노트가 각각 제목 기반 완역본 이름을 가리킨다.
