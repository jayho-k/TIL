# vLLM 기반 DeepSeekOCR V2 최적화 조사 계획

> 작성일: 2026-06-20  
> 목적: H200 MIG 30GB 환경에서 DeepSeekOCR V2의 PDF/OCR 처리 성능 병목을 구조적으로 분석하고, vLLM 옵션과 운영 구조를 근거 있게 최적화하기 위한 조사 계획을 정의한다.  
> 범위: 현재 대화에서 확인된 운영 구조와 기존 로컬 vLLM 노트를 기반으로 한 1차 계획이다. 외부 자료 조사는 이후 별도 research 문서에서 공식 문서, 모델 카드, 코드 기준으로 보강한다.

---

## 1. 현재 문제 정의

현재 PDF 100페이지 이상 입력에서 전체 처리 시간이 약 300초 이상 걸리는 문제가 있다. PDF를 이미지로 변환하는 작업은 별도 Parser 서버(CPU)에서 미리 수행한 뒤 Model 서버(GPU)로 넘기므로, 1차 병목 후보에서는 제외한다.

관찰된 증상은 다음과 같다.

- DeepSeekOCR V2 실행 중 `image prompt` progress bar 자체가 올라가는 속도는 느리지 않다.
- 하지만 한 batch의 progress bar가 끝난 뒤 다음 16개 batch의 progress bar가 생기기까지 긴 공백이 있다.
- Model 서버는 FastAPI endpoint로 노출되어 있다.
- DeepSeekOCR V2는 Python 코드에서 vLLM 객체를 직접 호출하는 방식이다.
- 모델 로드는 `deepseekocrv2.py`의 `load()` 함수에서 수행되며, FastAPI 시작 시 1회만 호출된다.
- H200 GPU를 사용하지만 MIG로 인해 현재 사용 가능한 GPU 메모리는 30GB이다.
- 같은 30GB MIG 안에 Heron101, CLIP, DeepSeekOCR V2가 모두 상주한다.
- 단, Heron101과 CLIP은 파라미터가 작은 모델이므로 weight memory 자체가 주 병목이라고 단정하면 안 된다.
- DeepSeekOCR V2의 vLLM `gpu_memory_utilization`은 현재 `0.8`이다.
- 이미지 batch size는 16이고, vLLM 쪽 sequence 관련 설정도 16에 맞춰져 있다.
- 과거 `float32` 사용 시 100페이지 이상 PDF 처리 시간이 약 300초 수준으로 길었고, `bfloat16`으로 변경한 뒤 확실한 속도 개선이 있었다.

따라서 이번 조사의 핵심은 단순히 옵션 값을 바꾸는 것이 아니라, vLLM이 VLM/OCR 모델을 어떤 방식으로 서빙하는지 이해하고 현재 서버 구조의 병목 지점을 구조적으로 좁히는 것이다.

특히 dtype 변경은 별도 분석 대상이다. `float32 -> bfloat16` 개선은 단순히 자료형 크기가 줄어든 효과뿐 아니라, H200 MIG 30GB 안에서 weight, activation, KV cache, memory bandwidth, Tensor Core 활용이 함께 바뀐 결과일 수 있다. 따라서 속도 개선과 OCR 정확도/품질 사이의 관계를 별도로 검증해야 한다.

---

## 2. 현재 서버 구조

```text
Parser Server (CPU)
  -> PDF를 page image로 변환
  -> 전체 image payload를 Model Server로 전달

Model Server (GPU / FastAPI / H200 MIG 30GB)
  -> FastAPI endpoint 수신
  -> images를 batch size 16으로 chunking
  -> Heron101 모델 사용
  -> CLIP 모델 사용
  -> DeepSeekOCR V2 호출
       -> vLLM LLM 객체는 startup 시 1회 load
       -> batch 단위 generate 수행
  -> 결과 취합 후 응답
```

GPU 메모리 상주 구조는 다음처럼 가정한다.

```text
H200 MIG 30GB
  ├─ Heron101 weights / runtime memory
  ├─ CLIP weights / runtime memory
  └─ DeepSeekOCR V2 via vLLM
       ├─ model weights
       ├─ processor / multimodal input handling
       ├─ activation / temporary buffers
       └─ KV cache pool
```

