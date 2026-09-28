# Search agent 출력 전략: 정보 보존과 응답 지연의 균형

> 조사일: 2026-09-26. 범위: Deep Agents에서 main agent의 긴 최종 답변을 줄이면서 검색 근거를 보존하는 방법. Subagent 핸드오프와 표·이미지 설명의 토큰 관리도 포함한다. 이 문서는 설계 조사이며 현재 시스템의 구현이나 실측 결과를 뜻하지 않는다.

## 판단

현재의 주된 문제는 main agent의 최종 답변이 1만 토큰 이상으로 길어지는 것이다. Subagent 결과를 파일로 저장하고 짧게 전달하면 중간 토큰은 줄지만, 그 자체로 최종 답변 길이는 줄지 않는다. 이 점을 전제로 **원문 보존 + 질문별 근거 선택 + 필요할 때 원문 재조회** 경로를 둔다. 원문은 문서/오브젝트 저장소에 남기고, 검색 agent의 반환값은 `claim/evidence/source locator`가 있는 작은 근거 묶음으로 제한한다. 표와 이미지는 검색용 표현과 모델 입력용 표현을 분리한다. 이는 [Anthropic의 다중 agent 연구](https://www.anthropic.com/engineering/multi-agent-research-system)가 제안한 파일 기반 결과물 참조, [LangChain Deep Agents의 큰 tool 결과 offload](https://www.langchain.com/blog/context-management-for-deepagents), [RECOMP의 질문 조건부 추출 압축](https://arxiv.org/abs/2310.04408)을 조합한 **설계 제안**이다. 특정 토큰 예산이나 지연 개선율은 실측 전에는 확정할 수 없다.

## 근거별 핵심 주장

| 주제 | 확인한 사실 | 설계에 주는 의미 | 신뢰도 |
| --- | --- | --- | --- |
| 지연의 위치 | OpenAI의 API 지연 가이드는 일반적으로 생성 토큰을 줄이는 편이 입력 토큰 절감보다 지연에 더 크게 작용한다고 설명한다. 다만 아주 긴 입력은 예외다. | subagent가 1만 토큰을 **생성**하는 구간과 main agent가 그 1만 토큰을 **읽는** 구간을 별도로 계측한다. | 높음: 공급자 공식 가이드. 모델·서버 부하에 따라 수치는 달라짐. [출처](https://developers.openai.com/api/docs/guides/latency-optimization) |
| 핸드오프 | Anthropic은 subagent가 결과를 외부 결과물로 저장하고 부모에게 가벼운 참조만 돌려주는 패턴을 제안한다. 그들의 연구 시스템은 근거 위치를 찾는 CitationAgent도 분리한다. | 원문을 부모 대화에 복사하지 않고, 식별자와 증거 범위를 넘긴다. | 높음: 1차 구현 사례. 다만 특정 제품 효과 수치를 일반화할 수 없음. [출처](https://www.anthropic.com/engineering/multi-agent-research-system) |
| 오프로드 | Deep Agents는 큰 tool 결과를 파일로 내보내고 경로와 미리보기만 남기며, 이후 검색/재읽기를 허용한다. 문서상 20,000토큰은 해당 SDK의 임계치다. | 도구 결과와 subagent 최종 답변에 같은 원칙을 적용한다. 20,000을 우리 기본값으로 복사할 근거는 없음. | 높음: 공식 구현 설명. [출처](https://www.langchain.com/blog/context-management-for-deepagents) |
| 증거 압축 | RECOMP는 검색 문서에서 질문에 유용한 문장을 뽑는 추출형 압축과 생성형 압축을 구분하고, 무관한 근거는 빈 문자열로 반환하는 선택적 보강도 평가했다. | 사실 누락이 문제라면 생성형 요약보다 먼저 원문 span 선택을 시험한다. 논문의 6% 압축률은 우리 데이터의 기대치가 아님. | 중간~높음: 과제별 연구 결과. [출처](https://arxiv.org/abs/2310.04408) |
| 검색 품질 | Anthropic의 Contextual Retrieval은 chunk 설명을 색인에 추가하고, BM25·embedding·reranking을 결합했을 때 내부 평가의 top-20 검색 실패를 줄였다고 보고했다. | 출력량을 줄이기 전에 후보 관련성과 근거 재현율을 확보한다. 벤더 수치는 독립적 보편 성능이 아님. | 중간: 방법은 명확하지만 수치는 벤더 평가. [출처](https://www.anthropic.com/engineering/contextual-retrieval) |
| 긴 컨텍스트 | TACL 2024 연구는 관련 정보의 위치에 따라 긴 문맥 활용 성능이 떨어질 수 있음을 보였다. 최근 모델 및 실제 RAG에서는 효과가 달라질 수 있다. | 1만 토큰을 그대로 넘겨도 중요한 정보가 반드시 활용되는 것은 아니다. | 중간~높음: 동료 심사 논문, 모델 의존성 있음. [출처](https://aclanthology.org/2024.tacl-1.9/) |
| 표 표현 | Microsoft 문서 출력은 병합 셀, 계층 헤더를 표현하기 위해 HTML `<table>`을 사용한다. 표를 평탄화하면 구조 손실 가능성이 있다. 표 직렬화 선택만으로도 embedding/검색 결과가 달라진다는 연구가 있다. | HTML을 영구 삭제하지 말고 원본 구조를 보관한다. 단순 표만 안전하게 Markdown/행 표현으로 선별 변환한다. | 높음(형식), 중간(성능 일반화). [문서](https://learn.microsoft.com/en-us/azure/ai-services/content-understanding/document/markdown), [연구](https://arxiv.org/abs/2604.24040) |
| 표 QA | T²-RAGBench는 실제 텍스트+표 질문에서 검색과 수치 추론을 함께 평가하며, 해당 실험에서는 hybrid BM25가 가장 효과적이었다고 보고한다. | 표 질문을 일반 문단 QA와 따로 평가하고 정확한 행/열/각주를 측정한다. | 중간~높음: 동료 심사, 해당 벤치마크 범위. [출처](https://aclanthology.org/2026.eacl-long.8/) |
| 이미지 | Azure의 멀티모달 검색 문서는 이미지 설명을 색인해 검색 가능하게 하고, 원본 이미지/위치 정보를 함께 유지하는 경로를 설명한다. | 자세한 이미지 설명 전체를 매번 본문에 싣지 않고, 짧은 검색용 설명과 원본 참조를 쓴다. | 높음: 공식 제품 문서, 우리 데이터 품질은 미검증. [출처](https://learn.microsoft.com/en-us/azure/search/search-how-to-semantic-chunking) |

## 제안하는 출력 계약

검색 agent에는 임의의 문장 수 제한보다 **질문, 결과 형식, 반드시 보존할 항목**을 지정한다. Anthropic도 위임 시 objective·output format·source/tool 지침·작업 경계를 명시해야 누락과 중복이 줄었다고 보고한다. [출처](https://www.anthropic.com/engineering/multi-agent-research-system)

```json
{
  "question": "질문 또는 하위 질문",
  "answerable": true,
  "findings": [
    {
      "claim": "원문에서 확인한 원자적 사실 하나",
      "evidence": "그 사실을 뒷받침하는 짧은 원문 span 또는 보존된 수치/셀",
      "source_id": "doc-17",
      "locator": {"page": 8, "section": "3.2", "table_id": "T2", "row": "2025", "column": "매출"},
      "confidence": "high"
    }
  ],
  "conflicts": ["다른 문서·버전과 불일치가 있을 때 명시"],
  "missing": ["근거가 없는 질문 부분"],
  "artifact_id": "원문/파싱 결과를 다시 읽을 수 있는 내부 식별자"
}
```

이 스키마는 **제안**이며 프레임워크의 내장 표준이 아니다. `evidence`는 질문에 관련된 원문을 짧게 *추출*하고, 숫자·단위·날짜·조건·부정·예외·표 헤더·각주는 자르지 않는다. `source_id`와 locator는 클라이언트 인용에 필요한 안정적인 ID여야 한다. 내용 해시·문서 버전도 원문 저장소에 보존해 수정 이후의 잘못된 인용을 피한다. 부모는 누락/충돌/표 계산이 있거나 확신이 낮으면 `artifact_id + locator`로 해당 범위만 다시 읽는다. 부모와 subagent에 동일한 전체 HTML/이미지 설명을 반복 주입하지 않는다.

## main agent의 최종 출력 계약

상세 결과는 파일에 보존하되, main agent는 질문에 직접 답하는 핵심 내용과 근거 인용만 생성한다. 전체 표와 장문의 원문은 main agent가 다시 쓰지 않고 UI나 백엔드가 저장된 결과물을 직접 보여주거나 링크한다. 따라서 파일 저장은 중간 전달을 줄이는 수단이고, 최종 생성 토큰을 줄이려면 최종 답변 형식과 상세 결과물 표시 방식을 별도로 정해야 한다. [OpenAI 지연 가이드](https://developers.openai.com/api/docs/guides/latency-optimization)는 생성 토큰 감소와 UI 직접 표시를 지연 개선 방법으로 설명한다.

## 파싱 표현과 출력 표현을 분리

```text
PDF/이미지
  → 파싱 원본: HTML 표·원본 이미지·상세 설명·bbox·페이지·각주 보존
  → 검색 색인: 문단 / 표 제목·헤더·행 / 이미지 짧은 설명을 별도 항목으로 색인
  → 검색 결과: 관련 근거 span·행/열·페이지와 원본 참조
  → subagent 결과: 원자적 사실 + 충돌/누락 + 참조
  → main agent: 필요한 표 영역/이미지만 추가 조회 후 답변
```

1. **표:** 원본 HTML과 병합 셀 좌표를 canonical artifact로 유지한다. 단순 2차원 표는 헤더를 유지한 Markdown 또는 `행 키 | 열 키 | 값 | 단위 | 각주`로 모델 입력을 구성할 수 있다. 복합 헤더·`rowspan`/`colspan`·표 내 각주·행간 계산이 있으면 단순 변환이 무손실인지 검증하고 관련 원본 부분을 함께 조회한다. 전체 표를 매번 반환하지 않는다. SQL처럼 행/열을 결정적으로 골라낼 수 있는 경우에는 코드로 추출하고 모델은 질문 해석과 검증에 쓴다. 이 중 행/열 선별 방식은 원문 구조와 표 직렬화 연구에서 도출한 **설계 추론**이다.
2. **이미지:** 검색용 짧은 설명, OCR 문자, 페이지·bbox·이미지 ID를 분리한다. 본문 OCR과 이미지 설명에서 같은 문장이 중복되면 반환 시 한 번만 싣는다. 차트·도식은 이미지 설명만으로 수치 관계가 불명확하면 원본 crop을 다시 보거나 사용자에게 불확실성을 표시한다. 이미지 설명은 모델이 해석한 2차 정보이므로 원문 OCR/시각 정보와 같은 신뢰도로 취급하지 않는다.
3. **청크:** 섹션/표/그림 경계를 기준으로 나누고 부모 문서 ID와 원본 위치를 연결한다. 표 전체가 매우 크면 헤더 문맥을 각 행 묶음에 붙여 색인하되, 최종 인용은 원본 표의 정확한 셀로 연결한다. Markdown 파서는 표를 평문으로만 취급할 수도 있으므로, 표 엔터티를 별도 관리하는 편이 안전하다. [Azure 구조 기반 청킹](https://learn.microsoft.com/en-us/azure/search/search-how-to-semantic-chunking), [Azure Markdown 색인 제한](https://learn.microsoft.com/en-us/azure/search/search-how-to-index-azure-blob-markdown).

## 선택 순서와 측정

1. **병목 분해:** main 최종 생성 토큰/초와 생성 시간, subagent 반환 생성 시간, main 입력 토큰과 prefill 시간, 전체 p50/p95 지연을 분리한다. 현재 관찰된 1만 토큰은 main 최종 답변이므로 이 출력을 우선 측정하고 줄인다. 이는 [OpenAI 지연 가이드](https://developers.openai.com/api/docs/guides/latency-optimization)의 방향과 맞지만 로컬 서빙에서는 직접 측정해야 한다.
2. **원본 보존과 참조 반환:** raw parser output, 원본 표, 이미지 설명을 결과물로 저장한다. agent에는 `artifact_id`·locator가 있는 근거 묶음만 반환한다. Deep Agents의 20,000토큰 임계치를 그대로 쓰기보다 우리 호출의 p95 길이와 모델 창 크기로 offload 조건을 정한다.
3. **결정적 정리:** HTML의 장식/불필요한 태그, 반복 페이지 머리말, 중복 OCR/캡션을 제거하되 원본 구조/수치/각주를 보존한다. 이 단계는 LLM 생성 비용이 없다.
4. **질문별 선택:** 관련 문장·표 셀을 추출하고, 복수 문서의 중복 주장만 합친다. 출처 간 불일치는 합치지 않는다. 근거가 부족하면 추가 검색/원본 재조회를 허용한다.
5. **적응 예산:** 첫 반환은 작은 예산으로 시작하되 고정 절단하지 않는다. 예를 들어 `1~2k` 토큰을 **실험 시작값**으로 놓고, 넓은 비교·수치 표·다중 문서 질문에 예산과 재조회 횟수를 늘린다. 이 수치는 공개 문헌의 권장 표준이 아니다.
6. **평가:** 현재의 원문 거의 그대로 전달 방식을 baseline으로 두고 `(a) 결정적 정리`, `(b) 근거 추출 + 참조`, `(c) 생성 요약`, `(d) 필요 시 원문 재조회`를 같은 질문 집합에서 비교한다. 핵심 지표는 최종 답변 정확도, 필수 사실 recall, 숫자/단위/각주 일치, citation support, 충돌 표시, 1만 토큰 이상 출력 비율, p50/p95 지연, 총 토큰/비용이다. 특히 표·그림·부정 조건·두 문서 충돌 질문을 별도 층으로 묶는다. 축소된 반환이 빠르지만 정확도가 낮아지면 성공으로 간주하지 않는다.

## 남은 질문과 상충점

- **짧은 출력 vs 정확성:** 추출형 압축도 관련성 판정이 틀리면 필수 근거를 버릴 수 있다. 원문 참조와 재조회 경로가 있어야 한다.
- **Markdown 변환 vs 표 구조:** HTML 태그 삭제는 토큰을 줄이지만 병합 셀의 의미를 잃을 수 있다. 복합 표는 구조를 유지하고 필요한 영역만 읽는다.
- **지연 vs reranking:** reranker는 근거 선택을 개선할 수 있지만 추가 단계의 시간이 든다. 데이터에서 이익이 확인될 때 채택한다.
- **입력 절감 vs 생성 절감:** 현재 main agent의 최종 답변 생성이 주요 병목이라면, subagent 결과를 파일로 옮기거나 prompt caching만 해서는 해결되지 않는다. 최종 답변과 상세 결과물의 전달 방식을 바꿔야 한다.
- **미확인 환경:** 실제 model, serving runtime, 토크나이저, 원문 저장소, 현재 chunk schema, 표의 복잡도 분포, 이미지 설명 중복률, 정확도 요구 수준을 아직 확인하지 않았다. 따라서 특정 포맷이나 수치를 운영 기본값으로 단정하지 않는다.

## 참고 자료

- Anthropic Engineering, [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system), 2025. 1차 구현 사례.
- LangChain, [Context Management for Deep Agents](https://www.langchain.com/blog/context-management-for-deepagents), 2026. 1차 구현 설명.
- LangChain, [Deep Agents Subagents](https://docs.langchain.com/oss/python/deepagents/subagents), 2026-09-26 확인. 공식 문서.
- OpenAI, [Latency optimization](https://developers.openai.com/api/docs/guides/latency-optimization), 2026-09-26 확인. 공식 API 가이드.
- Xu et al., [RECOMP](https://arxiv.org/abs/2310.04408), 2023. 연구 논문.
- Liu et al., [Lost in the Middle](https://aclanthology.org/2024.tacl-1.9/), TACL 2024. 동료 심사 논문.
- Anthropic Engineering, [Contextual Retrieval](https://www.anthropic.com/engineering/contextual-retrieval), 2024. 벤더 평가.
- Microsoft, [Document analysis: Markdown representation](https://learn.microsoft.com/en-us/azure/ai-services/content-understanding/document/markdown), 2026-09-26 확인. 공식 형식 문서.
- Microsoft, [Chunk and Vectorize by Document Layout](https://learn.microsoft.com/en-us/azure/search/search-how-to-semantic-chunking), 2026-09-26 확인. 공식 검색 문서.
- Strich et al., [T²-RAGBench](https://aclanthology.org/2026.eacl-long.8/), EACL 2026. 동료 심사 논문.
- [Improving Robustness of Tabular Retrieval via Representational Stability](https://arxiv.org/abs/2604.24040), 2026. 사전 공개 논문.


