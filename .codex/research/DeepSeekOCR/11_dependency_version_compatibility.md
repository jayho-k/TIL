# Dependency Version Compatibility

> 작성일: 2026-06-20  
> 목적: DeepSeekOCR V2를 공식 vLLM 구현으로 사용할 때, 기존 CLIP/Heron101 모델이 요구하는 낮은 Transformers 버전과 충돌할 수 있는지 판단한다.

---

## 1. 결론

vLLM version과 Transformers version은 직접 관련이 있다.

`pip install vllm`은 vLLM이 검증한 `transformers`, `tokenizers`, `torch`, `pydantic`, `fastapi` 등의 버전을 함께 요구한다. 따라서 같은 Python environment 안에서 다음 세 모델을 모두 로드하면 하나의 `transformers` 버전을 공유하게 된다.

```text
same Python env / same FastAPI process
  -> transformers version 1개
  -> CLIP
  -> Heron101
  -> DeepSeekOCR V2 via vLLM
```

CLIP/Heron101이 낮은 Transformers 버전에서만 검증되어 있고, DeepSeekOCR V2를 지원하는 최신 vLLM이 높은 Transformers 버전을 요구한다면 dependency conflict가 생길 수 있다.

```text
CLIP/Heron101
  -> old transformers 필요

DeepSeekOCR V2 official vLLM
  -> new vLLM 필요
  -> new transformers 필요

같은 venv
  -> 둘 중 하나의 요구사항을 포기해야 함
```

---

## 2. vLLM이 Transformers에 의존하는 이유

vLLM은 자체 scheduler, KV cache, attention backend를 갖지만, 모델 로딩과 tokenizer/processor/config 해석에는 Hugging Face 생태계를 많이 사용한다.

특히 multimodal 모델에서는 다음 부분이 Transformers와 강하게 묶인다.

```text
AutoConfig
AutoTokenizer
AutoProcessor / image processor
model architecture config
special token
chat template
multimodal input processor
```

DeepSeekOCR V2 같은 VLM/OCR 모델은 텍스트 모델보다 더 민감하다.

```text
image processor 변경
special image token 처리 변경
processor output schema 변경
model config field 추가/변경
```

따라서 "vLLM이 모델을 공식 지원한다"는 말은 보통 "해당 vLLM release와 그 release가 요구하는 Transformers 버전 조합에서 검증됐다"는 의미에 가깝다.

---

## 3. 확인된 vLLM 요구사항

공식 vLLM repository의 requirements 기준으로 다음을 확인했다.

| vLLM version | Transformers requirement |
| --- | --- |
| `v0.9.2` | `transformers >= 4.51.1` |
| `v0.10.2` | `transformers >= 4.55.2` |
| `v0.11.0` | `transformers >= 4.55.2` |
| latest main | 더 높은 최신 Transformers 요구 가능 |

즉 CLIP/Heron101이 `transformers 4.2x` 같은 낮은 버전에 묶여 있다면, DeepSeekOCR V2를 공식 vLLM 구현으로 쓰기 위한 최신 vLLM과 같은 environment에 넣기 어렵다.

추가로 중요한 점은 `v0.11.0`이 DeepSeekOCR V2 built-in 지원 버전이라고 단정할 수 없다는 것이다. `v0.11.0` tag의 model registry에는 `DeepseekOCR2ForCausalLM`이 확인되지 않았고, `main` 브랜치에는 `deepseek_ocr2.py` 구현이 확인된다. 따라서 `0.11.0`을 고정하면 dependency 버전은 맞더라도 모델 registry 문제로 official built-in 로딩이 실패할 수 있다.

같은 기준으로 `v0.12.0`, `v0.13.0`, `v0.22.0`, `v0.23.0` release tag의 registry도 확인했지만 `DeepseekOCR2ForCausalLM`은 확인되지 않았다. 따라서 현 시점의 결론은 "특정 stable release 번호를 고르면 된다"가 아니라, DeepSeekOCR2 구현과 registry 등록이 들어간 `main`/nightly/source build commit을 골라서 wheel을 고정해야 한다는 쪽에 가깝다.

