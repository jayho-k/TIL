# DeepSeekOCR V2 Model Notes

> 작성일: 2026-06-20  
> 목적: DeepSeekOCR V2를 vLLM으로 최적화하기 전에 모델 자체에서 확인해야 할 입력 형식, image prompt, generation 설정, vLLM 연동 주의사항을 정리한다.  
> 자료 기준: 현재 대화에서 확인된 운영 정보와 `02`, `03` 문서의 구조 분석을 기반으로 한다. 실제 `deepseekocrv2.py` 구현 파일은 폐쇄망 사내 PC에 있어 이 환경에서 직접 확인할 수 없다. 따라서 모델 카드, 실행 로그, 사용자가 공유하는 코드 일부로 확인해야 하는 항목은 "확인 대상"으로 분리한다.

---

## 1. 이 문서에서 답할 질문

이 문서는 DeepSeekOCR V2 자체에 대해 다음 질문을 정리한다.

- DeepSeekOCR V2는 입력 이미지를 어떤 형태로 받는가?
- GitHub 원본 기준 image/preprocess progress bar는 어떤 코드 경로에서 출력되는가?
- 모델이 요구하는 prompt 형식과 image placeholder 형식은 무엇인가?
- 권장 image 크기, crop/tiling, preprocessing 방식이 있는가?
- generation parameter 중 OCR 품질과 속도에 직접 영향을 주는 값은 무엇인가?
- vLLM direct call에서 주의해야 할 multimodal 입력 형식은 무엇인가?
- 현재 batch size 16, sequence 설정 16, `gpu_memory_utilization=0.8`이 모델 특성과 충돌할 수 있는가?

---

## 2. 현재 확인된 운영 정보

현재 대화에서 확인된 사실은 다음이다.

```text
Model Server
  -> FastAPI로 endpoint 노출
  -> startup 시 deepseekocrv2.py의 load() 호출
  -> DeepSeekOCR V2는 vLLM Python 객체를 직접 호출
  -> images를 batch size 16으로 처리
  -> vLLM sequence 관련 설정도 16에 맞춤
  -> gpu_memory_utilization = 0.8
  -> 같은 H200 MIG 30GB 안에 Heron101, CLIP, DeepSeekOCR V2가 모두 상주
  -> Heron101/CLIP은 파라미터가 작은 모델이므로 공존 영향은 실제 메모리 delta로 검증 필요
```

또한 관찰된 현상은 다음이다.

```text
DeepSeekOCR 실행 중 image/preprocess 계열 progress bar는 빠르게 올라간다.
하지만 한 batch가 끝난 뒤 다음 16개 batch progress bar가 생기기까지 오래 걸린다.
```

이 정보만으로는 DeepSeekOCR V2 내부 병목을 단정할 수 없다. 다음 절부터는 모델 코드에서 확인해야 할 항목을 구조화한다.

---

## 3. DeepSeekOCR V2 입력 경로에서 확인할 항목

DeepSeekOCR V2의 입력 경로는 다음 단계로 나눠 확인해야 한다.

```text
raw image
  -> image object 생성
  -> resize / crop / tiling
  -> normalize / tensor 변환
  -> image prompt 또는 multimodal prompt 구성
  -> vLLM input format 변환
  -> generate 호출
```

각 단계의 확인 포인트는 다음이다.

| 단계 | 확인할 내용 | 성능 영향 |
| --- | --- | --- |
| image object 생성 | PIL, OpenCV, bytes, base64 중 어떤 형태인지 | decode/serialization 비용 |
| resize | 고정 크기인지, 원본 해상도 유지인지 | visual token 수, OCR 품질 |
| crop/tiling | 긴 문서 이미지를 여러 crop으로 나누는지 | image 수와 prefill 비용 증가 |
| normalize/tensor | CPU에서 수행되는지 GPU에서 수행되는지 | batch 사이 공백 |
| prompt 구성 | image placeholder와 text prompt를 매번 재생성하는지 | Python overhead |
| vLLM 입력 변환 | vLLM multimodal input 규격에 맞춰 어떤 객체를 넘기는지 | validation/processing 비용 |

