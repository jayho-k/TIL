# Mem0 Library Mode 코드 분석

분석 대상은 `AI/mem0/code/mem0_code_analize/mem0`에 복사된 Mem0 OSS Python 소스다. `pyproject.toml` 기준 package version은 `mem0ai 2.0.12`다. 소스 폴더에는 `.git`이 없어 upstream commit/date는 확인할 수 없으며, 재현용 핵심 파일 SHA-256은 [00_분석_계획.md](00_분석_계획.md)에 기록했다.

이 폴더는 Python OSS library mode를 중심으로 source code 관찰 결과를 기록한다. self-hosted server, Platform client, TypeScript SDK는 library mode와의 차이를 설명해야 할 때만 참조한다.

## 분석 순서

1. `00_분석_계획.md`
2. 전체 아키텍처와 component 초기화
3. V3 write pipeline과 fact extraction prompt
4. read pipeline과 hybrid retrieval
5. Qdrant·entity collection·metadata filter
6. SQLite history·recent message와 lifecycle API
7. 강점·제약·우리 아키텍처 적용점
8. Gemma 4 31B PoC 기준
9. PostgreSQL State Store 대체 설계와 오픈소스 업데이트 전략
