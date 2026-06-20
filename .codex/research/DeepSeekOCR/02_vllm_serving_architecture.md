# vLLM Serving Architecture

> 작성일: 2026-06-20  
> 목적: DeepSeekOCR V2 최적화를 위해 vLLM이 모델을 어떻게 서빙하는지 구조적으로 정리한다.  
> 자료 기준: 현재 저장소의 `AI/vllM/` 로컬 노트와 일반 vLLM 구조 지식을 기반으로 한 1차 정리다. 버전별 세부 동작과 옵션 기본값은 이후 공식 문서 또는 실제 설치 버전에서 확인해야 한다.

---

## 1. 이 문서에서 답할 질문

이 문서는 다음 질문에 답하기 위한 기초 문서다.

- vLLM은 Transformers 직접 추론과 비교해 어떤 구조로 빠르게 동작하는가?
- `PagedAttention`, `KV cache`, `continuous batching`은 각각 어느 병목을 줄이는가?
- Python 코드에서 vLLM 객체를 직접 호출할 때 batch는 어떻게 해석해야 하는가?
- DeepSeekOCR V2 같은 VLM/OCR 모델에서 어떤 단계가 느려질 수 있는가?
- 현재 "progress bar는 빠른데 다음 progress bar까지 오래 걸리는 현상"을 vLLM 구조상 어디에 매핑할 수 있는가?

---

## 2. vLLM 처리 흐름 요약

vLLM을 단순히 "빠른 generate 함수"로 보면 옵션 최적화가 어렵다. 내부적으로는 request를 sequence 단위로 관리하고, prefill/decode를 scheduler가 GPU 자원과 KV cache 상황에 맞춰 실행한다.

일반적인 흐름은 다음과 같이 볼 수 있다.

```text
Application
  -> vLLM LLM.generate(...)
  -> input validation / prompt processing
  -> request 또는 sequence 등록
  -> scheduler
       -> prefill 대상 선택
       -> decode 대상 선택
       -> KV cache block 할당/해제
  -> model executor
       -> attention / MLP 연산
       -> PagedAttention으로 KV cache 참조
  -> sampler
  -> output assembly
  -> Application으로 결과 반환
```

DeepSeekOCR V2 같은 VLM/OCR에서는 이 앞뒤에 multimodal 처리가 붙는다.

```text
Image input
  -> image preprocessing / processor
  -> visual token 또는 image embedding 생성
  -> text prompt와 결합
  -> vLLM prefill
  -> vLLM decode
  -> OCR text output
```

따라서 vLLM 내부 generate가 빠르더라도, generate 호출 전후의 image 처리나 output 처리에서 시간이 길어질 수 있다.

---

## 3. Prefill과 Decode

LLM/VLM 추론은 크게 prefill과 decode로 나뉜다.

```text
Prefill
  -> 입력 prompt 전체를 한 번에 처리
  -> 각 token의 K/V를 계산해 KV cache에 저장
  -> prompt가 길수록 비용 증가

Decode
  -> 다음 token을 1개씩 생성
  -> 새 token의 K/V를 KV cache에 추가
  -> 출력 token 수가 길수록 비용 증가
```

텍스트 LLM에서는 prompt token 수와 output token 수가 주로 중요하다. VLM/OCR에서는 이미지가 visual token으로 확장되기 때문에 prefill 비용이 더 커질 수 있다.

```text
1 page image
  -> visual tokens N개
  -> OCR instruction prompt tokens M개
  -> prefill length = N + M
```

batch size 16은 다음 의미가 된다.

```text
16 page images
  -> 각 page마다 visual tokens 생성
  -> 16개 sequence의 prefill을 scheduler가 처리
  -> 각 sequence의 output OCR text를 decode
```

즉 batch size 16은 텍스트 16문장 처리보다 훨씬 무거울 수 있다.

---

## 4. KV Cache

Autoregressive decode에서는 매 token 생성마다 이전 token 전체에 attention을 해야 한다. 매번 이전 token의 key/value를 다시 계산하면 비효율적이므로, vLLM은 이전 token의 K/V를 GPU 메모리에 저장한다.

```text
Token 1 prefill
  -> K1, V1 저장

Token 2 decode
  -> K1, V1 재사용
  -> K2, V2 저장

Token 3 decode
  -> K1, V1, K2, V2 재사용
  -> K3, V3 저장
```

