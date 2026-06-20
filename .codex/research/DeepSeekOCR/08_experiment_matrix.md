# Experiment Matrix

> 작성일: 2026-06-20  
> 목적: DeepSeekOCR V2 + vLLM 최적화를 위해 폐쇄망 사내 PC에서 실행할 실험 순서, 수집 로그, 판단 기준을 정의한다.  
> 자료 기준: `00`~`07` research 문서를 기반으로 한다. 실제 수치는 폐쇄망 서버에서 계측 후 `09_experiment_results.md`에 기록한다.

---

## 1. 이 문서에서 답할 질문

이 문서는 다음 질문에 답한다.

- 첫 번째 실험 세트는 어떤 조합으로 구성할 것인가?
- 각 실험에서 어떤 로그를 필수로 수집할 것인가?
- 어떤 결과가 나오면 어떤 결정을 내릴 것인가?
- batch size, 모델 공존, `gpu_memory_utilization`, output limit을 어떤 순서로 비교할 것인가?
- 100페이지 이상 PDF에서 300초가 걸리는 문제를 어떤 기준으로 개선했다고 판단할 것인가?

---

## 2. 실험 원칙

옵션을 한 번에 많이 바꾸면 원인을 알 수 없다. 따라서 한 번에 하나의 축만 바꾼다.

```text
나쁜 실험:
  batch size 변경
  + gpu_memory_utilization 변경
  + max_model_len 변경
  + max_tokens 변경
  -> 어떤 변경이 효과를 냈는지 알 수 없음

좋은 실험:
  baseline 고정
  -> batch size만 변경
  -> 모델 공존 여부만 변경
  -> memory utilization만 변경
  -> output limit만 변경
```

모든 실험은 다음 로그가 있어야 비교 가능하다.

```text
request total time
batch prepare time
batch generate time
batch postprocess time
visible gap time
GPU memory snapshot
image resolution metadata
output length metadata
finish reason
```

---

## 3. 공통 실험 환경 기록

모든 실험 시작 전에 다음 정보를 기록한다.

| 항목 | 예시 | 이유 |
| --- | --- | --- |
| run id | `baseline_bs16_util08` | 결과 추적 |
| date/time | `2026-06-20 15:00` | 재현성 |
| server | model server id | 장비 차이 구분 |
| GPU | H200 MIG 30GB | 메모리 제약 명시 |
| visible GPU memory | 30GB | MIG 확인 |
| vLLM version | 폐쇄망 서버에서 확인 | 옵션 의미 차이 |
| CUDA version | 폐쇄망 서버에서 확인 | 성능 차이 |
| PyTorch version | 폐쇄망 서버에서 확인 | memory logging 해석 |
| dtype | `float32` 또는 `bfloat16` | 속도/품질 비교 기준 |
| model set | Heron101 + CLIP + DeepSeekOCR | 공존 여부 |
| Heron101/CLIP scale | small-parameter models | 공존 영향 해석 시 weight memory 과대평가 방지 |
| DeepSeekOCR model path | 실제 경로 | 모델 버전 확인 |
| input PDF/pages | 동일 테스트 문서 | 비교 기준 |
| page count | 100+ | 문제 재현 |

테스트 문서는 가능하면 동일한 100페이지 이상 PDF에서 만든 동일 이미지 세트를 사용한다.

---

## 4. 공통 수집 지표

실험별로 다음 지표를 남긴다.

### Request 지표

| 지표 | 의미 |
| --- | --- |
| `total_sec` | 전체 처리 시간 |
| `pages_total` | 처리 페이지 수 |
| `pages_per_sec` | 처리량 |
| `request_payload_parse_ms` | 요청 payload 처리 비용 |
| `response_serialize_ms` | 응답 생성 비용 |

### Batch 지표

| 지표 | 의미 |
| --- | --- |
| `batch_size` | 실제 batch 크기 |
| `prepare_ms` | image/prompt 준비 시간 |
| `generate_ms` | vLLM generate 시간 |
| `postprocess_ms` | output parsing 시간 |
| `visible_gap_ms` | 다음 batch generate까지 공백 |
| `pixels_total` | batch image 크기 총량 |
| `output_chars_total` | batch 출력 길이 |
| `output_chars_max` | 긴 page tail 확인 |

