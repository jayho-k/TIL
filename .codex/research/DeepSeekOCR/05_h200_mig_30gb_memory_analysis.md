# H200 MIG 30GB Memory Analysis

> 작성일: 2026-06-20  
> 목적: H200 GPU를 사용하지만 MIG로 30GB만 할당된 환경에서 Heron101, CLIP, DeepSeekOCR V2가 동시에 상주할 때 vLLM의 메모리 예산과 병목을 해석한다. Heron101과 CLIP은 파라미터가 작은 모델이라는 전제를 두고, 실제 병목 여부는 메모리 delta와 latency 비교로 판단한다.  
> 자료 기준: 현재 대화에서 확인된 운영 구조와 `02_vllm_serving_architecture.md`, `03_vlm_ocr_inference_characteristics.md`, `04_deepseekocr_v2_model_notes.md`를 기반으로 한다. 실제 GPU 로그와 폐쇄망 코드가 없으므로 이 문서는 계산 프레임워크와 확인 방법을 제공한다.

---

## 1. 이 문서에서 답할 질문

이 문서는 다음 질문에 답한다.

- H200 전체 GPU가 아니라 MIG 30GB를 쓰는 상황에서 메모리 병목을 어떻게 봐야 하는가?
- Heron101, CLIP, DeepSeekOCR V2가 같은 MIG 안에 상주하면 vLLM의 KV cache는 실제로 얼마나 영향을 받는가?
- `gpu_memory_utilization=0.8`은 현재 구조에서 어떤 의미인가?
- batch size 16, visual token, OCR 출력 길이가 메모리 압박으로 어떻게 연결되는가?
- DeepSeekOCR 단독 실행과 세 모델 공존 실행을 어떻게 비교해야 하는가?

---

## 2. 현재 GPU 사용 구조

현재 구조는 다음과 같다.

```text
H200 physical GPU
  -> MIG partition
       -> visible GPU memory: 30GB
       -> Model Server process
            -> Heron101
            -> CLIP
            -> DeepSeekOCR V2 via vLLM
```

중요한 점은 DeepSeekOCR V2가 H200 전체 메모리를 쓰는 것이 아니라, MIG로 나뉜 30GB 안에서 다른 모델과 공존한다는 것이다. 다만 Heron101/CLIP은 작은 모델이므로, 공존 자체를 주 병목으로 확정하지 말고 실제 사용량을 측정해야 한다.

```text
30GB MIG memory
  = Heron101 상주 메모리
  + CLIP 상주 메모리
  + DeepSeekOCR V2 weight
  + vLLM runtime buffer
  + vLLM KV cache
  + CUDA context / allocator overhead
  + temporary activation
  + fragmentation / reserved memory
```

따라서 "H200이니까 충분하다"가 아니라 "30GB 안에서 DeepSeekOCR V2와 KV cache가 먼저 충분한 예산을 확보하는가"로 봐야 한다. Heron101/CLIP은 작은 모델이므로 별도 항목으로 측정하되, 1차 최적화 축은 DeepSeekOCR V2의 dtype, visual token, batch size, output 길이다.

---

## 3. vLLM 메모리 사용을 나누는 방식

vLLM 메모리는 크게 네 영역으로 나눠 본다.

```text
vLLM memory
  -> model weights
  -> non-KV runtime memory
  -> KV cache blocks
  -> temporary buffers
```

각 영역의 의미는 다음과 같다.

| 영역 | 설명 | 최적화 영향 |
| --- | --- | --- |
| model weights | DeepSeekOCR V2 모델 파라미터 | dtype, quantization, 모델 크기 |
| non-KV runtime memory | CUDA context, graph, workspace, allocator reserved memory | 프로세스 구조, eager/CUDA graph |
| KV cache blocks | prompt/output token의 K/V 저장 공간 | `gpu_memory_utilization`, `max_model_len`, batch, output length |
| temporary buffers | prefill/decode 중 임시 activation과 연산 buffer | batch size, visual token, kernel 선택 |

vLLM은 초기화 시 GPU 메모리를 프로파일링하고, 남는 공간 일부를 KV cache block으로 잡는다. 이때 이미 Heron101과 CLIP이 올라가 있으면 vLLM이 보는 free memory 자체가 줄어든다. 다만 두 모델의 파라미터가 작다면 감소폭은 크지 않을 수 있으므로, 로드 전후 free memory와 KV cache block 수를 함께 봐야 한다.