현재 증상상 특히 중요한 구간은 progress bar가 뜨기 전과 끝난 뒤다.

```text
progress bar 전
  -> image object 준비
  -> processor
  -> prompt 구성
  -> vLLM input validation

progress bar 후
  -> output parsing
  -> result merge
  -> 다음 batch input 구성
```

---

## 4. Image / Preprocess Progress Bar의 의미

DeepSeek-OCR-2 GitHub 원본의 vLLM PDF 경로에서는 `image prompt`라는 desc의 progress bar는 보이지 않고, `run_dpsk_ocr2_pdf.py`에서 `Pre-processed images` progress bar가 사용된다. 이 구간은 `ThreadPoolExecutor.map(process_single_image, images)`를 감싸며, 각 page image를 `DeepseekOCR2Processor().tokenize_with_images(...)`로 변환해 `batch_inputs`를 만드는 단계다.

원본 기준 의미는 다음이다.

| 구간 | 코드상 역할 | 병목 해석 |
| --- | --- | --- |
| `Pre-processed images` | image resize/crop/tensor 변환, image token 삽입, `multi_modal_data` 생성 | vLLM 호출 전 CPU/PyTorch 입력 준비 |
| `llm.generate(...)` | vLLM multimodal 처리, vision embedding, prefill, decode | 실제 모델 추론 |
| output loop | text parsing, bounding box 처리, crop image 저장, mmd/pdf 저장 | 후처리 |

따라서 이 progress bar가 빠르다는 것은 `tokenize_with_images` 기반 입력 준비가 빠르다는 의미에 가깝다. 실제 vision encoder forward, image embedding 생성, LLM prefill/decode는 `llm.generate(...)` 안에서 수행된다.

폐쇄망 사내 구현에서 progress bar label이 `image prompt`라면, 원본의 `Pre-processed images`와 같은 구간인지 확인해야 한다. 확인할 코드는 다음 패턴이다.

```python
tqdm(..., desc="Pre-processed images")
tqdm(..., desc="image prompt")
DeepseekOCR2Processor().tokenize_with_images(...)
llm.generate(...)
```

중요한 점은 progress bar가 빠르다고 해서 전체 DeepSeekOCR 처리 단계가 빠르다는 뜻은 아니라는 것이다. progress bar 이후의 `llm.generate(...)`와 output 후처리가 더 큰 병목일 수 있다.

---

## 5. Prompt 형식과 Placeholder

VLM 모델은 보통 text prompt 안에 image placeholder를 넣고, 별도의 image 객체를 함께 전달한다.

일반화하면 다음 형태다.

```text
Prompt:
  <image>
  Extract text from this document page.

Multimodal data:
  image = page image
```

실제 DeepSeekOCR V2에서 확인해야 할 항목은 다음이다.

- image placeholder token이 무엇인가?
- 한 prompt에 image가 1개만 들어가는가, 여러 image가 들어갈 수 있는가?
- OCR task별 prompt template이 다른가?
- layout, table, markdown, plain text 등 output mode를 지정하는 prompt가 있는가?
- prompt를 매 page마다 새로 만드는가?
- 같은 prompt prefix를 반복한다면 prefix caching 이득이 있는가?

현재처럼 page image를 batch size 16으로 처리한다면, 일반적으로는 다음 구조일 가능성이 높다.

```text
sequence 1: image_001 + OCR prompt
sequence 2: image_002 + OCR prompt
...
sequence 16: image_016 + OCR prompt
```

이 구조에서는 16개 sequence가 같은 text prompt를 공유하더라도 image가 다르기 때문에 KV cache 전체를 공유할 수는 없다. 다만 text prompt prefix가 반복된다면 일부 최적화 가능성을 확인할 수 있다.

---

## 6. Image 크기, Crop, Tiling

OCR 모델에서 image 크기는 품질과 속도 모두에 영향을 준다.

```text
image size 낮춤
  -> visual token 감소
  -> prefill 빨라짐
  -> 작은 글자 인식률 하락 가능

image size 높임
  -> 작은 글자 보존
  -> visual token 증가
  -> memory/prefill 비용 증가
```

확인 대상은 다음이다.