### Memory 지표

| 지표 | 의미 |
| --- | --- |
| `nvml_used_mb` | GPU 전체 사용량 |
| `nvml_free_mb` | GPU free memory |
| `torch_allocated_mb` | PyTorch allocated |
| `torch_reserved_mb` | PyTorch reserved |
| `peak_used_mb` | run 중 peak memory |
| `kv_cache_blocks` | vLLM 초기화 로그에서 확인 |

---

## 5. 성공 기준

성능 개선은 단순히 한 번 빨라진 것으로 판단하지 않는다.

1차 성공 기준:

```text
100페이지 이상 PDF 처리 시간이 baseline 대비 감소
OOM 또는 memory warning 없음
OCR 결과가 max token 제한으로 잘리지 않음
visible gap 원인이 설명 가능
```

우선 목표는 다음이다.

```text
현재: 100+ pages에서 약 300초
1차 목표: 같은 입력에서 total_sec를 의미 있게 낮추고, 병목 구간을 설명 가능하게 만들기
```

정확한 목표 시간은 baseline 계측 후 정한다. 예를 들어 baseline이 300초로 재현된다면, 1차 개선 목표는 20~30% 감소처럼 잡을 수 있다.

---

## 6. Phase 0: Baseline 계측

현재 운영 설정 그대로 실행한다. 현재는 `bfloat16`이 `float32`보다 확실히 빨라진 관찰이 있으므로, 운영 기준 baseline은 `bfloat16`으로 둔다. `float32`는 필요할 때 품질 비교 기준선으로만 사용한다.

```text
run_id = baseline_current
models = Heron101 + CLIP + DeepSeekOCR V2
batch_size = 16
max_num_seqs = 16
gpu_memory_utilization = 0.8
dtype = bfloat16
max_tokens = current
max_model_len = current
```

목적:

- 300초 문제가 재현되는지 확인
- 시간이 prepare/generate/postprocess/gap 중 어디에 몰리는지 확인
- batch별 memory pressure를 확인

필수 결과:

| 지표 | 기록 |
| --- | --- |
| total sec |  |
| avg prepare ms |  |
| avg generate ms |  |
| avg postprocess ms |  |
| avg visible gap ms |  |
| peak used MB |  |
| min free MB |  |
| output chars max |  |

판단:

```text
generate_ms가 대부분
  -> Phase 1 batch size와 vLLM 옵션이 중요

visible_gap_ms가 대부분
  -> application boundary가 중요

memory free가 낮음
  -> Phase 2/3 모델 공존과 memory utilization이 중요
```

---

## 7. Phase 1: Batch Size 비교

`gpu_memory_utilization=0.8`과 모델 공존 구조는 유지하고 batch size만 바꾼다.

| run id | batch size | max num seqs | gpu mem util | 모델 구성 |
| --- | --- | --- | --- | --- |
| `bs16_util08_all_models` | 16 | 16 | 0.8 | Heron101 + CLIP + DeepSeekOCR |
| `bs8_util08_all_models` | 8 | 8 또는 현재값 | 0.8 | Heron101 + CLIP + DeepSeekOCR |
| `bs4_util08_all_models` | 4 | 4 또는 현재값 | 0.8 | Heron101 + CLIP + DeepSeekOCR |

`max_num_seqs`는 application batch size와 맞추는 실험과 유지하는 실험이 있을 수 있다. 첫 실험에서는 가능하면 batch size와 같은 값으로 맞춘다.

비교할 지표:

```text
total_sec
pages_per_sec
avg_generate_ms
avg_visible_gap_ms
peak_used_mb
min_free_mb
output 품질/잘림 여부
```

결정 기준:

