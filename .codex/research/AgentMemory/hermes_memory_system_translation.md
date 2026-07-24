# Hermes Agent Memory System 번역 및 분석

조사일: 2026-07-11

## 출처

- 제목: How Hermes Agent Memory Works - 3-Layer System Explained
- URL: https://hermes-agent.ai/blog/hermes-agent-memory-system
- 업데이트: 2026-06-07
- 출처 신뢰도: 중간 ~ 높음
  - Hermes Agent 공식 블로그로 보이며, Hermes 자체 메모리 구조를 설명하는 1차 자료에 가깝다.
  - 다만 제품/프로젝트 홍보 목적이 섞여 있으므로, 실제 구현 세부사항은 코드/문서로 추가 검증이 필요하다.

## 조사 목적

Chat Portal 서비스에 LangChain 진영의 DeepAgents를 적용할 예정이므로, 비교 대상은 단순한 LangChain 기본 memory가 아니라 DeepAgents의 agent 작업 구조와 memory/context 운용 방식이어야 한다. 이 문서는 Hermes Agent가 agent memory를 어떻게 계층화하는지 먼저 학습하고, 이후 DeepAgents 및 OpenViking 같은 장기 저장 memory 시스템과 비교하기 위한 기초 자료다.

관심사는 단순 대화 저장이 아니라 다음과 같다.

- 장기 사실 저장
- 절차/워크플로우 저장
- 과거 세션 검색
- 프로필별 memory 격리
- privacy와 memory hygiene
- 실제 행동을 바꾸는 memory 설계

## 전체 요지

Hermes의 메모리는 단일한 "remember this" 필드가 아니다. 미래의 agent 실행에서 반복적인 컨텍스트 제공과 수정 요청을 줄이기 위한 계층형 시스템이다.

Hermes Agent의 메모리는 실무적으로 세 계층으로 구성된다.

1. 안정적인 사실과 선호를 위한 durable memory
2. 재사용 가능한 절차를 위한 skills
3. 과거 대화를 회상하기 위한 session search

미래 행동에 영향을 줘야 하는 사실은 durable memory에 넣는다. 명령어와 검증 단계가 포함된 workflow는 skills에 넣는다. 사용자가 이전 대화의 내용을 언급할 때는 session search를 사용한다.

이 구조 때문에 Hermes는 stateless chat agent보다 memory 측면에서 강점을 가진다고 설명한다.

## Layer 1: Durable Facts

Durable memory는 계속 유용하게 남는 압축된 사실을 위한 공간이다.

예시는 다음과 같다.

- 선호하는 커뮤니케이션 방식
- 안정적인 프로젝트 경로
- 배포 규칙
- 환경 특이사항
- 사용자가 반복해서 고치지 않아도 되도록 저장해야 하는 수정 사항

좋은 memory는 선언형이다.

- 이 프로젝트는 GitHub push를 통해 배포한다.
- 사용자는 간결하고 쉬운 영어 상태 업데이트를 선호한다.
- 로컬 설정 파일은 특정 경로에 있다.

나쁜 memory는 작업 로그다.

- 오늘 X 버그를 고쳤다.
- Y PR을 열었다.
- 내일 세 번째 단계를 끝내야 한다.

이런 정보는 빠르게 만료되므로 durable memory가 아니라 session history, task system, issue tracker 같은 곳에 속한다.

### 해석

Hermes의 durable memory는 "대화 기록 저장소"가 아니라 agent의 미래 기본 행동을 바꾸는 설정값에 가깝다. 따라서 저장 기준은 "나중에도 다시 적용되어야 하는가"이다.

Chat Portal에 적용하면 durable memory는 다음과 같은 데이터를 담을 수 있다.

- 사용자 응답 스타일 선호
- 프로젝트별 금지 도구
- 배포/테스트 기본 정책
- 자주 쓰는 repository 경로
- tenant별 고정 규칙

반대로 다음은 durable memory에 넣지 않는 편이 좋다.

- 오늘 작업한 임시 상태
- 일회성 TODO
- 특정 PR의 진행 상황
- 곧 만료될 일정성 정보

## Layer 2: Procedural Skills

Skills는 절차 계층이다.

Skills는 Hermes에게 다음을 알려준다.

- 언제 특정 workflow를 로드해야 하는지
- 어떤 명령어를 실행해야 하는지
- 어떤 실수를 피해야 하는지
- 성공 여부를 어떻게 검증해야 하는지

