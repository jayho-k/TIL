# Self-ask의 프롬프트와 실행 방식: 번역본 분석 및 코드 예제

> 작성·출처 확인: 2026-10-10.
> 분석 대상: [Self-ask 한국어 번역본](self-ask_ko_translation.md), 사용자 제공 [원문 PDF](paper/self-ask.pdf), *Measuring and Narrowing the Compositionality Gap in Language Models*, arXiv:2210.03350v3, 2023-10-17.
> 이 문서는 번역본 3.1·3.3·3.4·3.5·3.6절, 그림 2·3, 부록 표 10·13, 각주 4·5를 읽고 작성한 분석이다. 논문의 방식, 저자 공개 데모, 아래에서 새로 작성한 설명용 코드를 구분한다.

## 1. 앞선 설명과 코드에서 바로잡을 부분

앞선 코드의 큰 흐름인 **모델이 후속 질문 생성 → 코드가 검색 → 결과를 모델에 전달 → 다음 질문 또는 최종 답변 생성**은 Self-ask + Search Engine과 일치한다. 그러나 system prompt에서 JSON 행동을 선택하도록 한 코드는 원 논문 구현을 재현한 것이 아니다. 현대 채팅 모델에 적용하기 위한 변형이었다.

| 항목 | 앞서 제시한 코드 | 논문에 서술된 방식 |
| --- | --- | --- |
| 입력 | system/user/assistant 메시지 | 예시와 실제 질문을 연결한 프롬프트 문자열 |
| 고정 프롬프트 | 검색 행동을 지시하는 규칙과 예시 | 질문·후속 질문·중간 답·최종 답이 완성된 one-shot/few-shot 예시 |
| 출력 | `action`, `query`, `answer` JSON | `Follow up:`, `Intermediate answer:`, `So the final answer is:` 표식이 있는 텍스트 |
| 검색 시점 | JSON의 `action`을 읽은 뒤 | 중간 답이 생성되기 전에 멈춘 뒤 |
| 검색 결과 삽입 | 별도 메시지에 문서 목록 추가 | `Intermediate answer:` 뒤에 답을 붙여 같은 프롬프트를 이어 쓰기 |
| 모델에 보이는 검색 API | 검색 행동을 출력하도록 명시 | API 호출 자체는 노출하지 않고 중간 답만 보여 줌 |
| 검색 결과 형태 | 문서 ID와 원문 목록 | 검색 엔진이 반환한 답 또는 스니펫 |
| 출처 표기·근거 부족 처리 | 지침으로 추가 | 해당 동작이 원 논문 방식의 필수 요소로 정의되지는 않음 |

근거: 번역본 3.1절과 3.3절. 따라서 앞선 코드를 원 논문과 같은 방식으로 이해하면 혼동이 생긴다. 또한 앞선 `search()`는 조건문으로 가상 문서를 반환했다. 실행 흐름을 설명하는 용도이며 검색 정확도를 검증한 코드가 아니다.

## 2. Self-ask와 Self-ask + Search는 구분해야 한다

### 2.1 검색 없는 Self-ask

번역본 3.1절의 Self-ask는 모델이 후속 질문과 중간 답을 모두 생성한다. 고정 예시 뒤에 실제 질문을 붙이고 모델이 전체 응답을 이어 쓰게 한다.

```text
[완성된 질문·후속 질문·중간 답·최종 답 예시]

Question: {이번 사용자 질문}
Are follow up questions needed here:
```

이 뒤의 필요 여부, 후속 질문, 중간 답, 최종 답은 모델 출력이다. 후속 질문이 필요하지 않다고 판단하면 바로 답할 수도 있다. 따라서 Self-ask 자체가 반드시 외부 검색을 수행하는 것은 아니다.

### 2.2 검색을 결합한 Self-ask

번역본 3.3절의 핵심은 **검색 없는 Self-ask와 같은 프롬프트를 사용하면서, 중간 답만 외부 검색 결과로 대신 채우는 것**이다.

1. 모델이 후속 질문을 작성한다.
2. 중간 답을 작성하기 직전에 생성을 멈춘다.
3. 애플리케이션이 후속 질문 전체를 검색 API에 전달한다.
4. 검색 엔진의 답을 `Intermediate answer:` 뒤에 삽입한다.
5. 누적된 프롬프트를 모델에 전달하여 생성을 계속한다.
6. 최종 답 표식이 나오면 종료한다.

모델 가중치를 바꾸거나 검색 도구 호출 문법을 학습시키지 않는다. 이미 예시에서 보여 준 중간 답 형식을 코드가 채우므로 기존 생성 패턴을 유지할 수 있다. 이것이 논문이 설명하는 파인튜닝 없이 검색을 결합하는 원리다.

### 2.3 “한 번의 생성”과 “모델을 여러 번 호출”의 관계

번역본 3.6절은 검색 없는 Self-ask를 설명하면서 하나의 프롬프트로 질문 분해와 중간 답을 생성하는 점을 강조한다. 이를 검색을 결합한 방식도 API 호출 한 번으로 끝난다는 뜻으로 읽으면 안 된다. 3.3절은 검색마다 생성을 중단하고 결과를 삽입한 뒤 재개하는 과정을 설명한다.

아래 코드는 재개를 **누적 문자열을 다시 전달하는 호출**로 구현한다. 고정 예시를 바꾸지 않는다는 것과 호출 횟수가 한 번이라는 것은 서로 다른 이야기다.

## 3. 고정 프롬프트와 동적으로 생성되는 검색 질문