| 결과 | 결정 |
| --- | --- |
| batch 8이 batch 16보다 빠름 | batch 16이 memory/tail latency 측면에서 과할 가능성 |
| batch 4가 가장 안정적이나 total time이 길다 | batch 8을 현실 후보로 둠 |
| batch 16이 가장 빠르고 안정적 | batch size보다 다른 병목을 우선 |
| batch size를 낮추면 visible gap도 줄어듦 | batch 전환/후처리 또는 memory pressure 연관 |
| batch size를 낮춰도 gap이 그대로 | application 구조 자체 병목 가능성 |

---

## 7.1 Phase 1-A: 동기 batch loop 구조 개선

현재 코드가 다음 구조라면 vLLM은 다음 batch를 미리 볼 수 없다.

```python
for batch in batches:
    prompts = []
    for image in batch:
        prompts.append(build_prompt(image))
    outputs = llm.generate(prompts, sampling_params)
```

따라서 batch size 자체 비교와 별도로, request 제출 구조를 바꾸는 실험을 진행한다.

| run id | 구조 | chunk/page 수 | 목적 |
| --- | --- | --- | --- |
| `sync_loop_bs16` | 현재 동기 loop | 16 | baseline |
| `sync_loop_chunk32` | 동기 loop, 더 큰 chunk | 32 | vLLM에 더 많은 request를 한 번에 제출 |
| `sync_loop_chunk48` | 동기 loop, 더 큰 chunk | 48 | 30GB MIG에서 OOM/속도 균형 확인 |
| `sync_prefetch_bs16` | 다음 batch prompt prefetch | 16 | `build_prompt`와 generate 겹치기 |
| `sync_prefetch_postprocess` | prompt prefetch + postprocess 분리 | 16 | visible gap 추가 감소 확인 |
| `vllm011_builtin_registry_check` | vLLM 0.11.0 registry 확인 | 없음 | `DeepseekOCR2ForCausalLM` built-in 등록 여부 확인 |
| `official_vllm_1image` | vLLM 내장 `DeepseekOCR2ForCausalLM` + local model path | 1 | DeepSeek repo custom code 없이 공식 vLLM 로드 확인. 0.11.0에서는 실패 가능성이 높음 |
| `vllm011_custom_backport_1image` | vLLM 0.11.0 + DeepSeekOCR2 custom/backport | 1 | 0.11.0 고정 시 custom 등록으로 동작 가능한지 확인 |
| `compat_clip_latest_tf` | CLIP + vLLM 요구 Transformers | 1 sample | CLIP이 최신 Transformers env에서 동작하는지 확인 |
| `compat_heron_rtdetrv2_latest_tf` | Heron101(RT-DETRv2 custom) + vLLM 요구 Transformers | 1 sample | RT-DETRv2 기반 Heron101이 최신 Transformers env에서 동작하는지 확인 |
| `async_smoke_1image` | V1 AsyncLLM smoke test | 1 | DeepSeekOCR V2 async path 로드 가능성 확인 |

결정 기준:

| 결과 | 해석 |
| --- | --- |
| chunk 32/48에서 total time 감소, OOM 없음 | 현재 batch 16이 vLLM scheduling 기회를 작게 줬을 가능성 |
| chunk 확대 시 OOM 또는 tail latency 증가 | 30GB MIG에서는 batch/chunk를 줄이고 pipeline 중심으로 개선 |
| prefetch에서 visible gap 감소 | `build_prompt` 또는 prepare가 application gap의 원인 |
| prefetch 효과 없음, generate가 대부분 | vLLM 내부 prefill/decode/KV cache 최적화 우선 |
| vLLM 0.11.0 registry에 DeepseekOCR2 없음 | 0.11.0 built-in 경로는 불가. custom/backport 또는 버전 업그레이드 필요 |
| 공식 vLLM local path 1-image 성공 | DeepSeek custom vLLM 코드 복사보다 vLLM 내장 구현 우선 검토 |
| vLLM 0.11.0 custom/backport 1-image 성공 | 동기 `LLM.generate` 기준 사용 가능. async는 별도 확인 |
| CLIP/Heron101 최신 Transformers smoke test 성공 | 같은 FastAPI process에 통합 가능 |
| CLIP 또는 Heron101 최신 Transformers smoke test 실패 | DeepSeekOCR V2를 별도 process/container로 분리 |
| async smoke test 실패 | V0 동기 `LLM.generate` 유지 + application pipeline 개선 |

