# Mem0 실험 코드

이 폴더는 `AI/mem0/text/`의 가설을 재현·검증하는 코드 전용 작업 공간이다.

- `p0_*`: V3 ADD-only, explicit update/delete, history 관찰
- `p1_*`: Qdrant schema·filter·hybrid retrieval 비교
- `p2_*`: SQLite history와 multi-worker/restart 실험
- `p3_*`: tenant authorization negative test
- `p4_*`: DeepAgents·LangGraph context materialization과 promotion flow

각 실험의 배경·결과·판정은 코드 파일이 아닌 `../text/`에 기록한다. 코드에는 실행 방법, 필요한 환경 변수, fixture, 측정 결과의 원시 출력만 남긴다.

