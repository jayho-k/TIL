# Hermes Memory 포지셔닝 번역 및 분석

조사일: 2026-07-11

## 출처

- 제목: Why Memory Makes Hermes the Smartest AI Agent
- URL: 원문은 사용자가 대화에 직접 제공
- 업데이트: 2026-06-07
- 태그: hermes agent memory, memory, persistence, ai-agents, chatgpt
- 출처 신뢰도: 중간 ~ 높음
  - Hermes Agent의 memory 가치 제안을 설명하는 공식 블로그 성격의 글로 보인다.
  - 앞선 "How Hermes Agent Memory Works - 3-Layer System Explained"와 내용이 이어진다.
  - 구현 세부보다 제품 포지셔닝/설계 철학에 가까우므로 실제 구현 검증은 별도로 필요하다.

## 조사 목적

이 글은 Hermes memory의 내부 구조 자체보다 "왜 memory가 agent의 핵심 차별점인가"를 설명한다. Chat Portal에 LangChain 진영의 DeepAgents를 적용할 때 memory를 단순 편의 기능이 아니라 operational context로 설계해야 하는 이유를 파악하는 데 목적이 있다.

## 전체 요지

대부분의 AI agent는 금붕어 같은 기억력을 가진다. 새 대화가 시작될 때마다 사용자는 다음 정보를 다시 설명해야 한다.

- 기술 스택
- 선호하는 응답 스타일
- credential 정책
- 프로젝트 제약사항

Hermes는 memory를 통해 이러한 반복 설명을 줄이고, agent가 장기간의 반복 작업에서 더 안정적으로 행동하게 만든다고 주장한다.

핵심 주장은 다음과 같다.

- Hermes는 durable facts, reusable procedures, past-session recall을 분리한다.
- 일반 chatbot은 preference 하나를 기억하는 수준에 머물 수 있다.
- Hermes는 preference를 기억하고, 오래된 세션을 검색하고, 익숙한 workflow를 건드리기 전에 skill을 로드하고, terminal/browser/messaging/cron/GitHub 같은 도구를 올바른 context로 실행할 수 있다.
- ChatGPT는 one-off conversation에 편리하고, Hermes는 memory, tools, automation이 시간이 지날수록 누적되는 반복 작업에 적합하다고 설명한다.

## 금붕어 Agent의 문제

Stateless agent는 세 가지 방식으로 시간을 낭비한다.

1. 매 세션마다 같은 프로젝트 배경을 다시 물어본다.
2. 사용자가 이미 준 correction을 반복해서 어긴다.
3. 오늘의 작업을 지난주 debugging, launch, research 작업과 안정적으로 연결하지 못한다.

채팅에서는 귀찮은 정도지만, agentic work에서는 비용과 위험이 된다.

Agent가 다음 행동을 할 수 있다면 forgotten context는 단순 불편이 아니라 위험이다.

- shell command 실행
- 파일 변경
- browser 열기
- message 전송

잘못된 deploy method, 잘못된 repository, 잘못된 credential assumption은 token 몇 개보다 훨씬 큰 비용을 만든다.

### 해석

이 글에서 memory는 personalization이 아니라 risk control이다.

Chat Portal에 적용하면 "agent가 기억하지 못해도 답변은 할 수 있다"가 아니라, "agent가 기억하지 못하면 위험한 action을 할 수 있다"가 핵심이다.

따라서 memory 설계는 다음과 연결된다.

- tool execution safety
- project policy enforcement
- deploy/release workflow correctness
- tenant/client boundary
- credentials/security policy

## Hermes는 Memory를 Operating Context로 사용한다

Hermes는 memory를 잡학 trivia가 아니라 action을 위한 context로 다룬다.

Hermes가 미래 세션으로 가져갈 수 있는 정보:

- durable user preferences
- environment facts
- stable project conventions

또한 long-term session search를 유지해, 사용자가 transcript를 다시 붙여 넣지 않아도 돌아온 프로젝트를 다시 찾을 수 있게 한다.