---

## 8. Phase 2: 모델 공존 영향 비교

가능하면 DeepSeekOCR V2만 로드한 상태로 같은 실험을 실행한다.

Heron101/CLIP은 파라미터가 작은 모델이라는 전제를 둔다. 따라서 이 phase의 목적은 "공존 구조가 병목이다"를 증명하는 것이 아니라, 실제 free memory delta, vLLM KV cache capacity, latency 차이가 충분히 큰지 확인하는 것이다.

| run id | 모델 구성 | batch size | gpu mem util |
| --- | --- | --- | --- |
| `deepseek_only_bs16_util08` | DeepSeekOCR only | 16 | 0.8 |
| `deepseek_only_bs8_util08` | DeepSeekOCR only | 8 | 0.8 |
| `all_models_bs16_util08` | Heron101 + CLIP + DeepSeekOCR | 16 | 0.8 |
| `all_models_bs8_util08` | Heron101 + CLIP + DeepSeekOCR | 8 | 0.8 |

목적:

- Heron101/CLIP 상주가 vLLM KV cache와 latency에 미치는 영향 확인
- 차이가 작으면 공존 구조는 후순위로 내리고 DeepSeekOCR V2 dtype, batch, visual token, output length를 우선 최적화
- 같은 batch size에서 DeepSeekOCR 단독이 얼마나 빨라지는지 확인

결정 기준:

| 결과 | 해석 |
| --- | --- |
| DeepSeekOCR 단독에서 KV cache block 수가 크게 증가 | 모델 공존이 memory capacity를 줄임 |
| DeepSeekOCR 단독에서 generate가 크게 빨라짐 | memory 또는 GPU resource 경합 가능성 |
| 단독과 공존의 generate는 비슷하지만 gap만 다름 | application pipeline 또는 다른 모델 후처리 영향 가능 |
| 단독과 공존 차이가 작음 | Heron101/CLIP이 작은 모델이라는 가정과 일치. 모델 공존보다 batch/옵션/전처리 병목 가능성 |

운영 제약상 단독 실행이 어렵다면, 최소한 Heron101/CLIP 미로드 상태에서 vLLM 초기화 로그의 KV cache capacity만 비교한다.

---

## 9. Phase 3: `gpu_memory_utilization` 비교

가장 유망한 batch size를 고른 뒤 `gpu_memory_utilization`만 바꾼다.

예를 들어 Phase 1에서 batch 8이 유망하다면 다음처럼 진행한다.

| run id | batch size | gpu mem util | 모델 구성 |
| --- | --- | --- | --- |
| `bs8_util08` | 8 | 0.8 | all models |
| `bs8_util07` | 8 | 0.7 | all models |
| `bs8_util06` | 8 | 0.6 | all models |

목적:

- memory pressure를 낮추면 안정성과 latency가 좋아지는지 확인
- KV cache capacity 감소가 throughput을 얼마나 떨어뜨리는지 확인

결정 기준:

| 결과 | 결정 |
| --- | --- |
| 0.7이 0.8보다 안정적이고 total time도 유사/개선 | 0.7 후보 |
| 0.6에서 total time이 크게 증가 | KV cache 부족 또는 scheduler 효율 저하 |
| 0.8에서만 OOM/warning | 0.7 이하 사용 |
| 모든 값 차이가 작음 | 병목은 memory utilization보다 다른 곳 |

---

## 10. Phase 4: Output Limit 비교

OCR 출력 길이가 긴 batch가 tail latency를 만든다면 `max_tokens` 계열 설정을 비교한다.

먼저 baseline에서 output length 분포를 본다.

```text
p50 output chars
p90 output chars
p95 output chars
max output chars
finish reason
```

그 후 다음 실험을 진행한다.

| run id | batch size | max tokens | 목적 |
| --- | --- | --- | --- |
| `tokens_current` | best batch | current | 기준 |
| `tokens_mid` | best batch | current보다 낮은 값 | tail latency 감소 |
| `tokens_high` | best batch | current보다 높은 값 또는 유지 | 결과 잘림 확인 |