KV cache 크기에 영향을 주는 요소는 다음이다.

| 요소 | 영향 |
| --- | --- |
| layer 수 | layer가 많을수록 K/V 저장량 증가 |
| hidden size / head dim | 각 token의 K/V 크기 증가 |
| KV head 수 | MHA, MQA, GQA 구조에 따라 달라짐 |
| dtype | fp16/bf16보다 낮은 정밀도면 메모리 감소 가능 |
| sequence 길이 | prompt + output token이 길수록 증가 |
| 동시 sequence 수 | batch/concurrency가 높을수록 증가 |

현재 환경에서는 Heron101, CLIP, DeepSeekOCR V2가 같은 30GB MIG에 상주한다. 따라서 vLLM이 KV cache로 사용할 수 있는 메모리는 DeepSeekOCR V2 단독 실행보다 작을 수 있다. 다만 Heron101과 CLIP은 파라미터가 작은 모델이므로, 실제 차이는 로드 전후 free memory와 vLLM 초기화 로그로 확인해야 한다.

---

## 5. PagedAttention

기존 방식은 sequence마다 KV cache를 연속된 큰 메모리 공간에 잡는 경향이 있다. 이 경우 sequence 길이가 제각각이면 메모리 파편화와 낭비가 커진다.

vLLM의 PagedAttention은 KV cache를 고정 크기 block 단위로 나눠 관리한다.

```text
Logical sequence tokens
  token 0..15    -> logical block 0
  token 16..31   -> logical block 1
  token 32..47   -> logical block 2

Block table
  logical block 0 -> physical block 103
  logical block 1 -> physical block 027
  logical block 2 -> physical block 411
```

핵심은 sequence 입장에서는 연속된 token처럼 보이지만, 실제 GPU 메모리에서는 block table을 통해 흩어진 physical block을 참조할 수 있다는 점이다.

효과는 다음과 같다.

- sequence별 최대 길이를 미리 크게 잡아두는 낭비를 줄인다.
- 완료된 sequence의 block을 회수해서 다른 sequence에 재사용할 수 있다.
- 길이가 다른 sequence가 섞여도 메모리 파편화를 줄인다.
- 같은 prompt에서 여러 output을 생성하는 경우 일부 block 공유가 가능하다.

DeepSeekOCR에서는 page별 OCR 출력 길이가 다르므로 PagedAttention의 이점이 있다. 하지만 30GB MIG에서 여러 모델이 같이 상주하면 block 관리가 좋아도 전체 block 수 자체가 부족할 수 있다. Heron101/CLIP이 작은 모델이라면 이 영향은 제한적일 수 있으므로, block 수 변화가 작으면 DeepSeekOCR V2의 입력/출력 길이와 batch 설정을 더 우선해서 본다.

---

## 6. Continuous Batching

정적 batch 방식에서는 batch 안의 모든 sequence가 끝날 때까지 다음 batch로 넘어가기 어렵다.

```text
Static batch
  batch A: seq1 short, seq2 short, seq3 very long
  -> seq1/seq2가 끝나도 seq3가 끝날 때까지 batch 자원 회수 지연
```

vLLM은 continuous batching으로 실행 중인 sequence가 끝나면 새 sequence를 scheduler에 넣을 수 있다.

```text
Time 0: seq1, seq2, seq3 실행
Time 1: seq1 완료 -> seq4 투입
Time 2: seq2 완료 -> seq5 투입
Time 3: seq3 완료 -> seq6 투입
```

이 구조는 API server처럼 여러 request가 계속 들어오는 환경에서 특히 효과가 크다.

다만 현재 구조는 FastAPI endpoint 안에서 이미지를 16개씩 잘라 Python loop로 `generate`를 호출하는 형태로 보인다.

```text
for batch in chunks(images, 16):
    outputs = llm.generate(batch)
```

이 경우 vLLM 내부 continuous batching의 장점을 얼마나 활용하는지는 코드 구조에 따라 달라진다. 한 번의 `generate(batch)`가 끝나고 다음 batch를 호출하는 동기 루프라면, vLLM은 batch 사이 공백을 자동으로 없애지 못한다.

