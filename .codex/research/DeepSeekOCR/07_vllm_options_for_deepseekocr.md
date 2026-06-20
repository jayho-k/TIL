# vLLM Options for DeepSeekOCR

> 작성일: 2026-06-20  
> 목적: DeepSeekOCR V2를 vLLM으로 실행할 때 주요 옵션이 어떤 내부 구조와 병목에 연결되는지 정리한다.  
> 자료 기준: 현재 research 문서 `02`~`06`의 구조 분석을 기반으로 한다. vLLM 옵션 이름, 기본값, 지원 여부는 설치 버전에 따라 달라질 수 있으므로 폐쇄망 서버의 실제 vLLM 버전에서 최종 확인해야 한다.

---

## 1. 이 문서에서 답할 질문

이 문서는 다음 질문에 답한다.

- `gpu_memory_utilization`은 언제 올리고 언제 내려야 하는가?
- `max_num_seqs`와 application batch size는 어떻게 다르게 봐야 하는가?
- `max_num_batched_tokens`는 VLM/OCR에서 왜 중요한가?
- `max_model_len`은 KV cache capacity에 어떤 영향을 주는가?
- `max_tokens` 계열 generation 설정은 OCR latency와 어떻게 연결되는가?
- prefix caching, chunked prefill, dtype/quantization은 어떤 조건에서 도움이 되는가?
- 현재 H200 MIG 30GB + 세 모델 공존 구조에서는 어떤 순서로 옵션을 실험해야 하는가?

---

## 2. 옵션을 보기 전에 필요한 전제

vLLM 옵션을 바로 바꾸기 전에, 먼저 병목 위치를 알아야 한다.

```text
generate 내부가 느림
  -> vLLM scheduler, prefill, decode, KV cache, batch size 관련 옵션

generate 전후가 느림
  -> image processor, prompt 구성, output parsing, Python loop 구조

memory free가 낮을 때 느림
  -> MIG 30GB, 모델 공존, KV cache capacity, gpu_memory_utilization

긴 output page가 느림
  -> max_tokens, stop condition, batch grouping
```

따라서 옵션 실험은 `06_bottleneck_measurement_plan.md`의 계측 결과와 함께 진행해야 한다. 계측 없이 옵션만 바꾸면 개선 원인을 설명하기 어렵다.

---

## 3. 옵션과 병목 매핑 요약

| 옵션/전략 | 주로 작용하는 병목 | 기대 효과 | 위험 |
| --- | --- | --- | --- |
| `gpu_memory_utilization` | KV cache capacity, memory pressure | KV cache block 수 조정 | 너무 높으면 OOM, 너무 낮으면 동시 처리량 감소 |
| `max_num_seqs` | 동시 sequence 수 | batch/concurrency 제어 | VLM에서는 token 총량을 못 보면 위험 |
| `max_num_batched_tokens` | scheduler step의 token 총량 | visual token이 큰 batch 제어 | 너무 낮으면 throughput 감소 |
| `max_model_len` | 최대 context 길이, KV cache capacity | 불필요한 cache 예산 감소 | 너무 낮으면 긴 OCR 출력 잘림 |
| `max_tokens` / `max_new_tokens` | decode 길이 | 긴 출력 tail latency 제한 | 너무 낮으면 OCR 누락 |
| dtype | weight/KV/compute memory | 메모리 절감, 속도 변화 | 품질/지원 여부 확인 필요 |
| quantization | weight memory | 모델 상주 메모리 절감 | VLM 지원/품질/속도 확인 필요 |
| prefix caching | 반복 prompt | 공통 text prompt 비용 감소 가능 | image가 다르면 이득 제한 |
| chunked prefill | 긴 prompt/visual token | 긴 prefill을 나눠 처리 | 버전/모델 지원 확인 필요 |
| eager/CUDA graph 관련 | kernel launch overhead | 반복 shape에서 속도 개선 가능 | shape 변동 크면 이득 제한 |

---

## 4. `gpu_memory_utilization`

현재 값은 `0.8`이다.

이 옵션은 단순히 "GPU 30GB의 80%를 쓴다"가 아니라, vLLM이 초기 메모리 프로파일링 후 사용할 메모리 예산을 얼마나 적극적으로 잡을지와 관련된다.

현재 구조에서는 다음 점이 중요하다.

```text
H200 MIG 30GB
  -> Heron101 상주
  -> CLIP 상주
  -> DeepSeekOCR V2 vLLM 상주
  -> 남은 공간에서 KV cache와 runtime buffer 확보
```