결정 기준:

| 결과 | 해석 |
| --- | --- |
| 낮은 max tokens에서 total time 감소, 잘림 없음 | decode 상한이 과도했음 |
| 낮은 max tokens에서 finish reason이 length로 자주 끝남 | OCR 누락 위험 |
| max tokens 변경에도 latency 차이 작음 | decode보다 prefill/prepare/memory 병목 |

결과 품질 확인이 중요하므로, 이 실험은 성능만 보고 결정하지 않는다.

---

## 11. Phase 5: `max_model_len` / `max_num_batched_tokens`

이 단계는 앞선 실험에서 generate 내부, 특히 prefill 또는 memory 병목이 의심될 때 진행한다.

### `max_model_len`

실험 조건:

```text
output이 잘리지 않는 범위에서 max_model_len을 줄인다.
```

기대 효과:

- KV cache capacity 효율 증가
- maximum concurrency 개선 가능

위험:

- visual token + output token이 긴 page에서 실패 또는 잘림

### `max_num_batched_tokens`

실험 조건:

```text
high-res page batch에서 latency spike가 보일 때 조정한다.
```

기대 효과:

- 한 번에 너무 큰 visual token batch가 들어가는 것을 제한
- memory spike 완화

위험:

- 너무 낮으면 GPU utilization 저하
- prefill overhead 증가

이 단계는 vLLM 로그와 실제 에러 메시지를 같이 봐야 한다.

---

## 12. Phase 6: 고급 옵션 검토

다음 옵션은 초기 실험에서 바로 건드리지 않는다.

| 항목 | 검토 조건 |
| --- | --- |
| prefix caching | OCR text prompt가 동일하고 vLLM 버전/모델이 지원할 때 |
| chunked prefill | visual token이 커서 prefill latency spike가 확인될 때 |
| dtype 변경 | 현재 dtype이 fp32이거나 memory 압박이 클 때 |
| quantization | weight memory가 주요 병목이고 OCR 품질 검증 가능할 때 |
| CUDA graph/eager | vLLM 로그에서 graph capture 또는 dynamic shape 문제가 보일 때 |

이 항목들은 개선 여지가 있지만 원인 분리 전에 적용하면 해석이 어려워진다.

---

## 13. Phase 7: Dtype 품질 검증

`float32 -> bfloat16` 변경은 이미 속도 개선이 관찰된 상태다. 따라서 dtype 실험의 목적은 "bf16이 빠른가"보다 "bf16이 OCR 품질을 유지하는가"에 둔다.

| run id | dtype | batch size | 목적 |
| --- | --- | --- | --- |
| `dtype_fp32_quality_sample` | float32 | small sample | 품질 기준선 |
| `dtype_bf16_quality_sample` | bfloat16 | same sample | 운영 후보 품질 확인 |

전체 100페이지를 fp32로 반복 실행할 필요는 낮다. 이미 fp32가 300초 수준으로 느렸기 때문에, 품질 비교는 대표 page 샘플로 수행한다.

샘플은 다음을 포함한다.

```text
작은 글씨 page
숫자/단위가 많은 page
표가 있는 page
긴 본문 page
특수문자 또는 수식이 있는 page
```

비교 항목:

| 항목 | 판단 |
| --- | --- |
| 문자 누락 | fp32 대비 bf16에서 누락이 늘었는가 |
| 숫자 오류 | 숫자/단위가 바뀌었는가 |
| 표 구조 | column/cell 순서가 유지되는가 |
| 출력 길이 | 비정상적으로 짧아지거나 길어졌는가 |
| 반복/잘림 | 반복 출력 또는 max token 잘림이 늘었는가 |

결정 기준:

```text
bf16 품질이 fp32와 실무상 동등
  -> bf16을 기본 dtype으로 유지

bf16에서 특정 page type 품질 저하
  -> 해당 page type만 fp32 fallback 또는 image preprocessing 조정 검토

bf16 품질 저하가 전반적
  -> 속도 개선과 품질 요구사항 사이 trade-off 재검토
```

