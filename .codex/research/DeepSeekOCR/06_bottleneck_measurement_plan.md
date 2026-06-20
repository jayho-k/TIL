# Bottleneck Measurement Plan

> 작성일: 2026-06-20  
> 목적: DeepSeekOCR V2 처리 중 "image/preprocess progress bar는 빠른데 다음 batch progress bar까지 오래 걸리는 현상"의 원인을 분리하기 위한 계측 계획을 정의한다.  
> 전제: 실제 `deepseekocrv2.py`는 폐쇄망 사내 PC에 있어 이 환경에서 직접 확인하거나 수정할 수 없다. 이 문서는 폐쇄망 코드에 적용할 timing log, memory log, metadata log 설계를 제공한다.

---

## 1. 이 문서에서 답할 질문

이 문서는 다음 질문에 답한다.

- FastAPI endpoint 기준으로 어떤 timestamp를 남겨야 하는가?
- batch prepare, generate, postprocess를 어떻게 분리해서 측정해야 하는가?
- GPU memory snapshot은 어느 시점에 찍어야 하는가?
- image resolution, output length, batch size를 어떤 형식으로 기록해야 하는가?
- vLLM 내부 병목과 application loop 병목을 어떻게 구분할 수 있는가?
- 폐쇄망 사내 PC에서 최소 수정으로 실행 가능한 계측 코드는 어떤 형태인가?

---

## 2. 계측의 핵심 목표

현재 관찰은 다음이다.

```text
batch_i image/preprocess progress bar
  -> 빠르게 진행
  -> progress bar 종료
  -> 다음 batch progress bar가 생기기까지 긴 공백
```

이 현상을 다음 구간으로 쪼개야 한다.

```text
request_start
  -> request_payload_ready
  -> batch_split_done
  -> batch_i_prepare_start
  -> batch_i_prepare_done
  -> batch_i_generate_start
  -> batch_i_generate_done
  -> batch_i_postprocess_done
  -> batch_i+1_prepare_start
  -> response_done
```

핵심은 다음 두 시간을 분리하는 것이다.

```text
vLLM 내부 시간
  = batch_i_generate_start -> batch_i_generate_done

batch 사이 공백
  = batch_i_generate_done -> batch_i+1_generate_start
```

만약 batch 사이 공백이 길다면 vLLM 옵션보다 application prepare/postprocess, GPU sync, memory cleanup, output parsing이 더 유력하다.

---

## 3. 계측 단위

계측은 세 레벨로 나눈다.

```text
Request level
  -> endpoint 전체 처리 시간
  -> image payload 수
  -> total pages

Batch level
  -> batch별 prepare/generate/postprocess 시간
  -> batch별 image 크기/개수
  -> batch별 output 길이

Page level
  -> page index
  -> image width/height
  -> output char length
  -> 가능하면 output token length
```

초기에는 page level을 너무 자세히 만들 필요는 없다. 최소한 다음 네 가지는 남긴다.

```text
request_id
batch_index
page_indices
image_width_height_list
```

그리고 batch 처리 후 다음을 남긴다.

```text
generate_time_ms
postprocess_time_ms
output_chars_total
output_chars_per_page
```

---

## 4. Request Level Timing

FastAPI endpoint 진입부터 응답까지의 큰 흐름을 측정한다.

```text
T0 request_start
T1 payload_parsed
T2 images_ready
T3 batch_split_done
T4 all_batches_done
T5 response_serialized
T6 response_done
```

각 timestamp의 의미는 다음이다.

| timestamp | 의미 | 병목 해석 |
| --- | --- | --- |
| `request_start` | endpoint 함수 시작 | 전체 기준점 |
| `payload_parsed` | 요청 body parsing 완료 | 큰 image payload 역직렬화 비용 |
| `images_ready` | 모델에 넘길 image 객체 준비 완료 | image object 변환 비용 |
| `batch_split_done` | batch list 생성 완료 | batch 구성 비용 |
| `all_batches_done` | 모든 OCR batch 처리 완료 | 모델 처리 전체 시간 |
| `response_serialized` | 응답 객체 생성/직렬화 완료 | 결과 payload 비용 |
| `response_done` | endpoint 반환 직전 | 전체 latency |

폐쇄망에서 처음 넣을 때는 모든 timestamp를 한 번에 넣지 않아도 된다. 우선 `request_start`, `batch_split_done`, `all_batches_done`, `response_done`만으로도 큰 흐름을 볼 수 있다.

---

## 5. Batch Level Timing

현재 문제를 가장 잘 분리하는 핵심은 batch level timing이다.

batch별로 다음 구간을 기록한다.

```text
batch_prepare_start
batch_prepare_done
batch_generate_start
batch_generate_done
batch_postprocess_done
```