Heron101/CLIP은 파라미터가 작은 모델이라는 점을 함께 고려한다. 따라서 이 구조의 핵심은 "작은 모델 두 개가 weight memory를 크게 잡아먹는다"가 아니라, 실제 free memory delta, CUDA context/reserved memory, 동시 request 실행이 DeepSeekOCR V2의 KV cache 예산에 얼마나 영향을 주는지 확인하는 것이다.

### 올리는 것이 유리할 수 있는 경우

```text
증상:
  generate 내부가 느림
  vLLM 로그상 KV cache capacity가 작음
  batch가 자주 scheduler 대기
  GPU memory free가 충분히 남음

해석:
  KV cache block이 부족할 수 있음
```

### 내리는 것이 유리할 수 있는 경우

```text
증상:
  OOM 또는 memory warning
  batch 전환 시 memory pressure
  Heron101/CLIP과 같이 실행할 때만 불안정
  GPU free memory가 낮고 reserved memory가 큼

해석:
  vLLM이 너무 공격적으로 메모리를 잡아 temporary buffer나 다른 모델과 충돌할 수 있음
```

### 현재 추천 실험

처음부터 많이 바꾸지 말고, batch size 비교 후 조정한다.

```text
1. 0.8 + batch 16 현재 상태 계측
2. 0.8 + batch 8
3. 0.8 + batch 4
4. 가장 안정적인 batch size에서 0.7
5. memory warning/OOM이 있으면 0.6
```

---

## 5. `max_num_seqs`

`max_num_seqs`는 vLLM scheduler가 동시에 다룰 수 있는 sequence 수의 상한이다.

application batch size와 비슷해 보이지만 같은 개념은 아니다.

```text
application batch size
  -> Python 코드가 한 번에 llm.generate에 넘기는 image/page 수

max_num_seqs
  -> vLLM scheduler가 동시에 처리할 수 있는 sequence 수
```

현재 application batch size와 sequence 관련 설정이 16으로 맞춰져 있다. 하지만 VLM/OCR에서는 이 설정이 항상 최적은 아니다.

```text
batch 16 text
  -> 16 sequences
  -> token 수가 작을 수 있음

batch 16 images
  -> 16 sequences
  -> visual token이 커질 수 있음
  -> output length 편차도 큼
```

### 줄이는 것이 유리할 수 있는 경우

```text
증상:
  batch 16에서 generate time이 길다
  GPU memory free가 낮다
  output length가 긴 page가 섞이면 batch 전체가 늦다
  batch 8/4가 전체 처리 시간에서 더 낫다
```

### 유지하거나 높이는 것이 유리할 수 있는 경우

```text
증상:
  GPU utilization이 낮다
  memory free가 충분하다
  output length 편차가 작다
  batch size를 키울수록 total time이 안정적으로 줄어든다
```

현재 환경에서는 `max_num_seqs=16`을 고정값으로 믿기보다 batch size 4/8/16과 함께 봐야 한다.

---

## 6. `max_num_batched_tokens`

VLM/OCR에서 매우 중요한 옵션이다.

`max_num_seqs`가 sequence 개수 제한이라면, `max_num_batched_tokens`는 scheduler가 한 번에 처리할 token 총량과 관련된다.

```text
16 sequences
  -> sequence 수는 같아도
  -> 각 sequence의 visual token 수에 따라 token 총량이 크게 달라짐
```

VLM/OCR에서는 page image가 visual token으로 확장된다.

```text
batch token load
  = sum(visual_tokens_per_page)
  + sum(text_prompt_tokens_per_page)
  + decode step tokens
```

따라서 batch size 16이 같아도 다음 두 batch는 완전히 다르다.

```text
batch A
  16 low-res pages
  short output

batch B
  16 high-res dense pages
  long output
```

### 낮게 잡는 것이 유리할 수 있는 경우

```text
증상:
  high-res page batch에서 memory pressure
  prefill 시간이 튐
  batch 16에서만 OOM 또는 latency spike
```

### 너무 낮을 때 생길 수 있는 문제

```text
문제:
  scheduler가 한 번에 처리하는 token이 너무 적음
  GPU utilization 저하
  prefill이 여러 step으로 쪼개져 overhead 증가 가능
```

현재는 실제 visual token 수를 모르므로, 먼저 image resolution과 generate time의 상관관계를 본 뒤 조정해야 한다.

---

## 7. `max_model_len`

`max_model_len`은 sequence가 가질 수 있는 최대 context 길이와 관련된다.