이 분리가 중요하다.

- "이 프로젝트는 GitHub push로 배포한다"는 durable fact이므로 memory에 속한다.
- "browser gateway를 debug하는 방법"처럼 긴 절차는 skill에 속한다.
- 일회성 실행 로그는 permanent memory가 아니라 session history에 속한다.

이 구분 덕분에 system이 bloated 되지 않고 유용성을 유지한다고 설명한다.

### 해석

Hermes의 핵심은 memory를 action context로 본다는 점이다.

Chat Portal의 memory도 다음 질문으로 저장 여부를 판단해야 한다.

- 이 정보가 미래 행동의 기본값을 바꾸는가?
- 이 정보가 tool 사용 전 안전 판단에 필요한가?
- 이 정보가 project/workspace convention인가?
- 이 정보가 반복 가능한 procedure인가?
- 이 정보는 단순 log인가?

## 세 가지 실용 Memory Layer

Hermes memory는 세 계층으로 가장 잘 동작한다고 설명한다.

### 1. User and Project Facts

안정적인 preference, environment path, team convention, secret이 아닌 setup note를 저장한다.

### 2. Skills

명령어, 함정, 검증 단계가 포함된 반복 workflow를 저장한다.

### 3. Session Search

사용자가 "전에 이거 했었지"라고 말할 때 과거 대화와 작업 결과를 회상한다.

### 해석

앞선 Hermes memory system 글과 같은 구조다. 다만 이 글은 구조 설명보다 "왜 이게 agent 작업에서 중요해지는가"에 초점이 있다.

Chat Portal에서는 memory layer를 다음처럼 도메인 객체로 나누는 것이 좋다.

```text
Memory Layer
├─ Fact Memory
│  ├─ user preference
│  ├─ project convention
│  ├─ environment note
│  └─ policy/correction
├─ Skill Memory
│  ├─ trigger
│  ├─ commands
│  ├─ pitfalls
│  └─ verification
└─ Session Recall
   ├─ transcript
   ├─ summary
   ├─ artifact refs
   └─ retrieval index
```

## 예시: Memory는 반복되는 배포 실수를 막는다

사용자가 특정 사이트에서 Vercel CLI 직접 배포보다 GitHub push를 선호한다고 하자.

Stateless agent는 자신이 아는 가장 빠른 도구를 쓰려고 할 수 있다.

Hermes는 그 preference를 다음 세션에도 가져가고, 현재 repo를 검사하고, 변경하고, test를 실행하고, commit하고, 기대되는 경로인 GitHub push를 통해 진행할 수 있다.

이 차이는 "bot이 내가 좋아하는 색을 기억한다"와 "agent가 내 workflow를 망가뜨리지 않는다"의 차이다.

첫 번째는 personalization이고, 두 번째는 operational memory다.

### 해석

이 예시는 Chat Portal에서 memory의 acceptance criteria를 정의하는 데 중요하다.

Memory 저장 성공은 다음이 아니다.

- "저장했습니다"라고 말함
- "기억합니다"라고 답함

진짜 성공 기준은 다음이다.

- 같은 종류의 작업에서 올바른 default action을 고름
- 금지된 tool을 피함
- project-specific checklist를 먼저 적용함
- 사용자의 correction을 반복하지 않음

## Memory에 넣어야 하는 것

좋은 memory는 compact하고 future-useful하다.

- 선호하는 communication style
- 안정적인 repo path 또는 environment quirk
- secret을 노출하지 않는 API/platform convention
- 오래 지속되는 workflow preference
- 사용자가 다시 반복하지 않아도 되는 correction

나쁜 memory:

- 오래된 task log
- PR number
- 임시 TODO
- raw transcript
- 다음 주면 만료될 가능성이 높은 정보

### 해석

Memory write policy는 자동화하더라도 classification이 필요하다.

예시 분류:

| 입력 | 저장 위치 |
| --- | --- |
| "나는 짧은 상태 업데이트가 좋아" | durable user preference |
| "이 프로젝트는 GitHub push로 배포해" | durable project convention |
| "배포할 때 lint/test/build를 돌려" | skill |
| "오늘 PR #123 열었어" | session/task history |
| "내일 3단계 마무리해" | task system, not durable memory |

## Skills는 Memory를 확장한다

Skills는 procedural memory다.

Hermes가 어려운 integration을 한 번 고쳤다면, 그 단계는 skill이 될 수 있다.

Skill에 포함될 수 있는 것:

- trigger condition
- exact commands
- common errors
- verification checks

다음에 같은 topic이 나타나면 Hermes는 행동하기 전에 skill을 로드한다.

따라서 Hermes Agent skills와 skills hub도 memory story의 일부라고 설명한다.

Memory는 무엇이 사실인지 말하고, skills는 어떻게 행동할지 말한다.

### 해석

Chat Portal이 단순 RAG memory만 가지면 "과거 정보를 찾는 agent"에 머무른다. 반복 작업을 잘하려면 procedure를 first-class object로 다뤄야 한다.

Skill 객체에 필요한 필드 후보:

- id
- name
- trigger description
- scope/profile/project
- preconditions
- steps
- commands
- verification
- known pitfalls
- last_updated
- source session refs

## Privacy and Safety

Memory는 강력하므로 boundary가 필요하다.

원칙:

- secret을 저장하지 않는다.
- tenant/client context는 profiles로 분리한다.
- 더 이상 사실이 아닌 stale fact는 제거한다.
- 민감한 workflow는 Hermes privacy guide, local Ollama setup, security hardening과 함께 사용한다.

### 해석

Memory는 persistent attack surface다. Chat Portal에서는 memory가 잘못 저장되거나 잘못 검색되는 순간 보안 문제가 된다.

필요한 기능:

- memory namespace/profile isolation
- secret redaction
- PII policy
- memory deletion/edit UI
- audit trail
- retrieval trace
- provider routing policy

## Hermes Memory가 가장 중요한 경우

Hermes memory는 agent가 실제 작업을 할 때 가장 가치 있다.

- 몇 주에 걸쳐 codebase 유지
- daily/weekly cron job 실행
- community/dashboard monitoring
- messaging integration 관리
- customer, project, environment convention 기억

고립된 답변 하나만 필요하다면 memory는 있으면 좋은 기능이다. 하지만 몇 달 동안 같이 일하는 agent를 원한다면 memory는 foundation이다.

### 해석

Chat Portal의 목표가 단순 챗봇이면 memory는 부가 기능일 수 있다. 하지만 DeepAgents 기반 agent가 도구를 쓰고, 작업을 반복하고, 장기 프로젝트를 유지한다면 memory는 핵심 인프라다.

## Next Step

Hermes Agent setup guide로 시작하고 memory system explainer를 읽으라고 안내한다. 이미 Hermes를 실행 중이라면 현재 memory를 audit하고 반복 가능한 procedure를 skill로 변환하라고 한다.

## Install Path

Memory가 Hermes를 다르게 느끼게 하는 이유라면, 설치가 증명 지점이라고 설명한다.

설치 후 persistent memory를 의도적으로 구성한다.

- 성공한 task 이후 durable preference 하나 저장
- project convention 하나 저장
- reusable skill 하나 저장

### 해석

Chat Portal memory도 PoC 검증이 필요하다. 단순 저장/검색 테스트가 아니라 행동 변화 테스트를 해야 한다.

PoC 시나리오:

1. 사용자가 project convention을 알려준다.
2. agent가 관련 작업을 수행한다.
3. 새 세션에서 비슷한 작업을 요청한다.
4. agent가 convention을 자동 적용하는지 확인한다.
5. 반복 절차가 있으면 skill로 승격되는지 확인한다.

## Recent Community Troubleshooting Note

현재 support pattern은 명확하다고 설명한다.