Skill은 관련 있을 때만 로드되기 때문에 memory보다 더 자세할 수 있다.

예를 들어 브라우저 QA용 Hermes skill은 다음을 포함할 수 있다.

- viewport 확인
- console 검사
- screenshot 규칙
- 알려진 renderer 이슈

이런 내용을 단일 memory 항목에 억지로 넣어서는 안 된다.

### 해석

Hermes는 "절차"를 durable fact와 분리한다. 이 구분이 중요하다.

- Durable fact: 무엇이 사실인가
- Skill: 어떻게 해야 하는가

Chat Portal에서 agent memory를 설계할 때도 절차형 지식은 별도 구조로 빼는 편이 좋다. 예를 들어 "이 프로젝트는 GitHub push로 배포한다"는 durable fact이고, "배포할 때 lint, test, build, git status, push 순서로 확인한다"는 skill이다.

DeepAgents와 비교할 때 핵심 질문은 "대화 이력을 얼마나 저장하는가"가 아니라, 반복 작업에 필요한 사실/절차/세션 회상을 각각 어떤 계층으로 다루는가이다. LangChain의 단순 buffer memory나 summary memory는 보조 비교 대상으로만 두고, 실제 비교는 DeepAgents가 제공하는 장기 작업 컨텍스트, 계획/작업 관리, 파일/상태 저장, sub-agent 또는 tool workflow와 Hermes의 durable memory/skills/session search를 나란히 놓고 봐야 한다.

따라서 Chat Portal에는 최소한 다음 타입 분리가 필요하다.

- facts
- preferences
- procedures
- session references

## Layer 3: Session Search

Session search는 회상을 위한 계층이다.

사용자가 "이거 전에 고쳤잖아" 또는 "지난번 접근 방식을 써줘"라고 말하면, Hermes는 사용자에게 전체 이야기를 다시 요청하는 대신 이전 세션을 검색할 수 있다.

이 방식은 영구 memory를 작게 유지하면서도 오래된 작업을 다시 찾을 수 있게 한다. 또한 원본 대화 전체를 영구 사실로 저장하려는 유혹을 줄여준다.

### 해석

Session search는 durable memory의 오염을 줄이는 역할을 한다.

모든 과거 대화를 durable memory로 승격시키면 다음 문제가 생긴다.

- 오래된 정보가 계속 agent 행동에 영향을 준다.
- tenant/client/project context가 섞인다.
- memory가 task log처럼 비대해진다.
- 검색 가능한 history와 행동 지침이 구분되지 않는다.

따라서 Chat Portal에서도 과거 대화/작업 이력은 별도 session store에 두고, 필요할 때 retrieval하는 구조가 적합하다.

## SOUL.md의 역할

`SOUL.md`는 personality와 운영 지침이다. memory의 대체물이 아니다.

`SOUL.md`는 안정적인 성격과 행동 계층으로 생각하면 된다.

- 말투
- 경계
- 정체성
- 고수준 스타일

Memory는 사실을 추가한다. Skills는 절차를 추가한다.

### 해석

Hermes는 personality, fact, procedure를 분리한다.

Chat Portal에서도 system prompt에 모든 것을 넣으면 안 된다. system prompt 또는 persona config는 identity와 high-level policy를 담당하고, memory store는 사용자/프로젝트별 사실을 담당하며, skill registry는 실행 절차를 담당해야 한다.

가능한 분리:

- System/persona: agent identity, tone, global boundary
- Durable memory: user/project/tenant facts
- Skill: repeatable workflow
- Session DB: historical recall

## Profiles는 Context 충돌을 막는다

같은 Hermes 설치가 개인 작업, 업무 작업, 공개 bot을 모두 처리한다면 profile이 중요하다.

업무용 배포 선호가 개인 assistant에 영향을 주면 안 된다. Telegram bot의 공개 응답 스타일이 private research에 영향을 주면 안 된다.

Hermes profiles를 사용해 이런 context를 깔끔하게 분리하라고 설명한다.

### 해석

Profile은 memory namespace에 해당한다. Chat Portal에서는 profile 개념을 더 명확히 설계해야 한다.

가능한 namespace 축:

- user_id
- workspace_id
- project_id
- agent_id
- tenant_id
- environment

핵심은 wrong memory leakage를 막는 것이다. 업무 프로젝트의 deploy convention이 개인 프로젝트에 적용되면 agent memory는 오히려 위험해진다.

## Privacy Model

