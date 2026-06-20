# Async Serving Considerations

> 작성일: 2026-06-20  
> 목적: 현재 FastAPI + DeepSeekOCR V2 + vLLM 직접 호출 구조에서 동기 실행이 병목이 될 수 있는지, vLLM의 비동기 엔진을 DeepSeekOCR V2에 적용할 수 있는지 판단한다.  
> 근거: vLLM 최신 문서와 DeepSeek-OCR-2 공개 GitHub 코드 기준으로 정리한다. 폐쇄망 사내 코드의 `deepseekocrv2.py`는 직접 확인할 수 없으므로, 실제 적용 가능성은 해당 서버의 vLLM 버전과 custom model 등록 방식으로 검증해야 한다.

---

## 1. 결론 요약

vLLM 공식 supported models 문서 기준으로는 DeepSeekOCR V2를 vLLM에서 사용할 수 있는 방향으로 들어와 있다. stable/latest 문서의 multimodal generative text generation 표에 `DeepseekOCR2ForCausalLM`, 모델명 `DeepSeek-OCR-2`, 예시 HF 모델 `deepseek-ai/DeepSeek-OCR-2`가 올라와 있다.

그러나 이 내용을 vLLM `0.11.0`에 그대로 적용하면 안 된다. `v0.11.0` tag의 `vllm/model_executor/models/registry.py`를 확인하면 `_MULTIMODAL_MODELS`에 `DeepseekOCR2ForCausalLM`이 없다. 반면 `main` 브랜치에는 `vllm/model_executor/models/deepseek_ocr2.py` 구현이 존재한다.

추가로 확인한 release tag 기준으로도 `v0.12.0`, `v0.13.0`, `v0.22.0`, `v0.23.0` registry에는 `DeepseekOCR2ForCausalLM`이 확인되지 않았다. 따라서 현재 확인 가능한 범위에서는 "정식 release 중 이 버전을 쓰면 된다"가 아니라, `main` 또는 nightly/source build에서 DeepSeekOCR2 구현이 들어간 commit을 써야 한다고 보는 것이 맞다.

따라서 현재 기준 결론은 다음이다.

```text
vLLM 0.11.0 built-in DeepSeekOCR V2 지원
  -> 확인 결과: 없음으로 보는 것이 맞음

vLLM 0.12.0/0.13.0/0.22.0/0.23.0 built-in DeepSeekOCR V2 지원
  -> 확인 결과: registry에 없음

vLLM main/latest docs의 DeepSeekOCR V2 지원
  -> 있음

공식 release 선택
  -> DeepseekOCR2가 포함된 다음 release 또는 main/nightly/source build 필요

vLLM 0.11.0에서 DeepSeekOCR V2 사용
  -> 공식 built-in 경로가 아니라 DeepSeek-OCR-2 repo의 custom vLLM 코드 또는 backport 필요

vLLM 0.11.0에서 DeepSeekOCR V2 async 처리
  -> built-in 모델이 없으므로 공식 V1 AsyncLLM 경로 사용 가능하다고 보기 어려움
```

다만 이 사실과 "V1 AsyncLLM 경로를 바로 운영에 써도 된다"는 사실은 분리해야 한다. 해당 supported models 섹션은 이 모델들이 주로 `LLM.generate` API를 받는다고 설명한다. 즉 공식 지원의 1차 의미는 vLLM의 모델 로딩/멀티모달 입력/`LLM.generate` 추론 경로를 지원한다는 것이다.

즉 정리하면 다음과 같다.

```text
vLLM 공식 stable/latest supported models에 DeepSeek-OCR-2가 있는가?
  -> 있음

vLLM 0.11.0에 DeepSeek-OCR-2가 built-in으로 있는가?
  -> v0.11.0 registry 기준 없음

따라서 vLLM 0.11.0에서 DeepSeek-OCR-2 전용 GitHub vLLM 코드를 반드시 복사해야 하는가?
  -> 0.11.0을 고정한다면 복사/backport/custom registration 가능성을 봐야 함

그럼 바로 V1 AsyncLLM/online serving까지 보장되는가?
  -> 별도 확인 필요
```

현재 공개 DeepSeek-OCR-2 GitHub vLLM 예제 기준으로는 DeepSeekOCR V2가 vLLM V1 `AsyncLLM` 경로를 공식적으로 사용한다고 보기 어렵다.

이유는 다음과 같다.