이 구조에서는 DeepSeekOCR V2 단독 성능만 볼 수 없다. 다만 Heron101, CLIP은 상대적으로 작은 모델이므로, 공존 영향은 weight memory보다 CUDA context, runtime buffer, request concurrency, 로드 순서, 실행 타이밍에서 확인하는 편이 더 정확하다. vLLM은 실제 남은 메모리 안에서 DeepSeekOCR V2 weight, runtime buffer, KV cache를 배분한다.

---

## 3. vLLM Serving Pipeline 분석 범위

조사할 vLLM serving pipeline은 다음 단계로 나눈다.

```text
Input preparation
  -> multimodal processor
  -> prompt construction
  -> image token / placeholder 처리
  -> prefill scheduling
  -> KV cache block allocation
  -> decode scheduling
  -> output postprocessing
  -> next batch preparation
```

각 단계에서 확인할 질문은 다음과 같다.

| 단계 | 확인 질문 |
| --- | --- |
| 입력 준비 | 이미지가 batch마다 어떤 형태로 변환되는가? CPU tensor, GPU tensor, PIL image, bytes 중 어디서 비용이 생기는가? |
| multimodal processor | 이미지 resize, crop, tiling, patch embedding 전처리가 batch 사이 공백에 포함되는가? |
| prompt 구성 | OCR prompt와 image placeholder가 batch마다 재생성되는가? |
| prefill | 이미지 토큰이 실제로 몇 token으로 확장되는가? batch 16이 prefill에 어느 정도 부담을 주는가? |
| KV cache | MIG 30GB에서 usable KV cache block 수가 충분한가? |
| decode | 출력 길이가 긴 페이지가 batch tail latency를 만드는가? |
| 후처리 | output parsing, text 정리, CPU copy, GPU sync가 다음 progress bar 생성을 늦추는가? |
| 다음 batch 준비 | batch loop 안에서 동기 작업, 메모리 해제, GC, CUDA sync가 있는가? |

---

## 4. VLM/OCR 추론에서 일반 LLM과 다른 점

VLM 기반 OCR은 일반 텍스트 LLM과 병목 구조가 다르다.

```text
Text LLM
  prompt tokens
  -> prefill
  -> decode

VLM / OCR
  image preprocessing
  -> visual encoder or image tokenization
  -> visual tokens + text prompt
  -> prefill
  -> decode OCR text
```

중요 차이는 다음과 같다.

- 한 장의 이미지가 많은 visual token으로 변환될 수 있다.
- page image 해상도, crop/tiling 방식, `limit_mm_per_prompt` 같은 설정이 prefill 비용을 크게 바꿀 수 있다.
- OCR 출력은 문서 밀도에 따라 짧을 수도 있고 매우 길 수도 있다.
- batch 안에 긴 출력 페이지가 섞이면 전체 batch 완료 시점이 지연될 수 있다.
- batch size 16은 단순히 "16개 요청"이 아니라 "visual token이 큰 요청 16개를 동시에 처리"한다는 의미가 될 수 있다.

---

## 5. H200 MIG 30GB 제약과 메모리 모델

현재 환경에서 중요한 제약은 H200 전체 GPU가 아니라 MIG로 분리된 30GB 메모리만 사용할 수 있다는 점이다.

vLLM 메모리는 대략 다음 범주로 나누어 봐야 한다.

```text
GPU memory 30GB
  -> already loaded models
       Heron101
       CLIP
  -> DeepSeekOCR V2 weights
  -> non-torch / CUDA context / fragmentation
  -> activation and temporary buffers
  -> vLLM KV cache blocks
```

`gpu_memory_utilization=0.8`은 단순히 DeepSeekOCR V2가 전체 30GB의 80%만 사용한다는 의미로 보면 안 된다. vLLM이 초기 메모리 프로파일링을 통해 사용할 수 있다고 판단한 영역 안에서 KV cache와 실행 공간을 배분하는 설정으로 봐야 한다.

따라서 조사할 항목은 다음과 같다.