OCR/VLM에서는 다음 값의 합을 감당해야 한다.

```text
sequence length
  = visual tokens
  + text prompt tokens
  + generated OCR tokens
```

`max_model_len`이 불필요하게 크면 vLLM이 최악의 sequence 길이를 감안해 KV cache capacity를 계산하면서 동시 처리량이 줄어들 수 있다.

```text
max_model_len 큼
  -> 긴 sequence 수용 가능
  -> KV cache 예산이 보수적으로 잡힘
  -> maximum concurrency 감소 가능

max_model_len 작음
  -> KV cache capacity 효율 증가 가능
  -> 너무 작으면 긴 OCR page 실패 또는 잘림
```

### 확인 순서

```text
1. 실제 output length 분포 기록
2. image visual token 또는 processor output 길이 확인
3. 현재 max_model_len이 과도한지 판단
4. 작은 값으로 줄여도 품질/완성도가 유지되는지 실험
```

폐쇄망에서 image visual token 수를 바로 알기 어렵다면, 우선 output char length와 finish reason을 기록한다. `max_tokens`에 자주 걸리는지부터 확인한다.

---

## 8. `max_tokens` / `max_new_tokens`

이 값은 vLLM 엔진 옵션이라기보다 generation parameter에 가깝지만, OCR 성능에는 매우 중요하다.

OCR은 출력이 길 수 있다. 특히 표, 논문, dense document에서는 한 page의 출력이 길어질 수 있다.

```text
max_tokens 큼
  -> 긴 페이지 출력 가능
  -> decode 시간 증가
  -> KV cache 증가
  -> batch tail latency 증가

max_tokens 작음
  -> decode 상한으로 latency 제한
  -> OCR 결과 누락 위험
```

### 먼저 볼 지표

```text
output_chars_per_page
finish_reason
generate_ms
batch_visible_gap_ms
```

만약 대부분의 page가 짧고 일부 page만 매우 길다면, 모든 page에 큰 `max_tokens`를 주기보다 page type 또는 예상 길이에 따라 batch를 나누는 전략이 나을 수 있다.

---

## 9. Multimodal 관련 제한

vLLM multimodal 입력에서는 prompt당 image 수나 multimodal item 수를 제한하는 설정이 있을 수 있다. 정확한 옵션명과 지원 여부는 설치 버전에서 확인해야 한다.

현재 구조에서는 보통 다음 형태를 예상한다.

```text
sequence 1 = page image 1장 + OCR prompt
sequence 2 = page image 1장 + OCR prompt
...
sequence 16 = page image 1장 + OCR prompt
```

확인할 항목은 다음이다.

- 한 prompt에 image가 몇 개 들어가는가?
- page 하나가 crop/tiling으로 여러 image item이 되는가?
- vLLM이 prompt당 image 수를 제한하고 있는가?
- 제한 초과 시 에러가 나는가, 내부에서 잘리는가?
- image processor가 vLLM 내부에서 수행되는가, 외부에서 수행되는가?

특히 crop/tiling이 있다면 다음 문제가 생긴다.

```text
application batch size = 16 pages
internal image items = 16 pages x tiles_per_page
```

이 경우 `max_num_seqs=16`만으로 부하를 설명할 수 없다.

---

## 10. Prefix Caching

OCR prompt가 모든 page에서 거의 동일하다면 prefix caching이 도움될 가능성이 있다.

```text
common text prompt:
  "Extract text from this document page ..."

page-specific image:
  image_001, image_002, ...
```

그러나 image가 sequence마다 다르기 때문에 캐시 이득은 제한될 수 있다.

```text
공유 가능성이 있는 부분
  -> 동일한 text instruction prefix

공유하기 어려운 부분
  -> image-derived visual tokens
```

확인할 질문은 다음이다.

- prompt에서 image placeholder가 text instruction 앞에 있는가, 뒤에 있는가?
- 공통 text prefix가 실제 KV cache 공유 가능한 위치에 있는가?
- vLLM 버전과 모델이 prefix caching을 지원하는가?
- prefix caching을 켰을 때 memory 사용량이 늘거나 줄어드는가?

현재 문제의 1차 후보는 batch 사이 공백과 memory pressure이므로, prefix caching은 초기 실험보다 후순위다.

---

## 11. Chunked Prefill

chunked prefill은 긴 prompt를 한 번에 prefill하지 않고 나눠 처리하는 방식이다.

VLM/OCR에서는 visual token 때문에 prompt가 길어질 수 있으므로 관련성이 있다.