---

## 4. CLIP과 Heron101에 대한 해석

CLIP은 Transformers에서 오래 지원된 모델이라 최신 Transformers에서도 동작할 가능성이 높다. 공개 Hugging Face 문서 기준으로 CLIP model docs는 `transformers v4.6.0` 계열 문서에서 확인되고, 최신 문서에도 유지되어 있다. 즉 CLIP 자체는 `v4.6.0` 이상부터 최신 `v4.5x`/`v5.x` 계열까지 모델 지원이 이어지는 것으로 볼 수 있다.

다만 운영 코드가 오래된 API에 의존하면 문제가 생길 수 있다.

예시:

```text
CLIPFeatureExtractor
  -> 최신 버전에서는 CLIPImageProcessor 쪽으로 이동/대체될 수 있음

processor return field
  -> pixel_values, attention_mask 등 처리 방식 확인 필요

tokenizer/image processor 저장 파일
  -> 오래된 checkpoint 구조와 최신 AutoProcessor 호환성 확인 필요
```

Heron101은 사용자가 설명한 기준으로는 별도 공개 모델명이 아니라 Transformers의 RT-DETRv2를 문서에 맞게 custom한 모델이다. 따라서 호환성 판단은 `RTDetrV2ForObjectDetection` / `RTDetrImageProcessor` 기준으로 보는 것이 맞다.

공개 Hugging Face 문서 기준으로 RT-DETRv2 문서는 `transformers v4.49.0`에서 확인되고, `v4.50.0`, `v4.51.3`, `v4.53.3`, `v4.55.4`, 최신 문서에서도 유지된다. 즉 vLLM `v0.9.2`가 요구하는 `transformers >= 4.51.1`, vLLM `v0.10.2`/`v0.11.0`이 요구하는 `transformers >= 4.55.2`와 버전 축에서는 맞을 가능성이 높다.

다만 Heron101이 RT-DETRv2를 그대로 호출하되 일부 head, label map, postprocess, image resize, checkpoint key mapping을 custom했다면 최신 Transformers에서 결과 동일성 검증은 필요하다.

확인해야 할 항목:

```text
from_pretrained 성공 여부
AutoConfig 로드 여부
AutoProcessor/AutoTokenizer 로드 여부
1-image 또는 1-sample inference 결과
기존 old-transformers 결과와 output 동일성
warning/deprecation이 error로 이어지는지
```

현재 공개 정보 기준의 1차 판정:

| component | 공개 확인 결과 | vLLM 최신 env 가능성 |
| --- | --- | --- |
| CLIP | Transformers `v4.6.0` 문서와 최신 문서 모두에서 CLIP 지원 확인 | 높음. 다만 `CLIPFeatureExtractor`/`CLIPImageProcessor` API 차이 smoke test 필요 |
| Heron101 | RT-DETRv2 기반 custom. RT-DETRv2 문서는 Transformers `v4.49.0`부터 확인, 최신 문서까지 유지 | 높음. 다만 custom head/postprocess/checkpoint key mapping smoke test 필요 |
| DeepSeekOCR V2 | vLLM stable/latest supported models에 `DeepseekOCR2ForCausalLM` 확인 | vLLM 지원 버전에서 가능 |

---

## 5. 운영 구조 선택지

### 선택지 A. 한 environment에 모두 올림

```text
FastAPI process
  -> transformers latest
  -> vLLM latest
  -> CLIP
  -> Heron101
  -> DeepSeekOCR V2
```

장점:

- 구조가 단순하다.
- 기존 FastAPI endpoint 통합이 쉽다.
- HTTP hop이 없다.

단점:

- dependency conflict 위험이 가장 크다.
- CLIP/Heron101이 최신 Transformers에서 깨지면 전체 서버가 막힌다.
- vLLM이 요구하는 torch/tokenizers/pydantic/fastapi 버전까지 같이 올라갈 수 있다.

이 선택지는 CLIP/Heron101이 최신 Transformers에서 smoke test를 통과할 때만 가능하다.

