# VLM/OCR Inference Characteristics

> 작성일: 2026-06-20  
> 목적: DeepSeekOCR V2 같은 VLM 기반 OCR 모델이 일반 텍스트 LLM과 다른 병목을 갖는 이유를 정리한다.  
> 자료 기준: 현재 운영 구조와 로컬 vLLM 조사 문서를 기반으로 한 1차 정리다. DeepSeekOCR V2의 정확한 image processor, image token 수, 권장 입력 크기는 `04_deepseekocr_v2_model_notes.md`에서 공식 자료와 코드 기준으로 확인한다.

---

## 1. 이 문서에서 답할 질문

이 문서는 다음 질문에 답한다.

- VLM/OCR 추론은 일반 텍스트 LLM 추론과 무엇이 다른가?
- DeepSeek-OCR-2 GitHub 코드 기준 image/preprocess progress bar는 어떤 단계인가?
- page image 1장이 token/embedding 관점에서 왜 무거운 입력이 되는가?
- batch size 16이 왜 단순히 "16개 요청"이 아닌가?
- OCR 출력 길이 편차가 batch latency에 어떤 영향을 주는가?
- 현재 관찰된 batch 사이 공백을 VLM/OCR 구조에서 어떻게 해석할 수 있는가?

---

## 2. 일반 LLM과 VLM/OCR의 차이

텍스트 LLM 입력은 이미 token id로 바꿀 수 있는 문자열이다.

```text
Text prompt
  -> tokenizer
  -> token ids
  -> prefill
  -> decode
```

VLM/OCR 입력은 문자열뿐 아니라 이미지가 포함된다.

```text
Page image
  -> image preprocessing
  -> vision encoder or image tokenization
  -> visual embeddings / visual tokens
  -> text prompt와 결합
  -> prefill
  -> decode OCR text
```

이 차이 때문에 VLM/OCR은 다음 병목이 추가된다.

| 구간 | 텍스트 LLM | VLM/OCR |
| --- | --- | --- |
| 입력 전처리 | tokenization 중심 | 이미지 decode, resize, crop, normalize, tensor 변환 |
| 입력 길이 | text token 수 | text token + visual token 수 |
| prefill 비용 | prompt 길이에 비례 | 이미지 해상도/patch/tiling 방식에도 비례 |
| output 길이 | task에 따라 다름 | 문서 밀도에 따라 편차가 큼 |
| batch 구성 | token 길이 중심 | 이미지 크기, visual token, output 길이를 함께 고려 |

따라서 OCR에서는 "batch size가 16"이라는 정보만으로 부하를 판단할 수 없다. 각 이미지가 얼마나 많은 visual token을 만드는지와 출력이 얼마나 긴지가 같이 필요하다.

---

## 3. VLM/OCR 요청의 전체 흐름

현재 서버 구조를 단순화하면 다음과 같다.

```text
Parser Server
  -> page images 생성
  -> Model Server로 images 전달

Model Server
  -> images를 16개 단위로 batch 구성
  -> batch images 준비
  -> DeepSeekOCR V2 processor / prompt 구성
  -> vLLM generate
  -> OCR text 후처리
  -> 다음 batch로 이동
```

VLM/OCR 관점에서 한 batch는 다음처럼 처리된다.

```text
batch images[0:16]
  -> image preprocessing x 16
  -> visual tokenization x 16
  -> OCR prompt 결합 x 16
  -> prefill x 16 sequences
  -> decode x 16 sequences
  -> output parsing x 16
```

여기서 batch 사이 공백은 다음 구간 중 하나일 수 있다.

```text
batch_i generate 완료
  -> output parsing
  -> GPU/CPU sync
  -> Python object 정리
  -> batch_i+1 image preprocessing
  -> batch_i+1 prompt 구성
  -> batch_i+1 generate 시작
```

즉 progress bar가 보이지 않는 시간은 vLLM이 아무 일도 하지 않는 시간이거나, vLLM 바깥에서 다음 입력을 준비하는 시간일 수 있다.

---

## 4. Image / Preprocess Progress Bar 해석

DeepSeek-OCR-2 GitHub 원본의 vLLM PDF 실행 경로를 확인하면, 사용자가 말한 `image prompt`에 해당할 수 있는 전처리 progress bar는 `run_dpsk_ocr2_pdf.py`의 `Pre-processed images` 구간이다. 이 코드는 `ThreadPoolExecutor`로 `process_single_image`를 모든 page image에 적용하고, 그 결과를 `batch_inputs`로 만든 뒤 `llm.generate(batch_inputs, sampling_params=...)`를 호출한다.