사용자의 질문은 두 부분으로 나눠 생각하면 된다.

| 내용 | 준비하는 주체 | 변경 시점 |
| --- | --- | --- |
| 완성된 분해·답변 예시 | 개발자 | 예시를 개선할 때 |
| 사용자 원래 질문 | 사용자 | 요청마다 |
| 후속 질문 | 모델 | 실행 중 |
| 중간 답 | 모델 또는 검색 엔진 | 실행 중 |
| 최종 답 | 모델 | 실행 마지막 |

**개발자가 질문마다 새로운 system prompt를 만들어야 하는 것이 아니다. 고정 예시와 사용자 질문을 입력하면 모델이 검색 질문을 출력한다.** 그 출력에 따라 애플리케이션이 실제 검색을 실행한다.

논문은 무예시 지침만 사용한 zero-shot 방식으로 이 방법을 검증한 것이 아니다. 번역본 3.4절은 실험에서 few-shot 예시를 사용한다고 설명하며, 3.5절은 데이터셋별 예시 선정 과정을 설명한다. 2WikiMultiHopQA에서는 네 예시를 사용했고, Bamboogle에는 같은 프롬프트를 사용했다. Musique에서는 학습 집합으로 예시와 형식을 선택했다. 따라서 “예시 개수는 항상 네 개”도 “예시를 요청마다 만들어야 한다”도 논문의 결론은 아니다.

각주 4는 작은 모델에서 프롬프트 끝에 `Yes. Follow up:`까지 붙이는 것이 도움이 되었다고 설명한다. 이는 후속 질문 생성을 유도하는 설정이며, 모든 질문에서 자유롭게 분해 필요 여부를 판단하게 하는 설정과는 차이가 있다.

## 4. 논문 방식의 최소 코드

아래 코드는 원 논문의 **문자열 이어 쓰기·중간 답에서 중단·외부 답 삽입**을 보존한 설명용 재구현이다. 저자 코드의 복사본이나 실험 전체를 재현하는 코드는 아니다.

고정 예시는 번역본 부록 표 13의 첫 예시를 기반으로 한국어 내용과 영어 표식을 결합했다. 이는 실행 구조를 설명하기 위한 것이며, 논문에서 사용한 영어 프롬프트와 동일한 성능을 보장하지 않는다.

모델 연결은 `complete(prompt, stop)` 함수로 받는다. 이 함수는 **프롬프트 뒤에 새로 생성된 텍스트만 반환**해야 한다. stop 문자열을 반환값에 포함하지 않고 그 직전에서 멈춘다는 계약을 사용한다.

```python
FEW_SHOT = """Question: 테오도어 해커와 해리 본 왓킨스 중 누가 더 오래 살았는가?
Are follow up questions needed here: Yes.
Follow up: 테오도어 해커는 사망 당시 몇 살이었는가?
Intermediate answer: 테오도어 해커는 사망 당시 65세였다.
Follow up: 해리 본 왓킨스는 사망 당시 몇 살이었는가?
Intermediate answer: 해리 본 왓킨스는 사망 당시 69세였다.
So the final answer is: 해리 본 왓킨스.

"""

FOLLOW_UP = "Follow up:"
INTERMEDIATE = "\nIntermediate answer:"
FINAL = "So the final answer is:"


def build_prompt(question):
    # 요청마다 바뀌는 것은 question이다. FEW_SHOT은 그대로다.
    return (
        FEW_SHOT
        + "Question: " + question
        + "\nAre follow up questions needed here:"
    )


def self_ask_with_search(question, complete, search_answer, max_searches=5):
    prompt = build_prompt(question)
    searches = 0
    events = []

    while True:
        # 모델의 중간 답을 생성하기 전에 중단한다.
        generated = complete(prompt, stop=[INTERMEDIATE, "\nQuestion:"])
        events.append(("model", generated))
        prompt += generated

        # 고정 예시에 있는 FINAL을 잘못 읽지 않도록 새 출력만 확인한다.
        if FINAL in generated:
            answer = generated.rsplit(FINAL, 1)[1].strip()
            if not answer:
                raise ValueError("최종 답 표식 뒤에 답이 없습니다.")
            return {"answer": answer, "transcript": prompt, "events": events}

        lines = generated.strip().splitlines()
        if not lines or not lines[-1].startswith(FOLLOW_UP):
            raise ValueError("후속 질문 또는 최종 답 형식이 아닙니다.")

        follow_up = lines[-1][len(FOLLOW_UP):].strip()
        if not follow_up:
            raise ValueError("후속 질문이 비어 있습니다.")
        if searches >= max_searches:
            raise RuntimeError("검색 횟수 제한에 도달했습니다.")

        # 키워드로 다시 바꾸지 않고 후속 질문 전체를 전달한다.
        intermediate_answer = search_answer(follow_up)
        searches += 1
        if not intermediate_answer or not intermediate_answer.strip():
            raise RuntimeError("검색에서 중간 답을 얻지 못했습니다.")

        events.append(("search", (follow_up, intermediate_answer)))

        # 검색 답을 별도 user 메시지가 아닌 같은 문자열에 삽입한다.
        prompt += INTERMEDIATE + " " + intermediate_answer.strip()
```

핵심은 아래 세 줄이다.

```text
generated = complete(prompt, stop=[INTERMEDIATE, ...])
intermediate_answer = search_answer(follow_up)
prompt += INTERMEDIATE + " " + intermediate_answer
```

