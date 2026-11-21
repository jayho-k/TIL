# RAG 평가·평가 데이터셋 관련 survey 선정

> 조사일: 2026-10-18. 이번 범위는 survey 후보 발굴·서지 확인·인용 수 비교·독서 우선순위까지다. 골든셋 50개 확장 파이프라인이나 개별 생성 방법의 채택은 결정하지 않는다.

## 선정 결과

**인용이 축적된 RAG 평가 survey는 Yu 등의 2024년 논문을, 합성 데이터 구축의 전체 지형은 Long 등의 ACL 2024 survey를 기초 자료로 권한다.** 최신 보완 자료로 2026년 RAG survey의 평가 장과 TMLR의 생성 데이터 품질 survey를 함께 검토한다.

단일 논문에 최신성·높은 인용 수·RAG 평가셋 구축 전용 범위가 모두 충족되는 것은 이번 조사에서 확인하지 못했다. 이를 억지로 하나의 순위 점수로 합치지 않는다. 아래 인용 수는 전체 학계의 총인용이 아니라 동일 DB의 개별 레코드 집계다.

## 조사 범위와 증거 기준

- 검색어 축: `RAG evaluation survey/review`, `evaluation datasets`, `benchmark construction/generation survey`, `LLM synthetic data generation curation evaluation survey`.
- 범위: 평가 전용 → 데이터 생성·구축·품질 → 일반 RAG/LLM survey의 평가 장 순서로 후보를 확장했다.
- 포함: 여러 연구를 분류·비교하는 survey/review. 개별 벤치마크·생성 도구·블로그·설문조사 응답 데이터는 핵심 목록에서 제외했다.
- 서지·내용: arXiv의 판본 이력과 본문 목차, 학회·출판사 페이지를 우선 확인했다. 후보 전체를 완독한 문헌고찰이 아니라 **읽을 survey를 고르기 위한 스크리닝**이다.
- 인용 수: OpenAlex 공식 API `cited_by_count`, 조회일 2026-10-18. [원본 API 응답](03_survey_citation_snapshot.json)에 15개 레코드를 저장했다.
- Semantic Scholar 공식 API는 HTTP 429로 수치를 확보하지 못했다. Google Scholar 수치는 확인하지 않았으며 OpenAlex 수치를 Google Scholar 인용 수로 표기하지 않는다.
- 출판일·개정일은 공식 페이지 기준이다. OpenAlex가 ACL 출판일을 `2024-01-01`처럼 보유한 경우 이를 정확한 행사 날짜로 사용하지 않는다.
- arXiv DOI와 출판 DOI가 같은 OpenAlex work로 연결되는 사례를 확인했다. 판본별 수치를 더하지 않는다. 0 역시 해당 레코드의 값이며 실제 인용 부재를 증명하지 않는다.

## A. RAG 평가를 직접 다루는 survey