### 선택지 B. DeepSeekOCR V2만 별도 process/container로 분리

```text
FastAPI model server A
  -> old transformers
  -> CLIP
  -> Heron101

DeepSeekOCR server B
  -> vLLM official supported version
  -> new transformers
  -> DeepSeekOCR V2
```

장점:

- dependency conflict를 깨끗하게 분리한다.
- DeepSeekOCR V2는 vLLM이 검증한 버전 조합을 그대로 쓸 수 있다.
- CLIP/Heron101은 기존 안정 버전을 유지할 수 있다.

단점:

- 프로세스/서버 간 호출이 추가된다.
- 같은 MIG 30GB를 공유하면 GPU memory는 여전히 나눠 써야 한다.
- 별도 process마다 CUDA context overhead가 생길 수 있다.

현재처럼 CLIP/Heron101이 작은 모델이라면 dependency 안정성을 위해 이 구조가 더 현실적일 수 있다. GPU memory 관점에서는 손해가 조금 있을 수 있지만, version conflict로 전체 migration이 막히는 위험을 줄인다.

### 선택지 C. CLIP/Heron101을 최신 Transformers에 맞게 migration

```text
old CLIP/Heron101 code
  -> latest transformers smoke test
  -> processor/tokenizer API 수정
  -> output regression 비교
  -> same FastAPI process 유지
```

장점:

- process 분리 없이 운영 가능하다.
- HTTP hop과 별도 배포 비용이 없다.

단점:

- Heron101 custom code 수정이 필요할 수 있다.
- 기존 결과와 동일성 검증이 필요하다.
- migration 비용이 예상보다 커질 수 있다.

---

## 6. 추천 순서

먼저 같은 environment 통합을 가정하지 말고, compatibility matrix를 만든다.

```text
1. 현재 운영 env 버전 기록
   - python
   - torch
   - transformers
   - tokenizers
   - vLLM
   - fastapi
   - pydantic

2. DeepSeekOCR V2 공식 vLLM env 생성
   - vLLM supported version 설치
   - DeepseekOCR2ForCausalLM 1-image smoke test

3. 같은 env에서 CLIP smoke test
   - load
   - preprocess
   - 1 inference
   - 기존 결과와 비교

4. 같은 env에서 Heron101 smoke test
   - load
   - preprocess
   - 1 inference
   - 기존 결과와 비교

5. 둘 다 통과하면 same process 가능

6. 하나라도 실패하면 DeepSeekOCR V2를 별도 process/container로 분리
```

---

## 7. 실험 기록 템플릿

| component | old env result | vLLM env result | decision |
| --- | --- | --- | --- |
| DeepSeekOCR V2 official vLLM load |  |  |  |
| DeepSeekOCR V2 1-image OCR |  |  |  |
| CLIP load |  |  |  |
| CLIP inference |  |  |  |
| Heron101 load |  |  |  |
| Heron101 inference |  |  |  |

판단 기준:

```text
DeepSeekOCR V2만 최신 env에서 성공
  -> DeepSeekOCR 분리 운영

CLIP/Heron101도 최신 env에서 성공
  -> same FastAPI process 유지 가능

CLIP은 성공, Heron101 실패
  -> Heron101만 old env 유지하거나 DeepSeekOCR 분리
```

---

## 8. 출처

- vLLM `v0.9.2` requirements: `transformers >= 4.51.1`  
  https://raw.githubusercontent.com/vllm-project/vllm/v0.9.2/requirements/common.txt
- vLLM `v0.10.2` requirements: `transformers >= 4.55.2`  
  https://raw.githubusercontent.com/vllm-project/vllm/v0.10.2/requirements/common.txt
- vLLM `v0.11.0` requirements: `transformers >= 4.55.2`  
  https://raw.githubusercontent.com/vllm-project/vllm/v0.11.0/requirements/common.txt
- vLLM stable supported models: `DeepseekOCR2ForCausalLM`, `deepseek-ai/DeepSeek-OCR-2` listed under multimodal text generation  
  https://docs.vllm.ai/en/stable/models/supported_models/#text-generation_1