- DeepSeek-OCR-2 vLLM 예제는 `VLLM_USE_V1=0`을 명시한다.
- 같은 예제는 `from vllm import LLM, SamplingParams`를 사용한다.
- 실제 추론은 `llm.generate(batch_inputs, sampling_params=...)`로 한 번에 호출한다.
- 즉 공개 예제는 vLLM V0 + offline `LLM.generate()` 동기 호출을 전제로 작성되어 있다.

반면 vLLM 최신 문서 기준으로는 vLLM 자체에 비동기 API가 있다.

- 최신 문서에서 `AsyncLLMEngine`은 V1 `AsyncLLM`의 alias로 설명된다.
- `AsyncLLM`은 vLLM engine의 asynchronous wrapper다.
- `AsyncLLM.generate(...)`는 async iterator로 output을 streaming 받을 수 있다.
- vLLM 문서에는 synchronous `LLM` entrypoint가 multimodal preprocessing을 serial하게 처리하고, async renderer path는 `vllm serve` 또는 `AsyncLLM`에서 사용된다는 설명이 있다.

따라서 정확한 판단은 다음처럼 나눈다.

```text
vLLM 0.11.0 공식 DeepSeek-OCR-2 모델 지원
  -> v0.11.0 registry 기준 없음
  -> 설치된 vLLM에서 `DeepseekOCR2ForCausalLM`이 잡히는지 반드시 확인

vLLM 자체의 비동기 지원
  -> 있음

DeepSeekOCR V2 공개 vLLM 코드의 V1 AsyncLLM 사용
  -> 근거 없음
  -> 오히려 VLLM_USE_V1=0으로 V1을 끔

폐쇄망 deepseekocrv2.py에서 바로 AsyncLLM으로 교체 가능성
  -> 미확정
  -> custom model이 V1에서 정상 동작하는지 별도 smoke test 필요
```

---

## 2. 공식 vLLM 구현을 그대로 쓸 수 있는지

vLLM `0.11.0` 고정이라면 가능성이 낮다. `v0.11.0` registry에 `DeepseekOCR2ForCausalLM`이 없기 때문에, DeepSeek-OCR-2 전용 repo 안의 `DeepSeek-OCR2-vllm` 코드를 쓰거나, 최신 vLLM의 `deepseek_ocr2.py` 관련 구현을 backport/custom registration 해야 할 가능성이 높다.

반대로 설치 버전을 `main` 이후 또는 DeepSeekOCR2가 포함된 정식 release로 올릴 수 있다면, 내장 구현으로 로드하는 경로를 먼저 시도하는 것이 맞다.

기본 형태는 vLLM multimodal 입력 규칙을 따른다. 외부망이 연결된 예시는 Hugging Face repo id를 쓰지만, 폐쇄망에서는 같은 모델 snapshot을 로컬 디렉터리에 옮긴 뒤 그 경로를 넘기면 된다.

```python
from PIL import Image
from vllm import LLM, SamplingParams

model_path = "/models/DeepSeek-OCR-2"

llm = LLM(
    model=model_path,
    tokenizer=model_path,
    dtype="bfloat16",
    gpu_memory_utilization=0.8,
    # 필요 시:
    # hf_config_path=model_path,
    # trust_remote_code=False,
    # limit_mm_per_prompt={"image": 1},
)

image = Image.open("page.png")
prompt = "<image>\nOCR this image."

outputs = llm.generate(
    {
        "prompt": prompt,
        "multi_modal_data": {"image": image},
    },
    SamplingParams(temperature=0, max_tokens=4096),
)
```

다만 prompt 형식은 임의로 정하면 안 된다. vLLM 문서도 multimodal prompt는 Hugging Face repo에 문서화된 형식을 따르라고 설명한다. DeepSeek-OCR-2가 요구하는 `<image>` 토큰, OCR instruction, special token이 있다면 기존 DeepSeek 예제의 prompt builder와 비교해서 맞춰야 한다.

폐쇄망 서버에서는 다음 순서로 확인한다.

```text
1. python -c "import vllm; print(vllm.__version__)"
2. 설치된 vLLM에 DeepseekOCR2ForCausalLM 구현이 있는지 확인
3. 기존 DeepSeek repo 코드 없이 1 image LLM.generate smoke test
4. 기존 deepseekocrv2.py 결과와 text 품질 비교
5. batch 16에서 memory/latency 비교
```

