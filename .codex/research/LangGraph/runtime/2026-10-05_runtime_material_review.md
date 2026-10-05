# LangGraph 런타임 학습자료 전체 검토와 보강 기록

> 검토일: 2026-10-05. 대상: 전체 학습 목록과 상세 자료 01, 01-1, 02~10.
>
> 기준: 사용법을 이미 아는 DeepAgents 개발자가 자주 쓰는 graph API에서 내부 실행을 추적하고 개발 시 지향·지양할 패턴을 판단할 수 있는가?
>
> 소스 기준: LangGraph 1.2.11, DeepAgents 0.7.13, LangChain 1.4.0의 실제 설치본. 새로운 웹 문서와 설치본을 같은 구현으로 가정하지 않는다.

전체 방향은 요청과 맞는다. 작성 → 등록 → compile → 실행 → 상태 병합 → 기억·수정·재개 → 실패·저장 → 스트리밍 → 실행 제어의 순서를 유지했다. 다만 **항목이 있다는 것과 설명이 충분하다는 것은 다르다.** 재검토에서는 용어·실행 단위·예제 연결·검증되지 않은 단정의 빈틈을 찾아 해당 문서에 직접 보강했다.

## 1. 발견한 문제와 적용한 수정

| 문제 | 학습에 미치는 영향 | 수정 위치와 내용 |
| --- | --- | --- |
| node, task, super-step, channel 등의 구분이 여러 장에 흩어짐 | 노드 하나를 단계 하나로 해석하거나 API 호출과 실행 객체를 혼동 | [전체 목록](2026-10-05_langgraph_runtime_source_guide.md)에 내부 객체·실행 단위 표와 Mermaid 추가 |
| add_node의 “결과”를 StateNodeSpec이라고 표현 | 메서드 반환값과 등록되는 객체를 혼동 | [01-1](01a_node_and_edge_registration.md)에서 반환값은 builder, 등록 결과는 명세라고 구분 |
| 일반 엣지 두 개와 list 대기 엣지 차이가 서술에 머무름 | 어떤 그래프에서 잘못된 합류가 발생하는지 알기 어려움 | [01-1](01a_node_and_edge_registration.md)에 깊이가 다른 경로의 단계별 입력, 같은 단계 완료, 누락 신호 사례와 실험 추가 |
| 채널 버전과 관찰 버전 설명이 추상적 | 읽는 필드와 실행 트리거, 같은 값 쓰기의 의미를 혼동 | [03](03_node_returns_reducers_and_supersteps.md)에 channel_versions/versions_seen과 다음 실행의 관계 보강 |
| DeepAgents와 런타임의 연결이 전체 경로와 messages에 치우침 | 실제 model 결과가 어느 API 경로로 들어오는지 연결이 약함 | [전체 목록](2026-10-05_langgraph_runtime_source_guide.md)에 factory의 add_node/조건부 연결/compile 및 Command 메시지 반환 경로 추가 |
| 08 예제가 compile 뒤에 timeout 노드를 추가하는 모양 | 새 설정이 기존 graph에 적용된다고 오해할 수 있음 | [08](08_retry_timeout_and_durability.md)의 retry와 timeout 예제를 별도 builder의 완결된 실행 흐름으로 변경 |
| 10 예제의 스키마·import·START/END 연결이 생략됨 | 예제 자체를 실행하며 내부 흐름을 따라가기 어려움 | [10](10_context_cache_concurrency_and_limits.md)의 context 예제 완성, 캐시 예제는 기존 등록 줄을 대체하도록 명시 |
| object()를 직렬화 불가능하다고 단정 | 실험이 증명한 범위를 초과하는 사실 설명 | [10](10_context_cache_concurrency_and_limits.md)에서 단순 표식이며 state 미저장만 관찰했다고 수정 |
| 캐시 writes가 라우터와 누적 채널에 미치는 영향이 부족 | 캐시를 순수 함수 결과만 재사용하거나 중복 제거로 이해 | [10](10_context_cache_concurrency_and_limits.md)에 라우터 생략·제어 쓰기 재사용·누적 재병합 실험 추가 |
| 일부 장 번호가 내부 분류와 상세 문서 번호를 혼용 | Send나 객체 공유 자료를 잘못 찾아갈 수 있음 | [01](01_state_schema_and_graph_compilation.md)의 관련 문서와 다음 읽기 순서를 링크로 정정 |

## 2. 각 자료의 방향과 설명 범위

