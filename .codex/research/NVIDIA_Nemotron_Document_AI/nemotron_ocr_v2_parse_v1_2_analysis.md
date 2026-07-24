# NVIDIA Nemotron OCR v2 / Nemotron Parse v1.2 분석

- 작성일: 2026-07-11
- 주제: NVIDIA 문서 AI 모델 비교 및 OmniDocBench 지표 해석
- 대상 모델:
  - https://huggingface.co/nvidia/nemotron-ocr-v2
  - https://huggingface.co/nvidia/NVIDIA-Nemotron-Parse-v1.2
- 주요 참고:
  - Hugging Face model card: `nvidia/nemotron-ocr-v2`
  - Hugging Face model card: `nvidia/NVIDIA-Nemotron-Parse-v1.2`
  - OmniDocBench GitHub: https://github.com/opendatalab/OmniDocBench

## 요약

두 모델은 모두 문서 이미지 처리에 쓰이지만 목적이 다르다.

`Nemotron OCR v2`는 이미지 안의 텍스트를 찾고 읽는 OCR 모델이다. 출력은 주로 bounding box, 인식된 텍스트, confidence score이다. RAG ingestion, 검색 인덱싱, 스캔 문서 텍스트화처럼 "글자를 정확하고 빠르게 뽑는" 작업에 적합하다.

`NVIDIA Nemotron Parse v1.2`는 단순 OCR보다 문서 구조 파싱 모델에 가깝다. 페이지 이미지를 입력받아 텍스트뿐 아니라 title, section, caption, footnote, list, table, bibliography, image 같은 문서 요소 class와 bounding box를 함께 출력한다. 출력 형식은 Markdown 텍스트와 구조 정보가 섞인 문자열이다.

실무적으로는 다음처럼 구분하면 된다.

| 목적 | 적합한 모델 |
| --- | --- |
| 이미지/PDF에서 텍스트만 빠르게 추출 | Nemotron OCR v2 |
| 문서를 Markdown 또는 구조화 데이터로 변환 | Nemotron Parse v1.2 |
| RAG용 원문 텍스트 추출 | Nemotron OCR v2 |
| 표, 제목, 캡션, 이미지 영역까지 구조화 | Nemotron Parse v1.2 |
| 다국어 OCR 자체가 핵심 | Nemotron OCR v2 multilingual |
| 문서 layout-aware parsing이 핵심 | Nemotron Parse v1.2 |

## Nemotron OCR v2

### 목적

`nvidia/nemotron-ocr-v2`는 다국어 텍스트 인식을 위한 OCR 모델이다. 복잡한 실제 이미지에서 텍스트 영역을 찾고, 텍스트를 인식하고, 읽기 순서 및 layout 관계를 분석하는 데 초점을 둔다.

주요 사용처:

- 문서 이미지 OCR
- 자연 장면 이미지 OCR
- RAG pipeline의 문서 ingestion
- 멀티모달 검색 시스템
- 스캔 문서, 표, 차트, 인포그래픽의 텍스트 추출

### 구조

모델은 세 구성요소로 설명된다.

| 구성요소 | 역할 |
| --- | --- |
| Text Detector | 이미지에서 텍스트 영역 위치 검출 |
| Text Recognizer | 검출된 영역의 문자를 인식 |
| Relational Model | 문서 내 읽기 순서, grouping, layout 관계 분석 |

두 가지 variant가 있다.

| Variant | 특징 |
| --- | --- |
| `v2_english` | 영어 OCR 최적화, word-level region 처리 |
| `v2_multilingual` | 영어, 중국어, 일본어, 한국어, 러시아어 등 다국어 지원, line-level region 처리 |

### 입출력

입력:

- RGB 이미지
- PNG/JPEG
- single image 또는 batch

출력:

- detected text region bounding boxes
- recognized text
- confidence score

예시 형태:

```python
ocr_boxes = [...]
ocr_txts = ["The previous notice was dated", "22 April 2016"]
ocr_confs = [0.977, 0.988]
```

### 성능 해석

Hugging Face 모델 카드의 OmniDocBench 표는 `Normalized Edit Distance (NED) sample_avg`를 사용한다. 낮을수록 좋다.

예시:

| Model | pages/s | EN | ZH | Mixed |
| --- | ---: | ---: | ---: | ---: |
| PaddleOCR v5 server | 1.2 | 0.027 | 0.037 | 0.041 |
| OpenOCR server | 1.5 | 0.024 | 0.033 | 0.049 |
| Nemotron OCR v2 multilingual | 34.7 | 0.048 | 0.072 | 0.142 |
| Nemotron OCR v2 EN | 40.7 | 0.038 | 0.830 | 0.437 |

