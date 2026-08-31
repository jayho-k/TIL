from app.prompts.registry import PromptRegistry


def build_system_prompt(registry: PromptRegistry, agent_name: str) -> str:
    sections = [registry.read("shared.safety"), registry.read(f"{agent_name}.system")]
    return "\n\n".join(section for section in sections if section)