`stop`은 예시 안의 기존 문자열을 검사하는 설정이 아니라 **새로 생성될 출력**에 적용되는 설정이다. 모델이 중간 답의 표식을 생성하려는 시점에 멈추므로, 코드가 표식을 다시 붙이고 외부 답으로 빈칸을 채운다.

이 재구현은 형식 오류, 다음 질문 시작, 검색 횟수 제한, 검색 실패를 명시적으로 처리한다. 이런 처리는 설명용 코드에 추가한 것이다. 특히 검색 실패 때 바로 중단하는 정책은 논문 방법의 필수 조건이 아니다. 저자 공개 데모는 검색 답이 없는 경우 모델 답을 쓰는 분기를 포함하므로 정책이 다르다. 원 논문과 같은 데이터셋·모델·프롬프트·검색 응답을 재현했다고 주장하지 않는다.

## 5. 실제 전달되는 문자열 확인

그림 3의 질문을 사용하면 첫 모델 입력의 끝부분은 다음과 같다. 아래에서는 고정 예시를 생략해서 표시했다.

```text
[고정 예시]

Question: 현재 가장 높은 목조 격자 탑은 어느 해에 완공되었는가?
Are follow up questions needed here:
```

모델의 첫 출력은 다음과 같은 모양이다.

```text
 Yes.
Follow up: 현재 가장 높은 목조 격자 탑은 무엇인가?
```

모델이 이어서 중간 답 표식을 생성하려는 순간 중단한다. 애플리케이션은 후속 질문을 검색하고 답을 삽입한다. 그러면 **두 번째 모델 입력**은 아래처럼 된다.

```text
[처음과 동일한 고정 예시]

Question: 현재 가장 높은 목조 격자 탑은 어느 해에 완공되었는가?
Are follow up questions needed here: Yes.
Follow up: 현재 가장 높은 목조 격자 탑은 무엇인가?
Intermediate answer: 글리비체 라디오 탑.
```

이것을 이어 쓰는 모델이 다음 질문을 생성한다.

```text
Follow up: 글리비체 라디오 탑은 언제 완공되었는가?
```

다음 검색 답을 넣은 **세 번째 모델 입력**은 다음과 같다.

```text
[처음과 동일한 고정 예시]

Question: 현재 가장 높은 목조 격자 탑은 어느 해에 완공되었는가?
Are follow up questions needed here: Yes.
Follow up: 현재 가장 높은 목조 격자 탑은 무엇인가?
Intermediate answer: 글리비체 라디오 탑.
Follow up: 글리비체 라디오 탑은 언제 완공되었는가?
Intermediate answer: 1935.
```

마지막으로 모델이 `So the final answer is: 1935.`를 생성한다. 후속 질문에 등장하는 탑 이름은 개발자가 사전에 넣은 것이 아니라 첫 검색 답에서 얻은 것이다.

이 사례는 논문 그림 3의 실행 흐름이다. 여기서 “현재”는 논문 사례의 표현을 설명한 것이며 2026년 현재 기록을 새로 확인한 주장이 아니다.

### 5.1 외부 모델 없이 실행 흐름만 확인하는 코드

아래 코드를 4절 코드 뒤에 붙이면 표준 Python만으로 실행할 수 있다. `scripted_complete`는 모델 출력을 미리 정해 놓은 대역이고 `example_search`도 그림 3의 답을 반환하는 대역이다. 실제 추론·검색 정확도를 보여 주는 실험이 아니다.

```python
QUESTION = "현재 가장 높은 목조 격자 탑은 어느 해에 완공되었는가?"
Q1 = "현재 가장 높은 목조 격자 탑은 무엇인가?"
Q2 = "글리비체 라디오 탑은 언제 완공되었는가?"

scripted_outputs = iter([
    " Yes.\nFollow up: " + Q1,
    "\nFollow up: " + Q2,
    "\nSo the final answer is: 1935.",
])


def scripted_complete(prompt, stop):
    print("\n--- 모델에 전달한 이번 질문의 누적 문자열 ---")
    print(prompt[len(FEW_SHOT):])
    return next(scripted_outputs)


def example_search(query):
    answers = {Q1: "글리비체 라디오 탑.", Q2: "1935."}
    print("검색 질문:", query)
    return answers.get(query)


result = self_ask_with_search(QUESTION, scripted_complete, example_search)
print("\n최종 답:", result["answer"])
```

이 코드는 모델이 만들어야 할 질문을 미리 고정한 실행 흐름 확인용이다. 실제 모델 연결 시 `scripted_complete`를 실제 모델 호출로 교체한다. 기본 반복 구조는 유지할 수 있지만, 실제 사용 전 보완 사항은 9절에서 확인한다.

## 6. 보유 모델과 기존 RAG에 연결하기

### 6.1 보유 모델 연결 예: Ollama

다음은 문자열 completion을 제공하는 연결 예다. 4절 코드와 함께 사용한다. Ollama가 실행 중이고 `OLLAMA_MODEL`에 이미 보유한 모델 이름을 지정해야 한다. 이 연결은 원 논문이 사용한 모델·런타임과 다르다.

```python
import json
import os
from urllib.request import Request, urlopen


def ollama_complete(prompt, stop):
    payload = {
        "model": os.environ["OLLAMA_MODEL"],
        "prompt": prompt,
        "raw": True,
        "stream": False,
        "options": {"temperature": 0, "num_predict": 256, "stop": stop},
    }
    request = Request(
        "http://localhost:11434/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=120) as response:
        data = json.load(response)
    return data["response"]


# example_search는 5.1절의 대역이므로 검색까지 실제로 연결한 예는 아니다.
# result = self_ask_with_search(QUESTION, ollama_complete, example_search)
```