관찰:

- `Nemotron OCR v2 multilingual`은 throughput이 매우 높다.
- EN/ZH/Mixed의 NED는 PaddleOCR/OpenOCR보다 높은 항목이 많다. NED는 낮을수록 좋으므로 이 표만 보면 순수 OCR 정확도는 PaddleOCR/OpenOCR가 더 좋은 항목이 있다.
- `v2_english`는 영어 전용이므로 중국어/혼합 언어에서 성능이 크게 떨어진다.
- `pages/s`와 `NED`를 같이 봐야 한다. Nemotron OCR v2는 속도 측면의 장점이 크다.

## NVIDIA Nemotron Parse v1.2

### 목적

`nvidia/NVIDIA-Nemotron-Parse-v1.2`는 OCR 모델이라기보다 문서 파싱 모델이다. 문서 페이지 이미지에서 텍스트를 추출하면서 동시에 문서 요소를 분류하고 좌표를 제공한다.

모델 카드에서 설명하는 주요 기능:

- text extraction
- document structure understanding
- PDF/PPT 문서 처리
- title, section, caption, index, footnote, list, table, bibliography, image 등 객체 분류
- bounding box 좌표 출력

### 구조

아키텍처는 Transformer 기반 vision-encoder-decoder이다.

| 구성요소 | 설명 |
| --- | --- |
| Vision Encoder | ViT-H 계열, C-RADIO 기반 |
| Adapter Layer | latent space의 차원과 sequence length 압축 |
| Decoder | mBART 10 blocks |
| Parameters | 약 0.9B |

### 입출력

입력:

- RGB 이미지
- prompt string

출력:

- string
- 문자열 안에 text content, Markdown formatting, bounding boxes, class attributes가 인코딩됨

기본 권장 prompt는 다음 계열이다.

```text
</s><s><predict_bbox><predict_classes><output_markdown><predict_no_text_in_pic>
```

또는 그림 내부 텍스트까지 추출하려면:

```text
</s><s><predict_bbox><predict_classes><output_markdown><predict_text_in_pic>
```

v1.2에서는 네 번째 제어 토큰인 `<predict_text_in_pic>` 또는 `<predict_no_text_in_pic>`가 중요하다. v1.1 방식의 3-token prompt를 그대로 쓰면 품질이 크게 떨어질 수 있다고 모델 카드가 경고한다.

### 사용 방식

주요 runtime:

- vLLM
- TensorRT-LLM

예시 실행 방식:

```bash
vllm serve nvidia/NVIDIA-Nemotron-Parse-v1.2 \
  --dtype bfloat16 \
  --max-num-seqs 8 \
  --limit-mm-per-prompt '{"image": 1}' \
  --trust-remote-code \
  --port 8000 \
  --chat-template chat_template.jinja
```

## OmniDocBench 지표 해석

### OmniDocBench란?

OmniDocBench는 문서 파싱 평가 benchmark이다. PDF page 단위의 다양한 문서 유형을 포함하며, OCR뿐 아니라 layout detection, table recognition, formula recognition, reading order, end-to-end parsing까지 평가한다.

지원 metric:

- Normalized Edit Distance
- BLEU
- METEOR
- TEDS
- COCO mAP/mAR

따라서 "OmniDocBench 점수"라고만 말하면 부족하다. 어떤 task의 어떤 metric인지 확인해야 한다.

### NED란?

NED는 `Normalized Edit Distance`이다. 정답 문자열과 예측 문자열이 얼마나 다른지를 편집 거리로 계산하고 문자열 길이로 정규화한 값이다.

직관적으로:

```text
NED ~= 필요한 삽입/삭제/치환 횟수 / 문자열 길이
```

예를 들어 정답이 100글자이고 모델 출력이 정답과 비교해 3글자 정도 수정이 필요하면 NED는 대략 `0.03` 근처가 된다.

중요한 점:

- `0`에 가까울수록 좋다.
- `1`에 가까울수록 나쁘다.
- 정확도 accuracy가 아니라 오류 거리 error distance이다.

즉 `0.031`은 "정확도 3.1%"가 아니다. 대략 "정답 대비 평균 편집 오류율이 3.1% 수준"이라고 이해하는 것이 자연스럽다.

거칠게 유사도를 보고 싶다면 `1 - NED`로 생각할 수 있다.

```text
NED = 0.031
1 - NED = 0.969
```

