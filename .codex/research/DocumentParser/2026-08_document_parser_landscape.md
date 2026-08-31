# 문서 파서 최신 동향과 Heron101 + DeepSeek-OCR-2 개선 후보

> 조사 기준일: 2026-08-21  
> 조사 범위: PDF/문서 이미지의 레이아웃 분석, OCR, 표·수식·차트 인식, Markdown/JSON 변환, 장문 문서 처리, 파서 라우팅  
> 현재 기준선: Docling `docling-layout-heron-101` + DeepSeek-OCR-2  
> 출처 원칙: 공식 GitHub·모델 카드·논문·공식 문서를 우선하고, 벤더 자체 보고 수치는 독립 재현 결과와 구분한다.

---

## 1. 먼저 내린 결론

현재 구성은 여전히 유효하지만, 2026년 8월의 기본 선택으로는 다음 구조가 더 합리적이다.

```text
PDF 입력
  -> PDF Inspector류의 빠른 분류
       ├─ born-digital / 정상 text layer
       │    -> PDF backend의 text + 좌표를 그대로 사용
       │    -> Heron/Egret 또는 VLM으로 구조만 보강
       ├─ mixed PDF
       │    -> OCR이 필요한 페이지만 전문 VLM으로 전송
       └─ scanned / image-based / broken encoding
            -> 전문 문서 VLM 또는 OCR pipeline
  -> bbox·reading order·table·formula·cross-page 후처리
  -> Markdown + 구조 JSON + provenance
  -> 품질 게이트 및 선택적 fallback
```

핵심 판단은 다음과 같다.

1. **Heron101은 OCR 모델이 아니라 레이아웃 검출기다.** Docling의 `docling-layout-heron-101`은 RT-DETRv2 계열 layout detector이며, DeepSeek-OCR-2는 페이지를 구조화 텍스트로 선형화하는 3B급 VLM이다. 두 모델은 중복이라기보다 역할이 다르다.
2. **다만 모든 페이지에 두 모델을 일괄 실행할 필요는 없다.** Firecrawl의 PDF Inspector가 보여 주듯 text-based·scanned·mixed를 먼저 분류하고, OCR이 필요한 페이지만 GPU로 보내는 편이 비용과 hallucination을 함께 줄인다.
3. **지금 가장 먼저 A/B 테스트할 모델은 PaddleOCR-VL-1.6, MinerU2.5-Pro, OvisOCR2다.** 각각 성숙한 다단계 pipeline, 제품형 hybrid parser, 최신 소형 end-to-end VLM을 대표한다.
4. **장문 PDF가 핵심이면 Baidu Unlimited-OCR를 별도 트랙으로 봐야 한다.** 이 모델의 차별점은 단일 페이지 점수보다 R-SWA를 이용해 여러 페이지를 하나의 생성 흐름으로 처리하는 데 있다.
5. **DeepSeek-OCR-2를 즉시 폐기할 근거는 없다.** 현재 데이터에서 좋은 결과가 나오고 이미 vLLM 운영 최적화가 되어 있다면 baseline으로 유지하되, 최신 모델과 같은 입력·출력 정규화 조건에서 재평가해야 한다.

---

## 2. 현재 구성의 정확한 위치

### 2.1 Heron101

Docling의 최신 model catalog에서 layout 계열은 다음과 같이 정리된다.

- `docling-layout-heron`: 현재 기본 layout model
- `docling-layout-heron-101`: 정확도 지향 대형 backbone 변형
- `docling-layout-egret-medium/large/xlarge`: 더 최근의 정확도 지향 후보
- `docling-layout-v2`: legacy이며 더 이상 직접 지원되지 않고 Heron으로 fallback

Heron 계열은 문단, 표, 그림, section header 같은 요소의 class와 bbox를 검출한다. 공식 기술 보고서상 Heron101은 RT-DETR/RT-DETRv2 계열 layout detector 연구에서 나온 모델이며, 150,000개 문서 corpus로 학습되었다. 보고된 최고 Heron101 결과는 A100에서 28 ms/image, 78% mAP지만 이 수치는 OCR이나 end-to-end Markdown 점수가 아니라 **layout detection 지표**다.

출처:

- [Docling model catalog](https://github.com/docling-project/docling/blob/main/docs/usage/model_catalog.md)
- [Advanced Layout Analysis Models for Docling](https://arxiv.org/abs/2509.11720)

### 2.2 DeepSeek-OCR-2

DeepSeek-OCR-2는 DeepEncoder V2의 **visual causal flow**를 통해 문서 의미에 따라 visual token 순서를 동적으로 재배치한다. 기존 raster scan 순서가 아닌 학습된 2차원 인과 흐름으로 reading order를 다루려는 것이 핵심이다.

OmniDocBench v1.6 비교표에서 보고된 값은 overall 90.25이며, text edit distance 0.050, formula CDM 91.84, table TEDS 83.89, reading-order edit distance 0.144다. 논문이 주로 강조한 v1.5 결과와 최신 v1.6 표의 숫자를 섞으면 안 된다.

출처:

- [DeepSeek-OCR-2 repository](https://github.com/deepseek-ai/DeepSeek-OCR-2)
- [DeepSeek-OCR 2: Visual Causal Flow](https://arxiv.org/abs/2601.20552)
- [PaddleOCR-VL-1.6 paper의 동일 조건 v1.6 비교표](https://arxiv.org/abs/2606.03264)

### 2.3 현재 조합의 장단점

| 관점 | 장점 | 한계 |
| --- | --- | --- |
| 디버깅 | layout bbox와 VLM 결과를 분리해 원인 분석 가능 | 두 결과를 합치는 규칙이 복잡해질 수 있음 |
| text PDF | PDF text layer와 결합하면 hallucination 억제 가능 | 모든 페이지를 이미지 OCR하면 원래 font/text 정보를 잃음 |
| scan PDF | DeepSeek-OCR-2가 text·표·수식·순서를 함께 생성 | 최신 0.8~1.2B 모델보다 크면서 v1.6 공개 점수는 낮음 |
| 처리량 | vLLM batch/continuous batching 활용 가능 | Heron·CLIP·DeepSeek가 같은 30GB MIG에 상주하면 scheduling과 memory가 복잡함 |
| 출력 구조 | Heron bbox를 provenance로 유지 가능 | DeepSeek Markdown과 bbox/class의 일관성 검증 필요 |

---

## 3. 2026년 핵심 모델 지도

아래 성능은 동일 benchmark version일 때만 직접 비교할 수 있다. OmniDocBench 점수도 대부분 저자 또는 벤더가 보고한 값이므로 실제 문서군에서 재현해야 한다.

| 모델/시스템 | 규모·방식 | 핵심 차별점 | 공개 성능의 대표 값 | 현재 stack에 대한 의미 |
| --- | --- | --- | --- | --- |
| **PaddleOCR-VL-1.6** | 0.9B VLM + PP-DocLayoutV3 pipeline | irregular polygon layout, 다국어, 표·수식·seal·chart, cross-page table | OmniDocBench v1.6 96.33 | 가장 우선적인 교체 후보 |
| **OvisOCR2** | 0.8B end-to-end | 소형 단일 모델, SFT+RL 계열 후처리 | v1.6 96.58 저자 보고 | end-to-end 단순화 후보, 아직 성숙도 검증 필요 |
| **NaviDC-OCR** | digital/camera 문서 통합 end-to-end | 디지털 PDF와 촬영 문서, content-structure decoupling | v1.6 96.87 논문 보고 | 매우 최신 watchlist; 코드·weight·운영 성숙도 확인 후 평가 |
| **MinerU2.5-Pro** | 1.2B, coarse-to-fine + hybrid system | global layout 후 local recognition, native text 보존, cross-page 병합 | v1.6 95.75 비교표 | 정확도뿐 아니라 제품형 pipeline 교체 후보 |
| **GLM-OCR** | 0.9B + PP-DocLayoutV3 2-stage | CogViT, token downsampling, MTP loss, full-task RL, KIE | v1.6 95.22 비교표 | Paddle보다 prompt/KIE가 중요할 때 후보 |
| **PaddleOCR-VL-1.5** | 0.9B + layout pipeline | skew·warp·screen photo·illumination 대응 | v1.5 94.5, v1.6 비교표 94.93 | 1.6으로 바로 평가하는 편이 낫다 |
| **Qianfan-OCR** | 4B end-to-end | Layout-as-Thought, parsing+KIE+DocQA+chart | v1.6 비교표 93.90 | 단순 OCR보다 document intelligence가 필요할 때 |
| **Unlimited-OCR** | 3B total, 약 0.5B activated, long-horizon | R-SWA, 32K context, multi-page one-shot | v1.6 93.92 저자 보고 | 40+ page 문맥·페이지 연결성 전용 후보 |
| **HunyuanOCR-1.5** | 약 1B end-to-end | DFlash speculative decoding, llama.cpp, 장문·chart·희소 언어 | vLLM 2.14배 speedup 저자 보고 | 속도와 PC/edge 배포 실험 후보 |
| **dots.mocr** | 약 3B급 multimodal OCR | 문서 text뿐 아니라 chart·UI·과학 그림을 SVG로 생성 | 저자 Elo 및 별도 graphics benchmark | 그림/차트가 정보의 핵심일 때 보완 모델 |
| **olmOCR 2** | 7B VLM | anchored PDF text, real-world scan, RLVR unit-test reward | olmOCR-Bench 82.4 | 영어권 오래된 scan·handwriting 별도 fallback |
| **Granite-Docling 258M** | 258M DocTags VLM | 매우 작은 구조화 parser, backend text 강제 결합 가능 | 모델별 benchmark 확인 필요 | Docling 내부의 저비용 hybrid 대안 |
| **Nemotron Parse v1.2** | 약 0.9B encoder-decoder | Markdown+bbox+semantic class | 기존 별도 조사 참조 | bbox/class가 중요한 보완 후보 |

### 3.1 Baidu 계열은 세 모델을 구분해야 한다

#### PaddleOCR-VL-1.6

Baidu/PaddlePaddle의 현재 실전 주력이다. 0.9B VLM 자체와 PP-DocLayoutV3 layout stage를 결합한다. 1.5와 architecture가 같아 swap이 쉽고, vLLM·SGLang·FastDeploy·MLX·llama.cpp server 등 여러 backend를 공식 pipeline에서 선택할 수 있다.

공식 문서는 OmniDocBench v1.6 96.33, Real5-OmniDocBench 전 시나리오 SOTA, 표·수식·text 개선을 주장한다. 표, 오래된 문서, 희귀 문자, seal, text spotting, chart understanding도 1.6에서 보강되었다.

출처:

- [PaddleOCR-VL-1.6 소개](https://www.paddleocr.ai/main/en/version3.x/algorithm/PaddleOCR-VL/PaddleOCR-VL-1.6.html)
- [PaddleOCR 공식 repository](https://github.com/PaddlePaddle/PaddleOCR)
- [PaddleOCR-VL pipeline 사용법](https://github.com/PaddlePaddle/PaddleOCR/blob/main/docs/version3.x/pipeline_usage/PaddleOCR-VL.en.md)

#### Qianfan-OCR

4B end-to-end document intelligence model이다. 이미지에서 바로 Markdown을 생성하지만, 내부 출력 과정에서 먼저 bbox·element type·reading order 형태의 layout reasoning을 만들고 최종 결과로 넘어가는 **Layout-as-Thought**가 핵심이다.

단순 PDF-to-Markdown뿐 아니라 table extraction, chart understanding, document QA, KIE처럼 prompt-driven downstream 작업을 한 모델에서 처리하려는 방향이다. 따라서 순수 파싱만 필요하면 PaddleOCR-VL-1.6보다 무겁지만, OCR 이후 별도 LLM을 붙이고 있다면 전체 pipeline 단순화 가능성이 있다.

출처:

- [Qianfan-OCR model card](https://huggingface.co/baidu/Qianfan-OCR)
- [Hugging Face Transformers QianfanOCR 문서](https://huggingface.co/docs/transformers/model_doc/qianfan_ocr)

#### Unlimited-OCR

DeepSeek-OCR 계열의 장문 한계를 직접 겨냥한다. **Reference Sliding Window Attention(R-SWA)**은 생성된 과거 token 전체를 계속 attention하는 대신, 원본 문서의 reference KV는 유지하고 최근 생성 구간을 sliding window로 관리한다. 목표는 KV cache를 통제하면서 여러 페이지의 문맥을 한 번에 이어 가는 것이다.

중요한 평가 포인트는 단일 페이지 OmniDocBench 점수보다 다음이다.

- 10·20·40·100페이지에서 누락/반복/페이지 경계 오류가 어떻게 증가하는가
- 표가 다음 페이지로 이어질 때 header와 cell 관계를 보존하는가
- 긴 생성 중 언어·format이 drift하지 않는가
- 현재 page-wise batch 방식보다 latency와 peak memory가 실제로 나은가

출처:

- [Baidu Unlimited-OCR repository](https://github.com/baidu/Unlimited-OCR)
- [Unlimited OCR Works](https://arxiv.org/abs/2606.23050)

### 3.2 가장 강한 즉시 후보: PaddleOCR-VL-1.6

현재 환경에서 첫 번째 A/B 후보로 권하는 이유는 다음과 같다.

- 0.9B로 DeepSeek-OCR-2보다 작다.
- v1.6 동일 비교표에서 text, formula, table composite가 가장 강한 축이다.
- layout stage까지 공식 pipeline에 포함되어 있어 Heron과의 수동 결합을 줄일 수 있다.
- polygon bbox를 지원해 skew/warp/photo 문서에서 axis-aligned bbox의 한계를 줄인다.
- cross-page table merging과 hierarchical heading reconstruction이 제품 pipeline에 포함된다.
- vLLM server를 공식 backend로 연결할 수 있어 기존 serving 경험을 재사용하기 쉽다.

주의점도 있다.

- 96.33은 저자 보고 수치다.
- pipeline 점수이므로 0.9B VLM 단독 능력으로 해석하면 안 된다.
- 현재 Heron class taxonomy와 PP-DocLayoutV3 taxonomy가 다르므로 기존 downstream schema mapping 비용이 든다.
- 한국어가 지원 목록에 포함되더라도 한국어 금융·행정 문서의 표와 spacing 품질은 별도로 평가해야 한다.

### 3.3 pipeline 제품성: MinerU2.5-Pro

MinerU2.5의 핵심은 full page를 저해상도로 보고 layout을 잡은 뒤, 중요한 region을 native resolution에 가깝게 crop하여 인식하는 **coarse-to-fine two-stage** 방식이다. 1.2B 수준에서 visual token과 연산을 필요한 영역에 집중한다.

2026년 MinerU 3.x는 다음 세 backend를 구분한다.

- `pipeline`: 빠르고 안정적이며 hallucination을 피하는 전통 pipeline
- `vlm-engine`: vLLM/LMDeploy/MLX 기반 고정확도 경로
- `hybrid-engine`: native PDF text와 VLM을 결합해 hallucination을 낮추는 경로

최근 Pro 계열은 chart/image 분석, truncated paragraph 병합, cross-page table 병합, table 내부 image 인식까지 지원한다. 즉 모델 하나보다 **문서 변환 제품 전체**를 비교할 때 강하다.

출처:

- [MinerU repository](https://github.com/opendatalab/MinerU)
- [MinerU2.5 paper](https://arxiv.org/abs/2509.22186)

### 3.4 최신 end-to-end 방향: OvisOCR2와 NaviDC-OCR

OvisOCR2는 0.8B end-to-end model로 OmniDocBench v1.6 96.58을 보고했다. 이는 pipeline이 우세하던 leaderboard에서 소형 단일 모델도 경쟁할 수 있음을 보여 준다.

NaviDC-OCR는 2026년 8월 공개된 더 최신 연구로 digital document와 camera-captured document를 함께 다루고 content와 structure 학습을 분리한다. v1.6 96.87을 보고했지만 매우 최신 논문이므로 weight, license, vLLM 호환성, 실제 multilingual 성능이 확인되기 전에는 production 후보가 아니라 watchlist로 둔다.

출처:

- [OvisOCR2 model card](https://huggingface.co/ATH-MaaS/OvisOCR2)
- [OvisOCR2 technical report](https://arxiv.org/abs/2607.13639)
- [NaviDC-OCR](https://arxiv.org/abs/2608.12898)

### 3.5 GLM-OCR와 HunyuanOCR-1.5

GLM-OCR은 0.9B 모델과 PP-DocLayoutV3 기반 layout+parallel recognition pipeline을 결합한다. CogViT encoder, visual token downsampling, Multi-Token Prediction loss, full-task RL이 특징이다. parsing뿐 아니라 formula, table, KIE까지 공식 SDK로 묶여 있다.

HunyuanOCR-1.5는 모델 정확도 외에 serving 속도를 중요한 연구 대상으로 삼았다. DFlash speculative decoding으로 논문은 Transformer inference 6.37배, vLLM end-to-end 2.14배 speedup을 보고한다. llama.cpp PC 배포, RL training stack, character-level hallucination을 보는 CHAOS-Bench도 함께 공개했다.

출처:

- [GLM-OCR repository](https://github.com/zai-org/GLM-OCR)
- [GLM-OCR technical report](https://arxiv.org/abs/2603.10910)
- [HunyuanOCR repository](https://github.com/Tencent-Hunyuan/HunyuanOCR)
- [HunyuanOCR-1.5 paper](https://arxiv.org/abs/2607.04884)

### 3.6 dots.mocr: OCR의 범위를 graphics parsing까지 확대

dots.mocr는 text/table/formula를 Markdown·HTML·LaTeX로 옮기는 데서 더 나아가 chart, UI layout, scientific figure, chemical diagram 같은 structured graphics를 SVG code로 재구성한다. 문서에서 그림이 단순 장식이 아니라 정보 그 자체라면 기존 OCR pipeline이 버리는 정보를 보존할 수 있다.

현재 stack에서는 모든 페이지의 기본 parser보다 다음 조건의 region fallback으로 적합하다.

- chart/diagram class로 검출된 region
- 표준 OCR 결과에 text는 있으나 그래픽 관계가 사라지는 region
- downstream이 차트 재렌더링, 구조 편집, vector 검색을 필요로 하는 경우

출처:

- [dots.mocr repository](https://github.com/rednote-hilab/dots.mocr)
- [Multimodal OCR: Parse Anything from Documents](https://arxiv.org/abs/2603.13032)

### 3.7 olmOCR 2: 다른 benchmark가 보여 주는 실제 문서 강건성

olmOCR 2는 Qwen 계열 7B VLM에 PDF의 embedded text와 위치 정보를 anchor로 함께 제공하고, binary unit test reward를 이용한 RLVR로 학습한다. Markdown heading, HTML table, LaTeX equation을 생성하며 오래된 scan, handwriting, multi-column 문서에 초점을 둔다.

OmniDocBench만 보면 최신 소형 모델보다 불리하지만, olmOCR-Bench 82.4는 실제 PDF에서 발생하는 reading order, header/footer, old scans, math table 등의 오류를 사람이 작성한 unit test로 평가한다. 영어 digitized print가 많다면 반드시 별도 baseline에 넣을 가치가 있다.

출처:

- [olmOCR repository](https://github.com/allenai/olmocr)
- [olmOCR 2 소개](https://allenai.org/blog/olmocr-2)
- [olmOCR 2 paper](https://arxiv.org/abs/2510.19817)

---

## 4. 모델보다 중요한 기술 동향

### 4.1 PDF-aware routing

Firecrawl의 `pdf-inspector`는 VLM이 아니다. Rust로 PDF object, font, drawing operation, text position을 분석하여 다음을 수행한다.

- `TextBased`, `Scanned`, `ImageBased`, `Mixed` 분류
- page별 OCR 필요 여부 반환
- CID/Type0 font와 ToUnicode CMap decoding
- multi-column reading order와 기본 table/headings Markdown 변환
- broken encoding 감지 후 OCR fallback

공식 benchmark는 OCR과 model-based parser를 끈 200 PDF에서 overall 0.875, reading order 0.915, table TEDS 0.814, 0.470초를 보고한다. 이 숫자는 VLM과 정면 비교할 수 없고, **born-digital PDF를 얼마나 싸고 정확하게 우회 처리하는가**를 보여 주는 수치다.

현재 pipeline에 주는 가장 큰 의미는 다음이다.

```text
기존: 모든 PDF page -> rasterize -> Heron + DeepSeek-OCR-2

권장: pdf-inspector/backend inspect
      -> text page: native text + bbox
      -> mixed page: 필요한 region/page만 OCR
      -> scan page: VLM OCR
```

출처:

- [firecrawl/pdf-inspector](https://github.com/firecrawl/pdf-inspector)
- [pdf-inspector Rust API와 benchmark](https://github.com/firecrawl/pdf-inspector/blob/main/docs/rust-api.md)

### 4.2 native text + VLM structure의 hybrid

born-digital PDF에서는 VLM이 글자를 다시 생성하게 할 이유가 적다. Docling의 `force_backend_text=True`는 DocTags VLM이 예측한 bbox/structure를 사용하되, 실제 text는 PDF backend에서 해당 bbox로 다시 추출한다.

장점:

- 숫자·고유명사 hallucination 감소
- font encoding이 정상인 PDF의 text fidelity 보존
- VLM은 layout/semantic classification에 집중

MinerU의 `hybrid-engine`도 같은 방향이다. 2026년의 실무 추세는 pipeline 대 end-to-end의 이분법보다 **어떤 페이지와 어떤 field에서 deterministic source를 보존할지**를 선택하는 쪽이다.

출처:

- [Docling VLM pipeline](https://github.com/docling-project/docling/blob/main/docling/pipeline/vlm_pipeline.py)
- [MinerU hybrid backend](https://github.com/opendatalab/MinerU)

### 4.3 dynamic resolution과 coarse-to-fine

문서 VLM의 핵심 병목은 파라미터 수보다 visual token 수다.

- DeepSeek-OCR 계열: 문서를 적은 visual token으로 압축
- DeepSeek-OCR-2: visual token의 causal order까지 학습
- PaddleOCR-VL: NaViT-style dynamic resolution과 region별 recognition
- MinerU2.5: global 저해상도 layout 후 local 고해상도 crop
- GLM-OCR: connector에서 visual token downsampling

따라서 모델 비교 시 `params`, `VRAM`만 기록하면 부족하고 다음을 함께 재야 한다.

- page당 visual token
- prefill time
- output token과 decode time
- crop 수와 crop당 해상도
- page당 peak memory
- dense page에서 batch tail latency

### 4.4 RL과 verifiable reward

2026년 모델들은 단순 SFT 이후 다음 reward를 사용한다.

- olmOCR 2: document unit tests를 binary reward로 사용
- GLM-OCR: full-task RL
- HunyuanOCR: RL stack과 hallucination 평가
- OvisOCR2 등: SFT 이후 parsing-format/accuracy 중심 RL

문서 파싱은 출력 형식을 자동 검증하기 쉬운 편이다. 예를 들어 table row/column consistency, Markdown tag balance, bbox containment, text anchor 포함 여부, equation compilation 여부를 reward 또는 inference-time gate로 사용할 수 있다.

### 4.5 long-document OCR

기존 page-wise OCR은 page 내부 정확도는 높아도 다음을 잃는다.

- 다음 페이지로 이어지는 표
- 문단 continuation
- repeated header/footer 판단
- heading hierarchy
- 페이지 간 footnote/reference 연결

Unlimited-OCR의 R-SWA, PaddleOCR/MinerU의 cross-page merge, Docling의 document object는 서로 다른 방식으로 이 문제를 다룬다. 앞으로는 page score와 document score를 분리해야 한다.

### 4.6 speculative decoding과 serving

OCR VLM은 image prefill뿐 아니라 긴 Markdown decode가 병목이다. HunyuanOCR-1.5의 DFlash, vLLM continuous batching, page difficulty routing은 decode 비용을 줄이는 서로 다른 접근이다.

현재 H200 MIG 30GB 환경에서는 다음이 모델 교체보다 먼저 효과를 낼 수도 있다.

- native text page를 GPU에서 제외
- scan/mixed page queue 분리
- page resolution 또는 예상 output length별 batch grouping
- page 단위가 아니라 region 단위 fallback
- draft model/speculative decoding이 지원되는 모델 경로 검토

---

## 5. benchmark를 읽는 방법

### 5.1 OmniDocBench

OmniDocBench는 1,651 PDF page, 10개 문서 유형, 5개 layout, 5개 language 유형과 text/table/formula/reading-order annotation을 제공한다. v1.5의 overall은 다음 composite다.

```text
Overall = ((1 - Text Edit Distance) * 100 + Table TEDS + Formula CDM) / 3
```

즉 overall에는 reading-order edit distance가 직접 포함되지 않는다. v1.6에서는 복잡한 nested table, dense formula, 비정형 layout page가 추가되고 matching 방식도 바뀌었다. repository changelog에는 v1.7 표기가 있으나 main 문서와 leaderboard는 v1.6_full 표기를 혼용하므로 **commit·branch·dataset hash를 고정**해야 한다.

출처:

- [OmniDocBench repository](https://github.com/opendatalab/OmniDocBench)
- [OmniDocBench CVPR 2025 paper](https://arxiv.org/abs/2412.07626)

### 5.2 OmniDocBench만으로 부족한 이유

- overall에서 reading order가 빠져 있다.
- born-digital PDF의 text layer 보존 능력을 충분히 반영하지 않는다.
- 장문 cross-page continuity를 page-level 평가로 놓칠 수 있다.
- KIE에서 숫자 하나가 틀리는 위험과 평균 edit distance가 다르다.
- Korean spacing, seal, 주민등록식 표, 세금계산서 같은 실제 분포가 다르다.
- vendor-reported result는 동일한 preprocessing/postprocessing인지 확인하기 어렵다.

보완 benchmark:

- **olmOCR-Bench**: 사람이 만든 unit test로 real-world rendering/ordering 오류 평가
- **Real5-OmniDocBench**: skew, warp, scan, screen photo, illumination
- **Wild-OmniDocBench**: real-world scene 문서
- **CHAOS-Bench**: character-level hallucination
- **OCR Arena**: 실제 업로드에 대한 blind preference; sample 수가 적은 pair는 방향성만 참고

---

## 6. 현재 stack에 대한 권고안

### 6.1 단기: 교체보다 routing 추가

가장 ROI가 높은 첫 단계다.

```text
1. PDF native inspection
2. page별 type과 encoding confidence 기록
3. native text page는 backend text 사용
4. scan/mixed/broken page만 DeepSeek-OCR-2
5. Heron bbox와 native/VLM text provenance를 함께 저장
```

PDF Inspector를 그대로 채택하지 않더라도 동일한 routing contract를 만든다.

```json
{
  "page": 12,
  "type": "mixed",
  "native_text_confidence": 0.91,
  "pages_or_regions_needing_ocr": true,
  "parser": "deepseek-ocr-2",
  "source": "native+vlm"
}
```

### 6.2 1차 A/B: 네 후보

| 우선순위 | 후보 | 확인하려는 질문 |
| ---: | --- | --- |
| 1 | PaddleOCR-VL-1.6 pipeline | Heron+DeepSeek 두 모델을 한 pipeline으로 대체하면서 정확도·VRAM·latency가 좋아지는가 |
| 2 | MinerU2.5-Pro hybrid | native text 보존과 cross-page 병합이 실제 RAG 품질을 높이는가 |
| 3 | OvisOCR2 | 0.8B 단일 모델이 동일 corpus에서도 저자 보고 수준의 정확도를 보이는가 |
| 4 | 기존 Heron101+DeepSeek-OCR-2 | 기존 최적화와 안정성이 최신 후보보다 실제로 뒤지는가 |

GLM-OCR은 KIE/정보 추출이 함께 필요할 때 5번째 후보로 추가한다. Unlimited-OCR은 20페이지 이상 long-document subset에서 별도 실험한다.

### 6.3 Heron 교체 여부

Heron101을 즉시 Egret으로 바꾸기보다 다음 세 구성을 비교한다.

1. Heron 기본 ResNet50: 속도 기준선
2. Heron101: 현재 정확도 기준선
3. Egret large/xlarge: layout mAP와 downstream parse 품질

layout detector는 bbox mAP만 보면 안 된다. 최종적으로 다음을 잰다.

- table/figure 누락률
- header/footer 오분류
- reading order
- key-value region과 pseudo-table 구분
- page edge에 붙은 table 누락
- downstream Markdown의 section hierarchy

Docling model catalog는 Egret을 제공하지만 현재 default는 Heron이며, issue tracker에는 Egret label mapping 및 edge-to-edge table 같은 통합 이슈가 보고된 적이 있다. production 적용 전 사용 중인 Docling version에서 반드시 smoke test한다.

### 6.4 권장 production architecture

```text
                        ┌─ native PDF text + positions ───────────┐
PDF -> fast inspector ─┤                                         ├─ merge
                        └─ raster pages/regions                    │
                              -> layout detector                   │
                              -> primary parser VLM                │
                              -> specialized fallback              │
                                   table/formula/chart/handwriting ┘
                                         |
                                         v
                         structured document + provenance
                                         |
                         validation / confidence / retry gate
```

권장 원칙:

- text는 가능한 한 deterministic source에서 보존한다.
- VLM은 structure와 어려운 visual content에 집중시킨다.
- 모델명뿐 아니라 source page, bbox, parser version, prompt, confidence를 저장한다.
- 모든 실패를 더 큰 VLM로 보내지 말고 실패 유형에 맞는 fallback을 선택한다.
- page 결과와 document-level merge 결과를 별도로 평가한다.

---

## 7. 사내 A/B 평가 설계

### 7.1 corpus

최소 200~500 page를 다음 bucket으로 고정한다.

| bucket | 예시 |
| --- | --- |
| born-digital simple | 단일 column 보고서 |
| born-digital complex | 다단 column, pseudo-table, font encoding 문제 |
| scan clean/noisy | 200/300 DPI, blur, skew |
| photographed | warp, shadow, illumination, screen photo |
| tables | borderless, merged cell, nested, cross-page |
| formula/code | inline/display math, code block |
| multilingual | 한국어, 영어, 한영 혼합, 필요 시 중·일문 |
| graphics | chart, diagram, scientific figure |
| long document | 20/50/100+ page |
| high-risk KIE | 금액, 날짜, 계좌, 계약 조항, ID |

### 7.2 metrics

```text
문자: CER / NED
구조: heading/list hierarchy F1
표: TEDS + critical-cell exact match
수식: CDM 또는 compile success + symbol exact match
순서: reading-order edit distance
레이아웃: class별 mAP/recall
장문: cross-page table/paragraph continuity
환각: unsupported span rate / blank-page hallucination
운영: pages/s, p50/p95, VRAM peak, GPU-hours/1k pages
RAG: retrieval hit@k와 answer exactness
```

특히 숫자·날짜·식별자는 별도 exact match를 둔다. 평균 CER이 좋아도 송장 total이나 계약 날짜 하나가 틀리면 실제 품질은 실패다.

### 7.3 공정한 비교 조건

- 동일 rasterizer, DPI, color mode
- model별 공식 권장 prompt와 별도의 공통 prompt를 모두 기록
- Markdown normalization 고정
- table HTML/Markdown 변환 규칙 고정
- header/footer 포함 정책 고정
- retry와 postprocessing 횟수 포함
- warm-up 제외 규칙과 batch/concurrency 기록
- model revision hash, inference framework, dtype 기록
- vendor score와 local score를 같은 표의 다른 열에 기록

---

## 8. 실행 순서

### Phase 0. 현재 baseline 고정

- Heron101 + DeepSeek-OCR-2의 model revision, prompt, DPI, batch, vLLM version 고정
- page별 latency, visual/output token, VRAM, parse result 저장
- native PDF와 scan PDF를 분리한 점수 산출

### Phase 1. PDF-aware routing

- PDF Inspector 또는 동등 heuristic으로 page type 분류
- native text extraction과 기존 전면 OCR 비교
- GPU로 보내는 page 비율과 숫자 hallucination 변화 측정

### Phase 2. parser 후보 A/B

- PaddleOCR-VL-1.6
- MinerU2.5-Pro hybrid
- OvisOCR2
- 기존 DeepSeek-OCR-2

### Phase 3. 특화 후보

- long document: Unlimited-OCR
- KIE/DocQA: GLM-OCR, Qianfan-OCR
- chart/diagram: dots.mocr-svg
- old scan/English/handwriting: olmOCR 2
- latency/edge: HunyuanOCR-1.5 또는 Granite-Docling 258M

### Phase 4. production gate

- document type router
- confidence/provenance schema
- exact-field validator
- fallback policy
- model/version canary

---

## 9. 최종 추천

현재 상태에서 바로 하나만 선택한다면 **PaddleOCR-VL-1.6 pipeline**을 첫 비교 대상으로 삼는다. 0.9B VLM, PP-DocLayoutV3, polygon bbox, cross-page merge, 공식 vLLM 연동이 현재 Heron101+DeepSeek-OCR-2의 역할을 가장 직접적으로 대체한다.

그러나 production architecture의 핵심 변화는 모델 교체가 아니다. **PDF Inspector류의 routing과 native text 보존을 먼저 도입하고, OCR/VLM은 필요한 page와 region에만 적용하는 것**이 더 중요하다. 그 위에서:

- 범용 1순위: PaddleOCR-VL-1.6
- 제품형 hybrid: MinerU2.5-Pro
- 소형 end-to-end 실험: OvisOCR2
- 장문: Unlimited-OCR
- KIE/DocQA: GLM-OCR 또는 Qianfan-OCR
- graphics: dots.mocr
- 영어 old scan: olmOCR 2

로 역할을 나누는 것이 합리적이다.

DeepSeek-OCR-2는 최신 leaderboard 최상단은 아니지만 visual token compression, causal reading order, 이미 구축된 vLLM 운영 자산이 있다. 따라서 제거 대상이 아니라 **고정 baseline이자 특정 문서군 fallback**으로 남겨 두고, 실제 한국어 사내 corpus에서 비용 대비 품질로 승부를 결정한다.

---

## 10. 핵심 출처 모음

### Benchmark

- [OmniDocBench GitHub](https://github.com/opendatalab/OmniDocBench)
- [OmniDocBench paper](https://arxiv.org/abs/2412.07626)
- [OCR Arena](https://www.ocrarena.ai/leaderboard)

### Parser/model

- [Docling model catalog](https://github.com/docling-project/docling/blob/main/docs/usage/model_catalog.md)
- [DeepSeek-OCR-2](https://github.com/deepseek-ai/DeepSeek-OCR-2)
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)
- [MinerU](https://github.com/opendatalab/MinerU)
- [GLM-OCR](https://github.com/zai-org/GLM-OCR)
- [HunyuanOCR](https://github.com/Tencent-Hunyuan/HunyuanOCR)
- [Qianfan-OCR](https://huggingface.co/baidu/Qianfan-OCR)
- [Unlimited-OCR](https://github.com/baidu/Unlimited-OCR)
- [OvisOCR2](https://huggingface.co/ATH-MaaS/OvisOCR2)
- [dots.mocr](https://github.com/rednote-hilab/dots.mocr)
- [olmOCR](https://github.com/allenai/olmocr)
- [Granite-Docling 258M](https://huggingface.co/ibm-granite/granite-docling-258M)

### Routing/tooling

- [Firecrawl PDF Inspector](https://github.com/firecrawl/pdf-inspector)
- [PDF Inspector Rust API](https://github.com/firecrawl/pdf-inspector/blob/main/docs/rust-api.md)