- Heron101, CLIP 로드 후 실제 free GPU memory
- DeepSeekOCR V2 weight load 후 free GPU memory
- vLLM 초기화 로그에 나타나는 KV cache block 수
- `gpu_memory_utilization=0.8`에서 동시 처리 가능한 token/seq 한계
- `gpu_memory_utilization`을 낮추거나 높였을 때 OOM, latency, throughput 변화
- 세 모델을 한 프로세스에 둘 때와 분리할 때의 메모리/스케줄링 차이

---

## 6. Batch Size 16과 Sequence 설정 16의 의미

현재 batch size와 sequence 관련 설정이 16으로 맞춰져 있다. 이 설정은 다음 두 관점에서 확인해야 한다.

```text
batch size 16
  -> Python application이 한 번에 넘기는 이미지 수

max_num_seqs 16
  -> vLLM scheduler가 동시에 처리할 수 있는 sequence 수
```

둘이 같은 값이라고 해서 항상 최적이라는 뜻은 아니다.

OCR/VLM에서는 다음 문제가 생길 수 있다.

- 각 이미지가 많은 visual token으로 확장되면 `max_num_batched_tokens`가 먼저 병목이 된다.
- batch 16이 prefill 단계에서 GPU memory와 compute를 크게 점유할 수 있다.
- 출력 길이 편차가 크면 batch 안의 긴 페이지가 tail latency를 만든다.
- 30GB MIG에서 Heron101/CLIP까지 상주하면 batch 16은 KV cache를 압박할 수 있다. 다만 두 모델이 작은 편이라면, 실제 압박 크기는 로드 전후 free memory delta로 검증해야 한다.

따라서 batch size는 4, 8, 16처럼 비교하고, 단순 총 처리 시간뿐 아니라 batch 사이 공백 시간과 GPU memory 사용량을 함께 봐야 한다.

---

## 7. Batch 사이 지연에 대한 병목 가설

현재 증상 기준으로 우선순위가 높은 병목 가설은 다음과 같다.

### 가설 A. Batch 전처리 또는 multimodal processor 병목

progress bar가 뜨기 전 이미지 전처리, processor 적용, prompt 구성에서 시간이 걸릴 수 있다.

확인 방법:

- batch loop에서 vLLM 호출 직전까지 단계별 wall time 측정
- 이미지 객체 변환, resize, tensor 변환 시간을 분리 측정
- processor가 CPU에서 도는지, GPU에서 도는지 확인

### 가설 B. Batch 후처리 또는 GPU 동기화 병목

progress bar가 끝난 뒤 output을 CPU로 가져오거나 후처리하는 과정에서 GPU 작업 완료를 기다릴 수 있다.

확인 방법:

- vLLM generate 반환 직후 시간 측정
- output parsing 시간 측정
- `torch.cuda.synchronize()`가 명시적/암묵적으로 호출되는 지점 확인

### 가설 C. 메모리 압박과 KV cache block 부족

세 모델이 같은 30GB MIG에 상주하기 때문에 vLLM KV cache 여유가 부족할 수 있다. 하지만 Heron101/CLIP의 파라미터 규모가 작다면, 더 큰 영향은 DeepSeekOCR V2의 dtype, visual token 수, batch size, output 길이에서 나올 가능성이 높다.

확인 방법:

- vLLM 초기화 로그에서 KV cache capacity 확인
- `nvidia-smi` 또는 NVML로 batch 전후 memory 추적
- batch size와 `max_num_seqs`를 낮췄을 때 batch 사이 공백이 줄어드는지 확인

### 가설 D. Decode tail latency

문서별 출력 길이 편차가 커서 batch 안의 긴 페이지가 전체 batch 완료를 늦출 수 있다.

확인 방법:

- page별 output token 수 기록
- page별 decode 완료 시각 또는 generate 결과 반환 시각 추적
- 긴 페이지를 분리하거나 output 길이 기준으로 batch를 구성했을 때 개선 여부 확인

### 가설 E. FastAPI/Python loop 병목

FastAPI 요청 처리, 큰 image payload 역직렬화, batch loop 구현, 동기 I/O가 병목일 수 있다.

확인 방법:

