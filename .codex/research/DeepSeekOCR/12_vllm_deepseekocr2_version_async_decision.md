# vLLM DeepSeekOCR2 Version and Async Decision

> 작성일: 2026-06-20  
> 목적: DeepSeekOCR V2를 vLLM 공식 지원 경로로 사용하려면 어떤 vLLM 버전을 봐야 하는지, 그리고 그 버전에서 async/continuous batching으로 갈 수 있는지 판단한다.

---

## 1. 결론

현재 확인 기준에서 DeepSeekOCR V2의 공식 지원 후보는 `vLLM v0.23.0`이다.

근거:

- GitHub latest release API 기준 최신 stable release는 `v0.23.0`이고, published date는 2026-06-15이다.
- vLLM stable supported models 문서의 multimodal text generation 표에 `DeepseekOCR2ForCausalLM`, `DeepSeek-OCR-2`, `deepseek-ai/DeepSeek-OCR-2`가 명시되어 있다.
- 같은 stable 문서는 multimodal generative models가 주로 `LLM.generate` API를 받는다고 설명한다.
- vLLM stable API 문서에는 V1 `AsyncLLM.generate(...)`가 async generator로 존재한다.

따라서 "0.11.0을 유지하면서 built-in async를 쓰자"가 아니라, 다음 순서로 봐야 한다.

```text
vLLM 0.23.0
  -> DeepSeekOCR2 공식 지원 후보
  -> Transformers >= 4.56.0 필요
  -> torch == 2.11.0 build 기준
  -> LLM.generate 경로는 문서상 1차 지원
  -> AsyncLLM 경로는 1-image smoke test로 확정 필요
```

즉 현 시점의 1순위 실험 버전은 `vLLM 0.23.0`이다.

---

## 2. 왜 0.23.0을 봐야 하는가

vLLM 문서에는 `latest`와 `stable`이 나뉜다.

```text
latest
  -> developer preview docs
  -> 아직 release wheel과 1:1로 맞지 않을 수 있음

stable
  -> 현재 stable release 문서
  -> 운영 후보 버전을 고를 때 우선 확인
```

stable supported models에서 DeepSeekOCR2가 보인다는 것은, 최소한 vLLM 프로젝트가 해당 stable 계열에서 이 모델을 공식 지원 대상으로 문서화했다는 뜻이다.

다만 이것만으로 다음이 모두 보장되는 것은 아니다.

```text
보장에 가까운 것
  -> vLLM에서 DeepSeek-OCR-2를 지원 대상으로 본다.
  -> multimodal input + LLM.generate 경로가 1차 사용 경로다.

아직 smoke test가 필요한 것
  -> Python 직접 호출에서 local snapshot path로 로드되는가
  -> V1 AsyncLLM에서 같은 multimodal input이 통과하는가
  -> DeepSeekOCR2가 AsyncLLM에서 continuous batching 효과를 실제로 받는가
  -> 30GB MIG 안에서 CLIP + Heron101 + DeepSeekOCR2가 같이 안정적으로 뜨는가
```

---

## 3. v0.23.0 Dependency Impact

`vLLM v0.23.0` requirements 기준:

```text
transformers >= 4.56.0
tokenizers >= 0.21.1
safetensors >= 0.6.2
fastapi[standard] >= 0.115.0, < 0.137
pydantic >= 2.12.0
torch == 2.11.0  # build-system 기준
python >= 3.10, < 3.15
```

따라서 CLIP/Heron101과의 호환성 검토는 `transformers 4.56.0+` 기준으로 해야 한다.

사용자 조건을 반영하면 다음처럼 판단한다.

```text
CLIP
  -> 작은 모델
  -> Transformers 최신 계열에서 오래 지원된 모델
  -> 호환 가능성이 높음
  -> 단, CLIPFeatureExtractor / CLIPImageProcessor API 차이는 확인 필요

Heron101
  -> RT-DETRv2 기반 custom
  -> RT-DETRv2는 Transformers 4.5x 계열에서 지원됨
  -> 호환 가능성이 있음
  -> 단, custom head / label map / postprocess / checkpoint key mapping 확인 필요

DeepSeekOCR2
  -> vLLM 0.23.0 공식 지원 후보
  -> 30GB MIG에서 bf16 + gpu_memory_utilization 조정 필요
```

