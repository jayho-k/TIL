from pathlib import Path
from typing import Any

from app.agents.common.contracts import AgentRunner
from app.agents.general.tools import build_knowledge_tools
from app.core.config import Settings
from app.prompts.assembly import build_system_prompt
from app.prompts.registry import PromptRegistry
from app.services.knowledge_service import KnowledgeService


def _message_text(message: Any) -> str:
    content = getattr(message, "content", message)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(
            block.get("text", "")
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        )
    return str(content)


def _load_skill_files(skill_root: Path) -> dict[str, Any]:
    from deepagents.backends.utils import create_file_data

    files: dict[str, Any] = {}
    for path in skill_root.rglob("*"):
        if path.is_file():
            relative = path.relative_to(skill_root).as_posix()
            files[f"/skills/{relative}"] = create_file_data(path.read_text(encoding="utf-8"))
    return files


class DeepAgentRunner:
    def __init__(self, graph: Any, skill_files: dict[str, Any]) -> None:
        self._graph = graph
        self._skill_files = skill_files

    async def run(self, message: str, thread_id: str) -> str:
        result = await self._graph.ainvoke(
            {
                "messages": [{"role": "user", "content": message}],
                "files": self._skill_files,
            },
            config={"configurable": {"thread_id": thread_id}},
        )
        return _message_text(result["messages"][-1])


def build_general_agent(
    settings: Settings,
    prompts: PromptRegistry,
    knowledge: KnowledgeService,
) -> AgentRunner:
    from deepagents import create_deep_agent
    from langgraph.checkpoint.memory import MemorySaver

    skill_root = Path(__file__).parent / "skills"
    graph = create_deep_agent(
        model=settings.model_name,
        tools=build_knowledge_tools(knowledge),
        system_prompt=build_system_prompt(prompts, "general"),
        skills=["/skills/"],
        checkpointer=MemorySaver(),
    )
    return DeepAgentRunner(graph, _load_skill_files(skill_root))


class LazyGeneralAgentRunner:
    def __init__(
        self,
        settings: Settings,
        prompts: PromptRegistry,
        knowledge: KnowledgeService,
    ) -> None:
        self._settings = settings
        self._prompts = prompts
        self._knowledge = knowledge
        self._runner: AgentRunner | None = None

    async def run(self, message: str, thread_id: str) -> str:
        if self._runner is None:
            self._runner = build_general_agent(self._settings, self._prompts, self._knowledge)
        return await self._runner.run(message, thread_id)
