1. worker :8000 -> LangGraph(invoke)
2. crew :8200 -> CrewAI(kickoff)
3. adk :8300 -> Google Adk(Runner)

# jsonRPC -> SendMessage

1. crewAI : app -> A2A -> crewAI
2. adk : app -> A2A -> adk -> A2A -> crewAI

# gRPC

1. JSON-RPC : method로 구분해서 요청
2. HTTP + JSON : URL 경로랑, HTTP 메서드로 구분
3. gRPC : a2a.proto 서비스 정의

// context_id -> contextId

--> google.protobuf.Value