구간별 해석은 다음이다.

| 구간 | 계산식 | 의미 |
| --- | --- | --- |
| prepare time | `prepare_done - prepare_start` | image processor, prompt 구성, vLLM input 생성 |
| generate time | `generate_done - generate_start` | vLLM `generate` 호출 내부 시간 |
| postprocess time | `postprocess_done - generate_done` | output parsing, text 정리, CPU copy |
| next gap | `next_prepare_start - postprocess_done` | loop overhead 또는 기타 대기 |
| visible gap | `next_generate_start - generate_done` | 사용자가 체감하는 progress bar 사이 공백 근사 |

특히 현재 증상에는 이 값이 중요하다.

```text
visible_gap_ms = next_batch_generate_start - current_batch_generate_done
```

만약 `visible_gap_ms`가 크고 `postprocess_time` 또는 `next_prepare_time`이 크다면 vLLM 내부보다 application 경계가 병목이다. 다만 DeepSeek-OCR-2 GitHub 원본 기준으로는 `Pre-processed images` 이후 `llm.generate(...)`가 실행되므로, 폐쇄망 코드에서 progress bar가 batch마다 반복된다면 `generate_done -> next_preprocess_start`와 `next_preprocess_start -> next_generate_start`를 분리해서 봐야 한다.

이 값은 async 구조가 필요한지 판단하는 기준이기도 하다. DeepSeekOCR V2 공개 vLLM 예제는 동기 `LLM.generate()`를 사용하므로, 먼저 현재 동기 구조에서 `generate_done -> next_generate_start`가 실제로 큰지 확인한 뒤 `10_async_serving_considerations.md`의 application pipeline 또는 AsyncLLM smoke test로 넘어간다.

---

## 6. GPU Memory Snapshot

메모리 병목을 보려면 batch 전후로 GPU memory를 찍어야 한다.

권장 시점은 다음이다.

```text
startup_before_model_load
after_heron101_load
after_clip_load
after_deepseekocr_vllm_load
request_start
batch_i_prepare_start
batch_i_generate_start
batch_i_generate_done
batch_i_postprocess_done
request_done
```

현실적으로 처음부터 모두 찍기 어렵다면 최소 시점은 다음이다.

```text
after_deepseekocr_vllm_load
batch_i_generate_start
batch_i_generate_done
batch_i_postprocess_done
```

기록할 값은 다음이다.

| 값 | 의미 |
| --- | --- |
| NVML used/free memory | GPU 전체 관점의 실제 사용량 |
| torch allocated | PyTorch tensor가 실제 사용 중인 메모리 |
| torch reserved | PyTorch caching allocator가 예약한 메모리 |
| max allocated | batch 중 peak 확인 |
| vLLM KV cache 로그 | 초기화 시 KV cache capacity 확인 |

주의할 점은 `torch.cuda.memory_allocated()`만으로 vLLM 전체 메모리를 설명할 수 없다는 것이다. NVML 기준 memory와 같이 봐야 한다.

---

## 7. 최소 계측 코드 예시

폐쇄망 코드에 넣기 쉬운 최소 형태는 다음이다.

```python
import time
import logging

logger = logging.getLogger("ocr_perf")


def now_ms() -> float:
    return time.perf_counter() * 1000


def log_event(request_id: str, event: str, **fields):
    payload = {
        "request_id": request_id,
        "event": event,
        "ts_ms": round(now_ms(), 3),
        **fields,
    }
    logger.info("OCR_PERF %s", payload)
```

batch loop에는 다음처럼 넣는다.

```python
for batch_index, batch_images in enumerate(image_batches):
    log_event(
        request_id,
        "batch_prepare_start",
        batch_index=batch_index,
        batch_size=len(batch_images),
    )

    prepare_t0 = now_ms()
    prompts = build_prompts(batch_images)
    prepare_t1 = now_ms()

    log_event(
        request_id,
        "batch_prepare_done",
        batch_index=batch_index,
        prepare_ms=round(prepare_t1 - prepare_t0, 3),
    )

    generate_t0 = now_ms()
    log_event(request_id, "batch_generate_start", batch_index=batch_index)
    outputs = llm.generate(prompts, sampling_params)
    generate_t1 = now_ms()

    log_event(
        request_id,
        "batch_generate_done",
        batch_index=batch_index,
        generate_ms=round(generate_t1 - generate_t0, 3),
    )

    post_t0 = now_ms()
    parsed_outputs = parse_outputs(outputs)
    post_t1 = now_ms()

    log_event(
        request_id,
        "batch_postprocess_done",
        batch_index=batch_index,
        postprocess_ms=round(post_t1 - post_t0, 3),
        output_chars_total=sum(len(x) for x in parsed_outputs),
    )
```