즉 약 96.9% 유사도처럼 감각적으로 해석할 수 있다. 다만 공식 metric은 accuracy가 아니라 NED이다.

### sample_avg와 page_avg

`sample_avg`는 샘플별 NED를 계산한 뒤 평균낸 값이다. `page_avg`는 페이지 단위로 평균낸 값이다.

| 평균 방식 | 의미 |
| --- | --- |
| sample_avg | 개별 샘플 단위 평균 |
| page_avg | 페이지 단위 평균 |

따라서 같은 `0.03`이라도 sample_avg인지 page_avg인지에 따라 비교 의미가 달라진다. 같은 benchmark, 같은 task, 같은 evaluation mode, 같은 averaging 방식에서만 직접 비교하는 것이 안전하다.

### NVIDIA OCR v2 표의 0.031 해석 예시

모델 카드의 OmniDocBench 표에서:

```text
PaddleOCR v5 (server), White = 0.031
```

이는 흰 배경 조건의 OCR 평가에서 normalized edit distance가 평균 `0.031`이라는 뜻이다. 낮을수록 좋으므로 같은 열에서 `0.027`은 `0.031`보다 더 좋은 결과이다.

다른 예:

```text
Nemotron OCR v2 multilingual, EN = 0.048
OpenOCR server, EN = 0.024
```

이 경우 영어 OCR NED 기준으로는 OpenOCR가 Nemotron OCR v2 multilingual보다 더 낮은 오류 거리를 보인다. 하지만 throughput은 Nemotron OCR v2 multilingual이 훨씬 높게 보고되어 있으므로, 정확도와 속도를 함께 판단해야 한다.

## 모델 선택 기준

### Nemotron OCR v2를 선택할 상황

- 대량 문서에서 텍스트를 빠르게 추출해야 한다.
- OCR 결과가 bounding box, text, confidence 정도면 충분하다.
- RAG indexing 전에 원문 텍스트를 확보하는 것이 목적이다.
- 다국어 OCR이 필요하다.
- 문서 구조보다는 글자 인식 성능과 처리량이 중요하다.

### Nemotron Parse v1.2를 선택할 상황

- PDF/PPT 페이지를 Markdown으로 변환하고 싶다.
- 제목, 본문, 표, 캡션, footnote, image 같은 semantic block 구분이 필요하다.
- downstream에서 문서 구조를 활용해야 한다.
- table/document parsing이 OCR보다 중요하다.
- bounding box와 class label을 함께 얻고 싶다.

## 주의점

1. OCR v2의 OmniDocBench 표는 `NED sample_avg`이며, 낮을수록 좋은 오류 지표이다. accuracy로 읽으면 안 된다.
2. Parse v1.2는 OCR benchmark 숫자 하나만으로 평가하기 어렵다. layout, table, formula, markdown 구조 품질을 함께 봐야 한다.
3. NVIDIA 모델 카드의 benchmark는 "reference metrics"이며, 재현에는 별도 dataset과 script가 필요하다고 명시되어 있다.
4. v1.2 Parse는 prompt format이 중요하다. 특히 `<predict_text_in_pic>` 또는 `<predict_no_text_in_pic>`를 포함해야 한다.
5. OCR 결과를 RAG에 넣을 때는 NED뿐 아니라 reading order, table serialization, header/footer 제거 품질도 별도로 확인해야 한다.

## 한 줄 결론

`Nemotron OCR v2`는 빠른 OCR 엔진이고, `Nemotron Parse v1.2`는 문서 구조를 Markdown/좌표/class로 풀어내는 document parser이다. OmniDocBench의 `0.031` 같은 값은 정확도가 아니라 normalized edit distance이므로 낮을수록 좋고, 대략 "문자 단위 편집 오류율 3.1%"에 가깝게 이해하면 된다.

---

## DeepSeek-OCR-2와 Nemotron Parse v1.2 성능 비교

- 추가 작성일: 2026-07-11
- 비교 대상:
  - DeepSeek-OCR-2: https://github.com/deepseek-ai/DeepSeek-OCR-2
  - NVIDIA Nemotron Parse v1.2: https://huggingface.co/nvidia/NVIDIA-Nemotron-Parse-v1.2
- 추가 참고:
  - DeepSeek-OCR-2 논문: https://arxiv.org/abs/2601.20552
  - Nemotron-Parse 논문(v1.1 중심): https://arxiv.org/abs/2511.20478
  - slOCR Benchmark: https://huggingface.co/spaces/valira-ai/slo-ocr-benchmark

### 먼저 정리할 점