---

## 4. `gpu_memory_utilization=0.8` 해석

현재 DeepSeekOCR V2의 vLLM 설정은 `gpu_memory_utilization=0.8`이다.

이 값은 단순히 다음처럼 해석하면 위험하다.

```text
잘못된 해석:
  DeepSeekOCR V2가 30GB의 80% = 24GB만 사용한다.
```

더 실용적인 해석은 다음에 가깝다.

```text
실용적 해석:
  vLLM이 초기화 시점에 확인한 GPU 메모리 상황에서
  model weight와 non-KV 메모리를 제외하고,
  실행 중 사용할 메모리 예산을 얼마나 적극적으로 잡을지 결정한다.
```

현재 구조에서는 다음 순서가 중요하다.

```text
1. Heron101 load
2. CLIP load
3. DeepSeekOCR V2 vLLM load
4. vLLM memory profiling
5. KV cache block 수 결정
```

만약 Heron101과 CLIP이 먼저 GPU 메모리를 점유하면, vLLM은 그만큼 줄어든 free memory에서 KV cache를 잡게 된다. 작은 모델이라면 이 차이가 작을 수 있고, 그 경우 로드 순서보다 DeepSeekOCR V2의 KV cache 요구량이 더 중요한 변수다.

반대로 DeepSeekOCR V2를 먼저 로드하고 vLLM이 메모리를 크게 예약하면, 이후 Heron101/CLIP 로드가 불안정해질 수 있다. 로드 순서도 확인 대상이다.

---

## 5. 왜 KV Cache가 중요한가

OCR/VLM에서 KV cache 길이는 단순히 출력 token 수만이 아니다.

```text
KV cache length per sequence
  = visual tokens
  + text prompt tokens
  + generated OCR tokens
```

batch size 16이면 동시에 다음 메모리를 요구할 수 있다.

```text
batch size 16
  -> sequence 1 KV cache
  -> sequence 2 KV cache
  ...
  -> sequence 16 KV cache
```

한 페이지가 dense 문서라면 output token이 길어지고, 고해상도 페이지라면 visual token이 커질 수 있다.

```text
high resolution page
  -> visual tokens 증가
  -> prefill 메모리 증가
  -> KV cache 길이 증가 가능

dense text page
  -> generated OCR tokens 증가
  -> decode 시간 증가
  -> KV cache 길이 증가
```

따라서 batch size 16은 GPU 메모리를 크게 압박할 수 있다. 특히 DeepSeekOCR V2의 visual token과 OCR 출력 길이가 크면 KV cache block 여유가 작아진다. Heron101/CLIP 공존은 보조 변수로 보고 실제 delta가 클 때만 주요 원인으로 올린다.

---

## 6. Float32에서 BFloat16으로 바꿨을 때 메모리 효과

현재 관찰상 `float32` 사용 시 100페이지 이상 PDF 처리 시간이 약 300초였고, `bfloat16`으로 변경한 뒤 확실히 빨라졌다. 메모리 관점에서 이는 자연스러운 결과다.

dtype별 대략적인 element 크기는 다음이다.

| dtype | element size | 의미 |
| --- | --- | --- |
| `float32` | 4 bytes | 메모리 사용량과 bandwidth 부담이 큼 |
| `float16` | 2 bytes | 메모리는 작지만 exponent 범위가 좁음 |
| `bfloat16` | 2 bytes | fp16처럼 2 bytes지만 exponent 범위가 fp32와 유사 |

vLLM/VLM 추론에서 dtype은 다음 영역에 영향을 준다.

```text
model weights
  -> fp32 대비 bf16은 대략 절반

activation / temporary buffers
  -> 연산 중 임시 메모리 감소

KV cache
  -> cache dtype이 bf16이면 fp32 대비 대략 절반

memory bandwidth
  -> GPU가 읽고 쓰는 byte 수 감소
```

H200 MIG 30GB 환경에서는 이 효과가 더 크게 체감될 수 있다.

```text
30GB MIG
  -> Heron101 + CLIP + DeepSeekOCR V2 공존
  -> fp32는 weight/activation/KV cache가 모두 무거움
  -> bf16은 같은 30GB 안에서 KV cache와 temporary buffer 여유를 늘림
```