`raw=True`는 모델의 자동 프롬프트 템플릿 적용을 건너뛰는 설정이다. 지침형·채팅형 모델이 이 원시 문자열 형식에서 원하는 completion을 생성한다는 보장은 없다. 보유 모델이 completion에 적합하지 않다면 채팅 형식으로 옮겨 검증해야 하며, 그때는 현대 모델에 맞춘 변형이라고 기록해야 한다. 위 함수는 실제 모델에 연결하는 예시이고 이번 문서 작성 중 실제 모델 호출은 수행하지 않았다. API 설정 근거: [Ollama Generate 공식 문서](https://docs.ollama.com/api/generate).

### 6.2 기존 RAG는 검색 결과와 중간 답의 차이를 처리해야 한다

논문은 검색 엔진의 답·스니펫을 중간 답으로 삽입한다. 기존 Advanced RAG의 retriever가 반환하는 것은 여러 문서 청크일 수 있다. 그러면 `search_answer()`에 다음 처리가 필요하다.

```text
후속 질문
    ↓
기존 검색 파이프라인: 검색 → 병합 → reranking
    ↓
선택한 청크에서 해당 후속 질문의 답 추출
    ↓
짧은 중간 답을 Self-ask 프롬프트에 삽입
```

짧은 답 추출에는 보유 모델을 사용할 수도 있지만, 이는 RAG 결과 형식에 맞춘 추가 설계이며 그만큼 모델 호출 비용이 늘어난다. 문서 원문 전체를 중간 답 자리에 넣는 구성도 가능하지만 원 논문의 짧은 답·스니펫 삽입과는 입력 길이 및 잡음 조건이 달라진다.

원문 청크와 출처 ID는 애플리케이션 상태에 별도로 보관하고, 최종 답변을 작성할 때 연결할 수 있다. 원 논문에서 출처 검증까지 자동으로 해결되었다고 해석하면 안 된다.

### 6.3 system prompt와 LangGraph는 어디에 해당하는가?

채팅 모델에서는 고정 지침을 system 메시지에, 예시를 대화에, 검색 결과를 tool 메시지에 넣는 구성이 가능하다. 다만 이는 논문 프롬프트를 현대 모델에 맞춰 옮기는 선택이다. system prompt만 넣으면 논문 방식과 같아지는 것은 아니다. 질문·중간 답·최종 답의 예시와 반복 실행 구조까지 확인해야 한다.

LangGraph는 `모델 생성 → 검색 → 중간 답 삽입 → 모델 생성`의 실행 상태와 반복을 관리할 수 있다. Self-ask의 기여는 프레임워크가 아니라 모델이 질문을 분해하고 답을 조합하도록 유도하는 프롬프팅 방식이다. 4절처럼 일반 Python 반복문으로도 핵심 흐름을 구현할 수 있다.

## 7. 단일 홉 검색 개선이라는 현재 목표에 대한 판단

Self-ask는 주로 복수 사실을 연결해야 하는 조합적 질문에서 질문 분해와 답 조합을 개선하는 연구다. 검색기 자체의 단일 홉 정확도를 개선했다는 결론을 제시한 논문으로 읽으면 안 된다.

번역본 표 1에서 검색 결합 전후의 2WikiMultiHopQA 정확도는 30.0% → 40.1%다. 이는 다중 홉 질의응답 결과이고, 동일한 단일 홉 검색기의 Recall@k 또는 nDCG 개선 수치가 아니다. 이 구분은 네가 이미 Advanced RAG를 구축했고 우선 단일 홉 검색 정확도를 올리려 한다는 조건에서 중요하다.

Self-ask를 적용할 때 확인할 것은 다음과 같다.

- 분해가 필요한 질문에서 모델이 정확한 후속 질문을 생성하는가?
- 앞선 검색 답의 엔티티·조건을 다음 질문에 제대로 반영하는가?
- 잘못된 중간 답이 뒤의 검색까지 오염시키는가?
- 단일 홉 질문을 불필요하게 분해해서 지연과 오류를 늘리는가?

단일 홉 질의를 더 잘 검색되는 표현으로 바꾸는 작업은 Query Reformulation 실험으로 별도 평가하는 것이 적합하다. Self-ask의 반복 구조를 도입하는 것만으로 그 목표를 달성했다고 판단할 수 없다.

## 8. 근거와 검증 범위

| 출처 | 사용한 내용 | 신뢰도·제약 |
| --- | --- | --- |
| [사용자 제공 PDF](paper/self-ask.pdf), v3, 2023-10-17 | 원 논문 기준 | 1차 자료. 이 문서는 기존 번역본을 주로 읽고 분석함 |
| [한국어 번역본](self-ask_ko_translation.md), 2026-10-10 작성 | 3.1·3.3절, 그림 2·3, 예시 선정·실험·각주 | 작업한 번역 자료. 원문과 구별하여 인용 |
| [저자 공식 데모](https://github.com/ofirpress/self-ask/blob/main/self-ask_plus_search-engine_demo.ipynb), 2026-10-10 확인 | 문자열 누적, stop, 답 삽입, 검색 실패 분기 | 1차 구현 자료. 데모의 네 예시는 논문 부록 예시와 동일하지 않음. 현재 서비스 구현의 일반적 표준으로 간주하지 않음 |
| [Ollama Generate API](https://docs.ollama.com/api/generate), 2026-10-10 확인 | 연결 예의 API·raw·stream 설정 | 제품 공식 문서. 실제 보유 모델의 동작은 별도 검증 필요 |

문서의 핵심 코드와 대역 실행을 검증하여 중간 답 삽입 후 누적 프롬프트가 다음 모델 호출에 전달되는지 확인한다. 대역 검증은 실제 모델의 질문 분해 능력, 실 검색 품질, 논문 성능 재현을 입증하지 않는다.

## 9. 코드 재검토와 최근 연구 방향

> 재검토·자료 확인: 2026-10-10. 실제 보유 모델 호출 없이 기존 코드에 대역 출력을 입력해 오류 경로를 확인했다. 다음은 구현 검토와 최근 1차 자료의 비교이며, 모든 업계 구현에 대한 전수 조사나 성능 개선 보장은 아니다.

### 9.1 “그대로 사용할 수 있다”는 판단의 보정

기본 반복 구조는 가져다 사용할 수 있다. 그러나 두 연결 함수만 구현하면 별도 보완 없이 안정적으로 사용할 수 있다는 뜻은 아니다. 4절 코드는 원 논문 동작을 설명하는 최소 예제이며, 아래에서 실제 재현된 파싱 문제와 반복 검색 처리가 남아 있다.

| 우선순위 | 발견 사항 | 확인 방식 | 필요한 보완 |
| --- | --- | --- | --- |
| 먼저 | 최종 답 표식을 부분 문자열로 검사 | 후속 질문 안에 `So the final answer is:`를 넣으면 검색 없이 질문 뒷부분을 최종 답으로 반환 | 표식이 독립된 행의 시작에 있는지 확인하고, 후속 질문·최종 답 동시 출력 등 잘못된 조합 거부 |
| 먼저 | 표식의 대소문자·줄바꿈에 의존 | `Intermediate Answer:`가 포함된 대역 출력에서 파싱 실패 재현 | 보유 모델과 출력 계약을 검증하고 허용할 형식을 명시. stop이 놓친 출력을 단순 정상 답으로 받아들이지 않기 |
| 먼저 | 중복 검색 제어 없음 | 같은 후속 질문을 다섯 번 검색한 뒤 횟수 제한으로 종료되는 것을 재현 | 정규화한 질문 기록과 검색 결과 캐시. 같은 결과를 얻는 반복이면 재작성 또는 중단 |
| 연결 시 | 검색 실패를 빈 문자열과 예외로만 처리 | 코드 검토: 근거 없음과 일시적 API 오류를 구분하지 않음 | `no_evidence`, `timeout`, `error` 같은 상태 구분. 일시 오류에만 제한된 재시도 |
| 연결 시 | 모델 응답의 종료 이유를 버림 | Ollama 연결 함수는 `response`만 반환 | 출력 길이 제한으로 잘렸는지 확인. 형식 오류 재생성도 횟수 제한 적용 |
| 데이터 연결 시 | 중간 답이 문자열 하나 | 코드 검토: 근거·충돌·추출 실패를 표현하는 상태 없음 | 애플리케이션 상태에 답, 근거 청크 ID, 원문 인용, 확인 여부 보관 |
| 요구사항에 따라 | 검색 없는 즉시 답을 허용 | `No.` 뒤에 최종 답을 주면 검색 없이 반환되는 것을 확인 | 원 논문에서는 허용. 문서 근거가 필수인 서비스라면 근거 확인 없이 종료하지 않도록 정책 추가 |
| 반복 비용 관리 | 누적 문자열에 크기 제한 없음 | 코드 검토: 매번 누적 프롬프트 전체 전달 | 토큰·시간 예산과 중간 답 길이 제한. 필요할 때 관련 근거를 선택해서 전달 |

첫 문제를 재현한 모델 출력 대역은 아래와 같다.

```text
 Yes.
Follow up: 문서의 So the final answer is: 표식 의미는?
```

기존 코드는 `if FINAL in generated`를 먼저 실행하여 `표식 의미는?`를 답으로 반환했다. 이는 문서의 원래 질문 분해 예시와 무관하게 출력 파싱을 보완해야 한다는 직접적인 근거다.

파서에서 행 경계를 확인하는 것이 최소 수정이다. 다만 파서만 고치면 모델이 필요한 검색을 수행하거나 근거 있는 답을 한다는 보장은 없다. 프로토콜 검증과 근거 검증은 서로 다른 확인이다.

실행 상태는 예를 들어 다음과 같이 보관할 수 있다. 이 JSON은 원 논문 출력 형식이 아니라 애플리케이션 내부 상태 예시다.

```json
{
  "question": "서비스 A가 사용하는 DB의 백업 주기는?",
  "searches": [
    {
      "query": "서비스 A가 사용하는 DB는 무엇인가?",
      "status": "supported",
      "answer": "데이터베이스 B",
      "evidence_ids": ["doc-1"]
    }
  ],
  "search_count": 1
}
```

다음 질문에 필요한 엔티티는 짧은 답으로 전달하되, 그 답을 뒷받침하는 원문은 따로 유지한다. 예컨대 “매일”로 요약하면서 “운영 DB만 해당”이라는 조건을 지워 버리면 다음 질문과 최종 답을 잘못 만들 수 있다. 근거 없는 요약을 확정 사실처럼 누적하지 않는 것이 중요하다.

### 9.2 요즘 방향과 일치하는 부분

**검색 결과를 보고 다음 검색을 결정하는 Self-ask의 핵심은 최근 검색 에이전트 연구와 같은 방향이다. 다만 2022년의 표식 기반 문자열 completion을 그대로 유지하는 것이 최신 구현의 필수 조건은 아니다.** 다음 자료들이 이 판단의 근거다.

| 자료·발표 시점 | 확인한 내용 | 현재 구성에 주는 의미 |
| --- | --- | --- |
| [Search-o1](https://arxiv.org/abs/2501.05366), 2025-01-09 최초 공개 | 추론 중 필요한 외부 정보를 동적으로 검색하며, 별도 Reason-in-Documents 모듈로 검색 문서를 분석한 후 추론에 삽입 | 후속 검색뿐 아니라 검색 결과를 다음 단계에 적합하게 정리하는 과정이 중요 |
| [Search-R1](https://arxiv.org/abs/2503.09516), 2025-03-12 최초 공개 | 다중 검색과 추론을 강화학습으로 학습 | 반복 검색이라는 문제의식은 이어짐. 이 학습 절차는 파인튜닝 불가 조건에서 직접 적용할 대상이 아님 |
| [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents), 2025-09-29 | 도구를 반복 사용하는 에이전트에서 다음 호출에 전달할 지침·예시·기록·외부 데이터를 선별하는 설계 강조 | 고정 프롬프트 외에 실행 상태와 근거 길이를 관리해야 함 |
| [Claude Web search 공식 문서](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool), 2026 버전 포함, 2026-10-10 확인 | 검색 결과가 모델 컨텍스트에 들어가기 전에 관련 정보를 필터링하는 기능 설명 | 검색 결과를 모두 누적하기보다 다음 판단에 필요한 내용만 전달하는 제품 구현 사례 |

위 표는 개별 연구·제품 사례에 기반한 비교다. “모든 회사가 Self-ask를 쓴다”거나 “도구 호출이 항상 문자열 completion보다 성능이 높다”는 결론은 아니다.

보유 모델이 도구 호출을 지원한다면, 후속 질문을 검색 도구의 인자로 출력하고 결과를 도구 메시지로 돌려주는 방식을 우선 검토할 수 있다. 그러면 문자열 표식 추출에 대한 의존을 줄인다. 도구 호출이 없으면 스키마가 정해진 JSON 출력과 검증기를 사용하는 선택도 있다. 두 방식 모두 앱이 입력·출력을 검증해야 한다. 파인튜닝 없이 이미 보유한 모델의 기능을 사용하는 구현 선택이다.

### 9.3 최근 흐름은 “검색 횟수를 무조건 늘린다”로 한정되지 않는다

[SIRA: Superintelligent Retrieval Agent: The Next Frontier of Agentic Retrieval](https://arxiv.org/abs/2605.06647v3)는 2026-05-07 최초 공개, 2026-08-24 v3로 갱신된 사전 공개 논문이다. 문서의 검색 어휘 보강, 질문에서 빠진 어휘 예측, 코퍼스 통계로 확장 어휘 검증을 결합해 최종 검색을 한 번의 가중 BM25 호출로 수행한다. 검색기 파인튜닝과 relevance label을 요구하지 않는다고 보고한다. 이는 초록·arXiv 메타데이터 수준에서 확인한 자료이며, 현재 검토에서 본문·실험을 독립적으로 검증한 추천은 아니다.

이 사례는 단일 홉 검색을 높이고 싶고 파인튜닝 여력이 없는 현재 조건과 가까운 읽기 후보다. 다만 인덱스 보강 비용과 BM25 기반 설계를 함께 검토해야 하며, 기존 파이프라인에 바로 넣을 수 있다고 단정하지 않는다.

따라서 최근 방향은 필요할 때 반복 검색을 하면서도, 더 정확한 질의·근거 처리로 불필요한 호출을 줄이는 것으로 해석하는 편이 적절하다. Self-ask의 다음 질문 생성 구조를 사용하더라도 최대한 많이 검색하는 것이 목적은 아니다.

### 9.4 이 부분만 적용할 때의 보완 순서

1. **실행 계약:** 표식 파싱, 중복 검색, 호출 실패, 생성 중단 이유를 먼저 처리한다.
2. **근거 상태:** 중간 답과 원문 출처를 함께 보관하고, 근거 부족·충돌을 확정 답과 구별한다.
3. **모델에 맞는 형식:** completion, 채팅, 도구 호출 중 보유 모델이 안정적으로 수행하는 형식을 작은 질문 세트로 선택한다.
4. **비용과 품질 비교:** 같은 질문에서 기존 방식과 비교해 답 정확도, 근거 충족 여부, 검색 횟수, 지연, 토큰 수를 함께 기록한다.

프로토콜은 표식 포함 질문·형식 변형·같은 질문 반복·빈 검색 결과·생성 길이 제한을 확인한다. 실제 모델 평가는 직접 답 가능한 질문, 두 단계 의존 질문, 조건·버전 보존이 필요한 질문, 근거 없는 질문을 포함한다. 대역 테스트가 모델 평가를 대신하지는 않는다.

여기서 제안한 보완은 Self-ask 모듈에 대한 것이다. 기존 검색기·색인·reranker 전체를 다시 구축해야 한다는 의미는 아니다. 원 논문 방식의 학습 자료를 보존하기 위해 4절 최소 코드는 이 검토에서 수정하지 않고, 재현된 문제와 개선 방향을 별도로 기록했다.

## 10. 보완한 실행 코드와 사용법

> 수정·검증: 2026-10-10. 9절에서 확인한 문제를 보완했다. 4절은 논문 설명용 최소 코드로 보존하고, 이 절의 별도 실행 파일을 사용한다. 원 논문의 문자열 생성·외부 중간 답 삽입 구조를 유지하면서 오류 처리와 근거 정책을 추가한 구현이다.

### 10.1 실행 파일

| 파일 | 역할 |
| --- | --- |
| [code/self_ask.py](code/self_ask.py) | 행 단위 파서, 반복 검색, 상태·근거 보관, 종료 정책 |
| [code/self_ask_ollama.py](code/self_ask_ollama.py) | 보유 Ollama 모델 연결. 생성 종료 사유와 연결 오류 처리 |
| [code/example_self_ask.py](code/example_self_ask.py) | API 없이 누적 프롬프트와 두 단계 검색 흐름을 확인하는 대역 예제 |
| [code/test_self_ask.py](code/test_self_ask.py) | 회귀·예산·근거 상태·모델 연결 계약 테스트 |

현재 실행 코드는 11절의 LangGraph 변환본이다. LangGraph 설치 후 아래 명령을 사용한다. 의존성·그래프 테스트 실행법은 [LangGraph 사용 문서](03_self_ask_langgraph.md)를 참고한다.

```powershell
python .codex/research/AgentComponent/Decomposer/code/example_self_ask.py
python .codex/research/AgentComponent/Decomposer/code/test_self_ask.py
```

예제는 대역 모델과 대역 검색기를 사용한다. 성공 상태 `completed`, 답 `매일 새벽 2시에 백업합니다.`, 근거 ID `doc-1`, `doc-2`를 반환한다. 실제 모델 추론이나 검색 성능을 검증하는 예제가 아니다.

### 10.2 연결 함수의 계약이 바뀌었다

기존 최소 코드의 두 함수는 문자열을 반환했다. 보완한 코드에서는 종료 사유와 근거 상태를 전달하기 위해 아래 자료형을 사용한다. 기존 문자열 콜백을 그대로 전달하면 정상 실행되지 않는다.

```python
from self_ask import Completion, Evidence, SearchResult

# 모델 출력: 이어 쓴 문자열 + 종료 사유
model_result = Completion(
    text=" Yes.\nFollow up: 서비스 A가 사용하는 DB는 무엇인가?",
    finish_reason="stop",
)

# 검색 결과: 질문에 필요한 답 + 실제 원문 근거
retrieval_result = SearchResult(
    status="supported",
    answer="데이터베이스 B",
    evidence=(Evidence("doc-1", "서비스 A는 데이터베이스 B를 사용한다."),),
)
```

`complete(prompt, stop)`은 `Completion`을 반환한다. `finish_reason="length"`는 생성 길이 제한으로 잘렸다는 의미이며, 완성된 행동으로 받아들이지 않는다. 알 수 없는 종료 사유도 정상 완료라고 추정하지 않는다.

`search_answer(query)`는 `SearchResult`를 반환한다. `supported`로 반환할 때는 해당 질문을 뒷받침하는 답과 근거 ID·원문 인용을 담는다. 검색기에서 아무 청크나 나왔다는 이유만으로 `supported`를 지정해서는 안 된다. 질문과 근거의 관계·충돌·추출 성공 여부는 이 콜백에서 판별한다.

검색 상태는 `supported`, `no_evidence`, `conflicting_evidence`, `timeout`, `error`다. 근거 없음과 충돌은 그대로 종료하며 같은 검색을 재시도하지 않는다. 일시적 timeout·연결 실패·`TransientError`만 제한적으로 재시도한다. 설정 오류·코드 버그 같은 임의 예외는 무조건 숨기지 않고 호출자에게 전달한다.

### 10.3 실제 모델 연결

`code/`에서 가져오는 다음 함수가 기존 6.1절의 문자열 반환 함수를 대체한다.

```python
from self_ask_ollama import make_ollama_complete

# 아래 모델명은 Ollama에 이미 설치된 보유 모델명으로 지정한다.
complete = make_ollama_complete("보유한-모델명", timeout=20)
```

이 모델명은 사용자가 지정할 연결 설정이다. 모델을 설치·다운로드하거나 서버를 실행하는 코드는 아니다. 실제 호출은 다음과 같이 `run_self_ask()`에 이 함수와 기존 RAG에 연결한 `search_answer` 콜백을 전달한다.

```text
result = run_self_ask(user_query, complete, search_answer)
```

Ollama 어댑터는 `response`와 `done_reason`을 함께 보존한다. HTTP 429/5xx는 일시 오류로 전달하고, 나머지 HTTP 오류는 유효하지 않은 완료로 종료한다. 네트워크 재시도는 실행기에서 담당한다. `raw=True` 문자열 completion이므로 보유 모델이 이 프롬프트 형식을 안정적으로 수행하는지는 실제 질문으로 확인해야 한다. API 계약 확인 출처: [Ollama Generate 공식 문서](https://docs.ollama.com/api/generate), 2026-10-10 확인.

### 10.4 반영한 수정

| 검토에서 발견한 문제 | 보완 코드의 처리 |
| --- | --- |
| 후속 질문 내부의 최종 답 표식 오인 | 행 시작의 표식만 읽으며 질문 본문에 들어간 표식은 답으로 해석하지 않음 |
| 대소문자·공백 변화 | 파서가 표식의 대소문자와 행 앞뒤 공백을 허용. 주요 중간 답 표식 변형을 stop에 포함 |
| stop을 놓치고 모델이 중간 답 생성 | 후속 질문 하나와 그 중간 답만 있으면 모델 답을 폐기하고 외부 검색으로 교체. 여러 질문·최종 답까지 생성한 출력은 거부 |
| 잘못된 출력 | 제한된 횟수만 재생성한 후 `invalid_output` 종료. 동일 입력 재호출이 항상 형식을 교정한다는 보장은 없음 |
| 같은 검색 반복 | 유니코드·대소문자·공백 정규화 후 중복 감지. 재검색하지 않고 `duplicate_query` 종료 |
| 검색 실패 구분 없음 | 근거 없음·충돌·일시 오류·영구 오류를 상태로 구분 |
| 생성 잘림 | `length` 응답은 답으로 사용하지 않고 제한된 재생성 후 `generation_truncated` 종료 |
| 원문 근거 소실 | `searches`에 질문·답·상태·근거 ID·원문 인용 보관. 충돌 근거도 보존 |
| 누적 길이·비용 제한 없음 | 검색 수, 모델 호출 수, 문자 수, 실행 시간 제한 |

모델 출력 원문 전체를 프롬프트에 그대로 붙이지 않고, 검증한 후속 질문과 외부 중간 답을 표준 표식으로 다시 작성한다. 예시 안의 최종 답을 실행 중 답으로 오인하지 않도록 파싱은 새 출력에만 적용한다. 검색 답의 줄바꿈은 프롬프트 삽입 시 한 행으로 정리하고 원문 인용은 별도로 보존한다.

### 10.5 결과를 사용하는 방법과 기본 정책

반환값의 `status`가 `completed`일 때만 최종 `answer`를 사용한다. 다른 상태에서는 `answer=None`이다. 실행 기록과 근거는 `transcript`, `searches`, `events`, `model_calls`에 있다. 실패 상태를 정상 답변처럼 사용자에게 내보내지 말고 애플리케이션의 재질문·실패 안내 정책에 연결한다.

기본값은 다음과 같다.

| 옵션 | 기본값 | 의미 |
| --- | ---: | --- |
| `max_searches` | 5 | 서로 다른 검색 단계 제한. 일시 오류 재시도는 별도 시도이며 횟수 제한이 있음 |
| `max_model_calls` | 12 | 재시도를 포함한 모델 호출 제한 |
| `max_retries` | 1 | 해당 생성·검색 단계에서 추가 시도 한 번 |
| `max_prompt_chars` | 24000 | 누적 프롬프트의 문자 예산. 토큰 예산과 같지 않음 |
| `max_answer_chars` | 2000 | 행동 값과 중간 답 길이. 초과하면 임의로 자르지 않고 종료 |
| `max_seconds` | 60 | 호출 전후 확인하는 총 실행 시간 예산 |
| `require_evidence` | `True` | 외부 근거 없이 즉시 생성한 답을 `unverified_answer`로 처리 |

`require_evidence=False`이면 원 논문처럼 검색 없이 즉시 답하는 경로를 허용한다. 단, 검색을 수행할 때는 여전히 근거가 있는 `SearchResult`를 요구한다. 이 옵션은 최종 답의 사실성을 보장하는 검증기가 아니다.

시간 예산은 진행 중인 동기 호출을 강제로 취소하지 않는다. 각 모델·검색 어댑터에도 timeout을 설정해야 한다. 문자 예산을 넘으면 종료하며, 자동 요약·토큰 계산·문맥 압축은 이번 코드에 포함하지 않았다. 중복 질의를 다른 표현으로 자동 재작성하거나 의미가 비슷한 질의까지 중복으로 판정하지도 않는다.

### 10.6 검증 범위

24개 테스트로 표식 오인, 중간 답 교체, 정규화한 중복 검색, 근거 없음·충돌, 근거 보존, 무검색 답 정책, 생성 잘림, 혼합 출력, 검색·모델 호출 제한, 문자 예산, 재시도, 시간 예산, Ollama 종료 사유 전달을 확인했다. 최초에는 기존 코드에서 핵심 회귀 사례가 실패하는 것을 확인한 뒤 보완했다.

Ollama 어댑터 테스트는 HTTP 응답 대역을 사용한다. 실제 보유 모델 호출·실제 검색기 연결·답의 의미적 타당성 검증은 수행하지 않았다. 이번 수정으로 실행 오류에 대한 처리는 보강했지만 검색 정확도나 논문 성능을 재현했다고 주장하지 않는다.


## 11. LangGraph 실행 구조로 변환

기존 반복문 실행을 `initialize → decide → retrieve / finalize`의 LangGraph 노드와 조건 분기로 변환했다. `retrieve`에서 중간 답을 상태에 저장하고 `decide`로 돌아간다. 기존 모델·검색 콜백과 10절의 보완 정책을 유지한다.

실행 코드는 [code/self_ask_langgraph.py](code/self_ask_langgraph.py), 자세한 설명과 그래프·실행 예제는 [03_self_ask_langgraph.md](03_self_ask_langgraph.md)에 있다. `code/self_ask.py`는 공통 자료형·파서와 기존 호출 형식의 진입점이다. `run_self_ask()`도 내부적으로 그래프를 실행한다.

LangGraph 1.2.11에서 기존 회귀 테스트 24개와 그래프 테스트 4개, 총 28개가 통과했다. 현재 실행본에는 LangGraph 의존성이 필요하며, 10절의 24개 테스트는 변환 전 검증 기록이다. 원 논문 설명용인 4절 최소 코드는 보존했다. 실제 모델·검색 성능은 이번에도 검증하지 않았다.
