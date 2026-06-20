# Gemma 4 on Mac mini M4 32GB for Document Agent

Date: 2026-06-20

## Goal

Mac mini M4, 32GB unified memory에서 Gemma 4 계열 모델을 로컬로 실행해 LangGraph 기반 개인 문서 Agent를 구성할 때의 모델/양자화/런타임 선택 기준을 정리한다.

## Hardware Assumption

- Mac mini M4
- 32GB unified memory
- 개인용 Agent, 주 작업은 문서 요약, 문서 질의응답, 문서 재작성, 메타데이터 추출, RAG 기반 탐색

## Current Official Facts

Google 공식 Gemma 4 문서 기준:

- Gemma 4 모델군은 E2B, E4B, 12B, 26B A4B, 31B를 제공한다.
- Q4_0 기준 모델 로드 메모리 추정:
  - E2B: 2.9GB
  - E4B: 4.5GB
  - 12B: 6.7GB
  - 26B A4B: 14.4GB
  - 31B: 17.5GB
- 위 수치는 static model weights 중심이며, KV cache와 런타임 오버헤드는 별도이다.
- 공식 QAT 모델이 제공된다.
- llama.cpp / LM Studio 로컬 배포용 suffix는 `{model-name}-qat-q4_0-gguf`이다.
- Ollama는 `gemma4:e2b`, `gemma4:e4b`, `gemma4:26b`, `gemma4:31b` 태그를 문서화하고 있다.
- MLX는 Apple Silicon용 실행 경로로 문서화되어 있으며, OpenAI-compatible endpoint 서버 실행이 가능하다.

Sources:

- Google AI for Developers, Gemma 4 model overview, last updated 2026-06-08: https://ai.google.dev/gemma/docs/core
- Google AI for Developers, Run Gemma with Ollama, last updated 2026-04-02: https://ai.google.dev/gemma/docs/integrations/ollama
- Google AI for Developers, Run Gemma with MLX, last updated 2026-04-16: https://ai.google.dev/gemma/docs/integrations/mlx
- Google AI for Developers, Run Gemma with llama.cpp, last updated 2026-04-16: https://ai.google.dev/gemma/docs/integrations/llamacpp

## Community / Case Evidence

Gemma 4는 2026-04 공개라 Mac mini M4 32GB + Gemma 4 전용 커뮤니티 벤치마크는 아직 충분히 축적되지 않았다. 그래서 다음 두 계열을 나눠 참고해야 한다.

### 1. Apple Silicon Local LLM Runtime Evidence

Apple Silicon 로컬 LLM 비교 연구에서는 MLX, MLC-LLM, Ollama, llama.cpp, PyTorch MPS를 비교했다. 실험 모델은 Gemma 4가 아니라 Qwen 계열이지만, Apple Silicon에서의 런타임 경향을 볼 수 있다.

핵심 시사점:

- MLX는 sustained generation throughput이 강하다.
- MLC-LLM은 moderate prompt에서 TTFT가 낮은 경향이 있다.
- llama.cpp는 단일 경량 스트림에서 효율적이다.
- Ollama는 개발 편의성이 좋지만 throughput/TTFT는 상대적으로 불리할 수 있다.
- PyTorch MPS는 큰 모델과 긴 컨텍스트에서 메모리 한계가 두드러질 수 있다.

Source:

- Production-Grade Local LLM Inference on Apple Silicon, arXiv 2511.05502: https://arxiv.org/abs/2511.05502

### 2. Local Document RAG / PDF Chatbot Evidence

로컬 Ollama 기반 PDF 챗봇 사례 연구는 자동차 산업 문서에서 PDF 처리, retrieval, context compression, LangGraph 기반 self-RAG agent 개선이 naive RAG보다 효과적이었다고 보고한다.

문서 Agent 설계 시사점:

- 긴 문서를 통째로 컨텍스트에 넣는 방식보다 RAG 품질이 중요하다.
- PDF layout, multi-column, table, technical specification 처리가 병목이 된다.
- retrieval precision/recall, faithfulness를 별도 평가해야 한다.
- LangGraph 기반 self-RAG는 local model과도 조합 가능하다.

Source:

- Optimizing RAG Techniques for Automotive Industry PDF Chatbots, arXiv 2408.05933: https://arxiv.org/abs/2408.05933

### 3. Gemma 4 Capability Evidence

Gemma 4 E4B와 31B를 비교한 병렬 프로그래밍 교육 보조 평가에서는 31B가 E4B보다 명확히 강했다.

시사점:

- E4B는 가볍지만 메인 문서 Agent 품질을 기대하기에는 한계가 있을 수 있다.
- 31B는 설명/수정/분석 품질이 필요한 작업에서 의미가 있다.
- 32GB 환경에서는 31B Q4 실행 가능성과 Agent 체감 속도를 분리해서 평가해야 한다.

Source:

- Evaluating Gemma4 Models as AI Teaching Assistants, arXiv 2606.14881: https://arxiv.org/abs/2606.14881

## Working Recommendation

### Model Profiles

1. Fast profile
   - Gemma 4 E4B QAT Q4
   - 용도: 라우팅, 문서 분류, chunk metadata 생성, 짧은 요약, 검색 쿼리 재작성

2. Default document profile
   - Gemma 4 12B QAT Q4
   - 용도: 일반 문서 질의응답, 요약, 문서 재작성, 근거 기반 답변
   - 32GB 메모리에서 가장 현실적인 기본값