원본 흐름은 다음과 같다.

```text
PDF image list
  -> ThreadPoolExecutor.map(process_single_image, images)
  -> tqdm(..., desc="Pre-processed images")
  -> batch_inputs 생성
  -> llm.generate(batch_inputs, sampling_params)
  -> outputs_list 후처리
```

`process_single_image`는 각 image를 다음 형태로 바꾼다.

```python
{
  "prompt": prompt_in,
  "multi_modal_data": {
    "image": DeepseekOCR2Processor().tokenize_with_images(
      images=[image],
      bos=True,
      eos=True,
      cropping=CROP_MODE,
    )
  },
}
```

따라서 GitHub 원본 기준으로 이 progress bar는 vLLM prefill/decode 진행률이 아니다. 더 정확히는 **vLLM 호출 전에 page image를 multimodal input으로 토큰화/전처리해서 `batch_inputs`를 만드는 구간**이다.

### 4.1 `tokenize_with_images`가 하는 일

`DeepseekOCR2Processor.tokenize_with_images`는 prompt 안의 `<image>` token 위치를 기준으로 text를 나누고, image를 전처리한다.

```text
prompt = "<image>\n<|grounding|>Convert the document to markdown."
  -> <image> 기준 text split
  -> image resize / padding
  -> 필요 시 dynamic crop / tiling
  -> image tensor 생성
  -> image token id를 num_image_tokens만큼 input_ids에 삽입
  -> pixel_values, images_crop, images_spatial_crop 반환
```

특히 큰 image에서는 `dynamic_preprocess`가 crop ratio를 계산하고, `IMAGE_SIZE` 단위 crop들을 만든다. 이때 page 1장이 내부적으로 여러 crop tensor가 될 수 있다.

```text
large page image
  -> crop_ratio = count_tiles(...)
  -> images_crop_raw = dynamic_preprocess(...)
  -> local crop tensors
  -> global view tensor
```

### 4.2 vLLM 내부 image token 치환

`deepseek_ocr2.py`의 multimodal processor는 prompt 안의 image token을 실제 image token 개수만큼 교체한다. `_get_prompt_updates`에서 `PromptReplacement`를 반환하고, replacement 함수는 image width/height와 crop 설정을 보고 `get_num_image_tokens(...)`를 호출한다.

```text
single <image> token
  -> PromptReplacement
  -> [image_token_id] * num_image_tokens
```

즉 `<image>`는 문자열상 1개 token처럼 보이지만, vLLM 처리에서는 global view token과 local crop token을 포함한 여러 image token으로 확장된다. README도 dynamic resolution 기본값을 `(0-6) x 768 x 768 + 1 x 1024 x 1024`, 즉 local crop 0~6개와 global view 1개 구조로 설명한다.

### 4.3 모델 forward에서 실제 vision embedding 생성

전처리 progress bar에서 vision encoder forward가 끝나는 것은 아니다. 원본 `deepseek_ocr2.py` 기준으로 실제 image embedding은 model forward 중 `_process_image_input -> _pixel_values_to_embedding` 경로에서 생성된다.

```text
vLLM generate
  -> get_multimodal_embeddings
  -> _process_image_input
  -> _pixel_values_to_embedding
       -> SAM model
       -> Qwen2 encoder as image encoder
       -> projector
       -> global/local visual embeddings
  -> merge_multimodal_embeddings
  -> language model prefill/decode
```

그리고 이 경로는 `torch.bfloat16`을 적극적으로 사용한다. 원본 코드에서도 `sam_model`을 bf16으로 옮기고, `pixel_values`와 `patches`를 bf16으로 변환하는 구간이 있다.

### 4.4 현재 증상에 대한 해석 변경

따라서 progress bar가 빠르다는 사실은 다음만 의미한다.

```text
빠른 것:
  PDF image -> DeepseekOCR2Processor.tokenize_with_images
  prompt + multi_modal_data dict 생성
  batch_inputs 생성
```

반대로 다음은 progress bar 이후에 남아 있다.

```text
남아 있는 것:
  vLLM multimodal prompt replacement
  image token 수 기반 prompt 확장
  vision embedding 생성
  LLM prefill
  decode
  output parsing / markdown 변환 / layout pdf 생성
```

따라서 "progress bar는 빠른데 다음 progress bar까지 오래 걸린다"는 증상은 원본 코드 기준으로 다음 두 가능성을 우선 의심해야 한다.