속도 개선의 가능한 원인은 다음이다.

| 원인 | 설명 |
| --- | --- |
| weight memory 감소 | 모델 상주 후 free memory 증가 |
| KV cache 여유 증가 | 같은 batch size에서 scheduler가 덜 압박받음 |
| memory bandwidth 절감 | prefill/decode 중 HBM 이동량 감소 |
| Tensor Core 경로 | H200에서 bf16 연산이 fp32보다 유리할 수 있음 |
| allocator 압박 감소 | batch 사이 memory pressure와 reserved memory 부담 완화 |

따라서 `float32 -> bfloat16` 개선은 단순히 "자료형 크기가 줄었다"가 아니라, 30GB MIG 안에서 vLLM이 사용할 수 있는 실행 공간과 KV cache 여유가 늘어난 결과로 해석해야 한다.

---

## 7. 메모리 예산을 계산하는 방법

정확한 계산은 모델 구조와 실제 로그가 필요하다. 하지만 조사에서는 다음 방식으로 예산을 분해한다.

```text
M_total = 30GB

M_available_for_vllm
  = M_total
  - M_heron101
  - M_clip
  - M_cuda_context_shared
  - M_other_process

M_vllm_runtime
  = M_deepseekocr_weights
  + M_non_kv
  + M_kv_cache
  + M_temp
```

실제 확인할 값은 다음이다.

| 시점 | 측정할 값 |
| --- | --- |
| 프로세스 시작 전 | MIG free memory |
| Heron101 로드 후 | allocated/reserved/free |
| CLIP 로드 후 | allocated/reserved/free |
| DeepSeekOCR V2 vLLM 초기화 후 | allocated/reserved/free, KV cache block 수 |
| batch 처리 중 peak | allocated/reserved/free, GPU utilization |
| batch 처리 후 | memory 회수 여부 |

가능하면 PyTorch 기준과 NVML 기준을 같이 본다.

```text
PyTorch allocated
  -> tensor가 실제 사용 중인 메모리

PyTorch reserved
  -> caching allocator가 잡아둔 메모리

NVML used/free
  -> 프로세스 전체와 CUDA context를 포함한 GPU 관점 메모리
```

vLLM은 PyTorch allocator 외부 또는 별도 방식으로 메모리를 관리할 수 있으므로, 한 지표만 보면 안 된다.

---

## 8. Batch Size 16이 메모리에 주는 압력

batch size를 늘리면 GPU 사용률이 올라갈 수 있지만, VLM/OCR에서는 다음 비용이 같이 증가한다.

```text
batch size 증가
  -> 동시 sequence 수 증가
  -> visual token 총량 증가
  -> prefill temporary memory 증가
  -> KV cache block 점유 증가
  -> 긴 output page가 섞일 확률 증가
```

현재 batch size 16과 `max_num_seqs=16`이 맞춰져 있다면, vLLM 입장에서는 최대 16개 sequence를 동시에 처리할 수 있게 허용한 것이다.

하지만 실제 병목은 sequence 개수가 아니라 token 총량일 수 있다.

```text
문제 없는 경우:
  16 sequences x 작은 visual tokens x 짧은 output

문제 되는 경우:
  16 sequences x 큰 visual tokens x 긴 output
```

따라서 batch 실험은 다음 식으로 해석한다.

```text
batch size 4
  -> KV cache 압박 낮음
  -> tail latency 낮을 가능성
  -> GPU utilization이 낮을 수 있음

batch size 8
  -> 중간 후보
  -> 30GB MIG에서 현실적인 균형점일 가능성

batch size 16
  -> throughput 후보
  -> visual token/output 길이가 크면 memory와 tail latency 위험
```

---

## 9. 세 모델 공존의 영향

Heron101, CLIP, DeepSeekOCR V2가 같은 MIG에 상주하면 두 가지 영향이 있다. 단, Heron101/CLIP은 파라미터가 작은 모델이므로 아래 영향은 가능성으로 두고 측정 결과로 우선순위를 정한다.

### 8.1 메모리 상주 비용

각 모델의 weights와 runtime buffer가 계속 GPU 메모리를 차지한다. 작은 모델이라면 weights보다 CUDA context, allocator reserved memory, temporary buffer가 더 의미 있는 차이를 만들 수 있다.

