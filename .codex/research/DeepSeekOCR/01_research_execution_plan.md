# DeepSeekOCR vLLM 최적화 Research 실행 계획

> 작성일: 2026-06-20  
> 기준 문서: `.codex/research/DeepSeekOCR/00_research_overview.md`  
> 원칙: 웹 검색 없이 로컬 노트, 현재 운영 가정, 이후 코드/로그 확인을 기준으로 단계별 research 문서를 작성한다. 외부 공식 문서 확인이 필요한 내용은 별도 표시한다.

---

## 목표

DeepSeekOCR V2 최적화를 위해 vLLM의 serving 구조를 먼저 이해하고, 현재 FastAPI + H200 MIG 30GB + 다중 모델 상주 구조에서 어떤 설정이 어떤 병목에 영향을 주는지 설명 가능한 형태로 정리한다.

---

## 산출물 순서

### 2. `02_vllm_serving_architecture.md`

vLLM이 request를 처리하는 흐름을 정리한다.

- engine 초기화
- memory profiling
- KV cache block 관리
- prefill
- decode
- scheduler
- continuous batching
- PagedAttention
- CUDA graph
- Python direct call에서의 batch loop 해석

### 3. `03_vlm_ocr_inference_characteristics.md`

VLM/OCR이 일반 LLM과 다른 점을 정리한다.

- image preprocessing
- visual token
- image prompt
- prefill 비용
- OCR output length
- page별 편차
- batch tail latency

### 4. `04_deepseekocr_v2_model_notes.md`

DeepSeekOCR V2 모델 자체의 입력 형식과 주의사항을 정리한다.

- 모델 카드 기준 입력 형식
- image prompt 의미
- 권장 image 크기와 crop/tiling 방식
- 권장 generation 옵션
- vLLM에서 지원되는 multimodal 입력 형태

### 5. `05_h200_mig_30gb_memory_analysis.md`

H200 MIG 30GB에서 세 모델이 공존할 때 메모리 예산을 정리한다. Heron101/CLIP은 파라미터가 작은 모델이므로, 공존 구조는 실제 메모리 delta와 latency 차이로 우선순위를 판단한다.

- Heron101 상주 메모리와 로드 전후 free memory delta
- CLIP 상주 메모리와 로드 전후 free memory delta
- DeepSeekOCR V2 weight
- vLLM KV cache
- `gpu_memory_utilization=0.8` 해석
- batch size와 KV cache capacity 관계

### 6. `06_bottleneck_measurement_plan.md`

실제 코드에 넣을 계측 지점을 정리한다.

- FastAPI request level timing
- batch loop timing
- prepare/generate/postprocess 분리
- GPU memory snapshot
- output token length 기록
- progress bar 사이 공백 검증

### 7. `07_vllm_options_for_deepseekocr.md`

vLLM 옵션을 구조와 연결해서 정리한다.

- `gpu_memory_utilization`
- `max_num_seqs`
- `max_num_batched_tokens`
- `max_model_len`
- multimodal 관련 제한
- dtype/quantization
- chunked prefill
- prefix caching

### 8. `08_experiment_matrix.md`

실험 순서와 비교표를 만든다.

- batch size 4/8/16
- DeepSeekOCR 단독 vs 세 모델 공존
- `gpu_memory_utilization` 변화
- sequence/token limit 변화
- 문서 특성별 batch 구성

---

## 진행 방식

각 문서는 다음 형식을 따른다.

```text
1. 이 문서에서 답할 질문
2. 핵심 구조
3. 현재 서버에 적용한 해석
4. 최적화와 연결되는 지점
5. 확인이 필요한 로그/코드
6. 다음 문서로 넘길 질문
```

---

## 현재 1순위

먼저 `02_vllm_serving_architecture.md`를 작성한다. 이 문서가 있어야 이후 `max_num_seqs`, `max_num_batched_tokens`, `gpu_memory_utilization` 같은 옵션을 단순 설정값이 아니라 vLLM 내부 구조와 연결해서 설명할 수 있다.