| 자료 | 검토 판단 | 독자가 확인할 핵심 |
| --- | --- | --- |
| [01. 상태와 compile](01_state_schema_and_graph_compilation.md) | API와 객체 전후 관계가 적절함. 참조 순서 수정 | builder 상태 채널, compiled 제어 채널, 읽기/출력 범위 |
| [01-1. 노드·엣지 등록](01a_node_and_edge_registration.md) | 대기 계약의 구체적 사례가 부족해 보강 | 반환값과 등록 명세, 스키마 추론, 깊이가 다른 경로의 join |
| [02. 조건부 분기](02_conditional_edges_and_execution.md) | 호출 경로와 관찰값 연결이 적절함 | 라벨/path_map, fresh read, Send, END와 일반 엣지 |
| [03. 반환값·단계](03_node_returns_reducers_and_supersteps.md) | 업데이트 설명은 적절함. 실행 버전 연결 보강 | 쓰기 버퍼, LastValue 충돌, reducer, 공유 객체, 단계 반영 |
| [04. 메시지와 DeltaChannel](04_messages_identity_and_deepagent_delta.md) | DeepAgents 목적에 직접 맞음 | ID 교체·삭제, batch reducer, snapshot와 writes 복원 |
| [05. Checkpointer·STM](05_checkpointer_stm_and_state_views.md) | 기억과 진행 정보의 구분이 적절함 | 새 턴과 resume, 최신 뷰와 특정 시점, pending writes |
| [06. 상태 수정](06_update_state_writers_and_execution_position.md) | 상태와 실행 위치를 함께 설명함 | as_node, 라우터 실행, reducer, 수동 메시지 ID |
| [07. 중단·재개](07_interrupt_resume_and_reexecution.md) | 재실행 범위와 개발 주의점이 적절함 | scratchpad, 호출 순서, 병렬 interrupt ID, 외부 변경 반복 |
| [08. 재시도·저장](08_retry_timeout_and_durability.md) | 경계 설명은 적절함. 예제 작성 시점 수정 | retry 범위, async timeout, durability와 저장 완료 |
| [09. 스트리밍·취소](09_stream_modes_lifecycle_and_cancellation.md) | 출력과 실행 수명을 구분함 | mode/version/namespace, 이벤트와 영속 상태, aclose |
| [10. 실행 제어](10_context_cache_concurrency_and_limits.md) | 캐시와 입력 관계를 더 세밀하게 보강 | context, 캐시의 라우팅 신호, thread 잠금, 단계 한도 |

## 3. 추가 실험으로 확인한 사실

[보강 코드](code/probe_review_gaps.py), [결과](code/review_gaps_result.json)에 네 그룹을 저장했다.

1. 깊이가 다른 경로에서 일반 엣지 두 개의 c는 a만 가진 입력과 a/b를 가진 입력으로 총 두 번 실행됐다. 대기 엣지의 c는 a/b를 가진 입력으로 한 번 실행됐다.
2. a/b가 같은 단계에 완료되면 두 구성 모두 c가 한 번 실행됐다.
3. barrier에 필요한 b가 실행되지 않으면 c는 실행되지 않았다. 다른 활성 작업도 없으면 전체 호출은 종료할 수 있었다.
4. cache hit는 work와 route를 재호출하지 않았지만, 다음 노드 실행 신호와 log 업데이트를 재사용했다. work/route/다음 노드 호출 횟수는 1/1/2였고 덧셈 log는 두 항목이 됐다.

예제의 시간·메시지 ID 같은 우연한 값을 일반 계약으로 확대하지 않았다. 합류 사례는 노드의 단계 배치, 캐시 사례는 실제 입력 스키마와 채널 병합 규칙을 기준으로 설명했다.

추가 소스의 해시와 함수 위치는 [검토 소스 매니페스트](runtime_review_source_manifest.json)에 있다. 소스는 설치본의 직접 근거다. [공식 Pregel 문서](https://docs.langchain.com/oss/python/langgraph/pregel)는 실행 모델의 배경 근거이며 2026-10-05에 재확인했다. 해당 웹 문서의 DeltaChannel reducer 시점 설명은 설치본의 update/replay 구현과 차이가 있어 기존 문서의 버전 구분을 유지했다.

## 4. 이 자료가 설명하는 범위와 남는 검증

재검토 후 compilation 관찰 코드와 11개 probe 스크립트가 모두 정상 종료했고, 총 59개 관찰 그룹이 통과했다. 08의 retry/async timeout 예제와 10의 context 예제도 본문에서 추출해 실행했다. [검증 결과](code/runtime_review_verification.json)에 실행 목록을 저장했다. 네 소스 매니페스트의 56개 해시 기록은 설치본과 일치했다. 중복을 제외하면 32개 파일이다.

이 자료는 일반적인 StateGraph API의 실행 경로와 그 경로가 DeepAgents에도 적용되는 위치를 설명한다. 각 함수의 모든 옵션·예외 분기를 해설한 라이브러리 전체 소스 주석집은 아니다. defer/error_handler나 복잡한 하위 그래프 조립 전체를 검증했다고 주장하지 않는다.

실험은 모델 호출 없는 작은 그래프와 InMemory 기반 사례다. 실제 모델의 토큰 이벤트, 외부 DB의 장애 복구, 다중 worker 경합, 프로세스 강제 종료, SSE disconnect 전파는 포함하지 않았다. 이들은 실제 개발 환경에 맞는 별도 검증 대상이며, 현재 학습 방향을 사용법 강의나 플랫폼 구축으로 바꾸지 않았다.

본문의 부분 코드와 의사 코드는 설명할 경로만 추린 것이다. 실제 설치본에서 재현할 때는 각 장 마지막의 code/ 실험 파일을 사용한다. 08·10에 보강한 완결 예제는 본문 코드 자체를 추출해 실행 확인했다. Mermaid는 도식의 소스이며 렌더러별 표시 검증은 별도로 구분한다.