이 smoke test가 성공하면 현재 `deepseekocrv2.py`의 custom loader는 공식 vLLM 구현으로 단순화할 수 있다. 실패하면 설치 vLLM 버전이 낮거나, 모델 repo revision/prompt/processor 입력이 현재 코드와 맞지 않는 것이다. 특히 vLLM `0.11.0`에서는 built-in 미등록 가능성이 높으므로 실패가 정상에 가깝다.

폐쇄망 반입 시 모델 디렉터리는 Hugging Face snapshot 구조를 유지해야 한다.

```text
/models/DeepSeek-OCR-2/
  config.json
  generation_config.json
  tokenizer.json / tokenizer.model / tokenizer_config.json
  preprocessor_config.json / processor_config.json
  special_tokens_map.json
  model.safetensors 또는 model-000xx-of-000xx.safetensors
  model.safetensors.index.json
  필요한 경우 chat_template 또는 remote code 파일
```

공식 vLLM 구현을 쓰는 경우 `trust_remote_code=False`가 우선이다. 로드가 실패하고 모델 repo의 custom Python code가 꼭 필요한 구조라면 `trust_remote_code=True`를 검토하지만, 폐쇄망에서는 해당 코드 파일도 같이 반입되어 있어야 한다.

폐쇄망에서 외부 접근을 막고 테스트할 때는 다음 환경변수를 함께 설정하면 누락 파일을 빨리 찾을 수 있다.

```text
HF_HUB_OFFLINE=1
TRANSFORMERS_OFFLINE=1
HF_DATASETS_OFFLINE=1
```

---

## 3. 현재 동기 구조가 만드는 문제

현재 설명된 구조는 다음에 가깝다.

```text
FastAPI request
  -> 이미지 목록 수신
  -> 16개 batch 구성
  -> llm.generate(batch_0)
  -> 결과 반환 대기
  -> postprocess
  -> 다음 16개 batch 구성
  -> llm.generate(batch_1)
  -> ...
```

이 구조에서 `llm.generate()`가 동기 호출이면 호출한 Python coroutine/thread는 결과가 나올 때까지 기다린다.

중요한 점은 vLLM 내부가 batch를 효율적으로 실행하더라도, application loop가 다음 batch를 늦게 제출하면 vLLM은 아직 도착하지 않은 다음 batch를 스케줄링할 수 없다는 것이다.

```text
batch_0 generate 중
  -> vLLM GPU 사용

batch_0 generate 완료
  -> Python 결과 반환
  -> output parsing
  -> CPU 후처리
  -> 다음 batch 준비

batch_1 generate 호출
  -> 이때서야 vLLM에 다음 request가 들어감
```

사용자가 본 "progress bar는 빠르게 올라가는데 다음 16개 progress bar가 생기기까지 오래 걸림"은 이 구조와 잘 맞는다. 이 경우 병목은 vLLM 내부 prefill/decode일 수도 있지만, `generate_done -> next_generate_start` 사이의 application gap일 수도 있다.

---

## 4. 현재 코드 패턴 해석

현재 코드는 다음 형태다.

```python
for batch in batches:
    sampling_params = SamplingParams(...)
    prompts = []
    for image in batch:
        prompts.append(build_prompt(image))
    outputs = llm.generate(prompts, sampling_params)
```

이 구조의 핵심 문제는 batch가 vLLM에 순차적으로 제출된다는 점이다.

```text
batch_0 prompt 구성
  -> batch_0 llm.generate 완료까지 block
  -> batch_1 prompt 구성
  -> batch_1 llm.generate 완료까지 block
  -> ...
```

따라서 vLLM은 `batch_0`을 실행하는 동안 `batch_1`의 존재를 모른다. 이 경우 vLLM의 continuous batching은 "이미 들어온 request들 사이"에서만 동작할 수 있고, application이 아직 제출하지 않은 다음 batch까지 자동으로 끌어와 섞을 수 없다.

즉 현재 코드는 vLLM을 빠른 batch 함수처럼 쓰고 있지만, serving engine처럼 계속 request를 받아 scheduler queue를 채우는 구조는 아니다.

---

## 5. 변경 가능한 구조

### 4.1 가장 단순한 변경: prompt를 먼저 모두 만들고 한 번에 제출

메모리가 허용된다면 가장 단순한 구조는 모든 page prompt를 먼저 만들고 `llm.generate()`를 한 번만 호출하는 것이다.

```python
sampling_params = SamplingParams(...)

prompts = []
for image in images:
    prompts.append(build_prompt(image))

outputs = llm.generate(prompts, sampling_params)
```

장점:

- application level batch loop가 사라진다.
- vLLM이 전체 page request를 한 번에 보고 내부에서 스케줄링할 수 있다.
- `generate_done -> next_generate_start` gap 자체가 사라진다.

단점:

- 100 page 이상을 한 번에 넣으면 visual token, KV cache, output token 때문에 30GB MIG에서 OOM 위험이 크다.
- OCR page별 출력 길이 편차가 커서 tail latency가 생길 수 있다.
- DeepSeekOCR V2의 multimodal preprocessing 메모리도 커질 수 있다.

현재 H200 MIG 30GB 조건에서는 바로 100 page 전체 제출보다 `32`, `48`, `64` page 정도의 larger chunk부터 실험하는 편이 안전하다.

```python
chunk_size = 32
for chunk in chunks(images, chunk_size):
    prompts = [build_prompt(image) for image in chunk]
    outputs = llm.generate(prompts, sampling_params)
```

이 방식은 엄밀히 말하면 여전히 chunk 단위 동기 호출이지만, 현재 batch 16보다 vLLM에 더 큰 scheduling 기회를 준다.

### 4.2 V0 동기 유지 + 다음 batch 미리 준비

DeepSeekOCR V2가 V1 AsyncLLM을 지원하지 않아도 application pipeline은 가능하다.

핵심은 `llm.generate(current_batch)`가 도는 동안 CPU에서 `next_batch`의 prompt/image preprocessing을 미리 끝내는 것이다.

```python
from concurrent.futures import ThreadPoolExecutor

def prepare_batch(batch):
    return [build_prompt(image) for image in batch]

sampling_params = SamplingParams(...)

with ThreadPoolExecutor(max_workers=1) as pool:
    next_future = pool.submit(prepare_batch, batches[0])

    for i in range(len(batches)):
        prompts = next_future.result()

        if i + 1 < len(batches):
            next_future = pool.submit(prepare_batch, batches[i + 1])

        outputs = llm.generate(prompts, sampling_params)
        postprocess(outputs)
```

주의:

- 위 구조는 `build_prompt()`가 CPU 작업일 때 효과가 있다.
- `build_prompt()` 내부에서 GPU tensor 생성, `.cuda()`, `torch.cuda.synchronize()`가 있으면 오히려 경합이 생길 수 있다.
- `postprocess(outputs)`가 길다면 postprocess도 별도 thread/process로 분리할 수 있다.

더 나은 구조는 prepare와 postprocess를 모두 분리하는 것이다.

```text
prepare worker
  -> 다음 batch prompt 구성

main GPU worker
  -> llm.generate(current_prompts)

postprocess worker
  -> 이전 outputs 저장/정리
```

이 방식은 vLLM continuous batching 자체를 완전히 활용하는 것은 아니지만, batch 사이 application gap을 줄이는 실용적인 개선이다.

### 4.3 request 단위를 page로 쪼개서 queue에 넣기

진짜 serving에 가까운 구조는 FastAPI request 안에서 직접 `for batch`를 돌지 않고, page 또는 small batch를 내부 job queue에 넣는 방식이다.

```text
FastAPI request
  -> images 수신
  -> page job N개 생성
  -> internal queue에 제출
  -> worker가 queue에서 계속 꺼내 vLLM에 제출
  -> 결과를 page order대로 모아 응답
```

하지만 동기 `LLM.generate()`만 쓰는 V0 구조에서는 worker가 한 번 `generate()`를 호출하면 완료까지 block된다. 따라서 이 구조만으로는 vLLM 내부 continuous batching이 크게 늘지 않는다.

효과를 내려면 다음 중 하나가 필요하다.

```text
1. worker가 여러 request의 page들을 모아 larger dynamic batch를 만든다.
2. vLLM OpenAI-compatible server 또는 AsyncLLM처럼 engine queue에 request를 계속 넣는 경로를 쓴다.
```

### 4.4 vLLM server 또는 AsyncLLM 경로

DeepSeekOCR V2가 해당 경로에서 정상 동작한다면 가장 vLLM다운 구조는 다음이다.

```text
FastAPI
  -> page 또는 small batch request를 vLLM engine에 비동기 제출
  -> vLLM scheduler queue에 여러 request가 쌓임
  -> continuous batching이 prefill/decode 단계에서 동작
```

다만 DeepSeek-OCR-2 공개 예제는 `VLLM_USE_V1=0`과 동기 `LLM.generate()`를 사용하므로, 이 경로는 바로 설계 전제로 두면 위험하다. 먼저 `1 image async smoke test`가 필요하다.

