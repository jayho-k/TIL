# 스트리밍 부하 테스트 보고서

## 환경과 해석 범위

현재 PC/GPU는 실제 운영 장비와 다르다. 따라서 운영 가정의 1/10인 30 SSE connections,
10 concurrent Agent runs, 1 new request/s를 검증한다. 결과는 구조적 안정성 및 두 transport의
상대 비교 자료이며 DAU 7,000 서비스의 절대 용량 보증이 아니다.

## 실행 명령

2026-09-21부터 모든 API 경로가 EventSourceResponse를 사용한다. 현재 부하 시험 명령:

```powershell
$env:STREAM_TRANSPORT='stream'
uv run locust -f load_tests/locustfile.py --headless -u 30 -r 1 -t 15m --csv event-source --host http://127.0.0.1:8000
```

`-r 1`은 사용자 생성 속도이며 신규 채팅 요청을 정확히 1 RPS로 제한하지 않는다.
현재 client는 POST 시작부터 body 소비 종료까지를 HTTP response time에 기록하고,
첫 이벤트와 첫 토큰을 별도 `SSE` 측정 행으로 기록한다. SSE 행은 추가 측정치이므로
Locust 집계 전체 request count/RPS를 실제 채팅 요청 수로 해석하지 않는다.
`response_length`는 파싱한 줄의 UTF-8 byte 합계이며 delimiter를 포함한 실제 wire 크기는 아니다.
slow consumer 측정에는 의도적으로 넣은 읽기 지연이 포함된다.

## 결과

아래는 **수정 전의 과거 결과**이며 수정 후 재측정 결과가 아니다.
과거 `stream=True` 사용 시 Locust의 기본 response time은 body 소비 전인 헤더 수신까지였다.
따라서 아래 Average/p95/Max는 스트림 완료 지연이나 첫 토큰 지연을 나타내지 않는다.
fake Agent는 실제 ChatStreamService, Agent limiter, DB/Redis를 우회하므로 이 결과로
공통 서비스나 실제 upstream 취소의 안정성을 판단할 수 없다.

2026-09-20에 동일한 fake Agent(20ms 간격 10 chunks)를 사용해 35초 smoke를 수행했다.

| Transport | Requests | Failures | Average | p95 | Max | Throughput |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `StreamingResponse` | 401 | 0 | 4ms | 7ms | 19ms | 11.78 req/s |
| `EventSourceResponse` | 385 | 0 | 4ms | 7ms | 19ms | 11.33 req/s |

추가 baseline smoke도 모두 0 failures였다.

| Users | `StreamingResponse` | `EventSourceResponse` |
| ---: | --- | --- |
| 3 | 12 requests, avg 34ms, max 322ms | 14 requests, avg 5ms, max 21ms |
| 10 | 57 requests, avg 4ms, max 18ms | 65 requests, avg 4ms, max 17ms |

3-user `StreamingResponse`의 322ms 단일 outlier는 짧은 표본이라 결론에 사용하지 않는다.

여기에는 normal, slow consumer, early disconnect workload가 섞여 있다. 짧은 smoke에서는 두
transport의 헤더 응답 지연에서 큰 차이가 관측되지 않았다. 이는 fake Agent transport smoke 결과일 뿐
실제 Ollama 처리량이나 DAU 7,000 운영 용량을 의미하지 않는다.

실제 운영 판단 전에는 15분 steady run과 CPU, RSS, event-loop lag, TTFE CSV를 추가해야 한다.
