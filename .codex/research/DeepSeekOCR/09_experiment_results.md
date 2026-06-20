# Experiment Results

> 작성일: 2026-06-20  
> 목적: 폐쇄망 사내 PC에서 DeepSeekOCR V2 + vLLM 실험을 실행한 뒤 결과를 기록하고, 최종 병목과 추천 설정을 도출한다.  
> 상태: 아직 실제 실험 결과는 없다. 이 문서는 `08_experiment_matrix.md`의 실험을 실행한 뒤 채우는 결과 템플릿이다.

---

## 1. 결과 기록 원칙

실험 결과는 전체 시간만 기록하지 않는다. 반드시 다음 네 가지를 함께 본다.

```text
1. total_sec
2. generate_ms
3. visible_gap_ms
4. memory pressure
```

최종 결론은 다음 조건을 모두 만족해야 한다.

```text
속도 개선
  + OOM 또는 memory warning 없음
  + OCR 결과 잘림 없음
  + 병목 원인을 설명 가능
```

---

## 2. 공통 환경

| 항목 | 값 |
| --- | --- |
| 실행 날짜 |  |
| 서버 |  |
| GPU | H200 MIG |
| visible GPU memory | 30GB |
| CUDA version |  |
| PyTorch version |  |
| vLLM version |  |
| 운영 dtype | bfloat16 |
| DeepSeekOCR V2 model path/version |  |
| Heron101 model path/version |  |
| CLIP model path/version |  |
| Heron101/CLIP parameter scale | small-parameter models |
| FastAPI worker 수 |  |
| 테스트 문서 |  |
| page count |  |
| image 입력 형태 |  |

---

## 3. Baseline Result

### Run: `baseline_current`

| 항목 | 값 |
| --- | --- |
| model set | Heron101 + CLIP + DeepSeekOCR V2 |
| batch size | 16 |
| max num seqs | 16 |
| gpu memory utilization | 0.8 |
| dtype | bfloat16 |
| max model len | current |
| max tokens | current |

### 결과

| 지표 | 값 |
| --- | --- |
| total sec |  |
| pages/sec |  |
| avg prepare ms |  |
| avg generate ms |  |
| avg postprocess ms |  |
| avg visible gap ms |  |
| p95 visible gap ms |  |
| peak used MB |  |
| min free MB |  |
| max output chars |  |
| OOM/warning |  |
| OCR 잘림 여부 |  |

### 해석

```text
가장 큰 시간 구간:
memory pressure 여부:
output length 영향:
image resolution 영향:
다음 실험:
```

---

## 4. Batch Size Results

### Summary

| run id | batch size | total sec | pages/sec | avg generate ms | avg visible gap ms | peak used MB | min free MB | 품질 이슈 | 판단 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `bs16_util08_all_models` | 16 |  |  |  |  |  |  |  |  |
| `bs8_util08_all_models` | 8 |  |  |  |  |  |  |  |  |
| `bs4_util08_all_models` | 4 |  |  |  |  |  |  |  |  |

### 해석 체크

| 질문 | 답 |
| --- | --- |
| batch 16이 가장 빠른가? |  |
| batch 8이 total time과 안정성의 균형점인가? |  |
| batch 4는 gap/memory를 줄였는가? |  |
| batch size를 줄이면 `visible_gap_ms`도 줄었는가? |  |
| batch size를 줄이면 memory pressure가 줄었는가? |  |

### 결정

```text
선택한 batch size:
선택 이유:
다음 실험:
```

---

## 5. Model Co-location Results

### Summary

| run id | model set | batch size | total sec | avg generate ms | avg gap ms | kv cache blocks | peak used MB | 판단 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `all_models_bs16_util08` | all models | 16 |  |  |  |  |  |  |
| `deepseek_only_bs16_util08` | DeepSeekOCR only | 16 |  |  |  |  |  |  |
| `all_models_bs8_util08` | all models | 8 |  |  |  |  |  |  |
| `deepseek_only_bs8_util08` | DeepSeekOCR only | 8 |  |  |  |  |  |  |

### 해석 체크

| 질문 | 답 |
| --- | --- |
| DeepSeekOCR 단독에서 KV cache block 수가 늘었는가? |  |
| DeepSeekOCR 단독에서 generate time이 줄었는가? |  |
| 단독과 공존의 차이가 memory 때문인가, application gap 때문인가? |  |
| 세 모델 공존이 batch size 선택에 영향을 주는가? |  |
| Heron101/CLIP이 작은 모델이라는 조건에서도 공존 delta가 유의미한가? |  |

### 결정

```text
모델 공존 영향:
Heron101/CLIP은 작은 모델이므로, 단독/공존 차이가 작으면 공존 구조보다 DeepSeekOCR V2 dtype, batch, visual token, output length를 우선 원인으로 본다.
운영 구조 변경 필요성:
다음 실험:
```

---

## 6. `gpu_memory_utilization` Results

### Summary

| run id | batch size | gpu mem util | total sec | avg generate ms | avg gap ms | peak used MB | min free MB | warning/OOM | 판단 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `bs8_util08` | 8 | 0.8 |  |  |  |  |  |  |  |
| `bs8_util07` | 8 | 0.7 |  |  |  |  |  |  |  |
| `bs8_util06` | 8 | 0.6 |  |  |  |  |  |  |  |

실제 best batch size가 8이 아니면 위 표의 batch size를 바꿔 기록한다.

### 해석 체크

| 질문 | 답 |
| --- | --- |
| 0.8에서 memory warning 또는 OOM이 있는가? |  |
| 0.7이 더 안정적인가? |  |
| 0.6에서 throughput이 크게 떨어지는가? |  |
| memory utilization 변경이 visible gap에도 영향을 주는가? |  |