```text
1. llm.generate(...) 내부가 오래 걸림
   -> vision embedding + prefill + decode + KV cache

2. llm.generate(...) 이후 후처리가 오래 걸림
   -> output parsing
   -> re_match
   -> bounding box drawing
   -> cropped image 저장
   -> mmd/pdf 결과 저장
```

폐쇄망 구현이 원본처럼 전체 image list를 한 번에 `llm.generate`에 넣지 않고 16개씩 batch loop를 돌린다면, 다음 구조로 해석한다.

```text
batch_i preprocess progress bar
  -> batch_i llm.generate(...)
  -> batch_i output postprocess
  -> batch_i+1 preprocess progress bar
```

이 경우 다음 progress bar까지의 공백은 **이전 batch의 `llm.generate` 시간 + 후처리 시간**일 가능성이 크다. 따라서 계측은 `preprocess_done`, `generate_start`, `generate_done`, `postprocess_done`, `next_preprocess_start`로 나눠야 한다.

참고한 원본 코드:

- DeepSeek-OCR-2 README: vLLM 실행 경로, dynamic resolution, prompt 예시
- `DeepSeek-OCR2-vllm/run_dpsk_ocr2_pdf.py`: `Pre-processed images` progress bar, `process_single_image`, `llm.generate`
- `DeepSeek-OCR2-vllm/process/image_process.py`: `DeepseekOCR2Processor.tokenize_with_images`, `dynamic_preprocess`
- `DeepSeek-OCR2-vllm/deepseek_ocr2.py`: `PromptReplacement`, `get_num_image_tokens`, `_process_image_input`, `_pixel_values_to_embedding`

---

## 5. Page Image 1장이 무거운 이유

텍스트 입력은 token 수를 눈으로 어느 정도 추정할 수 있다. 반면 이미지 입력은 해상도와 processor 방식에 따라 내부 길이가 크게 바뀐다.

예를 들어 VLM은 보통 이미지를 patch 단위로 나누거나 crop/tiling 후 vision encoder를 통과시킨다.

```text
Page image
  -> resize
  -> patch split
  -> visual embedding sequence
```

또는 고해상도 OCR 모델은 문서의 작은 글자를 보존하기 위해 이미지를 여러 crop으로 나눌 수 있다.

```text
High resolution page
  -> crop 1
  -> crop 2
  -> crop 3
  -> ...
  -> visual tokens 증가
```

이때 page image 1장은 다음 비용을 만든다.

| 비용 | 설명 |
| --- | --- |
| CPU 전처리 | 이미지 decode, resize, crop, normalize |
| CPU -> GPU 이동 | tensor 또는 image embedding 전송 |
| vision compute | visual encoder 또는 multimodal projector 연산 |
| prefill token 증가 | visual token이 LLM 입력 길이를 늘림 |
| KV cache 증가 | visual token도 attention 문맥에 포함되면 cache 부담 증가 |

따라서 페이지 해상도가 높거나 crop 수가 많으면 batch 16은 급격히 무거워진다.

---

## 6. Batch Size 16의 실제 의미

현재 application batch size와 vLLM sequence 관련 설정이 16으로 맞춰져 있다.

텍스트 LLM에서 batch 16은 대략 다음처럼 생각할 수 있다.

```text
16 text prompts
  -> 각 prompt token 수가 작거나 중간
  -> prefill 부담이 비교적 예측 가능
```

VLM/OCR에서 batch 16은 다르다.

```text
16 page images
  -> 각 page마다 visual token 생성
  -> page마다 OCR 출력 길이 다름
  -> prefill과 decode 편차가 모두 큼
```

특히 다음 상황에서는 batch 16이 오히려 느려질 수 있다.

- 한 batch 안에 고해상도 페이지가 많이 섞임
- 표, 논문, dense text 페이지처럼 출력이 긴 페이지가 섞임
- `max_num_batched_tokens` 또는 KV cache capacity가 부족함
- Heron101, CLIP, DeepSeekOCR V2가 같은 30GB MIG에 상주해서 vLLM 여유 메모리가 작을 수 있음
- 단, Heron101/CLIP은 파라미터가 작은 모델이므로 weight memory 자체보다 실제 free memory delta와 동시 실행 여부가 중요함
- Python loop가 batch 단위로 동기 실행되어 다음 batch를 미리 준비하지 못함

따라서 batch size는 throughput만 보고 정하면 안 된다.