위 코드는 실제 함수명에 맞춰 바꿔야 한다. 중요한 것은 prepare, generate, postprocess의 경계를 명확히 나누는 것이다.

---

## 8. GPU Memory Logging 코드 예시

PyTorch 기준 메모리는 다음처럼 남길 수 있다.

```python
import torch


def torch_memory_mb():
    if not torch.cuda.is_available():
        return {}

    return {
        "torch_allocated_mb": round(torch.cuda.memory_allocated() / 1024 / 1024, 2),
        "torch_reserved_mb": round(torch.cuda.memory_reserved() / 1024 / 1024, 2),
        "torch_max_allocated_mb": round(torch.cuda.max_memory_allocated() / 1024 / 1024, 2),
    }
```

NVML을 사용할 수 있으면 GPU 전체 기준도 남긴다.

```python
def nvml_memory_mb():
    try:
        import pynvml

        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
        info = pynvml.nvmlDeviceGetMemoryInfo(handle)
        return {
            "nvml_used_mb": round(info.used / 1024 / 1024, 2),
            "nvml_free_mb": round(info.free / 1024 / 1024, 2),
            "nvml_total_mb": round(info.total / 1024 / 1024, 2),
        }
    except Exception as exc:
        return {"nvml_error": type(exc).__name__}
```

event log에 합치는 형태는 다음이다.

```python
def log_memory_event(request_id: str, event: str, **fields):
    log_event(
        request_id,
        event,
        **fields,
        **torch_memory_mb(),
        **nvml_memory_mb(),
    )
```

처음에는 `batch_generate_start`, `batch_generate_done`, `batch_postprocess_done`에서만 호출해도 충분하다.

---

## 9. Image Metadata Logging

VLM/OCR에서는 image별 크기를 함께 남겨야 한다.

```python
def image_meta(image):
    width, height = image.size
    return {
        "width": width,
        "height": height,
        "pixels": width * height,
    }
```

batch 단위로는 다음처럼 요약한다.

```python
metas = [image_meta(image) for image in batch_images]
pixels_total = sum(m["pixels"] for m in metas)

log_event(
    request_id,
    "batch_image_meta",
    batch_index=batch_index,
    batch_size=len(batch_images),
    pixels_total=pixels_total,
    max_width=max(m["width"] for m in metas),
    max_height=max(m["height"] for m in metas),
    max_pixels=max(m["pixels"] for m in metas),
)
```

이 정보는 다음을 확인하는 데 쓴다.

```text
image 크기가 큰 batch
  -> prepare time이 긴가?
  -> generate time이 긴가?
  -> memory peak가 큰가?
```

---

## 10. Output Length Logging

OCR 출력 길이 편차는 decode tail latency를 만드는 핵심 후보이다.

초기에는 character length만 기록해도 된다.

```python
output_lengths = [len(text) for text in parsed_outputs]

log_event(
    request_id,
    "batch_output_meta",
    batch_index=batch_index,
    output_chars_total=sum(output_lengths),
    output_chars_max=max(output_lengths) if output_lengths else 0,
    output_chars_min=min(output_lengths) if output_lengths else 0,
    output_chars_list=output_lengths,
)
```

가능하면 tokenizer로 token length도 기록한다.

```python
def token_len(tokenizer, text: str) -> int:
    return len(tokenizer.encode(text))
```

다만 tokenizer 호출 자체가 overhead가 될 수 있으므로, 처음에는 character length를 우선한다.

---

## 11. Progress Bar 사이 공백 계산

로그 수집 후 다음 값을 계산한다.

```text
visible_gap_ms[i]
  = batch_generate_start[i + 1] - batch_generate_done[i]
```

그리고 다음 값들과 비교한다.

```text
postprocess_ms[i]
prepare_ms[i + 1]
output_chars_total[i]
image_pixels_total[i + 1]
gpu_free_mb at batch_generate_done[i]
```

해석 예시는 다음이다.

| 관찰 | 해석 |
| --- | --- |
| `visible_gap`이 `postprocess_ms`와 비슷함 | output parsing/정리 병목 |
| `visible_gap`이 다음 batch `prepare_ms`와 비슷함 | image processor/prompt 구성 병목 |
| `generate_ms`가 batch size에 강하게 증가 | vLLM prefill/decode 또는 KV cache 병목 |
| memory free가 낮을 때 gap 증가 | memory pressure 또는 allocator 영향 |
| output length가 큰 batch 뒤 gap 증가 | 긴 출력 후처리 또는 CPU copy 영향 |

---

## 12. 실험별 계측 최소 세트

### 실험 A. 현재 설정 그대로 계측

```text
batch_size = 16
gpu_memory_utilization = 0.8
models = Heron101 + CLIP + DeepSeekOCR V2
```

목적:

- 현재 300초의 시간 분해
- batch 사이 공백이 어디서 생기는지 확인

### 실험 B. Batch size 변경

```text
batch_size = 8
batch_size = 4
```

목적:

- batch size를 낮췄을 때 `generate_ms`, `visible_gap_ms`, total time이 어떻게 바뀌는지 확인

### 실험 C. DeepSeekOCR 단독 실행

```text
models = DeepSeekOCR V2 only
```

목적:

- Heron101/CLIP 상주가 KV cache와 latency에 미치는 영향 분리. 두 모델은 파라미터가 작은 편이므로 차이가 작으면 DeepSeekOCR V2 설정을 우선한다.

### 실험 D. `gpu_memory_utilization` 변경

```text
gpu_memory_utilization = 0.7
gpu_memory_utilization = 0.6
```

목적:

- 메모리 안정성과 throughput 균형 확인
- OOM 또는 allocator pressure 완화 여부 확인

---

## 13. 로그 분석 표

수집한 로그는 batch별로 다음 표로 정리한다.

| batch | size | prepare ms | generate ms | post ms | visible gap ms | pixels total | output chars | free MB start | free MB done |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 16 |  |  |  |  |  |  |  |  |
| 1 | 16 |  |  |  |  |  |  |  |  |
| 2 | 16 |  |  |  |  |  |  |  |  |

판단 기준은 다음이다.

```text
generate ms가 대부분
  -> vLLM scheduler, prefill, decode, KV cache, batch size 문제

prepare/post/gap이 대부분
  -> application loop, processor, output parsing, sync 문제

memory free가 낮은 batch에서 느림
  -> MIG 30GB와 모델 공존 구조 문제. 단, Heron101/CLIP의 로드 전후 delta가 작으면 DeepSeekOCR V2 batch/KV/dtype 문제로 해석

pixels/output length가 큰 batch에서 느림
  -> VLM/OCR 입력 특성 문제
```

---

## 14. 주의할 계측 오류

계측 자체가 성능을 크게 망치면 안 된다.

주의할 점은 다음이다.

- 매 page마다 너무 많은 로그를 찍지 않는다.
- output 전문을 로그로 남기지 않는다.
- tokenizer로 output token length를 계산하는 작업은 처음에는 생략할 수 있다.
- `torch.cuda.synchronize()`를 계측 목적으로 무분별하게 넣지 않는다.
- `torch.cuda.empty_cache()`를 계측 코드에 추가하지 않는다.
- 로그 직렬화가 너무 크면 response latency에 영향을 줄 수 있다.

특히 `torch.cuda.synchronize()`는 GPU 작업 완료를 강제로 기다리므로, 원래 성능을 바꿀 수 있다. 정확한 GPU kernel timing이 필요할 때만 별도 실험으로 사용한다.

---

## 15. 현재 단계의 판단

현재까지의 구조 분석만으로는 vLLM 옵션이 문제인지, batch loop가 문제인지, 모델 공존 메모리가 문제인지 단정할 수 없다. Heron101/CLIP이 작은 모델이라는 조건 때문에 공존 메모리는 반드시 측정하되, 초기 가설의 중심은 DeepSeekOCR V2의 dtype, batch, visual token, KV cache에 둔다.

따라서 다음 한 번의 계측으로 최소한 아래 세 가지를 분리해야 한다.

```text
1. generate 내부가 느린가?
2. generate 전후 application 구간이 느린가?
3. 느린 batch가 image 크기, output 길이, GPU memory와 상관이 있는가?
```

이 세 가지가 분리되면 이후 최적화 방향이 명확해진다.

```text
generate 내부 병목
  -> vLLM 옵션, batch size, KV cache, max tokens 조정

application 경계 병목
  -> processor 위치, batch 준비, output parsing, async/pipeline 구조 조정
  -> DeepSeekOCR V2의 vLLM V1 AsyncLLM 호환성은 별도 smoke test로 확인

memory 병목
  -> batch size 감소, 모델 분리, gpu_memory_utilization 조정, max_model_len 축소
```

---

## 16. 다음 문서로 넘길 질문

다음 문서는 `07_vllm_options_for_deepseekocr.md`다. 여기서는 계측으로 확인한 병목 유형별로 어떤 vLLM 옵션을 봐야 하는지 정리한다.

다음 질문을 다룬다.

- `gpu_memory_utilization`은 언제 올리고 언제 내려야 하는가?
- `max_num_seqs`와 application batch size는 어떻게 다르게 봐야 하는가?
- `max_num_batched_tokens`는 VLM/OCR에서 왜 중요한가?
- `max_model_len`이 KV cache capacity에 어떤 영향을 주는가?
- prefix caching, chunked prefill, dtype/quantization은 현재 문제에 어떤 조건에서 도움이 되는가?