```text
긴 visual prompt
  -> prefill이 무거움
  -> scheduler step이 커짐
  -> latency spike 또는 memory pressure

chunked prefill
  -> 긴 prefill을 나눠 처리
  -> 다른 decode 작업과 섞기 쉬움
  -> overhead와 설정 복잡도 증가 가능
```

도움될 수 있는 경우:

```text
generate_ms 중 prefill 구간이 큰 것으로 보임
high-res page에서 latency spike
max_num_batched_tokens와 관련된 제한이 자주 걸림
```

우선순위는 중간이다. 먼저 batch size와 memory 계측으로 큰 병목을 확인한 뒤 검토한다.

---

## 12. dtype과 Quantization

30GB MIG에서 세 모델이 같이 떠 있으므로 dtype은 단순 품질 옵션이 아니라 핵심 성능 옵션이다. 특히 Heron101/CLIP이 작은 모델이라면, 전체 성능 차이는 공존 weight memory보다 DeepSeekOCR V2의 dtype이 줄이는 weight/activation/KV cache 부담에서 더 크게 나올 가능성이 높다. 현재 관찰상 `float32` 사용 시 100페이지 이상 PDF 처리 시간이 약 300초였고, `bfloat16`으로 변경한 뒤 확실히 빨라졌다.

### dtype

```text
bf16/fp16
  -> 일반적인 GPU 추론 dtype
  -> H200에서는 bf16 지원이 좋을 가능성이 높음

fp32
  -> 메모리/속도 측면에서 불리
  -> 특별한 이유가 없으면 피해야 함
```

이 개선은 다음 경로로 설명할 수 있다.

```text
float32
  -> weight 4 bytes
  -> activation/KV cache도 커질 수 있음
  -> HBM bandwidth 부담 증가
  -> 30GB MIG에서 KV cache 여유 감소

bfloat16
  -> weight 2 bytes
  -> activation/KV cache memory 감소 가능
  -> H200 bf16 Tensor Core 활용 가능성
  -> batch 16 유지 가능성 증가
```

정확도 측면에서는 bf16이 fp32보다 표현 정밀도가 낮다. 다만 bf16은 fp16보다 exponent 범위가 넓어 대형 모델 추론에서 안정적인 경우가 많다.

OCR에서는 다음 품질 항목을 비교해야 한다.

| 품질 항목 | 확인 이유 |
| --- | --- |
| 작은 글자 누락 | precision 감소가 OCR 세부 인식에 영향 가능 |
| 숫자/단위 오류 | 문서 OCR에서 치명적 |
| 표 구조 | cell/column 순서가 흔들리는지 확인 |
| 특수문자/수식 | 낮은 정밀도에서 차이가 날 수 있음 |
| 출력 잘림/반복 | dtype 변경이 generation 안정성에 주는 영향 확인 |

현재 추천은 다음이다.

```text
기본 후보 dtype = bfloat16

단, 최종 적용 전:
  fp32 결과와 bf16 결과를 같은 page 샘플에서 비교
  속도뿐 아니라 OCR 품질 차이를 기록
```

### Quantization

Quantization은 model weight memory를 줄일 수 있다.

```text
장점:
  weight memory 감소
  30GB MIG에서 KV cache 여유 증가 가능

위험:
  VLM/OCR 품질 저하 가능
  multimodal 모델 지원 여부 확인 필요
  특정 quantization은 속도가 오히려 느릴 수 있음
```

현재 단계에서는 `bfloat16`이 이미 명확한 개선을 보였으므로, quantization은 후순위다. bf16에서도 30GB MIG 메모리가 부족하거나 batch size를 더 키워야 할 때 검토한다.

---

## 13. CUDA Graph / Eager 관련 옵션

vLLM은 반복되는 decode 연산에서 CUDA graph를 활용할 수 있다. 하지만 VLM/OCR은 image size, visual token, output length가 달라 shape 변동이 클 수 있다.

```text
CUDA graph 이득 조건
  -> 반복 shape가 안정적
  -> decode 패턴이 비슷함
  -> CPU kernel launch overhead가 병목

이득이 제한되는 조건
  -> page마다 image token 수가 크게 다름
  -> batch size가 자주 바뀜
  -> dynamic shape fallback이 많음
```

현재 문제는 먼저 batch 사이 공백과 memory pressure를 확인해야 한다. CUDA graph/eager 관련 옵션은 vLLM 로그에서 capture 시간이 크거나 shape 문제 경고가 보일 때 후순위로 본다.

---

