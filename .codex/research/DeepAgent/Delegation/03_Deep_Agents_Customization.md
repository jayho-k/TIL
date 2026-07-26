# Deep Agents Customization: 하네스 구성과 확장

> 원문: [Customize Deep Agents](https://docs.langchain.com/oss/python/deepagents/customization)  
> 문서 인덱스: [llms.txt](https://docs.langchain.com/llms.txt)  
> 작성일: 2026-07-26  
> 출처 신뢰도: LangChain 공식 문서 및 API Reference (1차 자료)

## 원문 충실 번역

목표에 맞게 하네스(harness)를 구성한다. `create_deep_agent`는 프로덕션 수준의 기반을 제공한다. 데이터에 연결하고, 동작을 형성하며, 사용 사례에 필요한 기능을 더한다.

```python
from deepagents import create_deep_agent

agent = create_deep_agent(
    model="openai:gpt-5.5",
    system_prompt="You are a helpful assistant.",
    tools=[search, fetch_url],
    memory=["./AGENTS.md"],
    skills=["./skills/"],
)
```

### `create_deep_agent` 구성 인자

| 인자 | 하는 일 |
| --- | --- |
| `model=` | 사용할 모델을 고른다. |
| `system_prompt=` | 에이전트의 사용자 지정 지시문이다. |
| `tools=` | 도메인 도구를 제공한다. |
| `memory=` | 시작 시 읽을 `AGENTS.md` 파일 목록이다. |
| `skills=` | 필요할 때 로드할 지식·작업 지침 디렉터리다. |
| `backend=` | 파일시스템 백엔드이며 기본값은 `StateBackend`다. |
| `permissions=` | 파일시스템 경로 단위 접근 제어다. |
| `subagents=` | 위임 작업을 위한 사용자 지정 서브에이전트다. |
| `middleware=` | 기본 스택에 병합할 추가 미들웨어다. 같은 `.name`이면 기본 인스턴스를 제자리에서 교체한다. |
| `interrupt_on=` | 도구 호출 전에 사람 승인을 위해 멈춘다. |
| `response_format=` | 구조화된 응답 스키마다. |
| `state_schema=` | 사용자 지정 그래프 상태 스키마다. |
| `context_schema=` | 사용자 ID, API 키, 기능 플래그처럼 실행마다 달라지는 런타임 컨텍스트 스키마다. |
| profiles | 모델별 기본값을 재사용 가능한 묶음으로 구성한다. |

### 전체 함수 시그니처

```python
create_deep_agent(
    model: str | BaseChatModel | None = None,
    tools: Sequence[BaseTool | Callable | dict[str, Any]] | None = None,
    *,
    system_prompt: str | SystemMessage | None = None,
    middleware: Sequence[AgentMiddleware] = (),
    subagents: Sequence[SubAgent | CompiledSubAgent | AsyncSubAgent] | None = None,
    skills: list[str] | None = None,
    memory: list[str] | None = None,
    permissions: list[FilesystemPermission] | None = None,
    backend: BackendProtocol | BackendFactory | None = None,
    interrupt_on: dict[str, bool | InterruptOnConfig] | None = None,
    response_format: ResponseFormat[ResponseT] | type[ResponseT] | dict[str, Any] | None = None,
    state_schema: type[DeepAgentState] | None = None,
    context_schema: type[ContextT] | None = None,
    checkpointer: Checkpointer | None = None,
    store: BaseStore | None = None,
    debug: bool = False,
    name: str | None = None,
    cache: BaseCache | None = None,
) -> CompiledStateGraph[AgentState[ResponseT], ContextT, InputAgentState, OutputAgentState[ResponseT]]
```

전체 인자 목록은 [API Reference](https://reference.langchain.com/python/deepagents/graph/create_deep_agent)를 보라. 하네스를 처음부터 완전히 조립하려면 LangChain의 `create_agent` 하네스 구성 문서 또는 Deep Agent from scratch 가이드를 따른다.

도구, 서브에이전트, 백엔드를 추가할수록 LangSmith 추적으로 이들이 함께 어떻게 동작하는지 관찰한다. 배포 관련 내용은 Going to production 문서를 참고한다.

## Model

`provider:model` 형식의 문자열 또는 초기화된 모델 인스턴스를 전달한다. 예를 들어 `openai:gpt-5.5` 형식을 쓰면 모델 전환이 빠르다. 지원 모델 전체와 검증된 추천 모델은 [Models](https://docs.langchain.com/oss/python/deepagents/models) 문서를 참고한다.

채팅 모델은 일시적 API 실패에 대해 지수 백오프로 자동 재시도한다. `max_retries`, `timeout` 조정은 LangChain Models의 connection resilience 문서를 참고한다.

### 제공자별 설치·초기화

| 제공자 | 설치 | 기본 모델 문자열 | 대표 모델 클래스 |
| --- | --- | --- | --- |
| OpenAI | `pip install -U "langchain[openai]"` | `openai:gpt-5.5` | `ChatOpenAI` |
| Anthropic | `pip install -U "langchain[anthropic]"` | `anthropic:claude-sonnet-4-6` | `ChatAnthropic` |
| Azure OpenAI | `pip install -U "langchain[openai]"` | `azure_openai:gpt-5.5` | `AzureChatOpenAI` |
| Google Gemini | `pip install -U "langchain[google-genai]"` | `google_genai:gemini-3.5-flash` | `ChatGoogleGenerativeAI` |
| AWS Bedrock | `pip install -U "langchain[aws]"` | `anthropic.claude-sonnet-4-6` + `bedrock_converse` | `ChatBedrock` |
| Hugging Face | `pip install -U "langchain[huggingface]"` | 모델 ID + `huggingface` | `ChatHuggingFace` |

#### OpenAI

```python
import os
from deepagents import create_deep_agent

os.environ["OPENAI_API_KEY"] = "sk-..."
agent = create_deep_agent(model="openai:gpt-5.5")
# 지정한 모델에 대해 기본 파라미터로 init_chat_model을 호출한다.
```

```python
import os
from langchain.chat_models import init_chat_model
from deepagents import create_deep_agent

os.environ["OPENAI_API_KEY"] = "sk-..."
model = init_chat_model(model="openai:gpt-5.5")
agent = create_deep_agent(model=model)
```

```python
import os
from langchain_openai import ChatOpenAI
from deepagents import create_deep_agent

os.environ["OPENAI_API_KEY"] = "sk-..."
model = ChatOpenAI(model="gpt-5.5")
agent = create_deep_agent(model=model)
```

#### Anthropic

```python
import os
from langchain.chat_models import init_chat_model
from langchain_anthropic import ChatAnthropic
from deepagents import create_deep_agent

os.environ["ANTHROPIC_API_KEY"] = "sk-..."
agent = create_deep_agent(model="anthropic:claude-sonnet-4-6")
model = init_chat_model(model="claude-sonnet-4-6")
agent_with_initialized_model = create_deep_agent(model=model)
agent_with_model_class = create_deep_agent(model=ChatAnthropic(model="claude-sonnet-4-6"))
```

#### Azure OpenAI

```python
import os
from langchain.chat_models import init_chat_model
from langchain_openai import AzureChatOpenAI
from deepagents import create_deep_agent

os.environ["AZURE_OPENAI_API_KEY"] = "..."
os.environ["AZURE_OPENAI_ENDPOINT"] = "..."
os.environ["OPENAI_API_VERSION"] = "2025-03-01-preview"

agent = create_deep_agent(model="azure_openai:gpt-5.5")
model = init_chat_model(
    model="azure_openai:gpt-5.5",
    azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
)
agent_with_initialized_model = create_deep_agent(model=model)
agent_with_model_class = create_deep_agent(
    model=AzureChatOpenAI(
        model="gpt-5.5",
        azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
    )
)
```

#### Google Gemini

```python
import os
from langchain.chat_models import init_chat_model
from langchain_google_genai import ChatGoogleGenerativeAI
from deepagents import create_deep_agent

os.environ["GOOGLE_API_KEY"] = "..."
agent = create_deep_agent(model="google_genai:gemini-3.5-flash")
agent_with_initialized_model = create_deep_agent(
    model=init_chat_model(model="google_genai:gemini-3.5-flash")
)
agent_with_model_class = create_deep_agent(
    model=ChatGoogleGenerativeAI(model="gemini-3.5-flash")
)
```

#### AWS Bedrock

```python
from langchain.chat_models import init_chat_model
from langchain_aws import ChatBedrock
from deepagents import create_deep_agent

# 자격 증명 설정은 AWS Bedrock getting started 문서를 따른다.
agent = create_deep_agent(
    model="anthropic.claude-sonnet-4-6",
    model_provider="bedrock_converse",
)
agent_with_initialized_model = create_deep_agent(
    model=init_chat_model(
        model="anthropic.claude-sonnet-4-6",
        model_provider="bedrock_converse",
    )
)
agent_with_model_class = create_deep_agent(
    model=ChatBedrock(model="anthropic.claude-sonnet-4-6")
)
```

#### Hugging Face 및 기타 제공자

```python
import os
from langchain.chat_models import init_chat_model
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from deepagents import create_deep_agent

os.environ["HUGGINGFACEHUB_API_TOKEN"] = "hf_..."
agent = create_deep_agent(
    model="microsoft/Phi-3-mini-4k-instruct",
    model_provider="huggingface",
    temperature=0.7,
    max_tokens=1024,
)
model = init_chat_model(
    model="microsoft/Phi-3-mini-4k-instruct",
    model_provider="huggingface",
    temperature=0.7,
    max_tokens=1024,
)
llm = HuggingFaceEndpoint(
    repo_id="microsoft/Phi-3-mini-4k-instruct",
    temperature=0.7,
    max_length=1024,
)
agent_with_model_class = create_deep_agent(model=ChatHuggingFace(llm=llm))

# 일반 형식
other_agent = create_deep_agent(model="provider:model-name")
```

## Tools

기본 제공되는 계획, 파일 관리, 서브에이전트 생성 도구 외에 사용자 도구를 제공할 수 있다.

```python
import os
from typing import Literal

from tavily import TavilyClient
from deepagents import create_deep_agent

tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])


def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
):
    """웹 검색을 실행한다."""
    return tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )


agent = create_deep_agent(
    model="openai:gpt-5.5",
    tools=[internet_search],
)
```

원문은 이 도구 예제를 Google, OpenAI, Anthropic, OpenRouter, Fireworks, Baseten, Ollama의 일곱 모델 문자열로 각각 제시한다. 함수 본문은 동일하고 `create_deep_agent(model=...)`의 모델만 바뀐다.

### MCP tools

Deep Agents는 [MCP(Model Context Protocol)](https://docs.langchain.com/oss/python/langchain/mcp) 도구를 지원한다. 데이터베이스·API·파일시스템 등의 MCP 서버에서 도구를 불러와 `create_deep_agent`에 직접 넘길 수 있다. 연결을 위해 `langchain-mcp-adapters`를 설치한다.

```bash
pip install langchain-mcp-adapters
```

```python
import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient
from deepagents import create_deep_agent


async def main():
    async with MultiServerMCPClient(
        {
            "my_server": {
                "transport": "http",
                "url": "http://localhost:8000/mcp",
            }
        }
    ) as client:
        tools = await client.get_tools()
        agent = create_deep_agent(model="openai:gpt-5.5", tools=tools)
        await agent.ainvoke(
            {"messages": [{"role": "user", "content": "Use the MCP server to help me."}]},
            config={"configurable": {"thread_id": "1"}},
        )


asyncio.run(main())
```

stdio 서버, OAuth 인증, 도구 필터링, 상태를 가진 세션은 MCP 전체 가이드를 참고한다.

### 문서 질의 에이전트: MCP로 도구를 발견해 연결

여기서 핵심은 “문서 검색 함수를 애플리케이션 코드에 직접 작성해 `tools=[search_docs]`로 넘긴다”는 방식과 다르다는 점이다. MCP에서는 **문서 제공자가 검색 도구와 그 계약(contract)을 MCP server에 공개**하고, agent 쪽은 server에 접속해 도구 목록을 받아 쓴다.

```text
문서 제공자
  └─ MCP 서버: 도구 이름 + 설명 + 입력 JSON Schema + 실행 구현을 공개
       ├─ docs-langchain      : 개념 가이드·how-to·튜토리얼
       └─ reference-langchain : 클래스·메서드·파라미터의 정식 API reference

애플리케이션 / Deep Agent
  └─ MCP client가 서버에 연결 → tool 목록 발견 → LangChain Tool로 변환
       └─ create_deep_agent(tools=발견한_도구들)
            └─ 모델이 적절한 도구를 선택하고 서버에 실제 호출을 보냄
```

MCP 도구 계약에는 적어도 **도구 이름**, **모델이 읽을 설명**, **입력 인자와 타입을 표현하는 JSON Schema**, **실행 결과**가 들어 있다. 따라서 agent를 만드는 사람이 `search_concept_docs(query: str)`와 `lookup_api(symbol: str)` 같은 wrapper 함수와 스키마를 매 서비스마다 다시 설계할 필요가 없다. 서버가 계약을 바꾸거나 새로운 도구를 제공하면 client는 다음 연결·발견 시점에 그 목록을 받아 쓸 수 있다.

LangChain의 MCP adapter는 MCP 도구를 LangChain Tool로 변환한다. `client.get_tools()`가 바로 이 발견·변환 단계다. 이때 tool 실행 실패는 기본적으로 예외로 중단시키기보다 `status="error"`인 tool message로 모델에 돌려주므로, 모델이 오류를 읽고 인자 수정이나 다른 도구 선택을 시도할 수 있다. 단, transport·session·content conversion 실패는 예외로 발생한다.

#### Deep Agents Code 설정: 두 문서 서버를 분리해 등록

공식 Deep Agents Code 빠른 시작은 `docs-langchain`을 개념·실습용, `reference-langchain`을 API 명세 확인용으로 권장한다. user 범위에서는 `~/.deepagents/.mcp.json`, 프로젝트 범위에서는 `<project>/.mcp.json` 또는 숨김 경로 `<project>/.deepagents/.mcp.json`에 등록한다. 전자는 모든 프로젝트에 적용되고, 후자는 해당 프로젝트에만 적용된다.

```json
{
  "mcpServers": {
    "docs-langchain": {
      "type": "http",
      "url": "https://docs.langchain.com/mcp"
    },
    "reference-langchain": {
      "type": "http",
      "url": "https://reference.langchain.com/mcp"
    }
  }
}
```

`dcode`를 시작하면 설정 파일을 자동 발견하고, 각 MCP server에 연결해 도구를 발견한 뒤 로드된 도구 수를 출력한다. 대화 중 `/mcp`를 실행하면 서버별 연결 상태, transport, 로드한 tool 목록을 확인할 수 있다. 즉 **agent가 문서 전체를 시작할 때 프롬프트에 넣는 것이 아니라**, 필요할 때 검색/조회 도구를 호출해 결과만 컨텍스트로 가져오는 구조다.

#### Python SDK에서 같은 구조 만들기

Deep Agents Code의 자동 설정 발견 대신, Python 애플리케이션에서는 `MultiServerMCPClient`에 두 endpoint를 선언하고 `get_tools()`의 반환값을 `create_deep_agent`에 전달한다.

```python
import asyncio

from deepagents import create_deep_agent
from langchain_mcp_adapters.client import MultiServerMCPClient


async def main():
    async with MultiServerMCPClient(
        {
            "docs-langchain": {
                "transport": "http",
                "url": "https://docs.langchain.com/mcp",
            },
            "reference-langchain": {
                "transport": "http",
                "url": "https://reference.langchain.com/mcp",
            },
        }
    ) as client:
        # 각 서버가 공개한 도구의 이름·설명·입력 스키마를 가져와 LangChain Tool로 만든다.
        tools = await client.get_tools()

        agent = create_deep_agent(
            model="openai:gpt-5.5",
            tools=tools,
            system_prompt=(
                "Use docs-langchain for conceptual explanations and tutorials. "
                "Use reference-langchain when confirming an API signature, class, "
                "method, parameter, or return value. Cite the source URL in answers."
            ),
        )

        result = await agent.ainvoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": "Explain StateBackend, then confirm the create_deep_agent backend parameter type.",
                    }
                ]
            },
            config={"configurable": {"thread_id": "docs-research-1"}},
        )
        print(result["messages"][-1].content)


asyncio.run(main())
```

위 prompt는 선택 규칙을 보강한 것이다. 모델이 스스로 tool description을 보고 선택할 수도 있지만, “개념 설명은 `docs-langchain`, 정확한 시그니처 검증은 `reference-langchain`”처럼 역할을 명시하면 잘못된 서버 선택을 줄일 수 있다.

#### 직접 wrapper를 쓸 때와 MCP를 쓸 때

| 관점 | 앱 내부 wrapper 함수 | MCP 문서 서버 |
| --- | --- | --- |
| 도구 계약 소유자 | 각 애플리케이션 개발자 | 문서/서비스 제공자 |
| 스키마 갱신 | 앱 코드를 수정·배포해야 한다 | 서버가 공개 계약을 갱신하고 client가 다시 발견한다 |
| 재사용성 | 같은 wrapper를 각 프로젝트에 복제하기 쉽다 | 같은 MCP 설정을 여러 agent/client가 공유한다 |
| 맞는 경우 | 사내 DB처럼 매우 도메인 특화된 간단한 호출 | 외부 문서, SaaS, 공통 API처럼 표준화·공유할 도구 |
| 보안·운영 | 앱 내부 권한 검사로 충분할 수 있다 | server URL, OAuth/header, 허용 tool, 프로젝트 신뢰 정책도 관리해야 한다 |

MCP가 자동으로 안전성을 보장하는 것은 아니다. 특히 프로젝트의 stdio MCP 설정은 실행 가능한 명령을 포함할 수 있으므로, Deep Agents Code의 신뢰/승인 정책을 확인하고 검증되지 않은 프로젝트 설정을 무심코 승인하지 않는다. HTTP MCP도 endpoint, 인증 header/OAuth, 노출할 tool을 최소 권한 원칙으로 구성한다.

## System prompt

`system_prompt`는 모델에 전달되는 **시스템 지시문 전체를 조립하는 입력**이다. Deep Agents에는 이미 “todo를 어떻게 쓰는지, 파일 도구와 서브에이전트를 어떻게 쓰는지”를 설명하는 내장 기본 프롬프트가 있다. 사용자가 아무것도 넣지 않아도 agent가 하네스 기능을 활용할 수 있는 이유다.

가장 먼저 이 한 가지를 기억하면 된다.

```text
문자열 system_prompt를 전달한다
    ↓
내 업무 규칙 + Deep Agents의 기본 사용법 + (파일시스템 등 미들웨어 안내)
    ↓
모델이 읽는 최종 시스템 프롬프트
```

예를 들어 문자열을 넘기는 가장 흔한 경우는 “Deep Agents의 기본 사용법은 유지하고, 내 제품의 역할만 앞에 추가”하는 것이다.

```python
from deepagents import create_deep_agent

agent = create_deep_agent(
    model="openai:gpt-5.5",
    system_prompt="""
    You are an expert researcher.
    Answer in Korean, cite sources, and keep the final report under 500 words.
    """,
)
```

개념적으로 모델은 다음 순서의 내용을 받는다.

```text
[내 규칙]
  You are an expert researcher. Answer in Korean ...

[Deep Agents 기본 규칙]
  계획, 파일시스템, task/subagent 등 하네스 사용 방법

[활성화된 미들웨어의 안내]
  예: 파일 도구의 사용 가능한 경로·명령, HITL 도구 승인 안내
```

따라서 보통의 제품 개발에서는 **문자열 `system_prompt`만 추가하면 충분**하다. 파일시스템처럼 특수 도구를 미들웨어가 추가하면, 해당 미들웨어도 런타임에 필요한 사용법을 덧붙인다.

### 언제 `prefix`, `base`, `suffix`를 쓰는가

`SystemPromptConfig`(`deepagents>=0.7.0a6`)는 기본 프롬프트를 포함한 조립 위치를 직접 제어할 때 쓴다. 단순한 업무 역할 추가에는 필요하지 않다.

| 키 | 쉬운 해석 | 일반적인 사용처 |
| --- | --- | --- |
| `prefix` | 기본 Deep Agents 안내 **앞에** 내 규칙을 넣는다. | 문자열 `system_prompt`와 같다. 가장 안전한 기본 선택이다. |
| `base` | Deep Agents의 기본 안내 자체를 지정한 문자열로 **바꾼다**. | 자체 하네스를 이미 완전히 이해하고 동일한 운영 규칙을 직접 제공할 때만 쓴다. |
| `suffix` | 기본 Deep Agents 안내 **뒤에** 내 규칙을 넣는다. | 하네스 규칙을 읽은 뒤 반드시 강조할 짧은 마무리 제약을 추가할 때 쓴다. |

`prefix → base → suffix → model profile suffix` 순으로 조립된다. 각 값은 문자열이거나, Anthropic prompt caching의 `cache_control` 같은 표시를 보존해야 할 때 쓰는 `SystemMessage`일 수 있다.

#### A. 권장: 기본 프롬프트를 유지하고 업무 규칙만 추가

```python
agent = create_deep_agent(
    model="openai:gpt-5.5",
    system_prompt={
        "prefix": "You are ACME's support researcher. Answer in Korean.",
        "suffix": "Never claim an API signature without checking an official source.",
    },
)
```

이 경우의 의미는 다음과 같다.

```text
ACME support researcher 규칙
    ↓
Deep Agents 기본 규칙은 그대로 유지
    ↓
공식 출처 확인 규칙을 마지막에 한 번 더 강조
```

#### B. 주의: `base`를 주면 내장 사용법을 교체한다

```python
# 내 문자열이 Deep Agents 기본 프롬프트를 완전히 대체한다.
agent = create_deep_agent(
    model="openai:gpt-5.5",
    system_prompt={"base": "You are an internal agent. Follow ACME runbook."},
)
```

이것은 “내 문장을 추가한다”가 아니라, 기본 하네스 사용 안내를 **없애고 바꾼다**는 뜻이다. 그러면 모델이 계획, 파일시스템, 서브에이전트 같은 Deep Agents 기능을 어떻게 사용해야 하는지에 대한 기본 지침을 잃을 수 있다. 그래서 `base` 교체는 자체 프롬프트에 그 운영 규칙을 충분히 다시 작성할 수 있을 때만 선택한다.

```python
# 내장 기본 프롬프트를 아예 제거한다.
# middleware가 넣는 개별 안내는 남을 수 있지만, 일반적으로 시작점으로 권장하지 않는다.
agent = create_deep_agent(
    model="openai:gpt-5.5",
    system_prompt={"base": None},
)
```

프롬프트는 행동을 안내할 뿐 보안 경계는 아니다. 파일 접근 제한은 `permissions`, 민감한 실행 전 중단은 `interrupt_on`, host 보호는 sandbox/backend로 별도 강제해야 한다.

### Profile은 “호출 코드”가 아니라 “선택한 모델”에 붙는 공통 덧붙임

Harness profile은 예를 들어 OpenAI 모델에서는 짧은 답변 규칙을, Anthropic 모델에서는 다른 도구 안내를 붙이고 싶을 때 쓴다. 따라서 위에서 `model="openai:gpt-5.5"`를 골랐고 그 모델 profile에 suffix가 있다면, 그 suffix가 `prefix/base/suffix` 뒤에 더해진다.

```python
from deepagents import HarnessProfile, register_harness_profile

register_harness_profile(
    "openai:gpt-5.5",
    HarnessProfile(system_prompt_suffix="Keep answers under 100 words."),
)

agent = create_deep_agent(
    model="openai:gpt-5.5",
    system_prompt="You are a Korean documentation assistant.",
)

# 최종 개념: 내 역할 → Deep Agents 기본 안내 → profile의 100단어 규칙 → middleware 안내
```

### 서브에이전트는 세 종류를 구분한다

여기서 가장 헷갈리기 쉬운 부분은 “서브에이전트도 부모 프롬프트를 그대로 쓰는가?”다. 답은 종류에 따라 다르다.

| 종류 | 프롬프트 출발점 | profile이 하는 일 |
| --- | --- | --- |
| Main agent | `create_deep_agent(system_prompt=...)` | main agent의 base/suffix를 적용한다. |
| 선언형 custom subagent | `subagents=[{"system_prompt": "..."}]`에서 직접 쓴 prompt | 보통 profile suffix를 뒤에 붙인다. profile에 `base_system_prompt`가 있으면 작성한 prompt를 교체할 수 있다. |
| 자동 general-purpose subagent | SDK가 자동 제공하는 일반 목적 prompt | 아래 우선순위로 시작 prompt를 고른 뒤 profile suffix를 붙인다. |

#### 선언형 custom subagent: 본인이 작성한 prompt가 출발점

```python
researcher = {
    "name": "researcher",
    "description": "공식 문서를 조사한다.",
    "system_prompt": "You are a research subagent. Return sources and a 5-bullet summary.",
}
```

이 `researcher`는 부모의 업무 prompt를 자동 상속하는 것이 아니다. 위의 `system_prompt`가 출발점이다. 다만 researcher가 선택한 모델에 profile suffix가 있으면 그 뒤에 붙는다. profile이 `base_system_prompt`까지 제공하는 특별한 경우에는 authored prompt를 그 base가 대체할 수 있으므로, profile을 전역 등록할 때 이 영향을 확인해야 한다.

#### 자동 general-purpose subagent: “가장 구체적인 설정이 이긴다”

아무 custom subagent를 지정하지 않아도 Deep Agents는 일반 작업을 위임할 `general-purpose` subagent를 자동으로 제공할 수 있다. 이 에이전트의 **출발 프롬프트**는 아래에서 위로 찾는 것이 아니라, 위에서부터 처음 있는 값을 선택한다.

```text
1. general_purpose_subagent.system_prompt가 있으면 그것을 사용
2. 없고 HarnessProfile.base_system_prompt가 있으면 그것을 사용
3. 둘 다 없으면 SDK의 general-purpose 기본 prompt를 사용
4. 선택된 prompt 뒤에 profile system_prompt_suffix를 추가
```

즉 문서의 화살표는 “세 문장을 모두 붙인다”가 아니라 **우선순위 fallback chain**이다.

```python
from deepagents import (
    GeneralPurposeSubagentProfile,
    HarnessProfile,
    register_harness_profile,
)

register_harness_profile(
    "anthropic",
    HarnessProfile(
        base_system_prompt="You are ACME's support orchestrator.",
        general_purpose_subagent=GeneralPurposeSubagentProfile(
            system_prompt="You are a research subagent. Cite sources.",
        ),
        system_prompt_suffix="Always think step by step.",
    ),
)
```

위 설정에서는 main agent가 `"You are ACME's support orchestrator."`를 출발점으로 쓰고, 자동 general-purpose subagent는 더 구체적인 `"You are a research subagent. Cite sources."`를 출발점으로 쓴다. 두 agent 모두 마지막에 `"Always think step by step."` suffix를 받는다.

## Middleware

먼저 한 문장으로 구분하면 다음과 같다.

```text
Tool       = 모델이 “이 일을 하겠다”고 선택해서 호출하는 업무 기능
Middleware = agent 실행 과정의 앞·뒤·주변에서 공통 규칙을 적용하는 운영 레이어
```

`get_weather`, `search_docs`, `send_email`처럼 어떤 일을 실제로 수행하는 함수가 **tool**이다. 반면 “모든 tool 호출을 감사 로그에 남겨라”, “외부 발송 전에 승인을 받아라”, “대화가 너무 길면 요약하라”, “파일 경로 권한을 확인하라”는 특정 업무 도구 하나의 책임이 아니라 agent 전체에 걸친 **middleware** 책임이다.

| 구분 | Tool | Middleware |
| --- | --- | --- |
| 누가 호출을 결정하는가? | 모델이 현재 문제에 필요하다고 판단할 때 | framework가 agent lifecycle에서 등록한 hook/조건에 따라 실행한다. |
| 모델에게 보이는가? | 예. 이름·설명·입력 schema를 보고 호출한다. | 보통 아니다. agent의 내부 실행 정책이다. |
| 주 책임 | 날씨 조회, DB 검색, 이메일 발송처럼 실제 도메인 작업 | 인증, 로깅, retry, 권한 검사, 요약, HITL, tool wrapping 같은 횡단 관심사 |
| 호출 빈도 | 모델이 선택한 경우에만 | hook 종류에 따라 agent 시작/모델 호출/tool 호출/종료 시 적용된다. |
| 예 | `search_docs(query)` | `HumanInTheLoopMiddleware`, `SummarizationMiddleware`, `FilesystemMiddleware` |

### 왜 middleware가 필요한가

다음처럼 tool 함수 안에 공통 정책을 직접 복사할 수도 있다.

```python
def send_email(to: str, body: str) -> str:
    audit_log("send_email", to=to)
    if not is_approved_by_human():
        return "not approved"
    if contains_pii(body):
        return "blocked"
    return provider.send(to, body)
```

하지만 `delete_file`, `write_file`, `export_data`, `deploy`처럼 도구가 늘어나면 감사·승인·PII 검사·retry를 모든 함수에 중복하게 된다. 정책 변경도 모든 tool을 고쳐야 한다. Middleware는 이 공통 작업을 tool 바깥 한곳에 두고, 여러 tool과 여러 agent run에 일관되게 적용한다.

Deep Agents에서 middleware는 선택적인 “부가 기능”만은 아니다. `create_deep_agent()`가 todo, filesystem, subagent, summarization 같은 기능을 제공하는 방식 자체가 middleware stack이기 때문이다. 다만 **사용자가 custom middleware를 꼭 작성해야 한다는 뜻은 아니다.** 기본 stack만으로 시작하고, 공통 정책이 생길 때 추가하면 된다.

### 언제 실행되는가: 한 번의 agent run을 따라가기

사용자가 “서울 날씨를 찾아서 알려줘”라고 말하고 모델이 `get_weather` tool을 선택한 상황을 보자.

```text
1. agent.invoke(...)
   └─ before_agent 계열 hook
      예: 초기 state 준비, todo 초기화

2. 모델을 부르기 직전/직후
   └─ before_model / after_model 계열 hook
      예: 너무 긴 message history 요약, model 입력 수정, 응답 검사

3. 모델이 "get_weather" tool call을 생성
   └─ wrap_tool_call 계열 middleware가 tool 실행을 감싼다
      예: 권한 검사 → HITL 승인 → 감사 로그 → 실제 get_weather 실행 → 결과 로그

4. tool 결과를 모델에 다시 전달
   └─ 모델이 추가 tool call 또는 최종 답변을 결정
      (2~4는 tool call이 더 없을 때까지 반복될 수 있다.)

5. 최종 답변을 반환하기 전/후
   └─ after_agent 계열 hook
      예: 종료 처리, 최종 state 정리
```

모든 middleware가 위의 모든 지점에서 실행되는 것은 아니다. 구현한 hook에 따라 다르다.

* `before_agent`를 구현한 middleware는 agent run 시작에 관여한다.
* `before_model`/`after_model`을 구현한 middleware는 model 호출 전후에 관여한다.
* `wrap_tool_call`을 구현한 middleware는 **모델이 tool을 실제 선택한 경우에만** tool 호출을 감싼다.
* `after_agent`를 구현한 middleware는 run 종료 지점에 관여한다.

예를 들어 사용자의 질문에 모델이 tool 없이 바로 답한다면 `get_weather`는 실행되지 않고, 이를 감싸는 `wrap_tool_call` 로거도 실행되지 않는다. 하지만 대화 요약처럼 model 호출 전 상태를 검사하는 middleware는 여전히 조건에 따라 작동할 수 있다.

### 원하는 hook에만 설정하는 방법

핵심은 간단하다. **원하는 hook에 해당하는 decorator를 붙인 함수만 만들거나, `AgentMiddleware` 클래스에서 그 메서드만 override한다.** 구현하지 않은 hook은 실행할 코드가 없으므로 개입하지 않는다.

#### 방법 1. decorator: hook 하나만 빠르게 추가

“모델을 부르기 직전에만 대화 길이를 검사하고 싶다”면 `@before_model`만 사용한다. 아래 middleware는 tool 호출을 감싸지도 않고, agent 종료 처리도 하지 않는다.

```python
from typing import Any

from deepagents import create_deep_agent
from langchain.agents.middleware import AgentState, before_model
from langgraph.runtime import Runtime


@before_model
def log_context_size(
    state: AgentState,
    runtime: Runtime,
) -> dict[str, Any] | None:
    """매 model call 직전에만 실행된다."""
    print(f"About to call model with {len(state['messages'])} messages")
    return None  # state를 바꾸지 않는다.


agent = create_deep_agent(
    model="openai:gpt-5.5",
    middleware=[log_context_size],
)
```

반대로 “모델이 실제로 도구를 선택했을 때만 로그를 남기고 싶다”면 `@wrap_tool_call`만 쓴다. 모델이 tool 없이 답하면 이 함수는 호출되지 않는다.

```python
from deepagents import create_deep_agent
from langchain.agents.middleware import wrap_tool_call
from langchain.tools import tool


@tool
def search_docs(query: str) -> str:
    """문서를 검색한다."""
    return f"results for {query}"


@wrap_tool_call
def audit_tool_call(request, handler):
    """각 tool call 전후에만 실행된다."""
    name = request.tool_call["name"]
    print(f"START {name}: {request.tool_call['args']}")
    result = handler(request)  # 실제 search_docs() 실행 지점
    print(f"END {name}")
    return result


agent = create_deep_agent(
    model="openai:gpt-5.5",
    tools=[search_docs],
    middleware=[audit_tool_call],
)
```

| 필요한 시점 | 사용할 decorator | 대표 용도 |
| --- | --- | --- |
| run 전체의 맨 처음 | `@before_agent` | 입력 검증, memory/state 준비 |
| 매 model call 직전 | `@before_model` | context 주입·trim, token/cost 제한 |
| 매 model call을 감싸기 | `@wrap_model_call` | retry, fallback, 동적 모델·도구 선택 |
| 매 model response 직후 | `@after_model` | guardrail, tool call 검사, response logging |
| 매 tool call을 감싸기 | `@wrap_tool_call` | 권한 검사, audit, retry, tool args/결과 변환 |
| run 전체의 맨 끝 | `@after_agent` | 결과 저장, cleanup, 종료 audit |

#### 방법 2. class: 여러 hook을 하나의 정책으로 묶기

예를 들어 “model 호출 수를 세고, tool 실행만 감사한다”처럼 관련 hook이 둘 이상이거나 생성자 설정값이 필요하면 클래스를 쓴다. 아래 클래스는 `before_agent`, `after_model`, `wrap_tool_call`만 구현한다. `before_model`, `after_agent`, `wrap_model_call`은 구현하지 않았으므로 이 middleware에는 해당 동작이 없다.

```python
from typing import Callable

from deepagents import create_deep_agent
from langchain.agents.middleware import (
    AgentMiddleware,
    AgentState,
    ToolCallRequest,
)
from langchain.messages import ToolMessage
from langgraph.runtime import Runtime


class AuditState(AgentState):
    # 실제 프로젝트에서는 NotRequired 등을 사용해 custom state를 선언한다.
    pass


class ModelAndToolAuditMiddleware(AgentMiddleware):
    def before_agent(self, state: AgentState, runtime: Runtime):
        print("Agent run started")
        return None

    def after_model(self, state: AgentState, runtime: Runtime):
        print("A model response was received")
        return None

    def wrap_tool_call(
        self,
        request: ToolCallRequest,
        handler: Callable,
    ) -> ToolMessage:
        print(f"Auditing tool: {request.tool_call['name']}")
        return handler(request)


agent = create_deep_agent(
    model="openai:gpt-5.5",
    tools=[search_docs],
    middleware=[ModelAndToolAuditMiddleware()],
)
```

#### hook에서 state를 바꾸거나 일찍 끝내기

node-style hook(`before_*`, `after_*`)은 `dict`를 반환해 state를 갱신할 수 있다. 예를 들어 `before_model`에서 대화 한도를 넘으면 `jump_to="end"`를 반환해 model 호출 없이 run을 끝내도록 만들 수 있다. 이처럼 agent 흐름을 jump하려면 해당 hook에 `@hook_config(can_jump_to=["end"])`를 선언해야 한다.

```python
from typing import Any

from langchain.agents.middleware import AgentState, before_model, hook_config
from langchain.messages import AIMessage
from langgraph.runtime import Runtime


@before_model
@hook_config(can_jump_to=["end"])
def stop_when_too_long(
    state: AgentState,
    runtime: Runtime,
) -> dict[str, Any] | None:
    if len(state["messages"]) >= 50:
        return {
            "messages": [AIMessage("Conversation limit reached.")],
            "jump_to": "end",
        }
    return None
```

wrap-style hook은 `handler(request)`를 호출할지 스스로 결정한다. 즉 handler를 0번 호출하면 tool/model call을 막거나 cache 결과로 대체할 수 있고, 1번 호출하면 일반 흐름이며, 여러 번 호출하면 retry를 구현할 수 있다.

```python
from typing import Callable

from langchain.agents.middleware import ModelRequest, ModelResponse, wrap_model_call


@wrap_model_call
def retry_model(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse],
) -> ModelResponse:
    for attempt in range(3):
        try:
            return handler(request)  # 일반적으로 한 번 호출
        except Exception:
            if attempt == 2:
                raise
```

#### 여러 middleware를 등록했을 때 실행 순서

```python
agent = create_deep_agent(
    model="openai:gpt-5.5",
    middleware=[first_policy, second_policy, third_policy],
)
```

일반 LangChain middleware 순서는 다음과 같이 이해하면 된다.

```text
before_* : first → second → third
wrap_*   : first( second( third( 실제 model/tool ) ) )
after_*  : third → second → first
```

Deep Agents에서는 이 사용자 middleware가 기본 stack의 `PatchToolCallsMiddleware` 뒤와 profile/prompt-caching/memory 앞에 병합된다. 단, 전달한 middleware의 `.name`이 기본 middleware와 같으면 추가되지 않고 해당 기본 인스턴스를 **교체**한다. 기본 동작을 바꾸고 싶을 때만 이름 일치 교체를 사용하고, 단순한 audit·retry·guardrail은 별도 이름의 middleware로 추가하는 편이 이해하기 쉽다.

#### 모든 lifecycle hook을 관찰하는 템플릿

agent 전체의 흐름을 trace하거나 운영 정책의 어느 지점이 실제로 실행되는지 학습할 때는 하나의 `AgentMiddleware` 클래스에 모든 hook을 구현할 수 있다. 다만 “모든 hook”은 가능한 lifecycle 지점을 모두 구현한다는 뜻이며, `wrap_tool_call`은 모델이 실제 tool call을 만들었을 때만 실행된다.

```python
from deepagents import create_deep_agent
from langchain.agents.middleware import (
    AgentMiddleware,
    AgentState,
    ModelRequest,
    ToolCallRequest,
)
from langchain.tools import tool
from langgraph.runtime import Runtime


@tool
def search_docs(query: str) -> str:
    """문서를 검색한다."""
    return f"results for {query}"


class FullLifecycleLogger(AgentMiddleware):
    """학습·관찰용: 가능한 모든 주요 middleware hook을 기록한다."""

    def before_agent(self, state: AgentState, runtime: Runtime):
        # invoke 한 번당 한 번
        print("[before_agent] agent run started")
        return None

    def before_model(self, state: AgentState, runtime: Runtime):
        # agent loop 안에서 model을 부를 때마다
        print("[before_model] about to call model")
        return None

    def wrap_model_call(self, request: ModelRequest, handler):
        # handler() 전후를 감싼다. retry/fallback/caching은 여기에 둘 수 있다.
        print("[wrap_model_call] before actual model call")
        result = handler(request)
        print("[wrap_model_call] after actual model call")
        return result

    def after_model(self, state: AgentState, runtime: Runtime):
        # model response를 받은 뒤마다
        print("[after_model] model response received")
        return None

    def wrap_tool_call(self, request: ToolCallRequest, handler):
        # 모델이 실제로 tool을 선택한 경우에만
        name = request.tool_call["name"]
        print(f"[wrap_tool_call] before tool: {name}")
        result = handler(request)
        print(f"[wrap_tool_call] after tool: {name}")
        return result

    def after_agent(self, state: AgentState, runtime: Runtime):
        # invoke 한 번이 최종 종료될 때 한 번
        print("[after_agent] agent run completed")
        return None


agent = create_deep_agent(
    model="openai:gpt-5.5",
    tools=[search_docs],
    middleware=[FullLifecycleLogger()],
)
```

사용자가 `"LangChain middleware를 찾아줘"`라고 요청했고 모델이 `search_docs`를 한 번 호출한 뒤 답했다고 가정하면, 로그의 개념적 순서는 다음과 같다.

```text
[before_agent] agent run started

[before_model] about to call model
[wrap_model_call] before actual model call
[wrap_model_call] after actual model call
[after_model] model response received

[wrap_tool_call] before tool: search_docs
[wrap_tool_call] after tool: search_docs

# tool 결과를 본 모델이 최종 답변을 만들기 위해 한 번 더 호출될 수 있다.
[before_model] about to call model
[wrap_model_call] before actual model call
[wrap_model_call] after actual model call
[after_model] model response received

[after_agent] agent run completed
```

반대로 모델이 도구 없이 즉시 최종 답변을 했다면 `wrap_tool_call` 두 줄은 없다. 모델이 `search_docs`와 `fetch_url`을 차례로 호출하면 `wrap_tool_call`은 각각 한 번씩 더 실행된다. 즉 lifecycle logger는 agent가 실제로 몇 번 모델을 호출하고 어떤 tool을 골랐는지 확인하는 데 유용하다.

### Tool 하나와 middleware 하나를 함께 놓고 보기

```python
from langchain.agents.middleware import wrap_tool_call
from langchain.tools import tool


@tool
def refund_order(order_id: str) -> str:
    """주문을 환불한다. 실제 비즈니스 작업을 수행하는 tool."""
    return f"Refunded {order_id}"


@wrap_tool_call
def audit_and_guard(request, handler):
    """어떤 tool이 호출되든 공통 정책을 적용하는 middleware."""
    print(f"AUDIT start: {request.name}, args={request.args}")

    if request.name == "refund_order" and request.args.get("order_id") is None:
        # 실제 tool을 실행하지 않고 표준화된 오류를 돌려줄 수도 있다.
        return "order_id is required"

    result = handler(request)  # 이 한 줄에서 실제 refund_order()가 실행된다.
    print(f"AUDIT end: {request.name}")
    return result
```

이 예시에서 `refund_order`는 “환불”이라는 업무를 안다. `audit_and_guard`는 환불의 비즈니스 로직을 구현하지 않고, 환불·삭제·발송 등 여러 tool에 재사용할 수 있는 공통 운영 규칙을 담당한다.

### Deep Agents의 기본 middleware를 이 관점으로 다시 읽기

| 기본 middleware | tool과 비교해 맡는 역할 |
| --- | --- |
| `TodoListMiddleware` | 특정 업무를 수행하지 않고, 여러 단계 작업의 계획 state를 관리한다. |
| `FilesystemMiddleware` | `read_file`·`write_file` 같은 file tool을 제공하고, backend·경로 권한을 일관되게 연결한다. |
| `SubAgentMiddleware` | `task` tool을 제공하고 위임 실행 규칙을 관리한다. |
| `SummarizationMiddleware` | 모델을 부르기 전에 긴 대화를 압축해 context overflow를 피한다. |
| `HumanInTheLoopMiddleware` | 민감 tool이 호출되는 순간 실행을 멈추고 승인 결정을 기다린다. |
| `PatchToolCallsMiddleware` | interrupt 뒤 재개하거나 잘못된 tool call이 남았을 때 message history를 복구한다. |

따라서 middleware가 “tool과 경쟁하는 기능”은 아니다. 미들웨어는 tool을 **제공**할 수도 있고(`FilesystemMiddleware`, `SubAgentMiddleware`), tool 호출을 **제어**할 수도 있으며(HITL, permissions, logging), model 호출 자체를 **보정**할 수도 있다(summarization, caching).

Deep Agents는 LangChain의 모든 미들웨어, 내장 미들웨어, 제공자 전용 미들웨어, 직접 작성한 미들웨어를 지원한다. `middleware=`에 전달한 인스턴스는 기본 스택의 `.name`과 비교된다. 이름이 같으면 그 기본 인스턴스를 제자리에서 교체하고, 다르면 `PatchToolCallsMiddleware` 다음에 넣는다.

### Main agent 기본 스택: 앞에서 뒤 순서

1. `TodoListMiddleware`: 작업 조직을 위한 todo 목록을 관리한다.
2. `SkillsMiddleware`: `skills`를 전달했을 때만 추가한다. todo 직후이자 filesystem 전에 주입되어 파일 도구 실행 전에 skill 메타데이터를 쓸 수 있다.
3. `FilesystemMiddleware`: 파일 읽기·쓰기·탐색을 처리한다. `permissions`가 있으면 이곳에서 모든 파일 도구의 권한을 검사한다.
4. `SubAgentMiddleware`: 특화된 서브에이전트를 생성·조정한다.
5. `SummarizationMiddleware`: 대화가 길어질 때 메시지 이력을 압축하여 컨텍스트 한도 안에 유지한다.
6. `PatchToolCallsMiddleware`: 인터럽트 뒤 재개하거나 잘못된 도구 인자가 들어왔을 때 매달린 도구 호출을 복구한다.
7. `AsyncSubAgentMiddleware`: 비동기 서브에이전트를 구성했을 때만 추가한다.
8. 사용자 `middleware=`: Patch 뒤, 이후 tail stack 전에 병합된다.
9. Harness profile extras: 모델 profile이 제공하는 추가 미들웨어다.
10. excluded-tool filtering: profile이 제외할 도구를 열거했다면 모델에 노출하기 전 걸러 낸다.
11. Prompt caching: Anthropic·Bedrock prompt caching 미들웨어는 항상 등록되지만 지원하지 않는 모델에서는 no-op다. Patch 및 사용자 미들웨어 뒤에서 실행된다.
12. `MemoryMiddleware`: `memory`를 넘긴 경우에만 추가한다. 캐시 prefix 무효화를 줄이기 위해 profile extras와 caching 뒤에 둔다.
13. `HumanInTheLoopMiddleware`: `interrupt_on`을 넘긴 경우에만 도구 호출에서 사람 승인/입력을 기다린다.

### 동기 서브에이전트 기본 스택

내장 general-purpose와 선언형 동기 `SubAgent`는 todo, filesystem, summarization, Patch, profile extras, Anthropic·Bedrock caching, 선택적 permissions라는 큰 형태는 부모와 같다. 다만 다음이 다르다.

* Skills가 있을 때 main agent와 달리 `PatchToolCallsMiddleware` **뒤**에서 실행된다.
* 서브에이전트 그래프 내부에는 `SubAgentMiddleware`가 없다. `task` 도구는 부모만 노출한다.
* 선언형 subagent가 `interrupt_on`을 지정하면 그 값은 해당 `create_agent`에 전달되어 그 도구에 HITL을 붙인다.

### 사용자 지정 미들웨어

```python
from langchain.agents.middleware import wrap_tool_call
from langchain.tools import tool
from deepagents import create_deep_agent


@tool
def get_weather(city: str) -> str:
    """도시의 날씨를 가져온다."""
    return f"The weather in {city} is sunny."


call_count = [0]  # 중첩 함수에서 수정할 수 있도록 list를 사용한다.


@wrap_tool_call
def log_tool_calls(request, handler):
    """모든 도구 호출을 가로채 로그한다."""
    call_count[0] += 1
    tool_name = request.name if hasattr(request, "name") else str(request)
    print(f"[Middleware] Tool call #{call_count[0]}: {tool_name}")
    print(f"[Middleware] Arguments: {request.args if hasattr(request, 'args') else 'N/A'}")
    result = handler(request)
    print(f"[Middleware] Tool call #{call_count[0]} completed")
    return result


agent = create_deep_agent(
    model="openai:gpt-5.5",
    tools=[get_weather],
    middleware=[log_tool_calls],
)
```

#### 초기화 후 속성을 변경하지 말 것

hook 호출 사이에 카운터나 누적 데이터를 추적할 때 미들웨어 인스턴스 속성을 바꾸지 말고 그래프 상태를 사용한다. 그래프 상태는 thread 범위라 동시성에서 안전하다. 서브에이전트, 병렬 도구, 서로 다른 thread의 병렬 호출은 같은 미들웨어 객체를 동시에 실행할 수 있다.

```python
from langchain.agents.middleware import AgentMiddleware


class CustomMiddleware(AgentMiddleware):
    def before_agent(self, state, runtime):
        return {"x": state.get("x", 0) + 1}  # 상태를 갱신한다.


class CustomMiddlewareBad(AgentMiddleware):
    def __init__(self):
        self.x = 1

    def before_agent(self, state, runtime):
        self.x += 1  # 공유 객체 변경은 race condition을 만든다.
```

### 기본 미들웨어 교체

기본 미들웨어의 `.name` 일치 교체는 `deepagents>=0.7.0a3`이 필요하다. 교체는 merge가 아니라 **완전 교체**다. 특히 `FilesystemMiddleware`를 교체하면 `backend`와 필요 시 `permissions`를 새 인스턴스에 직접 넣어야 한다.

```python
from deepagents import create_deep_agent
from deepagents.backends import StateBackend
from deepagents.middleware import SummarizationMiddleware

backend = StateBackend()
model = "openai:gpt-5.5"
custom_summarization = SummarizationMiddleware(
    model=model,
    backend=backend,
    summary_prompt="Your custom summary prompt here.",
)
agent = create_deep_agent(model=model, middleware=[custom_summarization])
```

일반 목적 서브에이전트는 main agent에서 기본 미들웨어를 교체한 사실을 상속하지만, main agent 전용 미들웨어는 갖지 않는다. `subagents=`로 정의한 선언형 서브에이전트는 부모의 미들웨어 커스터마이즈를 상속하지 않으므로 자신의 `middleware` 필드에 직접 전달한다.

```python
from deepagents import create_deep_agent
from deepagents.backends import StateBackend
from deepagents.middleware import FilesystemMiddleware, SubAgentMiddleware, SummarizationMiddleware

backend = StateBackend()
model = "anthropic:claude-sonnet-4-6"

# 대화를 100k 토큰에서 압축하고 최근 20개 메시지는 남긴다.
agent = create_deep_agent(
    model=model,
    middleware=[
        SummarizationMiddleware(
            model=model,
            backend=backend,
            trigger=("tokens", 100000),
            keep=("messages", 20),
        ),
        FilesystemMiddleware(
            backend=backend,
            system_prompt=(
                "Use the virtual filesystem to track long-running work. "
                "Write intermediate results to files instead of repeating them in messages."
            ),
        ),
    ],
)
```

`trigger`는 컨텍스트 창의 비율을 뜻하는 `("fraction", ...)`도 받고 여러 임계값을 주면 OR 의미로 결합한다. task 도구 설명을 바꾸려면 `SubAgentMiddleware`를 교체하되, 이 경우 `backend`와 `subagents`를 다시 선언해야 하며 자동 general-purpose subagent는 직접 넣지 않으면 포함되지 않는다. 더 좁게 task 설명만 바꾸려면 HarnessProfile의 `tool_description_overrides`를 사용한다.

### Interpreter

인터프리터는 범위가 제한된 QuickJS 런타임에서 JavaScript를 실행하는 `eval` 도구를 추가한다. 도구를 코드로 조합하거나, 일괄 작업·오류 처리·구조화 데이터 변환이 필요하지만 전체 shell은 원하지 않을 때 쓴다.

```python
from deepagents import create_deep_agent
from langchain_quickjs import CodeInterpreterMiddleware

agent = create_deep_agent(
    model="openai:gpt-5.5",
    middleware=[CodeInterpreterMiddleware()],
)
```

설치, 프로그래밍 방식 도구 호출, 서브에이전트 오케스트레이션, 제한은 [Interpreters](https://docs.langchain.com/oss/python/deepagents/interpreters)를 본다.

## Subagents

상세 작업을 격리하고 컨텍스트 비대화를 피하려면 서브에이전트를 쓴다.

```python
import os
from typing import Literal

from deepagents import create_deep_agent
from tavily import TavilyClient

tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])


def internet_search(query: str, max_results: int = 5, topic: Literal["general", "news", "finance"] = "general", include_raw_content: bool = False):
    """웹 검색을 실행한다."""
    return tavily_client.search(query, max_results=max_results, include_raw_content=include_raw_content, topic=topic)


research_subagent = {
    "name": "research-agent",
    "description": "심층 조사가 필요한 질문에 사용한다.",
    "system_prompt": "You are a great researcher",
    "tools": [internet_search],
    "model": "openai:gpt-5.5",  # 선택 사항; 생략하면 main agent 모델을 쓴다.
}

agent = create_deep_agent(
    model="google_genai:gemini-3.5-flash",
    subagents=[research_subagent],
)
```

자세한 모델은 [Subagents](https://docs.langchain.com/oss/python/deepagents/subagents)를 참고한다.

## Backends

Deep Agent의 도구는 가상 파일시스템을 이용해 파일을 저장·접근·수정할 수 있다. 기본값은 LangGraph state에 저장되는 `StateBackend`다. `skills` 또는 `memory`를 쓸 경우 agent를 만들기 **전에** 예상 skill/memory 파일을 백엔드에 넣어야 한다.

| 백엔드 | 범위·특성 | 주의점 |
| --- | --- | --- |
| `StateBackend` | thread 범위, checkpointer를 통해 같은 thread의 turn 사이에만 지속 | thread 간 공유되지 않는다. |
| `FilesystemBackend` | 로컬 파일시스템 | host 파일 읽기/쓰기를 직접 허용한다. 프로젝트 파일과 내부 데이터를 분리하려면 Composite로 감싼다. |
| `LocalShellBackend` | host 파일시스템 + `execute` shell | 무제한 host shell이므로 통제된 개발 환경에서만 쓴다. |
| `StoreBackend` | thread 간에도 지속되는 장기 저장소 | 다중 사용자라면 namespace factory로 tenant/user를 분리한다. |
| `ContextHubBackend` | LangSmith Hub repo에 내구성 있게 저장 | 별도 store를 준비하지 않는 Hub 기반 선택지다. |
| `CompositeBackend` | 경로별로 서로 다른 백엔드로 routing | scratch와 durable memory를 분리할 때 적합하다. |

```python
from deepagents import create_deep_agent
from deepagents.backends import (
    CompositeBackend,
    ContextHubBackend,
    FilesystemBackend,
    LocalShellBackend,
    StateBackend,
    StoreBackend,
)
from langgraph.store.memory import InMemoryStore

# 기본값도 StateBackend다.
state_agent = create_deep_agent(model="openai:gpt-5.5", backend=StateBackend())

# 로컬 디스크: virtual_mode를 통해 agent에 가상 경로를 노출할 수 있다.
filesystem_agent = create_deep_agent(
    model="openai:gpt-5.5",
    backend=FilesystemBackend(root_dir=".", virtual_mode=True),
)

# host shell 실행은 격리되지 않는다.
shell_agent = create_deep_agent(
    model="openai:gpt-5.5",
    backend=LocalShellBackend(root_dir=".", virtual_mode=True, env={"PATH": "/usr/bin:/bin"}),
)

# local development용 장기 store
store_agent = create_deep_agent(
    model="openai:gpt-5.5",
    backend=StoreBackend(namespace=lambda rt: (rt.server_info.user.identity,)),
    store=InMemoryStore(),
)

hub_agent = create_deep_agent(
    model="openai:gpt-5.5",
    backend=ContextHubBackend("my-agent"),
)

composite_agent = create_deep_agent(
    model="openai:gpt-5.5",
    backend=CompositeBackend(
        default=StateBackend(),
        routes={"/memories/": StoreBackend(namespace=lambda _rt: ("memories",))},
    ),
    store=InMemoryStore(),  # backend가 아니라 create_deep_agent에 전달한다.
)
```

LangSmith Deployment에서는 `StoreBackend`를 쓸 때 `store=`를 생략한다. 플랫폼이 store를 자동 제공한다.

### Sandboxes

Sandbox는 독립 파일시스템과 shell `execute`를 가진 특수 backend다. 로컬 머신을 바꾸지 않고 파일 작성·의존성 설치·명령 실행을 하려면 sandbox backend를 넘긴다.

| 제공자 | 어댑터 패키지 | 생성·정리 |
| --- | --- | --- |
| LangSmith | `langsmith[sandbox]` | `SandboxClient.create_sandbox()` / `delete_sandbox()` |
| Daytona | `langchain-daytona` | `Daytona().create()` / `stop()` |
| E2B | `langchain-e2b` | `Sandbox.create()` / `kill()` |
| Modal | `langchain-modal` | `modal.Sandbox.create()` / `terminate()` |
| Runloop | `langchain-runloop` | `client.devbox.create()` / `shutdown()` |
| Vercel | `langchain-vercel-sandbox` | `Sandbox.create()` / `stop()` |

```python
from deepagents import create_deep_agent
from deepagents.backends import LangSmithSandbox
from langchain_anthropic import ChatAnthropic
from langsmith.sandbox import SandboxClient

client = SandboxClient()
ls_sandbox = client.create_sandbox()
backend = LangSmithSandbox(sandbox=ls_sandbox)

agent = create_deep_agent(
    model=ChatAnthropic(model="claude-sonnet-4-6"),
    system_prompt="You are a Python coding assistant with sandbox access.",
    backend=backend,
)
try:
    result = agent.invoke({"messages": [{"role": "user", "content": "Create a small Python package and run pytest"}]})
finally:
    client.delete_sandbox(ls_sandbox.name)
```

Sandbox별 전체 설정은 [Sandboxes](https://docs.langchain.com/oss/python/deepagents/sandboxes)를 참고한다.

## Human-in-the-loop

민감한 도구 호출은 실행 전에 사람 승인을 요구할 수 있다. tool별로 설정한다. checkpointer는 필수다.

```python
from langchain.tools import tool
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import MemorySaver


@tool
def remove_file(path: str) -> str:
    """파일시스템에서 파일을 삭제한다."""
    return f"Deleted {path}"


@tool
def fetch_file(path: str) -> str:
    """파일시스템에서 파일을 읽는다."""
    return f"Contents of {path}"


@tool
def notify_email(to: str, subject: str, body: str) -> str:
    """이메일을 보낸다."""
    return f"Sent email to {to}"


agent = create_deep_agent(
    model="openai:gpt-5.5",
    tools=[remove_file, fetch_file, notify_email],
    interrupt_on={
        "remove_file": True,  # approve, edit, reject, respond
        "fetch_file": False,
        "notify_email": {"allowed_decisions": ["approve", "reject"]},
    },
    checkpointer=MemorySaver(),
)
```

agent·subagent의 도구 호출 인터럽트와 도구 내부의 인터럽트를 모두 구성할 수 있다. 전체 흐름은 [Human-in-the-loop](https://docs.langchain.com/oss/python/deepagents/human-in-the-loop) 노트와 문서를 참고한다.

## Skills

Skill은 Deep Agent에 새 역량과 전문성을 제공한다. 도구가 원시 파일 조작·계획 같은 저수준 기능을 담당한다면, skill은 작업 수행 상세 지침, 참고 정보, 템플릿 등의 자산을 포함한다. agent가 현재 프롬프트에 skill이 유용하다고 판단할 때만 파일을 로드한다. 이 progressive disclosure는 시작 시 고려할 토큰·컨텍스트를 줄인다.

예제 skill은 [Deep Agents example skills](https://github.com/langchain-ai/deepagentsjs/tree/main/examples/skills)에서 볼 수 있다.

### StateBackend에 skill 파일 심기

```python
from urllib.request import urlopen

from deepagents import create_deep_agent
from deepagents.backends import StateBackend
from deepagents.backends.utils import create_file_data
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
backend = StateBackend()
skill_url = "https://raw.githubusercontent.com/langchain-ai/deepagents/refs/heads/main/libs/cli/examples/skills/langgraph-docs/SKILL.md"
with urlopen(skill_url) as response:
    skill_content = response.read().decode("utf-8")

skills_files = {"/skills/langgraph-docs/SKILL.md": create_file_data(skill_content)}
agent = create_deep_agent(
    model="openai:gpt-5.5",
    backend=backend,
    skills=["/skills/"],
    checkpointer=checkpointer,
)
result = agent.invoke(
    {
        "messages": [{"role": "user", "content": "What is langgraph?"}],
        # StateBackend를 위한 가상 경로는 /로 시작한다.
        "files": skills_files,
    },
    config={"configurable": {"thread_id": "12345"}},
)
```

### StoreBackend·FilesystemBackend의 skill

```python
from pathlib import Path
from urllib.request import urlopen

from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend, StoreBackend
from deepagents.backends.utils import create_file_data
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore

# Store에 skill 파일을 넣는다.
store = InMemoryStore()
backend = StoreBackend(namespace=lambda _rt: ("filesystem",))
with urlopen("https://raw.githubusercontent.com/langchain-ai/deepagents/refs/heads/main/libs/cli/examples/skills/langgraph-docs/SKILL.md") as response:
    skill_content = response.read().decode("utf-8")
store.put(
    namespace=("filesystem",),
    key="/skills/langgraph-docs/SKILL.md",
    value=create_file_data(skill_content),
)
store_agent = create_deep_agent(
    model="openai:gpt-5.5", backend=backend, store=store, skills=["/skills/"]
)

# 실제 파일시스템 skill과 write/edit HITL
root_dir = "/Users/user/{project}"
filesystem_agent = create_deep_agent(
    model="google_genai:gemini-3.5-flash",
    backend=FilesystemBackend(root_dir=root_dir),
    skills=[str(Path(root_dir) / "skills")],
    interrupt_on={"write_file": True, "read_file": False, "edit_file": True},
    checkpointer=MemorySaver(),
)
```

## Memory

`AGENTS.md` 파일로 Deep Agent에 추가 컨텍스트를 제공한다. `memory=`에 하나 이상의 파일 경로를 전달한다.

### StateBackend memory

```python
from urllib.request import urlopen

from deepagents import create_deep_agent
from deepagents.backends.utils import create_file_data
from langgraph.checkpoint.memory import MemorySaver

with urlopen("https://raw.githubusercontent.com/langchain-ai/deepagents/refs/heads/main/examples/text-to-sql-agent/AGENTS.md") as response:
    agents_md = response.read().decode("utf-8")

agent = create_deep_agent(
    model="openai:gpt-5.5",
    memory=["/AGENTS.md"],
    checkpointer=MemorySaver(),
)
result = agent.invoke(
    {
        "messages": [{"role": "user", "content": "Please tell me what's in your memory files."}],
        "files": {"/AGENTS.md": create_file_data(agents_md)},
    },
    config={"configurable": {"thread_id": "123456"}},
)
```

### StoreBackend 및 FilesystemBackend memory

```python
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend, StoreBackend
from deepagents.backends.utils import create_file_data
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()
store.put(
    namespace=("filesystem",),
    key="/AGENTS.md",
    value=create_file_data(agents_md),
)
store_agent = create_deep_agent(
    model="openai:gpt-5.5",
    backend=StoreBackend(namespace=lambda _rt: ("filesystem",)),
    store=store,
    memory=["/AGENTS.md"],
)

filesystem_agent = create_deep_agent(
    model="openai:gpt-5.5",
    backend=FilesystemBackend(root_dir="/Users/user/{project}"),
    memory=["./AGENTS.md"],
    interrupt_on={"write_file": True, "read_file": False, "edit_file": True},
    checkpointer=MemorySaver(),
)
```

## Profiles

Harness profile은 matching model이 선택될 때 `create_deep_agent`가 자동 적용하는 모델별 설정 묶음이다. Claude 지시 스타일에 맞춘 system prompt suffix, GPT용으로 고친 도구 설명, 특정 제공자에서만 의미 있는 추가 미들웨어처럼 **호출 지점이 아니라 모델을 따라야 하는 동작**에 알맞다.

profile 하나에는 custom base system prompt(`base_system_prompt`), appended suffix(`system_prompt_suffix`), tool description overrides, 제외할 tools/middleware, 추가 미들웨어, 자동 general-purpose subagent 변경을 담을 수 있다.

```python
from deepagents import HarnessProfile, register_harness_profile

# gpt-5.5가 선택될 때마다 suffix를 붙인다.
register_harness_profile(
    "openai:gpt-5.5",
    HarnessProfile(system_prompt_suffix="Respond in under 100 words."),
)
```

등록 키, 병합 의미, plugin packaging은 [Profiles](https://docs.langchain.com/oss/python/deepagents/profiles)를 참고한다. provider profile은 API key, timeout, retry 설정처럼 모델 생성 인자를 제공자별로 묶는 보조 API다.

## Structured output

Deep Agents는 구조화된 출력을 지원한다. `create_deep_agent()`에 `response_format`으로 원하는 스키마를 넘긴다. 모델이 구조화 데이터를 생성하면 검증되고 deep agent state의 `structured_response` 키로 반환된다.

```python
from pydantic import BaseModel, Field

from deepagents import create_deep_agent


class WeatherReport(BaseModel):
    """현재 상태와 예보를 담는 구조화된 날씨 보고서."""

    location: str = Field(description="날씨 보고서의 위치")
    temperature: float = Field(description="섭씨 현재 기온")
    condition: str = Field(description="현재 날씨 상태")
    humidity: int = Field(description="습도 백분율")
    wind_speed: float = Field(description="풍속(km/h)")
    forecast: str = Field(description="향후 24시간의 짧은 예보")


agent = create_deep_agent(
    model="openai:gpt-5.5",
    response_format=WeatherReport,
    tools=[internet_search],
)
result = agent.invoke(
    {"messages": [{"role": "user", "content": "What's the weather like in San Francisco?"}]}
)
print(result["structured_response"])
```

더 많은 스키마·전략 예시는 LangChain [response format](https://docs.langchain.com/oss/python/langchain/structured-output#response-format)을 참고한다.

## Advanced

`create_deep_agent`는 `create_agent` 위에 미들웨어 스택을 미리 조립한다. 포함할 역량을 하나씩 완전히 고르고 싶다면 LangChain의 Configure the harness 문서를 사용한다.

## 조사와 실제 적용

### 1. 커스터마이즈 우선순위: 인자 → 미들웨어 → profile

* **호출 한 번의 요구**는 `system_prompt`, `tools`, `backend`, `response_format` 등 `create_deep_agent()` 인자로 표현한다.
* **실행 흐름을 가로지르는 정책**은 미들웨어에 둔다. 예: tool logging, PII 필터, retry, context summary.
* **모델을 바꿔도 일관되게 따라야 할 규칙**은 profile에 둔다. 호출부마다 조건문을 복제하지 않는다.

이 구분은 설정을 찾기 쉽게 만들고, provider/model 변경 때 적용 범위를 예측 가능하게 만든다.

### 2. 안전한 제품형 기본 구성

다음 구성은 사용자별 memory, thread 내부 scratch, 민감한 파일 쓰기 승인, 좁은 custom tool set을 함께 보여 준다.

```python
from dataclasses import dataclass

from deepagents import FilesystemPermission, create_deep_agent
from deepagents.backends import CompositeBackend, StateBackend, StoreBackend
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore


@dataclass
class RequestContext:
    user_id: str
    tenant_id: str


def search_docs(query: str) -> str:
    """승인된 문서 인덱스만 검색한다."""
    return f"results for {query}"


agent = create_deep_agent(
    model="openai:gpt-5.5",
    system_prompt="You are a concise product-support research agent. Cite source URLs.",
    tools=[search_docs],
    backend=CompositeBackend(
        default=StateBackend(),
        routes={
            "/memories/": StoreBackend(
                namespace=lambda rt: ("memory", rt.context.tenant_id, rt.context.user_id)
            ),
        },
    ),
    store=InMemoryStore(),
    permissions=[
        FilesystemPermission(operations=["write", "edit"], paths=["/memories/**"], mode="allow"),
    ],
    interrupt_on={"write_file": {"allowed_decisions": ["approve", "edit", "reject"]}},
    checkpointer=MemorySaver(),
    context_schema=RequestContext,
)
```

### 3. 운영 점검표

| 질문 | 확인할 설정 |
| --- | --- |
| 모델 변경이 프롬프트/도구 설명도 바꿔야 하는가? | Harness profile |
| tool 호출 공통 정책이 있는가? | middleware, 단 상태는 graph state에 둔다. |
| 파일이 thread 간 남아야 하는가? | `StoreBackend` 또는 `ContextHubBackend` |
| agent가 host shell을 실행해야 하는가? | 가능하면 sandbox를 우선하고 `LocalShellBackend`는 피한다. |
| 쓰기·외부 발송이 민감한가? | `permissions` + `interrupt_on` + checkpointer |
| 디버깅할 수 있는가? | LangSmith trace, agent/서브에이전트·도구별 run 확인 |

## 참고 자료

1. [LangChain — Customize Deep Agents](https://docs.langchain.com/oss/python/deepagents/customization) — 1차 공식 문서, 2026-07-26 확인.
2. [create_deep_agent API Reference](https://reference.langchain.com/python/deepagents/graph/create_deep_agent) — 1차 API reference.
3. [LangChain — Deep Agents Backends](https://docs.langchain.com/oss/python/deepagents/backends) — backend와 권한 설계.
4. [LangChain — Deep Agents Human-in-the-loop](https://docs.langchain.com/oss/python/deepagents/human-in-the-loop) — 승인·중단·재개 흐름.
5. [LangChain — Deep Agents Profiles](https://docs.langchain.com/oss/python/deepagents/profiles) — model별 profile 구성.