Memory는 persistent하기 때문에 강력하다. 따라서 casual chat이 아니라 configuration처럼 다뤄야 한다.

저장하면 안 되는 것:

- 원본 secret
- token
- agent가 필요로 하지 않는 개인 정보

민감한 프로젝트에서는 memory를 privacy control, security hardening, 필요한 경우 local model route와 함께 사용해야 한다.

### 해석

Agent memory는 기능이 아니라 보안 표면이다.

Chat Portal에서는 memory write 단계에 다음 장치가 필요하다.

- secret/token 패턴 필터링
- PII 저장 정책
- 사용자가 memory 저장을 확인/삭제할 수 있는 UI
- tenant/project 단위 접근 제어
- memory audit log
- TTL 또는 archival 정책

## Practical Memory Hygiene Checklist

Memory를 주기적으로 검토한다.

- 오래된 path와 더 이상 쓰지 않는 convention 제거
- 명령형 note를 선언형 fact로 교체
- 절차는 skills로 이동
- client 또는 tenant 관련 사실은 분리
- 일주일 안에 만료될 정보는 저장하지 않기

이렇게 하면 시간이 지날수록 agent가 더 날카롭게 동작한다.

### 해석

Memory는 자동으로 좋아지는 저장소가 아니다. 쓰레기 데이터가 쌓이면 agent 행동이 나빠진다.

따라서 Chat Portal에는 memory hygiene workflow가 필요하다.

- memory review 화면
- stale memory 감지
- fact/procedure/session 분류 오류 감지
- memory merge/dedup
- "이 memory 때문에 이런 행동을 했다"는 설명 가능성

## Example Workflow

사용자가 Hermes에게 다음처럼 정정했다고 하자.

> "이 프로젝트에서는 Vercel 직접 배포를 쓰지 마. GitHub에 push해."

Hermes는 이 durable project convention을 memory로 저장해야 한다.

만약 배포 과정에 여러 명령어와 확인 단계가 있다면, Hermes는 deploy skill을 만들거나 업데이트해야 한다.

나중에 사용자가 페이지 배포를 요청하면, Hermes는 다시 알려주지 않아도 올바르게 행동할 수 있다.

### 해석

이 예시는 memory write의 분해 방식을 보여준다.

사용자 발화:

- "Vercel 직접 배포 금지"
- "GitHub push 사용"

저장 결과:

- Durable fact: 이 프로젝트는 직접 Vercel deploy를 사용하지 않는다.
- Durable fact: 이 프로젝트는 GitHub push 기반 배포를 사용한다.
- Skill candidate: 배포 절차가 반복된다면 deploy skill 생성/수정

중요한 점은 memory의 성공 기준이 "기억한다고 말하는 것"이 아니라 "다음 행동의 default가 바뀌는 것"이라는 점이다.

## Next Step

Hermes가 memory에서 왜 강한지 읽고, 첫 profile과 재사용 가능한 skill 하나를 설정하라고 안내한다.

Privacy가 주된 관심사라면 Hermes privacy guide와 Ollama setup을 함께 보라고 한다.

## Install Path

Memory system을 평가하려면 Hermes Agent를 설치하고 통제된 테스트를 만들라고 설명한다.

테스트 방법:

1. Hermes에게 안정적인 프로젝트 convention 하나를 알려준다.
2. 관련 작업을 완료하게 한다.
3. 나중에 돌아와 비슷한 작업을 요청한다.
4. 절차가 반복된다면 persistent memory와 skill을 함께 사용한다.

중요한 테스트는 행동이다.

Hermes가 단순히 "기억한다"고 말하는 것이 아니라, 그 memory 때문에 올바른 기본 행동을 선택해야 한다.

예시는 다음과 같다.

- 선호하는 배포 경로를 사용한다.
- 사용자가 거부한 tool을 피한다.
- 파일을 수정하기 전에 프로젝트별 checklist를 로드한다.

## Recent Community Troubleshooting Note

최근 Discord에서 나온 다음 주제들은 memory architecture가 이야기의 절반일 뿐이라는 점을 보여준다.

- Hermes memory를 고치는 방법
- Local hindsight memory 설치 후 Hermes가 깨진 문제
- auxiliary timeout failure

Recall 또는 compaction이 실제로 실패한다면, provider를 바꾸거나 state를 삭제하기 전에 Hermes memory troubleshooting checklist를 사용하라고 설명한다.