---

## 4. Async 가능성 판단

vLLM 자체에는 V1 `AsyncLLM.generate(...)` 경로가 있다.

중요한 점은 "vLLM에 AsyncLLM이 있다"와 "DeepSeekOCR2가 그 경로에서 문제 없이 돈다"는 서로 다른 명제라는 것이다.

현재 판단:

```text
vLLM 0.23.0 + DeepSeekOCR2 + LLM.generate
  -> 1순위 공식 지원 경로로 실험

vLLM 0.23.0 + DeepSeekOCR2 + AsyncLLM.generate
  -> 가능성 있음
  -> 하지만 실제 모델 로드와 1-image inference로 검증해야 함

DeepSeekOCR2 GitHub 예제의 VLLM_USE_V1=0
  -> 예제는 V0 sync generate 기준일 가능성이 큼
  -> 최신 vLLM stable 지원과 별개로, async 지원의 직접 증거는 아님
```

따라서 결론은 다음과 같다.

```text
"가능한 버전이 뭔가?"
  -> 우선 vLLM 0.23.0

"그 버전에서 async까지 된다고 확정 가능한가?"
  -> 문서상 AsyncLLM은 있으나 DeepSeekOCR2 조합은 smoke test 필요

"0.23.0에서 async smoke test가 실패하면?"
  -> vLLM serve/OpenAI-compatible path도 확인
  -> 그래도 실패하면 sync LLM.generate + application queue/pipeline 최적화로 우회
```

---

## 5. 내부망 반입 기준

외부망에서 다음을 고정해서 반입한다.

```text
vllm == 0.23.0
transformers >= 4.56.0
torch == 2.11.0 compatible wheel
tokenizers >= 0.21.1
safetensors >= 0.6.2
DeepSeek-OCR-2 model snapshot
```

내부망에서는 Hugging Face repo id가 아니라 local path로 호출한다.

```python
from vllm import LLM, SamplingParams

model_path = "/models/DeepSeek-OCR-2"

llm = LLM(
    model=model_path,
    tokenizer=model_path,
    dtype="bfloat16",
    gpu_memory_utilization=0.8,
    limit_mm_per_prompt={"image": 1},
)
```

---

## 6. Async Smoke Test 방향

실험 순서:

```text
1. vLLM 0.23.0 환경에서 sync LLM.generate 1-image 성공 확인
2. 같은 prompt/image/sampling_params로 AsyncLLM.generate 1-image 성공 확인
3. 4 image를 request_id 4개로 async 제출해 engine queue 동작 확인
4. 16 page, 32 page에서 total time과 peak memory 비교
5. CLIP + Heron101을 같은 process에 올린 상태에서 다시 확인
```

판단 기준:

```text
sync 성공 + async 성공
  -> FastAPI 내부 queue를 page 단위 request로 바꾸는 방향 검토

sync 성공 + async 실패
  -> vLLM 0.23.0 공식 모델은 쓰되, LLM.generate 기반 chunk/pipeline 최적화

sync 실패
  -> model snapshot, prompt format, trust_remote_code, processor files, vLLM bug 순서로 확인
```

---

## 7. 출처

- vLLM GitHub latest release API: `v0.23.0`, published at 2026-06-15  
  https://api.github.com/repos/vllm-project/vllm/releases/latest
- vLLM stable supported models: `DeepseekOCR2ForCausalLM`, `DeepSeek-OCR-2`, `deepseek-ai/DeepSeek-OCR-2` listed under multimodal text generation  
  https://docs.vllm.ai/en/stable/models/supported_models/#text-generation_1
- vLLM stable supported models note: multimodal generative models primarily accept `LLM.generate`  
  https://docs.vllm.ai/en/stable/models/supported_models/
- vLLM `v0.23.0` requirements: `transformers >= 4.56.0`  
  https://raw.githubusercontent.com/vllm-project/vllm/v0.23.0/requirements/common.txt
- vLLM `v0.23.0` pyproject: Python range and build dependency context  
  https://raw.githubusercontent.com/vllm-project/vllm/v0.23.0/pyproject.toml
- vLLM stable API docs: V1 `AsyncLLM.generate(...)` async generator  
  https://docs.vllm.ai/en/stable/api/vllm/v1/engine/async_llm/