| 항목 | 확인 이유 |
| --- | --- |
| 입력 이미지 권장 해상도 | 불필요하게 큰 이미지를 넣고 있는지 확인 |
| 최대 image size | 초과 시 자동 resize/crop 여부 확인 |
| crop/tiling 방식 | page 1장이 내부적으로 여러 image 조각으로 늘어나는지 확인 |
| aspect ratio 처리 | 문서 페이지 비율이 padding을 많이 만드는지 확인 |
| table/dense page 처리 | 특정 페이지 유형이 과도하게 느린지 확인 |

특히 crop/tiling이 있다면 batch size 16의 의미가 바뀐다.

```text
application batch size = 16 pages
internal tiles per page = 4
actual visual inputs = 64 tiles
```

이 경우 사용자는 16개만 처리한다고 생각하지만, 실제 visual encoder 또는 prefill 부담은 훨씬 클 수 있다.

---

## 7. Generation Parameter 확인

OCR 작업은 창의적인 생성보다 정확하고 안정적인 추출이 중요하다. 따라서 generation parameter는 일반 chatbot과 다르게 봐야 한다.

확인할 항목은 다음이다.

| 설정 | 확인 이유 |
| --- | --- |
| `max_tokens` 또는 `max_new_tokens` | 긴 페이지 decode 시간과 KV cache 증가를 제한 |
| `temperature` | OCR은 보통 낮거나 deterministic한 설정이 적합 |
| `top_p`, `top_k` | sampling 비용과 출력 안정성 확인 |
| stop token / stop sequence | 불필요한 긴 생성을 막는지 확인 |
| repetition penalty | 반복 출력 방지와 속도 영향 확인 |
| beam search 사용 여부 | beam search는 OCR 품질에 도움될 수 있지만 비용 증가 |

성능 관점에서 가장 먼저 봐야 할 값은 `max_tokens` 계열이다.

```text
max_tokens가 너무 큼
  -> 긴 페이지에서 decode가 길어짐
  -> batch tail latency 증가
  -> KV cache 사용량 증가

max_tokens가 너무 작음
  -> OCR 결과가 잘림
  -> 품질 저하
```

따라서 page별 output length를 먼저 기록하고, 실제 필요한 상한을 잡아야 한다.

---

## 8. Dtype이 DeepSeekOCR V2에 줄 수 있는 영향

현재 관찰상 DeepSeekOCR V2를 `float32`로 실행했을 때 100페이지 이상 PDF 처리 시간이 약 300초 수준으로 길었고, `bfloat16`으로 변경한 뒤 확실히 빨라졌다. 이 관찰은 중요한 최적화 근거다.

단순히 "float 크기가 줄어서 빨라졌다"로 끝내면 부족하다. DeepSeekOCR V2 같은 VLM/OCR에서는 dtype 변경이 다음 구간에 동시에 영향을 준다.

```text
float32 -> bfloat16
  -> model weight memory 감소
  -> activation / temporary buffer 감소
  -> KV cache memory 감소 가능
  -> memory bandwidth 부담 감소
  -> H200 Tensor Core 활용 가능성 증가
  -> batch size 또는 KV cache 여유 증가
```

속도 개선은 다음 원인이 섞인 결과일 수 있다.

| 원인 | 설명 |
| --- | --- |
| 메모리 사용량 감소 | 30GB MIG에서 free memory와 KV cache 여유가 늘어남 |
| memory bandwidth 감소 | 같은 연산에서 읽고 쓰는 byte 수가 줄어듦 |
| Tensor Core 활용 | H200에서 bf16 연산 경로가 fp32보다 훨씬 유리할 수 있음 |
| allocator pressure 완화 | temporary buffer와 reserved memory 압박이 줄어 batch 전환이 안정화될 수 있음 |
| batch 유지 가능성 증가 | 같은 batch size 16에서도 OOM 또는 cache 압박이 줄어듦 |

정확도 관점에서는 별도로 검증해야 한다.