| 논문 | 공개·개정 및 출판 | OpenAlex 인용 수 | 확인한 범위와 선정 판단 |
| --- | --- | ---: | --- |
| [Evaluation of Retrieval-Augmented Generation: A Survey](https://arxiv.org/abs/2405.07437) — Hao Yu 외 | 최초 2024-05-13, v2 2024-07-03. 출판 DOI: 10.1007/978-981-96-1024-2_8 | [182](https://openalex.org/W4406771321) | 평가 대상·데이터셋·지표를 연결하는 기초 지도. **RAG 평가 입문 1순위**. 2025–2026 동향 보완 필요 |
| [Retrieval Augmented Generation Evaluation in the Era of Large Language Models: A Comprehensive Survey](https://arxiv.org/abs/2504.14891) — Aoran Gan 외 | v1 2025-04-21. arXiv | [9](https://openalex.org/W6966545553) | 전통 지표·LLM 평가·안전·효율·자원 목록. 2024 논문보다 최근 자료 보완. 고인용 논문으로 분류하지 않음 |
| [Can LLMs Be Trusted for Evaluating RAG Systems? A Survey of Methods and Datasets](https://arxiv.org/abs/2504.20119) — Lorenz Brehme 외 | 최초 2025-04-28, v2 2025-05-01. IEEE SDS 2025, DOI: 10.1109/SDS66131.2025.00010 | [11](https://openalex.org/W4412966133) | 데이터셋·인덱싱·검색·생성을 나눠 검토. **기존 평가셋 보강 주제와 직접적인 접점**. 인용 축적은 적음 |
| [Evaluating Retrieval Augmented Generation: A Comprehensive Review of Evaluation Dimensions, Question Types, and Application](https://link.springer.com/article/10.1007/s42979-026-05134-x) — Simon Knollmeyer 외 | 2026-06-16, SN Computer Science | [3](https://openalex.org/W7164908464) | 최근 출판된 평가 전용 review. 그러나 검색 종료가 2024-08이고 최종 분석 12편. **2026 동향 총정리로 해석하지 않음** |

### A1. 기초 자료: Yu 외

[본문](https://arxiv.org/html/2405.07437v2) §3은 평가 대상·데이터셋·지표를 구분한다. 특히 §3.2와 Table 2는 벤치마크가 재사용하거나 자체 구축한 데이터의 관계를 보여준다. 관련성과 충실성 등 무엇을 측정하는지 먼저 정리하는 데 적합하다. 확인한 평가 전용 후보 중 인용 축적이 가장 컸다. 출판본과 arXiv DOI가 동일한 OpenAlex work에 연결되므로 182를 한 번만 센다. 신뢰도: 서지·목차·인용 레코드 높음, 최신 동향 포괄성 제한.

### A2. 최근 평가 범위 보완: Gan 외

[본문](https://arxiv.org/html/2504.14891v1)의 §3 Internal Evaluation, §4 External Evaluation, §5 Resources, §6 Discussion을 확인했다. 자원표는 2025년 자료를 포함하며, 통계 그림의 2025 H1 수집은 3월 31일까지라고 명시한다. 따라서 2026년 최신 동향 자료는 아니다. A1과 저자가 상당수 겹치므로 서로 독립된 연구 집단의 합의 증거로 세지 않는다. 신뢰도: 범위 확인 높음. 이번에 확인한 페이지에서는 별도 학회·저널 출판을 확정하지 않았다.

### A3. 데이터셋 관점에서 읽을 후보: Brehme 외

[본문](https://arxiv.org/html/2504.20119v2)은 63편을 검토하며 §III에서 사람 구축, 기존 데이터셋 보강, LLM 생성으로 나눈다. 기존 데이터셋의 답 보완·질문 변형도 조사 범주에 포함한다. 우리 50개를 어떻게 확장할지 결정하기 전 **관련 방법들이 어떤 분류에 놓이는지** 파악하기 좋다. 논문 제목을 ‘LLM judge만 다루는 survey’로 오해하면 안 된다. 특정 확장법의 우월성을 실험한 논문은 아니다. 신뢰도: 서지·범위 높음, 방법 선택의 직접 실험 근거 아님.

### A4. 최신 출판일과 최신 문헌 범위의 차이: Knollmeyer 외

[출판사 Methodology](https://link.springer.com/article/10.1007/s42979-026-05134-x)는 문헌 검색을 2024-08까지 수행했다고 밝힌다. 평가 차원·지표·평가자·필요 데이터의 대응은 참고할 수 있지만, 2026년 출판이라는 이유로 최근 방법론을 가장 넓게 다룬다고 순위를 올릴 수 없다. KMIS 2024 논문을 확장한 저널판이다. 신뢰도: 이 범위 제한은 저자 설명으로 확인.

## B. 데이터 구축·생성·품질을 조망하는 survey

| 논문 | 공개·개정 및 출판 | OpenAlex 인용 수 | 범위와 선정 판단 |
| --- | --- | ---: | --- |
| [On LLMs-Driven Synthetic Data Generation, Curation, and Evaluation: A Survey](https://aclanthology.org/2024.findings-acl.658/) — Lin Long 외 | arXiv 최초 2024-06-14, Findings of ACL 2024-08 | [126](https://openalex.org/W4402684073) | **생성·정제·검증의 전체 방법 지도를 얻을 기초 자료**. RAG 평가셋 전용은 아님 |
| [A Survey on Evaluating Quality and Trustworthiness in LLM-Generated Data](https://arxiv.org/abs/2601.17717) — Kaituo Zhang 외 | 최초 2026-01-25, v3 2026-06-09. TMLR 2026 | [0](https://openalex.org/W7125803282) | 생성 데이터 자체의 품질·신뢰성 지표. **최신 품질 검증 보완용**, 고인용 자료 아님 |
| [Datasets for Large Language Models: A Comprehensive Survey](https://link.springer.com/article/10.1007/s10462-025-11403-7) — Yang Liu 외 | arXiv 최초 2024-02-28, 저널 출판 2025-10-31, Artificial Intelligence Review | [116](https://openalex.org/W4415725257) | 학습·선호·평가 데이터 전체와 평가 데이터 구축 방식. 카탈로그 성격이 강해 후순위 |

### B1. 생성 방법의 지도: Long 외

[공식 PDF](https://aclanthology.org/2024.findings-acl.658.pdf) §2.1은 소수 seed 또는 미라벨 입력을 활용하는 문제를 정의한다. §3은 Generation, Curation, Evaluation으로 구성되며 예시 선택·조건 설정·다단계 생성·필터링·라벨 보강을 함께 다룬다. 우리 목적과 연관은 있으나 논문 상당 부분은 학습 데이터 생성과 그 유용성 평가도 포함한다. ‘학습 성능을 올리는 합성 데이터’와 ‘시스템을 공정하게 비교하는 평가셋’을 동일시하면 안 된다. 신뢰도: 학회 출판과 범위 높음, 2026 최신성은 없음.

### B2. 최신 검증 관점: Zhang 외

[v3 본문](https://arxiv.org/html/2601.17717v3)의 §2 Text Data는 validity, fidelity, diversity, faithfulness/consistency와 benchmark contamination 등을 구분한다. §2.5에는 synthetic evaluation sets도 있다. 초기 제목 **The LLM Data Auditor: A Metric-oriented Survey on Quality and Trustworthiness in Evaluating Synthetic Data**와 동일 arXiv ID이며, 최종 제목 변경 및 TMLR 출판은 arXiv 메타데이터로 확인했다. OpenReview 본문 직접 열람은 브라우저 검증 화면으로 제한됐으므로 내용 확인은 arXiv v3에 근거한다. 신뢰도: 서지·분류 확인 높음. 0회는 OpenAlex 레코드 값으로만 해석.

### B3. 데이터셋 카탈로그: Liu 외

[저널 본문](https://link.springer.com/article/10.1007/s10462-025-11403-7)의 §6은 평가 데이터와 구축 방식 등을 다룬다. 다만 Fig. 17의 평가 데이터 통계는 2024-02 기준으로 명시돼 있다. 2025년 저널 출판일이 곧 전체 데이터 수집 시점은 아니다. 최신 생성법 탐색보다는 데이터 구성·출처·질문 형식의 분류를 확인하는 보조 자료다. 신뢰도: 범위 확인 높음, 최신 통계로 사용하지 않음.

## C. 인용이 많거나 최근이지만 범위가 더 넓은 보조 후보

| 논문 | 날짜/판본 | OpenAlex 인용 수 | 위치 |
| --- | --- | ---: | --- |
| [Retrieval-augmented generation for natural language processing: a survey](https://link.springer.com/article/10.1007/s10462-026-11605-7) — Shangyu Wu 외 | 2026-06-01 출판, version of record 2026-08-06, Artificial Intelligence Review | [78](https://openalex.org/W4402854593) | **최근 RAG 보완 자료**. §7 평가·벤치마크를 우선 확인. 2026 연구 인용도 확인했으나 엄격한 수집 종료일은 본 조사에서 확정하지 못함 |
| [A Survey on Evaluation of Large Language Models](https://doi.org/10.1145/3641289) — Yupeng Chang 외 | ACM TIST, 2024-01-23 온라인 출판 | [3,088](https://openalex.org/W4391136507) | 인용이 큰 일반 평가 survey. RAG 전용이 아니므로 첫 독서에서 제외 |
| [Retrieval-Augmented Generation for Large Language Models: A Survey](https://arxiv.org/abs/2312.10997) — Yunfan Gao 외 | 최초 2023-12-18, v5 2024-03-27 | [871](https://openalex.org/W4389984066) | RAG 전체 아키텍처 배경. 평가셋 구축 중심 자료가 아니므로 후순위 |
| [Toward Generalizable Evaluation in the LLM Era: A Survey Beyond Benchmarks](https://arxiv.org/abs/2504.18838) — Yixin Cao 외 | v1 2025-04-26 | [0](https://openalex.org/W4416888703) | 자동·동적 평가 데이터 구축과 일반화 논의를 다룸. 고인용 조건은 미충족 |
| [Trustworthiness in Retrieval-Augmented Generation Systems: A Survey](https://arxiv.org/abs/2409.10102) — Yujia Zhou 외 | 최초 2024-09-16, v2 2026-05-16 | [18](https://openalex.org/W4403702563) | 사실성·강건성·공정성 등 신뢰성 범위를 넓힐 보조 후보. 평가셋 확장 전용은 아님 |

Wu 등의 자료는 출판사 §7을 확인한 결과 retrieval quality, generation performance, end-to-end robustness, system efficiency를 구분하고 벤치마크 한계를 논의한다. 일반 RAG survey를 전부 읽기보다 해당 장을 최신 보완용으로 읽는 선택이 가능하다. 인용 수가 최신 판본의 내용에만 쌓인 것이라는 뜻은 아니다.

추가 인용 스크리닝: `A Survey on Data Synthesis and Augmentation for Large Language Models`(arXiv:2410.12896)은 9회, `Surveying the Effects of Quality, Diversity, and Complexity in Synthetic Data From Large Language Models`(arXiv:2412.02980)은 5회, KMIS 2024의 평가 review는 6회였다. 이 세 편은 범위 중복 또는 낮은 우선순위로 핵심 독서에서 제외했으며 전체 판본 내용은 정독하지 않았다.

## 선택 논리와 읽기 우선순위

1. **Yu 외 — RAG 평가의 기본 지도.** 평가 대상·데이터셋·지표를 먼저 구분한다. 평가 전용 후보 중 인용이 가장 많이 축적돼 있다.
2. **Long 외 — 데이터 구축의 방법 지도.** 생성만이 아니라 정제와 데이터 검증까지 함께 본다. 이 단계에서도 특정 확장법을 채택하지 않는다.
3. **Brehme 외 §III — RAG 평가셋에 범위를 좁히기.** 사람 구축·기존셋 보강·LLM 생성의 분류를 확인한다.
4. **Wu 외 §7, Zhang 외 §2 — 2026 보완.** 최근 RAG 평가 이슈와 생성 데이터 품질 분류를 더한다. 둘은 다루는 대상이 달라 서로 대체하지 않는다.

Gan 외의 2025 survey는 1번과 비교해 평가 범위를 넓히는 선택지다. ‘최신 survey 한 편’이 우선이라면 Wu 등의 §7 또는 Zhang 등의 텍스트 데이터 장을 고를 수 있지만, RAG 평가 전용·인용 축적이라는 조건까지 모두 만족한다고 말할 수는 없다.

## 해석 시 남겨둘 한계

- 인용 수는 영향력의 보조 지표이며 연구 품질이나 우리 문제의 적합성 순위가 아니다.
- 이번 수치는 한 DB의 스냅샷이다. OpenAlex의 판본 병합·색인 지연·누락 때문에 다른 서비스와 다를 수 있다. 서로 다른 서비스의 수치를 섞어 순위를 만들지 않았다.
- 최신 출판일, 최신 개정일, 실제 검토 문헌 종료일은 별개다. 종료일을 확인하지 못한 논문에는 날짜를 추정해 채워 넣지 않았다.
- ‘평가셋 구축 전용 최신 고인용 survey’의 존재를 부정하는 결론이 아니다. 이번 조사에서 확인한 후보들이 모든 조건을 함께 충족하지 못했다는 뜻이다.
- 골든셋 50개는 이후 survey의 분류를 이용해 분석할 대상이다. 이번 단계에서는 분포나 생성 비율을 임의로 정하지 않는다.

## 보존한 근거

- [OpenAlex 원본 응답 15개](03_survey_citation_snapshot.json): 요청 DOI·API URL·조회 시간·응답 전체. 판본 정보와 인용 수를 재확인할 수 있다.
- 논문별 공식 링크와 본문 위치는 위 표와 설명에 기재했다.
- 기존 01·02번은 이전 조사 이력이다. 사용자가 요청한 현재 첫 단계의 독서 선정은 이 문서를 기준으로 한다.