## 14. 병목 유형별 옵션 선택

계측 결과에 따라 다음처럼 접근한다.

### Case A. `generate_ms`가 대부분

```text
우선 확인:
  batch size 4/8/16
  max_num_seqs
  max_num_batched_tokens
  max_model_len
  max_tokens
```

해석:

- prefill이 크면 visual token, `max_num_batched_tokens`, chunked prefill을 본다.
- decode가 크면 output length, `max_tokens`, page grouping을 본다.
- memory가 부족하면 `gpu_memory_utilization`, `max_model_len`, batch size를 본다.

### Case B. `visible_gap_ms`가 대부분

```text
우선 확인:
  prepare_ms
  postprocess_ms
  output parsing
  image processor 위치
  Python loop 구조
```

해석:

- vLLM 옵션보다 application 구조 개선이 우선이다.
- 다음 batch input을 미리 준비하거나, output 후처리를 분리하는 전략을 검토한다.

### Case C. Memory free가 낮을 때 느림

```text
우선 확인:
  gpu_memory_utilization
  batch size
  max_model_len
  dtype
  DeepSeekOCR 단독 vs 세 모델 공존
```

해석:

- batch size 16은 과할 수 있다.
- `gpu_memory_utilization`을 낮추는 것이 안정성에 도움될 수 있다.
- 모델 분리 또는 로드 순서가 더 큰 개선일 수 있다.

### Case D. 특정 문서/page에서만 느림

```text
우선 확인:
  image resolution
  output length
  page type
  crop/tiling count
```

해석:

- 전역 옵션보다 page grouping과 adaptive batch size가 더 효과적일 수 있다.

---

## 15. 현재 환경의 추천 실험 순서

현재 정보 기준으로는 다음 순서가 가장 합리적이다.

```text
1. 현재 설정 계측
   batch_size=16
   max_num_seqs=16
   gpu_memory_utilization=0.8
   dtype=bfloat16

2. batch size만 낮춰 비교
   batch_size=8
   batch_size=4

3. DeepSeekOCR 단독 기준선 확보
   Heron101/CLIP 미로드 상태와 비교
   두 모델이 작은 편이므로 차이가 작으면 공존 구조는 후순위로 내림

4. 안정적인 batch size에서 gpu_memory_utilization 비교
   0.8 -> 0.7 -> 0.6

5. 필요하면 fp32 vs bf16 품질 샘플 비교

6. output length 분포를 보고 max_tokens 조정

7. 필요하면 max_model_len, max_num_batched_tokens 검토

8. 후순위로 prefix caching, chunked prefill, CUDA graph/eager, quantization 검토
```

이 순서의 이유는 다음이다.

```text
batch size와 DeepSeekOCR V2 dtype/visual token/KV cache
  -> 가장 큰 영향 가능성

모델 공존 구조
  -> Heron101/CLIP이 작은 모델이므로 measured delta가 클 때만 주요 원인으로 승격

gpu_memory_utilization
  -> memory pressure가 확인된 후 조정해야 함

max_tokens/max_model_len
  -> output length와 visual token 근거가 필요

고급 옵션
  -> 근본 병목이 확인된 뒤 적용해야 함
```

---

## 16. 옵션 실험 기록 포맷

옵션 실험은 다음 표로 남긴다.

| run | batch size | max seqs | gpu mem util | max model len | max tokens | total sec | avg generate ms | avg gap ms | peak used MB | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| baseline | 16 | 16 | 0.8 |  |  |  |  |  |  | current |
| bs8 | 8 |  | 0.8 |  |  |  |  |  |  |  |
| bs4 | 4 |  | 0.8 |  |  |  |  |  |  |  |

결론은 단순히 total time만 보지 않는다.

```text
좋은 설정
  -> total time 감소
  -> visible gap 감소
  -> OOM/memory warning 없음
  -> OCR 결과 잘림 없음
  -> page별 output 품질 유지
```

---

## 17. 다음 문서로 넘길 질문

다음 문서는 `08_experiment_matrix.md`다. 여기서는 지금까지 정리한 병목 가설과 옵션을 바탕으로 실제 실험 매트릭스를 만든다.

다음 질문을 다룬다.

- 첫 번째 실험 세트는 어떤 조합으로 구성할 것인가?
- 각 실험에서 어떤 로그를 필수로 수집할 것인가?
- 어떤 결과가 나오면 어떤 결정을 내릴 것인가?
- batch size, 모델 공존, memory utilization, output limit을 어떤 순서로 비교할 것인가?