추가 확인 사항은 vLLM 비동기 엔진 사용 가능성이다. vLLM 자체에는 `AsyncLLM`/`AsyncLLMEngine` 경로가 있지만, DeepSeek-OCR-2 공개 vLLM 예제는 `VLLM_USE_V1=0`과 동기 `LLM.generate()`를 사용한다. 따라서 DeepSeekOCR V2에서 V1 async path를 바로 쓸 수 있다고 가정하지 말고, `10_async_serving_considerations.md`의 smoke test로 호환성을 먼저 확인한다.

즉 현재 관찰된 "다음 progress bar가 늦게 생김"은 다음과 같이 해석할 수 있다.

```text
batch_i generate 완료
  -> Python으로 결과 반환
  -> 후처리
  -> 다음 batch 입력 준비
  -> llm.generate(batch_i+1) 호출
  -> progress bar 생성
```

이 공백은 vLLM scheduler 내부보다 application loop 경계에서 생길 수 있다.

---

## 7. Scheduler와 주요 제한값

vLLM scheduler는 제한된 GPU memory와 compute 안에서 어떤 sequence를 prefill/decode할지 결정한다. 이때 중요한 제한값은 다음이다.

| 설정/개념 | 의미 |
| --- | --- |
| `max_num_seqs` | 동시에 처리할 sequence 수 상한 |
| `max_num_batched_tokens` | 한 scheduler step에서 처리할 token 수 상한 |
| `max_model_len` | sequence가 가질 수 있는 최대 길이 |
| KV cache block 수 | 실제로 수용 가능한 token cache capacity |
| `gpu_memory_utilization` | vLLM이 GPU 메모리를 얼마나 적극적으로 사용할지 결정하는 값 |

VLM/OCR에서는 `max_num_seqs=16`만 보면 부족하다. 각 sequence가 visual token을 많이 만들면 `max_num_batched_tokens` 또는 KV cache capacity가 먼저 병목이 될 수 있다.

```text
Case A: text prompt 16개
  -> sequence 수는 16
  -> token 수는 작음

Case B: page image 16개
  -> sequence 수는 16
  -> visual token 때문에 token 수가 큼
```

따라서 batch size와 `max_num_seqs`를 16으로 맞추는 것이 항상 최적은 아니다. **오히려 4 또는 8이 더 안정적으로 빠를 수 있다.**

---

## 8. CUDA Graph

CUDA graph는 반복되는 GPU 연산 실행 절차를 미리 capture해서 CPU와 GPU 사이의 launch overhead를 줄이는 기법이다.

```text
Without CUDA graph
  CPU launches kernel A
  CPU launches kernel B
  CPU launches kernel C
  ...

With CUDA graph
  CPU launches captured graph once
  GPU executes known sequence
```

decode처럼 반복적이고 shape가 안정적인 단계에서는 이득이 있다. 반면 VLM/OCR처럼 image 크기, visual token 수, output 길이가 크게 달라지면 capture 가능한 shape가 제한되거나 fallback이 생길 수 있다.

현재 조사에서는 CUDA graph 자체를 먼저 튜닝하기보다 다음을 확인하는 정도가 적절하다.

- vLLM 로그에 CUDA graph capture 관련 시간이 있는가?
- batch shape가 계속 달라져 capture 이득이 줄어드는가?
- eager mode를 켰을 때 latency가 바뀌는가?

---

## 9. Python Direct Call 구조에서의 의미

현재 DeepSeekOCR V2는 OpenAI-compatible server가 아니라 FastAPI 서버 내부 Python 코드에서 vLLM 객체를 직접 호출한다.

이 방식의 장점은 다음이다.

- 기존 FastAPI pipeline에 통합하기 쉽다.
- Heron101, CLIP, DeepSeekOCR의 결과를 한 request 안에서 조합하기 쉽다.
- 별도 vLLM server process와 HTTP hop이 없다.

하지만 성능 관점에서는 다음을 주의해야 한다.

- application batch loop가 vLLM continuous batching의 이점을 제한할 수 있다.
- 같은 프로세스/같은 MIG에 여러 모델이 상주해 vLLM memory profiling이 불리해질 수 있다.
- Heron101/CLIP은 작은 모델이므로, 공존 영향은 weight memory보다 CUDA context, reserved memory, 동시 request 실행에서 나타날 가능성이 더 크다.
- output 후처리와 다음 batch 준비가 동기적으로 이어지면 GPU가 놀 수 있다.
- FastAPI worker/concurrency 설정에 따라 같은 vLLM 객체에 요청이 겹칠 수 있다.