---

## 6. 추천 변경 순서

현재 코드 기준으로는 다음 순서가 가장 안전하다.

```text
1. 현재 batch 16 구조에 timestamp 추가
   - build_prompt_start/done
   - generate_start/done
   - postprocess_start/done
   - next_generate_start

2. batch 16 -> chunk 32 또는 48 실험
   - OOM 없고 total time이 줄면 larger submit이 효과 있음

3. build_prompt prefetch 적용
   - generate 중 다음 batch prompt 준비
   - visible gap 감소 여부 확인

4. postprocess 분리
   - output parsing/save가 긴 경우에만 적용

5. AsyncLLM/V1 smoke test
   - import 가능 여부가 아니라 실제 DeepSeekOCR V2 1-image generate 성공 여부 확인

6. Async path 성공 시 request/page queue 구조 검토
```

이 순서가 중요한 이유는 async migration은 실패 가능성이 있고, 성공해도 단일 PDF 한 건의 GPU compute 시간을 직접 줄이지는 않기 때문이다. 현재 관찰된 공백이 application loop에서 생기는지 먼저 확인해야 한다.

---

## 7. vLLM Async가 해결할 수 있는 것과 없는 것

비동기 방식이 항상 단일 PDF 처리 시간을 줄이는 것은 아니다.

### 해결 가능성이 있는 것

```text
여러 request가 동시에 들어옴
  -> AsyncLLM / vllm serve가 request를 계속 받아 engine queue에 넣음
  -> vLLM scheduler가 continuous batching 기회를 더 많이 얻음
```

또는 application이 다음 batch를 미리 준비해서 engine에 빨리 제출할 수 있다면 batch 사이 공백을 줄일 수 있다.

```text
batch_0 generate 중
  -> CPU thread에서 batch_1 image/token 준비

batch_0 완료 직후
  -> batch_1 즉시 제출
```

### 해결하지 못하는 것

```text
단일 PDF를 16 page씩 순차 처리
  -> 다음 batch를 generate 완료 후에야 만들 수 있음
  -> postprocess가 동기적으로 길다
  -> AsyncLLM만 바꿔도 GPU compute 자체는 빨라지지 않음
```

즉 async는 GPU kernel을 마법처럼 빠르게 만드는 옵션이 아니라, request 제출과 결과 소비를 겹쳐서 vLLM scheduler가 놀지 않도록 만드는 구조적 개선이다.

---

## 8. DeepSeekOCR V2에서 바로 확인해야 할 호환성

폐쇄망 서버에서 다음 항목을 확인해야 한다.

```text
vLLM version
VLLM_USE_V1 값
DeepSeekOCR custom model 등록 방식
AsyncLLMEngine 또는 AsyncLLM import 가능 여부
DeepSeekOCR2ForCausalLM이 V1 model runner에서 정상 로드되는지
multi_modal_data 입력 형식이 AsyncLLM.generate에서 그대로 통과되는지
```

최소 smoke test는 다음 방향이다.

```python
import os

print("VLLM_USE_V1 =", os.environ.get("VLLM_USE_V1"))

try:
    from vllm import AsyncLLMEngine
    print("AsyncLLMEngine import OK", AsyncLLMEngine)
except Exception as e:
    print("AsyncLLMEngine import failed", repr(e))

try:
    from vllm.v1.engine.async_llm import AsyncLLM
    print("AsyncLLM import OK", AsyncLLM)
except Exception as e:
    print("AsyncLLM import failed", repr(e))
```

그 다음 실제 모델 로드 smoke test를 해야 한다.

```text
1 image
  -> 기존 동기 LLM.generate 결과 저장
  -> AsyncLLM 또는 AsyncLLMEngine 방식으로 같은 입력 실행
  -> 로드 성공 여부
  -> output text 동일성
  -> memory peak
  -> latency
```

이 테스트에서 model load 단계에서 실패하면, 현재 DeepSeekOCR V2 custom vLLM 구현은 V1 async 경로와 맞지 않는다고 판단한다.

---

## 9. 현실적인 개선 순서

현재는 바로 V1 AsyncLLM으로 바꾸는 것보다 다음 순서가 더 안전하다.

### 1단계. 동기 구조에서 gap을 정확히 측정

```text
batch_i_generate_done
batch_i_postprocess_done
batch_i+1_prepare_start
batch_i+1_generate_start
```

이 네 timestamp를 찍어야 한다.

판단 기준:

```text
generate_done -> next_generate_start가 길다
  -> async/pipeline 구조 개선 후보

generate_start -> generate_done이 길다
  -> vLLM 옵션, batch size, KV cache, dtype, visual token 문제
```

### 2단계. V0 동기 LLM 유지 + application pipeline 개선

DeepSeekOCR V2가 V1 async를 지원하지 않아도 application level pipeline은 가능하다.

```text
CPU thread/process
  -> 다음 batch image/token 준비

GPU thread
  -> 현재 batch llm.generate

postprocess thread
  -> 이전 batch output parsing/save
```

목표는 GPU generate가 끝나는 순간 다음 batch를 바로 넣는 것이다.

### 3단계. FastAPI endpoint concurrency 제한

같은 vLLM 객체에 여러 요청이 동시에 들어가면 안정성과 latency가 흔들릴 수 있다.

```text
asyncio.Semaphore(1)
  -> DeepSeekOCR generate 구간은 1개 request만 허용

또는 job queue
  -> request는 job id만 받고
  -> background worker가 순차/배치 처리
```

단일 30GB MIG에서 DeepSeekOCR V2가 큰 모델이면 무제한 async concurrency는 오히려 OOM과 tail latency를 키울 수 있다.

### 4단계. V1 AsyncLLM 호환성 smoke test

`VLLM_USE_V1=1` 또는 기본 V1에서 DeepSeekOCR custom model이 로드되고 1-image inference가 성공할 때만 async migration을 검토한다.

---

## 10. 실험 매트릭스에 추가할 항목

| run id | engine path | request submit 방식 | batch pipeline | expected check |
| --- | --- | --- | --- | --- |
| `sync_llm_current` | V0 `LLM.generate` | sequential | 없음 | 현재 baseline |
| `sync_llm_pipelined_prepare` | V0 `LLM.generate` | sequential | 다음 batch prepare 겹침 | visible gap 감소 여부 |
| `sync_llm_pipelined_post` | V0 `LLM.generate` | sequential | postprocess 분리 | postprocess gap 감소 여부 |
| `async_import_smoke` | V1 `AsyncLLM` 또는 `AsyncLLMEngine` | 1 request | 없음 | 모델 로드/1 image 성공 여부 |
| `async_batch_submit` | V1 async path | multiple requests | engine queue 사용 | 성공 시 throughput/latency 비교 |

현재 가장 먼저 할 실험은 `async_import_smoke`가 아니라 `sync_llm_current`의 gap 계측이다. async가 필요한지 판단하려면 먼저 `generate_done -> next_generate_start`가 실제로 큰지 확인해야 한다.

---

## 11. 출처

- vLLM stable supported models: `DeepseekOCR2ForCausalLM`, DeepSeek-OCR-2, `deepseek-ai/DeepSeek-OCR-2` listed under multimodal generative text generation  
  https://docs.vllm.ai/en/stable/models/supported_models/#text-generation_1
- vLLM latest supported models: same DeepSeek-OCR-2 listing in developer preview docs  
  https://docs.vllm.ai/en/latest/models/supported_models/#text-generation_1
- vLLM multimodal inputs: offline image input uses `{"prompt": ..., "multi_modal_data": {"image": image}}` and batched lists of that schema  
  https://docs.vllm.ai/en/stable/features/multimodal_inputs/
- vLLM latest API docs: `AsyncLLMEngine` is an alias of `vllm.v1.engine.async_llm.AsyncLLM`  
  https://docs.vllm.ai/en/latest/api/vllm/index.html
- vLLM latest API docs: `AsyncLLM` is an asynchronous wrapper for the vLLM engine  
  https://docs.vllm.ai/en/latest/api/vllm/v1/engine/async_llm/
- vLLM async streaming example using `async for output in engine.generate(...)`  
  https://docs.vllm.ai/en/latest/examples/offline_inference/async_llm_streaming/
- vLLM docs/code note: offline `LLM` entrypoint uses synchronous multimodal preprocessing; async renderer path is used by `vllm serve` / `AsyncLLM`  
  https://docs.vllm.ai/en/latest/api/vllm/index.html
- DeepSeek-OCR-2 vLLM PDF example: `VLLM_USE_V1=0`, `from vllm import LLM`, `llm.generate(...)`  
  https://github.com/deepseek-ai/DeepSeek-OCR-2/blob/main/DeepSeek-OCR2-master/DeepSeek-OCR2-vllm/run_dpsk_ocr2_pdf.py