Hindsight, Recall, Obsidian 또는 다른 local memory layer를 테스트할 때는 profiles와 함께 사용하라고 한다.

### 해석

메모리 설계는 architecture만으로 끝나지 않는다. 실제 운영에서는 recall, compaction, auxiliary model, provider integration이 실패할 수 있다.

Chat Portal도 memory provider를 도입하거나 직접 설계할 때 다음을 검증해야 한다.

- memory write가 실제로 일어났는가
- retrieval이 기대한 profile/namespace에서 수행되는가
- compaction 후에도 중요한 사실이 유지되는가
- provider 장애 시 fallback이 있는가
- memory 때문에 잘못된 행동을 했을 때 추적 가능한가

## FAQ 번역

### Hermes memory의 계층은 무엇인가?

Hermes는 안정적인 사실을 위한 durable memory, 재사용 가능한 절차를 위한 skills, 과거 대화나 작업을 회상하기 위한 session search를 사용한다.

### 모든 작업 결과를 memory로 만들어야 하는가?

아니다. 임시 진행 상황과 실행 로그는 session history나 task system에 남겨야 한다. Memory에는 나중에도 계속 중요할 사실만 저장해야 한다.

### Skills도 memory의 일부인가?

그렇다. Skills는 procedural memory다. 명령어, 피해야 할 함정, 검증 단계를 포함해 workflow를 수행하는 방법을 저장한다.

### Profiles는 memory에 어떤 영향을 주는가?

Profiles는 개인, 업무, bot 설정 같은 context를 분리해 잘못된 사실이 잘못된 workflow로 새어 들어가지 않게 한다.

### Memory를 안전하게 유지하려면 어떻게 해야 하는가?

Secret을 저장하지 말고, 오래된 사실을 제거하고, 분리를 위해 profiles를 사용한다. 민감한 workflow는 local model 또는 hardened deployment와 함께 사용한다.

### Hermes Agent가 내가 말한 것을 기억하지 못하는 이유는 무엇인가?

다음을 확인한다.

- memory가 활성화되어 있는지
- 해당 사실이 저장될 만큼 durable한지
- 같은 profile 안에 있는지
- 현재 session이 너무 길어서 `/compress`가 필요한지
- provider 또는 auxiliary model failure가 있는지

Memory와 context maintenance는 일반 chat이 정상 동작하는 상황에서도 실패할 수 있다.

## Chat Portal 설계 시사점

Hermes 구조를 Chat Portal에 그대로 적용하기보다, DeepAgents의 실행 모델과 결합 가능한 memory 모델로 재해석해야 한다. 우선 Hermes 관점에서 필요한 memory 모델은 다음과 같다.

```text
Agent Memory
├─ Durable facts
│  ├─ user preferences
│  ├─ project conventions
│  ├─ environment quirks
│  └─ rejected/default tools
├─ Procedural skills
│  ├─ trigger condition
│  ├─ steps/commands
│  ├─ pitfalls
│  └─ verification
├─ Session search
│  ├─ raw sessions
│  ├─ summaries
│  ├─ embeddings
│  └─ citations/backlinks
├─ Persona/system layer
│  └─ tone, boundary, identity
└─ Profiles/namespaces
   ├─ user
   ├─ workspace
   ├─ project
   └─ agent
```

핵심 판단:

- 비교 대상은 LangChain 기본 memory가 아니라 DeepAgents다. LangChain 기본 memory는 DeepAgents 검토 중 하위 memory primitive 또는 배경 지식으로만 다룬다.
- DeepAgents와 비교할 때는 Hermes의 durable facts / procedural skills / session search가 DeepAgents의 장기 작업 context, tool execution, planning, state/file abstraction과 어떻게 대응되는지 봐야 한다.
- Chat Portal에는 memory를 fact/procedure/session/persona/profile로 분리하는 구조가 필요하다.
- memory의 성공 기준은 저장 여부가 아니라 다음 agent 행동의 default가 바뀌었는지다.
- memory write는 자동화하되, privacy와 hygiene 때문에 review/delete/audit 기능이 필요하다.

## 다음 조사 후보

- Hermes memory troubleshooting checklist
- Hermes profiles 구조
- Hermes skills 구조
- LangChain DeepAgents memory/context 구조
- DeepAgents와 Hermes 3-layer memory 비교
- OpenViking memory/resource/skill virtual filesystem
- LangGraph memory/store
- Mem0
- Letta memory blocks / archival memory
- Obsidian 기반 local memory