```text
좋은 batch size
  = GPU가 충분히 바쁘고
  + KV cache가 부족하지 않고
  + batch tail latency가 과도하지 않고
  + batch 사이 공백이 작아지는 값
```

---

## 7. OCR 출력 길이 편차와 Tail Latency

OCR은 페이지마다 출력 길이가 크게 다르다.

```text
page 1: 제목 + 짧은 문단
page 2: 일반 텍스트
page 3: 표 + 작은 글씨
page 4: 논문 본문 2단 구성
```

batch 안에서 출력 길이가 긴 페이지가 있으면 전체 batch 완료 시간이 길어질 수 있다.

```text
batch size 16
  page 01 -> output short  -> early finish
  page 02 -> output medium
  page 03 -> output short  -> early finish
  ...
  page 11 -> output long   -> late finish

batch result 반환
  -> page 11 완료 후 가능
```

vLLM은 continuous batching을 통해 완료된 sequence 자리에 새 sequence를 넣을 수 있지만, application이 다음처럼 동기 batch loop를 구성하면 그 이점이 제한될 수 있다.

```python
for batch in image_batches:
    outputs = llm.generate(batch)
    results.extend(outputs)
```

이 구조에서는 batch 안의 긴 페이지가 끝나기 전까지 Python loop가 다음 batch로 넘어가지 않는다. 그래서 짧은 페이지가 빨리 끝났더라도 다음 batch progress bar는 늦게 생길 수 있다.

---

## 8. Page Resolution과 Batch Grouping

OCR 모델은 이미지 해상도에 민감하다. 해상도를 낮추면 글자를 놓칠 수 있고, 해상도를 높이면 visual token과 전처리 비용이 증가한다.

성능 관점에서는 page를 무작정 원래 순서대로 16개씩 자르는 것이 최적이 아닐 수 있다.

```text
원래 순서 batch
  batch 1: short, short, long, high-res, short, ...
  batch 2: medium, high-res, high-res, long, ...

특성 기반 batch
  batch A: low/medium resolution pages
  batch B: high resolution pages with smaller batch size
  batch C: dense pages with smaller batch size
```

가능한 grouping 기준은 다음이다.

| 기준 | 기대 효과 | 위험 |
| --- | --- | --- |
| image resolution | visual token 편차 감소 | 원래 page order를 나중에 복원해야 함 |
| file size | 전처리 비용 추정 | 압축률 때문에 부정확할 수 있음 |
| OCR 예상 길이 | decode tail latency 감소 | 사전 예측 모델 또는 heuristic 필요 |
| page type | 표/본문/이미지 페이지 분리 | 분류 비용 추가 |

초기 실험에서는 복잡한 분류보다 간단한 기준부터 시작한다.

```text
1. image width/height 기록
2. output length 기록
3. batch latency와 상관관계 확인
4. high-res 또는 long-output page가 많은 batch를 작은 batch로 분리
```

---

## 9. VLM/OCR에서 KV Cache를 볼 때 주의할 점

KV cache는 decode 단계에서만 중요하다고 생각하기 쉽지만, VLM/OCR에서는 prompt 자체가 visual token 때문에 길어질 수 있다.

```text
KV cache length
  = visual tokens
  + text prompt tokens
  + generated OCR tokens
```

따라서 같은 `max_num_seqs=16`이라도 다음 두 케이스는 메모리 부담이 다르다.

```text
Case A
  16 short text prompts
  output 100 tokens each

Case B
  16 page images
  visual tokens large
  output 1000 tokens each
```

H200 MIG 30GB에서 세 모델이 같이 상주하는 현재 구조에서는 `gpu_memory_utilization=0.8`을 높이는 것만으로 해결되지 않을 수 있다. 다만 Heron101/CLIP이 작은 모델이라면, 이 옵션의 민감도는 DeepSeekOCR V2의 dtype과 KV cache 요구량 쪽에서 더 크게 나타날 가능성이 높다.

```text
free memory가 작음
  -> vLLM KV cache block 수 제한
  -> 큰 visual token batch 수용 어려움
  -> batch size를 낮추는 것이 더 안정적일 수 있음
```

---

## 10. 현재 증상에 대한 VLM/OCR 관점 가설

현재 증상:

```text
image/preprocess progress bar는 빠르게 올라간다.
다음 16개짜리 progress bar가 생기기까지 시간이 오래 걸린다.
```

VLM/OCR 관점의 가설은 다음 순서로 의심한다.

### 가설 1. Batch 후처리와 결과 조립이 느리다