- endpoint 진입부터 batch loop 시작까지 측정
- batch별 입력 image 수, payload 크기, serialization 비용 기록
- GPU 작업과 무관한 Python 처리 시간을 분리

---

## 8. 계측해야 할 지점

우선 코드에 다음 구간별 시간을 기록한다.

```text
request_start
  -> payload_received
  -> batch_split_done
  -> batch_i_prepare_start
  -> batch_i_prepare_done
  -> batch_i_generate_start
  -> batch_i_generate_done
  -> batch_i_postprocess_done
  -> response_done
```

batch 단위로 기록할 메타데이터는 다음과 같다.

| 항목 | 목적 |
| --- | --- |
| batch index | 느린 batch 위치 확인 |
| image count | 마지막 batch 등 크기 차이 확인 |
| image size / resolution | visual token 증가 원인 확인 |
| prompt 길이 | text token 영향 확인 |
| output length | decode tail latency 확인 |
| generate wall time | vLLM 내부 시간 근사 |
| prepare/postprocess wall time | progress bar 사이 공백 원인 확인 |
| GPU allocated/reserved/free memory | 메모리 압박 확인 |

가능하면 vLLM 로그에서 다음을 함께 수집한다.

- initialized KV cache blocks
- maximum concurrency 관련 로그
- prefill/decode throughput
- scheduler 관련 warning
- OOM 또는 memory profiling warning

---

## 9. vLLM 옵션별 조사 항목

우선 조사할 옵션은 다음과 같다.

| 옵션/개념 | 조사 이유 |
| --- | --- |
| `gpu_memory_utilization` | 30GB MIG에서 KV cache와 타 모델 상주 메모리의 균형 확인 |
| `max_num_seqs` | batch 16이 실제로 동시 seq 처리에 적절한지 확인 |
| `max_num_batched_tokens` | visual token이 큰 VLM에서 prefill batch 한계 확인 |
| `max_model_len` | 불필요하게 큰 context 설정이 KV cache capacity를 줄이는지 확인 |
| `limit_mm_per_prompt` | prompt당 image 수/멀티모달 입력 제한 확인 |
| dtype / quantization | 30GB MIG에서 weight/KV cache 메모리 절감 가능성 확인 |
| eager mode / CUDA graph 관련 설정 | batch shape 변화와 graph capture 영향 확인 |
| prefix caching | OCR prompt가 반복될 때 이득이 있는지 확인 |
| chunked prefill | 긴 visual token prefill이 batch 사이 지연에 미치는 영향 확인 |
| tensor parallel / pipeline parallel | MIG 30GB 단일 인스턴스에서 적용 가능성이 낮지만 제약 확인 |

이 옵션들은 단독으로 외우지 않고 다음 매핑으로 정리한다.

```text
옵션
  -> vLLM 내부 어느 단계에 작용하는가
  -> 기대 효과
  -> 부작용
  -> 현재 환경에서 위험한 이유
  -> 실험 방법
```

---

## 10. 실험 우선순위

실험은 다음 순서로 진행한다.

### 1단계. 계측 추가

먼저 batch 사이 공백이 어디서 생기는지 확인한다. 이 단계 없이 옵션을 바꾸면 개선 원인을 설명하기 어렵다.

### 2단계. Batch size 비교

`batch_size = 4, 8, 16`을 비교한다.

측정 항목:

- 전체 문서 처리 시간
- batch별 prepare/generate/postprocess 시간
- batch 사이 공백
- GPU memory 사용량
- output token 길이와 latency 관계

### 3단계. vLLM scheduler/KV cache 관련 설정 비교

batch size 결과를 보고 `max_num_seqs`, `max_num_batched_tokens`, `max_model_len`, `gpu_memory_utilization`을 조정한다.

### 4단계. 모델 공존 구조 비교

가능하면 다음 구성을 비교한다.

```text
구성 A: Heron101 + CLIP + DeepSeekOCR V2 같은 MIG 30GB
구성 B: DeepSeekOCR V2만 단독 실행
구성 C: 프로세스 분리, GPU/MIG 분리 가능성 검토
```