### 결정

```text
선택한 gpu_memory_utilization:
선택 이유:
다음 실험:
```

---

## 7. Output Limit Results

### Output Length Distribution

| 지표 | 값 |
| --- | --- |
| output chars p50 |  |
| output chars p90 |  |
| output chars p95 |  |
| output chars max |  |
| length finish count |  |
| stop/eos finish count |  |

### Summary

| run id | max tokens | total sec | avg generate ms | max output chars | length finish count | 품질 이슈 | 판단 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `tokens_current` | current |  |  |  |  |  |  |
| `tokens_mid` |  |  |  |  |  |  |  |
| `tokens_high` |  |  |  |  |  |  |  |

### 결정

```text
선택한 max tokens:
선택 이유:
OCR 잘림 여부:
다음 실험:
```

---

## 8. Advanced Option Results

이 섹션은 필요할 때만 채운다.

| 옵션 | 실행 여부 | 결과 요약 | 결정 |
| --- | --- | --- | --- |
| `max_model_len` 조정 |  |  |  |
| `max_num_batched_tokens` 조정 |  |  |  |
| prefix caching |  |  |  |
| chunked prefill |  |  |  |
| dtype 변경 |  |  |  |
| quantization |  |  |  |
| CUDA graph/eager 관련 |  |  |  |

---

## 9. Dtype Quality Results

`float32`에서 100페이지 이상 처리 시간이 약 300초였고, `bfloat16`으로 변경한 뒤 확실히 빨라진 관찰이 있다. 이 섹션은 bf16을 기본 운영 dtype으로 유지해도 되는지 품질 관점에서 확인한다.

### Summary

| run id | dtype | sample pages | total sec | avg generate ms | 품질 이슈 | 판단 |
| --- | --- | --- | --- | --- | --- | --- |
| `dtype_fp32_quality_sample` | float32 |  |  |  |  | 기준 |
| `dtype_bf16_quality_sample` | bfloat16 |  |  |  |  |  |

### Page Quality Check

| page | page type | fp32 output issue | bf16 output issue | difference | accept |
| --- | --- | --- | --- | --- | --- |
|  | small text |  |  |  |  |
|  | numbers/units |  |  |  |  |
|  | table |  |  |  |  |
|  | long text |  |  |  |  |
|  | symbols/formula |  |  |  |  |

### 결정

```text
bf16 속도 개선:
bf16 품질 저하 여부:
fp32 fallback 필요 여부:
최종 dtype:
```

---

## 10. Batch Detail Table

느린 batch를 찾기 위해 대표 run의 batch별 결과를 붙인다.

| run id | batch | size | prepare ms | generate ms | post ms | visible gap ms | pixels total | output chars | free MB start | free MB done |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | 0 |  |  |  |  |  |  |  |  |  |
|  | 1 |  |  |  |  |  |  |  |  |  |
|  | 2 |  |  |  |  |  |  |  |  |  |
|  | 3 |  |  |  |  |  |  |  |  |  |

### 느린 batch 해석

```text
가장 느린 batch:
느린 이유 후보:
image resolution 영향:
output length 영향:
memory 영향:
```

---

## 11. 최종 병목 판정

아래 항목 중 하나 이상을 선택한다.

| 병목 유형 | 해당 여부 | 근거 |
| --- | --- | --- |
| vLLM generate 내부 병목 |  |  |
| batch prepare 병목 |  |  |
| output postprocess 병목 |  |  |
| visible gap/application loop 병목 |  |  |
| GPU memory pressure |  |  |
| 세 모델 공존 영향 |  | Heron101/CLIP이 작은 모델이라는 전제에서 measured delta 기반 판단 |
| 긴 OCR output tail latency |  |  |
| image resolution/visual token 영향 |  |  |
| dtype 영향 |  |  |

판정 문장:

```text
현재 가장 큰 병목은 ______ 이다.
근거는 ______ 이다.
따라서 우선 개선 방향은 ______ 이다.
```

---

## 12. 최종 추천 설정

| 항목 | 추천값 | 근거 |
| --- | --- | --- |
| batch size |  |  |
| max num seqs |  |  |
| gpu memory utilization |  |  |
| dtype | bfloat16 |  |
| max tokens |  |  |
| max model len |  |  |
| max num batched tokens |  |  |
| 모델 공존 구조 |  | 단독/공존 delta가 클 때만 우선 개선 |

---

## 13. 추가 개선 작업

실험 후 필요하면 다음 작업을 별도로 진행한다.

| 개선 작업 | 우선순위 | 이유 |
| --- | --- | --- |
| batch prepare와 generate pipeline화 |  |  |
| output parsing 비동기화 |  |  |
| page resolution 기반 grouping |  |  |
| 긴 page 작은 batch 처리 |  |  |
| DeepSeekOCR 전용 MIG/GPU 분리 |  |  |
| Heron101/CLIP lazy load 또는 별도 프로세스 분리 |  |  |
| vLLM server 분리 검토 |  |  |
| 특정 page type fp32 fallback 검토 |  |  |

---

## 14. 결론

실험 전 결론은 내리지 않는다. 결과 입력 후 다음 형식으로 결론을 작성한다.

```text
Baseline은 ___초였고, 최종 후보 설정은 ___초였다.
개선폭은 ___%이다.
가장 큰 개선 요인은 ___이다.
bf16 품질 검증 결과는 ___이다.
남은 병목은 ___이다.
운영 적용 전 추가 확인이 필요한 항목은 ___이다.
```