```text
free memory 감소
  -> vLLM KV cache block 수 감소
  -> 동시 sequence/token 수 감소
  -> batch size 16 안정성 하락
```

### 8.2 실행 자원 경합

같은 GPU에서 여러 모델이 번갈아 실행되면 compute, memory bandwidth, kernel launch가 경합할 수 있다.

```text
Heron101 실행
  -> CLIP 실행
  -> DeepSeekOCR 실행
  -> batch 후처리
```

만약 한 request 안에서 Heron101/CLIP/DeepSeekOCR가 순차 실행된다면 동시 kernel 경합은 작을 수 있고, Heron101/CLIP이 작은 모델이라면 메모리 상주 비용도 제한적일 수 있다. 반대로 request concurrency가 높아서 여러 endpoint 요청이 겹치면 작은 모델이라도 kernel launch, memory bandwidth, allocator 동기화 영향이 커질 수 있다.

---

## 10. 로드 순서와 프로세스 구조

로드 순서는 vLLM memory profiling에 영향을 줄 수 있다.

```text
Case A
  Heron101 load
  CLIP load
  vLLM load
  -> vLLM은 남은 메모리 기준으로 KV cache를 잡음

Case B
  vLLM load
  Heron101 load
  CLIP load
  -> vLLM이 먼저 메모리를 많이 예약하면 이후 모델 로드가 불안정할 수 있음
```

현재 사용자는 FastAPI 시작 시 `deepseekocrv2.py`의 `load()`가 한 번 호출된다고 설명했다. 다만 Heron101, CLIP, DeepSeekOCR V2의 정확한 로드 순서는 별도로 확인해야 한다.

프로세스 구조도 중요하다.

```text
single process
  -> 모델 간 Python 메모리와 CUDA context 공유 가능
  -> 통합은 쉬움
  -> 한 프로세스 안에서 메모리 사용 추적이 복잡

multi process
  -> 모델별 격리 쉬움
  -> 프로세스마다 CUDA context overhead 발생
  -> 같은 MIG를 공유하면 총 메모리는 더 부족할 수 있음

separate MIG/GPU
  -> 성능 격리 가장 좋음
  -> 자원 배치 변경 필요
```

현재 30GB 하나만 주어진다면, 우선은 single process 안에서 batch와 vLLM memory 옵션을 조정하는 것이 현실적이다. 그러나 DeepSeekOCR 단독 실행과의 비교는 반드시 필요하다. 단독/공존 차이가 작다면 Heron101/CLIP 분리보다 DeepSeekOCR V2 옵션 조정이 더 높은 우선순위다.

---

## 11. DeepSeekOCR 단독 실행 비교가 중요한 이유

성능 문제의 원인이 vLLM 옵션인지, 모델 공존 구조인지 구분하려면 DeepSeekOCR 단독 기준선이 필요하다.

```text
Baseline A: 현재 구조
  Heron101 + CLIP + DeepSeekOCR V2

Baseline B: DeepSeekOCR V2만 로드
  Heron101/CLIP 미로드
```

비교할 지표는 다음이다.

| 지표 | 해석 |
| --- | --- |
| vLLM KV cache block 수 | 단독 실행에서 크게 늘면 메모리 공존 영향이 큼 |
| batch 16 성공 여부 | 공존 구조에서만 불안정하면 메모리 압박 가능성 |
| batch 사이 공백 | 단독에서 줄면 다른 모델 상주/후처리 영향 가능 |
| generate time | 단독에서 줄면 GPU 자원 경합 또는 KV 여유 영향 가능 |
| peak memory | batch 크기별 위험 구간 확인 |

단독 실행이 어렵다면 최소한 Heron101/CLIP을 로드한 상태와 로드하지 않은 상태의 vLLM 초기화 로그만 비교해도 의미가 있다. 두 모델이 작은 만큼, 이 비교에서 차이가 작으면 공존 구조는 후순위로 내린다.

---

## 12. `gpu_memory_utilization` 조정 방향

`gpu_memory_utilization`은 높다고 항상 빠르지 않고, 낮다고 항상 느리지 않다.

```text
값을 높임
  -> KV cache block 증가 가능
  -> 더 긴 sequence/더 많은 batch 수용 가능
  -> 다른 모델/temporary buffer와 충돌하면 OOM 위험

값을 낮춤
  -> KV cache block 감소
  -> 동시 처리량 감소 가능
  -> 메모리 안정성 증가
  -> batch 전환 시 OOM/fragmentation 위험 감소 가능
```