```text
bf16 장점
  -> fp16보다 exponent 범위가 넓어 overflow/underflow에 강함
  -> 대형 모델 추론에서 fp16보다 안정적인 경우가 많음

bf16 위험
  -> mantissa precision은 fp32보다 낮음
  -> 작은 차이가 중요한 OCR 문자 판별에서 일부 결과 차이가 생길 수 있음
  -> 표, 작은 글씨, 숫자, 특수문자, 좌표/레이아웃 복원에서 품질 차이를 확인해야 함
```

따라서 dtype 변경은 성능 최적화로 유효하지만, OCR 품질 회귀를 반드시 확인해야 한다.

확인할 품질 항목은 다음이다.

| 항목 | 이유 |
| --- | --- |
| 누락 문자 | 작은 글씨나 저해상도 영역에서 차이 확인 |
| 숫자/단위 | OCR에서 0/O, 1/l 같은 혼동 확인 |
| 표 구조 | cell merge, 줄바꿈, column 순서 유지 확인 |
| 특수문자 | 괄호, 하이픈, 수식, 기호 확인 |
| 긴 문서 안정성 | page 후반부에서 출력 잘림이나 반복 여부 확인 |

결론적으로 `bfloat16`은 현재 관찰상 기본 후보 dtype으로 두는 것이 합리적이다. 다만 최종 적용은 `float32` 대비 OCR 품질 샘플 비교를 통과해야 한다.

---

## 9. vLLM Direct Call 입력 형식

현재 구조는 vLLM OpenAI-compatible server가 아니라 Python direct call이다.

```text
FastAPI endpoint
  -> Python function
  -> llm.generate(...)
```

이 방식에서 확인해야 할 항목은 다음이다.

- `LLM(...)` 생성 시 사용한 모델명과 옵션
- `generate(...)`에 넘기는 prompt 객체 구조
- multimodal data를 어떤 키와 타입으로 넘기는지
- batch 16을 한 번의 `generate` call에 넣는지
- batch 안에서 prompt list와 image list 길이가 정확히 맞는지
- `SamplingParams`를 batch마다 새로 만드는지 재사용하는지
- processor를 vLLM 내부에 맡기는지, 외부에서 수행하는지

성능상 주의할 패턴은 다음이다.

```python
for batch in batches:
    sampling_params = SamplingParams(...)
    prompts = []
    for image in batch:
        prompts.append(build_prompt(image))
    outputs = llm.generate(prompts, sampling_params)
```

이 구조 자체가 나쁜 것은 아니지만, batch마다 반복 생성되는 객체가 많으면 batch 사이 공백이 커질 수 있다. 특히 `build_prompt(image)` 안에서 image preprocessing이 같이 일어나면 progress bar 사이 공백의 원인이 된다.

---

## 10. Batch Size 16과 모델 특성의 충돌 가능성

현재 batch size 16은 다음 조건을 만족할 때만 유리하다.

```text
batch size 16이 유리한 조건
  -> page별 visual token 수가 크지 않음
  -> output 길이 편차가 작음
  -> KV cache block이 충분함
  -> batch 사이 prepare/postprocess 시간이 작음
  -> GPU가 memory-bound보다 compute-bound에 가까움
```

DeepSeekOCR V2가 고해상도 문서 OCR을 위해 많은 visual token 또는 crop을 사용한다면 batch 16은 과할 수 있다.

```text
batch size 16이 불리한 조건
  -> crop/tiling으로 page당 visual input 증가
  -> dense 문서로 output token 증가
  -> MIG 30GB에서 KV cache 부족
  -> Heron101/CLIP 상주로 free memory 부족 가능
  -> 단, 두 모델이 작은 편이면 DeepSeekOCR V2 dtype/visual token/KV cache가 더 큰 원인일 수 있음
  -> batch 안의 긴 page가 전체 반환을 지연
```

따라서 batch size는 모델 권장값이 아니라 현재 환경에서 다시 측정해야 하는 값이다.

---

## 11. DeepSeekOCR V2 코드에서 찾아야 할 위치

폐쇄망 사내 PC에서 실제 코드를 볼 수 있을 때 다음 순서로 확인한다. 이 파일은 현재 research 환경에서 직접 열람할 수 없으므로, 확인 결과는 사용자가 공유하는 로그나 코드 일부를 기준으로 별도 문서에 반영한다.