3. Quality profile
   - Gemma 4 31B QAT Q4
   - 용도: 어려운 문서 분석, 복잡한 비교, 긴 추론, 최종 보고서 생성
   - 단점: 긴 context, 동시 LangGraph 노드, vector DB, 브라우저/IDE 병행 시 메모리와 latency 부담

### Runtime Order

1. Ollama
   - 가장 빠른 설치와 LangGraph 연동
   - 초기 검증용

2. llama.cpp
   - GGUF/QAT 세부 옵션과 서버 옵션을 직접 제어하기 좋음
   - production-like local server 실험용

3. MLX
   - Apple Silicon 최적화 실험용
   - 속도가 중요하고 모델 포맷/서버 구성을 직접 관리할 수 있을 때 검토

## LangGraph Agent Design

권장 구조:

```text
입력 문서
  -> parser / chunker
  -> embedding / vector store
  -> E4B: routing, query rewrite, metadata extraction
  -> retriever
  -> 12B: grounded answer / summary / rewrite
  -> optional 31B: difficult synthesis / final report
  -> citation / verification node
```

중요한 점:

- 32GB라고 해서 항상 31B를 메인으로 쓰는 것이 최선은 아니다.
- 문서 Agent는 모델 크기보다 retrieval 품질, chunking, citation, context compression의 영향이 크다.
- E4B를 메인으로 쓰기는 아쉽지만, LangGraph 내부 보조 노드로는 가치가 있다.
- 12B를 default, 31B를 escalation model로 두는 구성이 가장 실용적이다.

## Open Questions

- 실제 Mac mini M4 32GB에서 Gemma 4 12B/31B QAT Q4의 tokens/sec 측정 필요
- Ollama vs llama.cpp vs MLX의 같은 prompt 기준 TTFT, throughput, memory 압력 비교 필요
- 한국어 문서 요약/질의응답 품질 비교 필요
- PDF, Markdown, web page, code document별 chunking 전략 비교 필요

## Public Token Speed Benchmark Gap

2026-06-20 기준으로 검색한 범위에서는 다음 조건을 모두 만족하는 공개 벤치마크를 확인하지 못했다.

- Mac mini base M4
- 32GB unified memory
- Gemma 4 E4B / 12B / 26B A4B / 31B
- QAT Q4 또는 Q4_0 GGUF
- 동일 런타임, 동일 prompt, 동일 context 길이 기준 tokens/sec 비교

대신 확인 가능한 근거는 다음처럼 간접적이다.

- Google 공식 문서는 각 Gemma 4 Q4_0 모델의 메모리 요구량을 제공하지만 tokens/sec는 제공하지 않는다.
- Apple Silicon runtime 비교 연구는 MLX, MLC-LLM, Ollama, llama.cpp, PyTorch MPS의 경향을 비교하지만, 실험 장비가 M2 Ultra 192GB이고 모델도 Qwen 계열이라 Mac mini M4 32GB + Gemma 4의 직접 근거는 아니다.
- vllm-mlx 연구는 Apple M4 Max에서 MLX 기반 throughput 개선을 보고하지만, base M4 32GB와 Gemma 4 QAT Q4 비교는 아니다.
- Open-TQ-Metal 연구는 Gemma 4 31B와 long-context/KV-cache 압축을 다루지만, 64GB급 환경과 특수 커널 중심이라 일반 Ollama/llama.cpp 사용자의 baseline으로 직접 쓰기는 어렵다.

따라서 실제 선택에는 로컬 벤치마크가 필요하다.

권장 측정 항목:

- prompt processing tokens/sec
- generation tokens/sec
- time to first token
- peak memory pressure
- swap 발생 여부
- 4K, 16K, 32K context별 변화
- 동일 문서 요약/RAG/재작성 prompt의 품질 비교

권장 비교 후보:

- Gemma 4 12B QAT Q4
- Gemma 4 26B A4B QAT Q4
- Gemma 4 31B QAT Q4
- 필요 시 E4B QAT Q4는 보조 노드 기준으로만 측정

### Community Thread Evidence Found

직접적인 Mac mini M4 32GB 사례는 아니지만, r/LocalLLaMA 기반으로 보도된 Gemma 4 E4B 로컬 실행 사례가 있다.

사례:

- Hardware: Nvidia Jetson Orin NX Super 16GB
- Model: Gemma 4 E4B
- Quantization/runtime: Q4_K_M via llama.cpp
- KV cache: q8_0
- flash attention 사용
- context: 12K conversation memory
- reported performance:
  - cached TTFT: 약 200ms
  - generation: 약 14-15 tokens/sec

해석:

- 이 수치는 Apple Silicon이 아니라 Jetson Orin 계열이므로 Mac mini M4 32GB에 직접 대입하면 안 된다.
- 다만 E4B Q4_K_M이 edge/local 환경에서 실시간 대화 수준은 가능하다는 참고값으로 쓸 수 있다.
- 문서 Agent 메인 후보인 12B, 26B A4B, 31B의 속도 판단에는 여전히 직접 벤치마크가 필요하다.

Source:

- Tom's Hardware coverage of r/LocalLLaMA thread, 2026-05-17: https://www.tomshardware.com/tech-industry/artificial-intelligence/maker-packs-an-opinionated-googly-eyed-ai-chatbot-into-a-mobile-suitcase-powered-by-an-nvidia-jetson-entirely-local-machine-entity-runs-gemma-4-e4b-and-can-respond-in-200ms