현재처럼 세 모델이 30GB 안에 같이 있으면 `0.8`이 공격적일 수도 있고, 반대로 이미 free memory가 작아 KV cache가 부족할 수도 있다. 다만 Heron101/CLIP이 작은 모델이면 이 판단은 대부분 DeepSeekOCR V2의 weight dtype, visual token, output length, batch size에 의해 결정될 가능성이 높다. 실제 판단은 초기화 로그와 batch 중 peak memory로 해야 한다.

실험 후보는 다음과 같다.

```text
gpu_memory_utilization: 0.6, 0.7, 0.8
batch size: 4, 8, 16
```

먼저 모든 조합을 돌리기보다 다음 순서가 낫다.

```text
1. 현재값 0.8 + batch 16 계측
2. 0.8 + batch 8 비교
3. 0.8 + batch 4 비교
4. 가장 안정적인 batch에서 0.7 비교
5. OOM 또는 memory warning이 있으면 0.6 비교
```

---

## 13. 메모리 관점 계측 포맷

batch마다 다음 로그를 남긴다.

```text
[memory]
stage=request_start
gpu_used_mb=
gpu_free_mb=
torch_allocated_mb=
torch_reserved_mb=

[memory]
stage=batch_003_prepare_start
batch_size=16
image_pixels_total=
gpu_used_mb=
gpu_free_mb=
torch_allocated_mb=
torch_reserved_mb=

[memory]
stage=batch_003_generate_done
output_chars_total=
gpu_used_mb=
gpu_free_mb=
torch_allocated_mb=
torch_reserved_mb=
```

함께 남기면 좋은 vLLM 초기화 정보는 다음이다.

```text
vllm_version
model_path
dtype
gpu_memory_utilization
max_model_len
max_num_seqs
max_num_batched_tokens
kv_cache_blocks
maximum_concurrency
```

`kv_cache_blocks`와 `maximum_concurrency`는 vLLM 로그 표현이 버전에 따라 다를 수 있으므로, 실제 로그에서 대응되는 문구를 찾아 기록한다.

---

## 14. 현재 단계의 판단

현재 구조에서 가장 중요한 판단은 다음이다.

```text
DeepSeekOCR V2 최적화는 모델 옵션만의 문제가 아니다.
30GB MIG 안에서 세 모델이 상주하므로
vLLM KV cache 예산이 줄어들 수 있다.
다만 Heron101/CLIP은 작은 모델이므로
DeepSeekOCR V2의 dtype, visual token, output length, batch size가
batch size 16의 안정성과 효율을 흔드는 더 큰 변수일 가능성이 높다.
```

따라서 우선순위는 다음이다.

```text
1. 현재 구조에서 vLLM 초기화 로그와 KV cache capacity 확인
2. fp32와 bf16의 memory peak, KV cache capacity, total time 차이 확인
3. batch 16의 prepare/generate/postprocess 시간과 memory peak 확인
4. batch 8, batch 4와 비교
5. DeepSeekOCR 단독 기준선과 비교
6. 그 후 gpu_memory_utilization과 max token 관련 옵션 조정
```

메모리 관점에서는 batch size를 낮추는 것이 단순히 throughput을 포기하는 선택이 아닐 수 있다. batch 16이 KV cache와 tail latency를 과하게 만들고 있다면, batch 8이 전체 100페이지 처리 시간에서는 더 빠를 수 있다.

---

## 15. 다음 문서로 넘길 질문

다음 문서는 `06_bottleneck_measurement_plan.md`다. 여기서는 실제 코드에 어떤 timing log와 memory log를 넣어야 "progress bar 사이 공백"의 원인을 분리할 수 있는지 정리한다.

다음 질문을 다룬다.

- FastAPI endpoint 기준으로 어떤 timestamp를 남겨야 하는가?
- batch prepare/generate/postprocess를 어떻게 나눠야 하는가?
- GPU memory snapshot은 어느 시점에 찍어야 하는가?
- output length와 image resolution을 어떤 형식으로 기록해야 하는가?
- 폐쇄망 사내 PC에서 실행 가능한 최소 계측 코드 형태는 무엇인가?