```text
deepseekocrv2.py
  -> load()
       -> LLM(...) options
       -> tokenizer/processor load
       -> SamplingParams 기본값
  -> predict() 또는 infer()
       -> input image type
       -> batch split
       -> prompt construction
       -> image/preprocess progress bar 위치
       -> llm.generate(...) 호출
       -> output parsing
```

특히 다음 코드 패턴을 찾는다.

```text
tqdm(..., desc="Pre-processed images")
tqdm(..., desc="image prompt")
LLM(...)
SamplingParams(...)
llm.generate(...)
processor(...)
resize
crop
tile
torch.cuda.synchronize()
.cpu()
.numpy()
.item()
gc.collect()
torch.cuda.empty_cache()
```

`torch.cuda.empty_cache()`가 batch마다 호출된다면 메모리 해제처럼 보이지만 실제로는 성능을 악화시킬 수 있다. `.cpu()`, `.numpy()`, `.item()`은 GPU 연산 완료를 기다리는 동기화 지점이 될 수 있다.

---

## 12. 성능 로그에 반드시 남길 모델 메타데이터

DeepSeekOCR V2 모델 특성을 확인하려면 vLLM timing뿐 아니라 모델 입력/출력 메타데이터가 필요하다.

| 항목 | 이유 |
| --- | --- |
| model id/path | 실제 사용 모델 확인 |
| vLLM version | multimodal 지원과 옵션 의미가 버전별로 다를 수 있음 |
| DeepSeekOCR code version | progress bar와 processor 동작 확인 |
| dtype | fp32/bf16 변경 효과와 품질 차이 확인 |
| input image width/height | visual token과 전처리 비용 추정 |
| internal crop/tile count | page당 실제 visual input 수 확인 |
| prompt template hash | prompt가 batch마다 달라지는지 확인 |
| max_tokens | decode 상한 확인 |
| output char/token length | 긴 페이지 병목 확인 |
| finish reason | max_tokens로 잘렸는지 확인 |

초기에는 모든 정보를 완벽히 수집하기보다 다음 네 가지를 먼저 남긴다.

```text
batch index
page index
image width/height
output length
```

이 네 가지와 batch별 시간을 연결하면, 모델 특성 기반 병목 가설을 빠르게 좁힐 수 있다.

---

## 13. 현재 단계의 판단

현재 정보만 놓고 보면 DeepSeekOCR V2 모델 자체의 확정적인 권장 설정을 말하기는 이르다. 그러나 최적화 전에 반드시 확인해야 할 핵심은 명확하다.

```text
1. image/preprocess progress bar가 실제로 측정하는 코드 구간
2. page image 1장이 내부적으로 몇 개의 visual input으로 변환되는지
3. OCR prompt template과 image placeholder 형식
4. max_tokens 계열 설정과 실제 output 길이 분포
5. fp32와 bf16의 속도/품질 차이
6. batch 16이 모델의 visual token/crop 구조와 맞는지
7. vLLM direct call에 넘기는 multimodal input 객체 구조
```

이 확인이 끝나야 `max_num_seqs`, `max_num_batched_tokens`, `gpu_memory_utilization`, batch size 같은 옵션을 의미 있게 조정할 수 있다.

---

## 14. 다음 문서로 넘길 질문

다음 문서는 `05_h200_mig_30gb_memory_analysis.md`다. 여기서는 모델 자체 입력 형식보다 H200 MIG 30GB에서 세 모델이 같이 상주할 때 메모리 예산이 어떻게 나뉘는지 정리한다. Heron101/CLIP은 작은 모델이라는 전제를 두고, 실제 영향이 큰지 측정으로 분리한다.

다음 질문을 다룬다.

- 30GB MIG에서 vLLM이 실제로 사용할 수 있는 메모리는 얼마인가?
- Heron101, CLIP, DeepSeekOCR V2가 상주하면 KV cache block 수가 실제로 얼마나 줄어드는가?
- `gpu_memory_utilization=0.8`은 현재 구조에서 어떤 의미인가?
- batch size 16과 output length가 KV cache에 어떤 압력을 주는가?
- DeepSeekOCR 단독 실행과 세 모델 공존 실행을 어떻게 비교해야 하는가?