OCR output이 길고 page별 결과를 파싱/정리하는 과정이 batch 뒤에 몰려 있을 수 있다.

확인:

- `generate_done -> postprocess_done` 시간 측정
- batch별 output character/token length 기록

### 가설 2. 다음 batch image 준비가 느리다

다음 16개 이미지에 대해 processor, prompt 구성, tensor 변환이 progress bar 구간 또는 progress bar 직전에 실행될 수 있다. GitHub 원본 기준 `Pre-processed images`는 이 입력 준비 구간을 직접 감싼다.

확인:

- `batch_prepare_start -> batch_prepare_done` 시간 측정
- image size, resolution, bytes 기록

### 가설 3. 긴 출력 페이지가 batch 완료를 늦춘다

batch 안의 몇 페이지가 긴 decode를 만들고, Python loop가 batch 전체 완료를 기다릴 수 있다.

확인:

- page별 output length와 batch latency 비교
- batch size 4/8/16 비교
- 긴 페이지가 포함된 batch와 아닌 batch 비교

### 가설 4. GPU memory 압박으로 batch 전환 비용이 커진다

세 모델이 같은 MIG에 상주해 vLLM KV cache와 temporary buffer 여유가 작을 수 있다. 그러나 Heron101/CLIP이 작은 모델이라는 조건을 고려하면, 단독/공존 차이가 작게 나올 가능성도 열어둬야 한다.

확인:

- batch 전후 GPU memory snapshot
- vLLM 초기화 시 KV cache block 수 확인
- DeepSeekOCR 단독 실행과 세 모델 공존 실행 비교

---

## 11. 계측에 추가해야 할 VLM/OCR 메타데이터

`06_bottleneck_measurement_plan.md`에서 자세히 다루겠지만, VLM/OCR 특성을 보려면 timing 외에 다음 메타데이터가 필요하다.

| 메타데이터 | 이유 |
| --- | --- |
| page index | 원본 순서 복원과 느린 페이지 추적 |
| image width/height | visual token 또는 processor 비용 추정 |
| image bytes | 전송/역직렬화 비용 추정 |
| batch index | 느린 batch 위치 확인 |
| output character length | decode 길이 근사 |
| output token length | KV cache/decode 비용 근사 |
| prepare time | image processor 병목 확인 |
| generate time | vLLM 내부 처리 시간 확인 |
| postprocess time | batch 사이 공백 확인 |

초기에는 token length 계산이 어렵다면 character length부터 기록해도 된다. 이후 tokenizer를 사용해 output token 수를 추가한다.

---

## 12. 최적화 방향

VLM/OCR 특성을 고려하면 초기 최적화 방향은 다음이다.

```text
1. batch size 16을 고정하지 않는다.
2. batch별 image resolution과 output length를 기록한다.
3. batch 사이 공백을 prepare/generate/postprocess로 분리한다.
4. high-res 또는 long-output page가 많은 batch는 작은 batch로 처리한다.
5. vLLM 옵션은 visual token과 KV cache 관점에서 해석한다.
```

바로 시도할 수 있는 비교는 다음이다.

| 실험 | 목적 |
| --- | --- |
| batch size 4/8/16 | throughput과 tail latency 균형 확인 |
| output length logging | 긴 페이지가 batch를 끄는지 확인 |
| image resolution logging | 고해상도 페이지가 prepare/prefill을 늘리는지 확인 |
| DeepSeekOCR 단독 실행 | 세 모델 공존의 영향을 분리. 차이가 작으면 Heron101/CLIP보다 DeepSeekOCR V2 설정을 우선 |
| 원래 순서 batch vs 크기 기반 batch | page grouping 효과 확인 |

---

## 13. 다음 문서로 넘길 질문

다음 문서는 `04_deepseekocr_v2_model_notes.md`다. 이 문서에서는 일반 VLM/OCR 특성이 아니라 DeepSeekOCR V2 자체의 입력 형식과 주의사항을 확인한다.

다음 질문을 다룬다.

- DeepSeekOCR V2는 실제로 image를 어떤 방식으로 prompt에 넣는가?
- image/preprocess progress bar가 폐쇄망 코드에서 원본의 `Pre-processed images`와 같은 위치인가?
- 권장 image 크기, crop/tiling, generation parameter가 있는가?
- vLLM direct call에서 요구하는 multimodal input format은 무엇인가?
- 현재 batch size 16과 sequence 설정 16이 모델 권장 사용법과 맞는가?