현재 구조에서 확인해야 할 핵심은 다음이다.

```text
Does GPU work continuously?
  yes -> vLLM internal compute/KV/scheduler bottleneck likely
  no  -> Python loop, preprocessing, postprocessing, synchronization bottleneck likely
```

---

## 10. 현재 증상과 구조 매핑

관찰:

```text
image prompt progress bar는 빠르게 진행된다.
하지만 다음 16개 progress bar가 생기기까지 오래 걸린다.
```

가능한 구조적 해석:

```text
batch_i prepare
  -> 빠름 또는 미측정
batch_i generate
  -> progress bar 표시, 비교적 빠름
batch_i postprocess
  -> 느릴 수 있음
batch_i+1 prepare
  -> 느릴 수 있음
batch_i+1 generate 시작
  -> 다음 progress bar 표시
```

이 경우 vLLM 옵션만 바꿔서는 충분히 개선되지 않을 수 있다. 먼저 timing을 다음처럼 쪼개야 한다.

```text
prepare_start
prepare_done
generate_start
generate_done
postprocess_done
next_batch_start
```

만약 `generate_done -> next_batch_generate_start`가 길다면, vLLM 내부보다 application boundary 문제가 크다.

반대로 `generate_start -> generate_done`이 길고 progress bar가 실제 전체 시간을 반영하지 못한다면, prefill/decode/KV cache 병목을 더 봐야 한다.

---

## 11. 최적화와 연결되는 지점

vLLM 구조를 기준으로 옵션과 최적화 방향은 다음처럼 연결된다.

| 병목 | 관련 구조 | 볼 옵션/전략 |
| --- | --- | --- |
| GPU 메모리 부족 | KV cache block 수 | `gpu_memory_utilization`, `max_model_len`, dtype, quantization |
| batch 16이 무거움 | scheduler, prefill | batch size, `max_num_seqs`, `max_num_batched_tokens` |
| image token이 큼 | multimodal prefill | image resolution, crop/tiling, multimodal limit |
| 긴 OCR 출력 | decode, KV cache 증가 | `max_tokens`, page grouping, output length logging |
| batch 사이 공백 | Python loop boundary | prepare/postprocess timing, async/pipeline 구조 |
| 다중 모델 공존 | memory profiling, GPU contention | 작은 모델이면 영향이 제한적일 수 있으므로 로드 전후 free memory와 단독/공존 latency 비교 |

---

## 12. 확인이 필요한 로그/코드

다음 항목은 실제 서버 코드와 로그에서 확인해야 한다.

- `deepseekocrv2.py`의 `load()`에서 vLLM `LLM(...)` 생성 옵션
- batch loop 구현 위치와 `generate` 호출 방식
- image processor가 batch loop 안에서 매번 수행되는지 여부
- output 후처리 로직
- `torch.cuda.synchronize()`, `.cpu()`, `.numpy()`, `.item()` 같은 암묵적 동기화 가능 지점
- FastAPI worker 수와 request concurrency
- DeepSeekOCR V2가 vLLM V1 `AsyncLLM` 또는 기존 `AsyncLLMEngine` 경로에서 로드되는지 여부
- vLLM 초기화 로그의 KV cache block 수
- batch 실행 중 GPU utilization과 memory 변화

---

## 13. 다음 문서로 넘길 질문

다음 문서는 `03_vlm_ocr_inference_characteristics.md`로 작성한다. 여기서는 vLLM 일반 구조가 아니라 DeepSeekOCR V2 같은 VLM/OCR에서 왜 image prompt, visual token, page resolution, OCR output length가 병목을 만드는지 정리한다.

특히 다음 질문을 다룬다.

- `image prompt` progress bar는 정확히 어떤 단계를 의미하는가?
- page image 1장이 token/embedding 관점에서 얼마나 무거운 입력이 되는가?
- OCR 출력 길이 편차가 batch 16 latency를 어떻게 흔드는가?
- 문서 해상도와 page grouping이 성능에 어떤 영향을 줄 수 있는가?