---

## 14. 실험 결과 기록 템플릿

`09_experiment_results.md`에는 다음 형식으로 기록한다.

```markdown
## Run: baseline_current

### 설정

| 항목 | 값 |
| --- | --- |
| model set | Heron101 + CLIP + DeepSeekOCR |
| batch size | 16 |
| max num seqs | 16 |
| gpu memory utilization | 0.8 |
| dtype | bfloat16 |
| max tokens | current |
| max model len | current |

### 결과

| 지표 | 값 |
| --- | --- |
| total sec |  |
| pages/sec |  |
| avg prepare ms |  |
| avg generate ms |  |
| avg postprocess ms |  |
| avg visible gap ms |  |
| peak used MB |  |
| min free MB |  |
| max output chars |  |

### 해석

- 가장 큰 시간 구간:
- memory pressure 여부:
- output length 영향:
- 다음 실험:
```

---

## 15. 의사결정 트리

실험 후 다음 순서로 판단한다.

```text
1. total_sec가 줄었는가?
  no -> 병목 구간이 바뀌었는지 확인
  yes -> 품질/안정성 확인

2. visible_gap_ms가 큰가?
  yes -> application prepare/postprocess 개선 우선
  no -> generate 내부 최적화 우선

3. generate_ms가 큰가?
  yes -> batch size, max_num_seqs, max_num_batched_tokens, max_tokens 확인

4. memory free가 낮은가?
  yes -> batch size, gpu_memory_utilization, 모델 공존 구조 확인

5. output length가 긴 batch만 느린가?
  yes -> max_tokens, page grouping, adaptive batch size 확인

6. image pixels가 큰 batch만 느린가?
  yes -> image resize/crop/tiling, batch grouping 확인

7. bf16 품질이 fp32와 달라졌는가?
  yes -> page type별 fallback 또는 preprocessing 조정 검토
```

---

## 16. 추천 첫 실행 세트

처음 폐쇄망에서 바로 실행할 최소 세트는 다음이다.

```text
Run 1: baseline_current
  models = all
  batch_size = 16
  gpu_memory_utilization = 0.8
  dtype = bfloat16

Run 2: bs8_util08_all_models
  models = all
  batch_size = 8
  gpu_memory_utilization = 0.8
  dtype = bfloat16

Run 3: bs4_util08_all_models
  models = all
  batch_size = 4
  gpu_memory_utilization = 0.8
  dtype = bfloat16
```

이 세 개만으로도 다음 질문에 답할 수 있다.

```text
batch 16이 정말 최적인가?
batch를 줄이면 visible gap이 줄어드는가?
batch를 줄이면 memory pressure가 줄어드는가?
total time은 batch size에 어떻게 반응하는가?
```

그 다음 가능한 경우에만 다음을 실행한다.

```text
Run 4: deepseek_only_bs8_util08
Run 5: bs8_util07_all_models
Run 6: bs8_util06_all_models
Run 7: dtype_fp32_quality_sample
Run 8: dtype_bf16_quality_sample
```

---

## 17. 다음 문서로 넘길 질문

다음 문서는 `09_experiment_results.md`다. 실제 폐쇄망 서버에서 얻은 결과를 이 문서의 템플릿에 맞춰 기록한다.

다음 질문을 결과 문서에서 답한다.

- baseline 300초 문제는 재현됐는가?
- 가장 큰 병목은 `generate_ms`, `visible_gap_ms`, `prepare_ms`, `postprocess_ms` 중 무엇인가?
- batch size 16/8/4 중 어떤 값이 가장 낫는가?
- 세 모델 공존이 DeepSeekOCR 성능에 얼마나 영향을 주는가? Heron101/CLIP이 작은 모델이라는 조건에서도 유의미한 delta가 있는가?
- `gpu_memory_utilization` 변경이 안정성 또는 속도에 영향을 줬는가?
- `bfloat16`이 `float32` 대비 OCR 품질을 유지했는가?
- 최종 추천 설정과 추가 코드 개선 방향은 무엇인가?