구성 B가 크게 빠르다면 vLLM 옵션보다 모델 공존 구조가 더 큰 원인일 수 있다. 반대로 차이가 작다면 Heron101/CLIP 상주 비용은 낮게 보고 DeepSeekOCR V2 옵션과 batch pipeline을 우선 최적화한다.

### 5단계. 문서 특성별 batch 전략

출력 길이와 이미지 해상도 편차가 큰 경우 다음 전략을 검토한다.

- page resolution 기준 batch grouping
- 예상 OCR 출력 길이 기준 grouping
- 긴 페이지 단독 또는 작은 batch 처리
- 작은 batch를 더 자주 흘리는 방식

---

## 11. 이후 세부 Research 문서 분리 계획

조사가 진행되면 다음 문서로 분리한다.

```text
.codex/research/DeepSeekOCR/
  00_research_overview.md
  01_research_execution_plan.md
  02_vllm_serving_architecture.md
  03_vlm_ocr_inference_characteristics.md
  04_deepseekocr_v2_model_notes.md
  05_h200_mig_30gb_memory_analysis.md
  06_bottleneck_measurement_plan.md
  07_vllm_options_for_deepseekocr.md
  08_experiment_matrix.md
  09_experiment_results.md
  10_async_serving_considerations.md
  11_dependency_version_compatibility.md
  12_vllm_deepseekocr2_version_async_decision.md
```

각 문서의 역할은 다음과 같다.

| 문서 | 내용 |
| --- | --- |
| `02_vllm_serving_architecture.md` | vLLM scheduler, PagedAttention, KV cache, continuous batching 구조 |
| `03_vlm_ocr_inference_characteristics.md` | VLM/OCR에서 image token, prefill, decode가 만드는 병목 |
| `04_deepseekocr_v2_model_notes.md` | DeepSeekOCR V2 모델 카드, 입력 형식, 권장 설정, 주의사항 |
| `05_h200_mig_30gb_memory_analysis.md` | MIG 30GB에서 모델 공존, KV cache, 메모리 예산 계산 |
| `06_bottleneck_measurement_plan.md` | 실제 코드에 넣을 계측 지점과 로그 포맷 |
| `07_vllm_options_for_deepseekocr.md` | vLLM 옵션별 구조적 의미와 실험 후보 |
| `08_experiment_matrix.md` | batch/option 변경 실험 설계 |
| `09_experiment_results.md` | batch/option 변경 실험 결과와 결론 |
| `10_async_serving_considerations.md` | 동기 `LLM.generate` 구조, vLLM AsyncLLM/V1 호환성, application pipeline 개선 |
| `11_dependency_version_compatibility.md` | vLLM/Transformers 버전과 CLIP/Heron101 호환성 검토 |
| `12_vllm_deepseekocr2_version_async_decision.md` | DeepSeekOCR2 공식 지원 후보 vLLM version, async 가능성, v0.23.0 smoke test 기준 |

dtype 관련 분석은 `04`, `05`, `07`, `08`, `09`에 분산되어 있다. 읽는 흐름은 다음과 같다.

```text
04 -> DeepSeekOCR V2 품질 관점의 dtype 영향
05 -> H200 MIG 30GB 메모리 관점의 fp32/bf16 차이
07 -> vLLM 옵션 관점의 dtype 선택 기준
08 -> fp32/bf16 품질 검증 실험 설계
09 -> dtype 품질/속도 결과 기록 템플릿
```

---

## 12. 1차 결론

현재 증상만 보면 "vLLM generate 자체가 느리다"보다 "batch와 batch 사이의 준비/후처리/메모리/동기화 구간이 느리다"는 가설이 더 강하다. 세 모델이 H200 MIG 30GB 안에 같이 상주한다는 점은 확인 대상이지만, Heron101/CLIP이 작은 모델이라면 공존 자체보다 DeepSeekOCR V2의 dtype, batch size 16, visual token 수, KV cache와 scheduler 동작을 우선 확인해야 한다.

따라서 다음 작업은 바로 옵션을 바꾸는 것이 아니라, batch 단위 계측을 추가하고 vLLM 초기화 로그와 GPU 메모리 상태를 수집하는 것이다. 그 후 vLLM 구조 조사와 실제 측정 결과를 연결해 옵션 후보를 좁힌다.
