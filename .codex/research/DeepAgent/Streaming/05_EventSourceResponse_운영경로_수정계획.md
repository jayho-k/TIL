# EventSourceResponse 운영 경로 수정 계획

작성일: 2026-09-20. 사용자 승인: 공통 문제 수정 후 EventSourceResponse 채택.

## 설계

- `/v1/chat/stream`을 기본 경로로 추가하고 기존 두 URL도 동일한 EventSourceResponse 경로로 연결한다. 사용자 추가 지시에 따라 기존 StreamingResponse 구현과 비교 테스트는 그대로 보존하고 운영 라우팅에서만 제외한다.
- service generator의 첫 `stream.started`를 HTTP 응답 생성 전에 읽는다. Agent permit과 초기 DB 기록 실패는 503으로 변환하며 연결 permit도 반환한다. Agent timeout은 배칭 루프의 절대 deadline으로 처리하고 generator yield를 가로지르는 timeout context를 두지 않는다.
- Response가 iterator 종료와 connection permit 반환을 소유한다. generator가 한 번도 소비되지 않은 경우, header 전송 실패, body timeout, disconnect, task cancellation에서도 finally로 정리한다.
- Agent source는 하나의 producer task에서 소비하고 크기 1 queue로 전달한다. task 전환으로 source 내부 timeout context를 훼손하지 않는다. 종료 시 producer를 취소하고 기다린다.
- 완료 저장 성공 후에만 completed를 보낸다. 저장 실패는 PERSISTENCE_ERROR, Agent 실패는 AGENT_ERROR, 실행 제한은 AGENT_TIMEOUT으로 구분한다. 실패 로그 기록 자체가 실패해도 공개 error는 전송한다.
- 공개 messages는 root namespace의 허용 model node로 제한한다. 내부 tag와 subgraph 출력을 제외하고 text content block도 지원한다.
- 배칭 deadline은 첫 토큰 도착 시점부터 계산한다. 기존 TokenBatcher를 실제 서비스에서 재사용한다.
- 부하 측정은 요청 시작부터 첫 이벤트, 첫 토큰, 전체 종료 시간을 별도 기록한다. 기존 4ms 수치는 헤더 응답 지연이며 운영 용량 근거가 아님을 명시한다.

## 실행 순서

- [x] 기존 결함을 재현하는 service/projector/API/response 테스트를 추가하고 실패를 확인한다.
- [x] service lifecycle, bounded producer, batching, 공개 출력 필터를 수정하고 해당 테스트를 실행한다.
- [x] EventSourceResponse 정리 책임과 preflight를 구현하고 실제 ASGI send/receive 장애 테스트를 실행한다.
- [x] 부하 측정과 README/보고서를 변경하고 전체 단위·로컬 통합 검사와 lint를 실행한다.

검증 명령 (AI/agent_streaming): `.venv/Scripts/python.exe -m pytest tests/unit tests/integration/test_api.py -q`, `.venv/Scripts/ruff.exe check app tests load_tests`.

## 검증 결과 (2026-09-21)

- 전체 pytest: 59 passed, 2 skipped. `RUN_LIVE_TESTS=0`, `RUN_POSTGRES_TESTS=0`으로 실제 외부 서비스 시험을 제외했다.
- Ruff: All checks passed.
- Starlette TestClient에서 AnyIO BlockingPortal 별칭의 DeprecationWarning 1건. 애플리케이션 테스트 실패는 아니다.
- 실제 DeepAgent 0.7.13 + in-memory checkpoint + 로컬 가짜 모델에서 v2 namespace/node 필터가 정상 답변을 통과시킴을 검증했다.
- 취소 중 source 정리 오류가 발생해도 가득 찬 queue에 error를 넣으려다 종료가 막히지 않는 회귀 테스트를 추가했다.
- 기존 StreamingResponseAdapter와 비교용 테스트는 보존했다. 모든 HTTP chat 경로는 EventSourceResponseAdapter로 연결된다.
- 실제 DB/Redis/모델 장애, 프록시, 15분 부하 시험은 수행하지 않았다. 과거 부하 수치는 재측정 결과로 표시하지 않았다.

## 유지하는 범위 및 운영 전제

인증·thread 소유권 검증과 분산 thread 잠금은 통합 대상 운영 시스템의 책임이다. 취소 후 RUNNING 로그 유지 정책은 이번 수정으로 변경하지 않는다. 실제 인프라 장애·장시간 부하·프록시 시험을 수행하기 전 운영 용량이나 전체 시스템 안전성을 보증하지 않는다. Git 상태 변경 명령을 실행하지 않는다.