사용자들은 긴 프로젝트를 견디는 memory를 원하지만, context, compaction, third-party memory layer가 실패할 때 안전하게 복구하는 방법도 필요하다.

이 positioning page 다음으로 실용적인 단계는 Hermes memory and context troubleshooting guide, 그리고 더 깊은 memory system explainer를 읽는 것이다.

### 해석

Memory는 "한 번 설계하면 끝"이 아니다. 운영 중 장애 대응이 필요하다.

Chat Portal에서 필요한 failure handling:

- compaction 실패
- retrieval 실패
- provider timeout
- stale memory 적용
- wrong profile retrieval
- skill trigger 오탐/미탐
- memory write 누락

## FAQ 번역

### Hermes Agent는 실제로 어떤 memory를 보관하는가?

Hermes는 user preference, durable project fact, reusable skill, searchable session history를 보관할 수 있다. 목적은 모든 transcript를 prompt에 덤프하는 것이 아니라, 미래 행동을 바꾸는 fact를 보존하는 것이다.

### Hermes memory는 private한가?

Memory는 기본적으로 vendor SaaS 계정이 아니라 사용자의 Hermes 설치에 저장된다. 다만 각 실행에서 prompt를 받는 LLM provider는 사용자가 선택하므로, 최대 privacy가 필요하다면 local model과 함께 사용해야 한다.

### Hermes memory는 ChatGPT memory와 어떻게 다른가?

Hermes memory는 operational하다. terminal, browser, cron, messaging, code workflow를 안내할 수 있으며, skills는 반복된 fix를 재사용 가능한 procedure로 바꾼다.

### 나쁜 memory를 제거할 수 있는가?

그렇다. 사실이 바뀌면 memory와 skill을 수정하거나 제거할 수 있다. 좋은 memory hygiene은 agent가 더 좋아지게 만들고 cluttered 되지 않게 하는 운영의 일부다.

### 언제 memory 대신 skill을 사용해야 하는가?

Durable fact와 preference에는 memory를 사용한다. 반복 workflow, command, gotcha, verification step, multi-step procedure에는 skill을 사용한다.

## Chat Portal 설계 시사점

이 글에서 얻을 수 있는 핵심은 "memory는 personalization이 아니라 operation layer"라는 점이다.

비교 축은 일반 LangChain memory가 아니라 DeepAgents여야 한다. 즉, Hermes가 durable facts / skills / session search를 분리하는 방식이 DeepAgents의 장기 작업 context, planning, tool execution, 상태/파일 관리, sub-agent workflow와 어떻게 맞물리는지 확인해야 한다.

Chat Portal에 필요한 memory 설계 원칙:

1. Memory는 미래 행동을 바꾸는 정보만 durable로 승격한다.
2. Procedure는 fact memory가 아니라 skill로 분리한다.
3. Session history는 검색 가능하게 두되 permanent fact와 섞지 않는다.
4. Profile/namespace로 context leakage를 막는다.
5. Tool execution 전 memory 기반 policy를 확인한다.
6. Memory 품질은 저장량이 아니라 행동 정확도로 평가한다.

## 앞선 Hermes Memory System 글과의 관계

앞선 글은 구조 설명이다.

- durable facts
- procedural skills
- session search
- SOUL.md
- profiles
- privacy
- hygiene

이번 글은 가치 주장이다.

- stateless agent의 반복 설명 문제
- operational memory의 중요성
- ChatGPT와 Hermes의 차이
- memory가 tool-using agent에서 risk control이 되는 이유

두 글을 합치면 Hermes의 memory 철학은 다음 문장으로 요약된다.

> Memory should not merely help an agent remember. It should change the agent's default action safely and correctly in future work.

## 다음 조사 후보

- Hermes memory troubleshooting guide
- Hermes skills hub 구조
- Hermes profiles 구현 방식
- OpenViking의 memory/resource/skill 통합 구조
- LangGraph Store와 checkpoint memory
- Mem0의 memory extraction/update 구조
- Letta의 memory blocks와 archival memory
