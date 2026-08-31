from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class PromptRegistry:
    root: Path
    paths: Mapping[str, str]

    def read(self, key: str) -> str:
        try:
            relative_path = self.paths[key]
        except KeyError:
            raise KeyError(key) from None
        return (self.root / relative_path).read_text(encoding="utf-8").strip()


def default_prompt_registry() -> PromptRegistry:
    root = Path(__file__).parent
    return PromptRegistry(
        root=root,
        paths={
            "shared.safety": "shared/safety.md",
            "general.system": "general/system.md",
            "reflection.system": "reflection/system.md",
        },
    )