DeepSeek-OCR-2와 Nemotron Parse v1.2는 실제 사용 관점에서 역할이 많이 겹친다. 둘 다 문서 이미지를 입력받아 OCR 결과를 Markdown/구조화 텍스트로 만들 수 있다.

다만 모델이 강조하는 방향은 다르다.

| 항목 | DeepSeek-OCR-2 | Nemotron Parse v1.2 |
| --- | --- | --- |
| 핵심 포지션 | document OCR / Markdown 변환 | document parsing / layout-aware 구조화 |
| 출력 | Markdown 중심 | Markdown + bbox + class |
| 강점으로 주장하는 부분 | 고해상도 문서 압축, 효율적 OCR, OmniDocBench 성능 | layout object class, bbox, Markdown 동시 출력 |
| 주요 공개 성능 | OmniDocBench v1.5 결과 공개 | v1.2 자체의 표준 공개 벤치마크는 제한적, v1.1 논문/외부 벤치마크 참고 필요 |

즉 둘 다 "문서 이미지를 Markdown으로 바꾼다"는 점에서는 같은 역할을 하지만, DeepSeek-OCR-2는 OCR/Markdown 변환 성능을 강하게 내세우고, Nemotron Parse는 block-level 구조와 좌표 정보를 함께 내는 parser 성격이 더 강하다.

### 공개 벤치마크 비교의 한계

두 모델을 같은 조건에서 직접 비교한 신뢰도 높은 공개 benchmark는 찾기 어렵다.

특히 주의할 점:

1. DeepSeek-OCR-2는 OmniDocBench v1.5 성능을 논문/README에서 강조한다.
2. Nemotron Parse v1.2는 Hugging Face model card에 architecture와 사용법은 자세히 있지만, DeepSeek-OCR-2와 같은 방식의 OmniDocBench v1.5 종합표는 공개적으로 명확히 제공되어 있지 않다.
3. Nemotron Parse 관련 논문은 v1.1 중심이며, v1.2와 완전히 동일하다고 단정하면 안 된다.
4. slOCR Benchmark에는 Nemotron Parse v1.2가 포함되어 있지만, DeepSeek-OCR-2는 포함되어 있지 않다.

따라서 아래 비교는 "동일 benchmark에서의 정면 비교"가 아니라 공개된 결과를 같은 평가축으로 해석한 간접 비교이다.

### DeepSeek-OCR-2의 성능 근거

DeepSeek-OCR-2는 논문에서 OmniDocBench v1.5 기준 성능을 제시한다. 논문은 DeepSeek-OCR-2가 텍스트, 표, 수식, reading order 평가에서 강한 성능을 보인다고 설명한다.

논문/README에서 확인되는 핵심 포인트:

- dynamic resolution 방식 사용
- `0-6 x 768 x 768` local view와 `1 x 1024 x 1024` global view 조합
- document image를 markdown으로 변환하는 prompt 제공
- OmniDocBench v1.5 batch evaluation script 제공
- vLLM 추론 지원

실무적으로 해석하면 DeepSeek-OCR-2는 "문서 페이지를 Markdown으로 잘 뽑는 것" 자체를 주요 목표로 하고, 공개 평가도 이 목표에 맞춰 제시되어 있다.

### Nemotron Parse v1.2의 성능 근거

Nemotron Parse v1.2는 model card 기준으로 document parsing을 위한 vision-encoder-decoder 모델이다. 출력에는 Markdown, bounding box, semantic class가 포함된다.

확인되는 장점:

- title, section, caption, footnote, list, table, bibliography, image 등 class 출력
- bbox 좌표 출력
- vLLM/TensorRT-LLM 서빙 고려
- 약 0.9B 규모로 비교적 작은 parser

다만 v1.2 자체에 대해 DeepSeek-OCR-2의 OmniDocBench v1.5 결과처럼 바로 비교 가능한 공개 종합 성능표는 부족하다.

외부 slOCR Benchmark에서는 Nemotron Parse v1.2가 포함되어 있다. 이 벤치마크는 슬로베니아어 OCR/문서 파싱 평가이며, 20개 시스템을 비교한다.

slOCR에서 Nemotron Parse v1.2의 결과:

| 항목 | 결과 |
| --- | ---: |
| Overall rank | 17 / 20 |
| Overall score | 0.6873 |
| Web category rank | 3 / 20 |
| Web score | 0.9727 |
| Textbook score | 0.9646 |
| Academic score | 0.7449 |
| Historical score | 0.5928 |
| Handwriting score | 0.1048 |

해석:

- 웹 페이지/정돈된 디지털 문서 계열에서는 좋은 결과가 나온다.
- 필기체, 오래된 스캔, 복잡한 학술 문서에서는 약점이 보인다.
- 전체 순위가 높지는 않으므로 "범용 최고 OCR/parser"라고 보기 어렵다.

### 성능을 같은 축으로 비교하면

| 평가 축 | DeepSeek-OCR-2 | Nemotron Parse v1.2 | 판단 |
| --- | --- | --- | --- |
| Markdown OCR 품질 | OmniDocBench v1.5 성능을 직접 강조 | Markdown 출력 가능하지만 공개 종합 성능 근거 부족 | DeepSeek-OCR-2 우세로 보는 것이 합리적 |
| Layout/class/bbox 구조화 | 가능 범위는 있으나 핵심 강조점은 OCR/Markdown | bbox + semantic class가 핵심 기능 | Nemotron Parse 우세 |
| 표/수식/reading order | DeepSeek-OCR-2가 공개 평가에서 강조 | 가능하지만 v1.2 공개 비교 근거 부족 | DeepSeek-OCR-2 쪽 근거가 더 강함 |
| 웹/디지털 문서 | 공개 자료상 강할 가능성 높음 | slOCR Web 3위로 좋음 | 둘 다 테스트 가치 있음 |
| 손글씨/오래된 스캔 | 별도 검증 필요 | slOCR에서 약함 | Nemotron Parse는 주의 |
| 속도/배포 | vLLM 지원, OCR 목적 | vLLM/TensorRT-LLM 지원, 0.9B parser | 환경에 따라 판단 |
| 공개 사용자/생태계 | 관심도와 사용량이 큼 | 상대적으로 후기 적음 | DeepSeek-OCR-2 우세 |

### 현재 DeepSeek-OCR-2를 쓰고 있다면

현재 목적이 다음과 같다면 DeepSeek-OCR-2를 유지하는 쪽이 자연스럽다.

- PDF/이미지를 Markdown으로 변환
- RAG ingestion용 텍스트 추출
- 표/수식/reading order가 중요한 문서 OCR
- 이미 운영 파이프라인에 붙어 있고 품질이 괜찮음
- 공개 벤치마크 근거가 더 많은 모델을 선호

Nemotron Parse v1.2를 추가로 볼 만한 경우:

- 각 문서 block의 bbox가 꼭 필요함
- block class가 필요함: title, section, caption, footnote, table, image 등
- OCR 결과를 원문 이미지 위에 overlay하거나 page coordinate와 연결해야 함
- NVIDIA TensorRT-LLM/NIM/vLLM 계열 배포 환경과 맞추고 싶음
- 문서 parsing 결과를 후처리 pipeline에서 block 단위로 다루고 싶음

### 실무 A/B 테스트 권장 기준

두 모델은 공개 benchmark만으로 결론내리기보다, 실제 사용하는 문서 30-100페이지 정도로 A/B 테스트하는 것이 좋다.

평가 항목:

| 항목 | 확인 방법 |
| --- | --- |
| CER/WER | 정답 텍스트가 있는 샘플에서 문자/단어 오류율 계산 |
| Markdown 구조 | heading, list, paragraph가 깨지지 않는지 확인 |
| 표 품질 | table cell 누락, 행/열 병합 오류, Markdown table 품질 확인 |
| 수식 품질 | LaTeX 변환 또는 수식 문자열 오류 확인 |
| Reading order | multi-column, footnote, caption 순서 확인 |
| Hallucination | 원문에 없는 문장/단어 생성 여부 확인 |
| bbox/class | Nemotron Parse 사용 시 좌표와 class가 실제 후처리에 유용한지 확인 |
| 처리량 | pages/s, GPU memory, batch size 확인 |

### 결론

성능 관점에서만 보면, 현재 공개 근거는 DeepSeek-OCR-2 쪽이 더 강하다. 특히 Markdown OCR, 표/수식/reading order까지 포함한 문서 변환 품질을 중요하게 본다면 DeepSeek-OCR-2를 유지하는 것이 합리적이다.

Nemotron Parse v1.2는 DeepSeek-OCR-2의 대체재라기보다, bbox와 semantic class가 필요한 경우에 붙이는 구조 파싱 후보로 보는 것이 좋다. "텍스트/Markdown 품질"은 DeepSeek-OCR-2를 우선 보고, "좌표와 블록 class"가 필요할 때 Nemotron Parse를 A/B 테스트하는 전략이 현실적이다.
