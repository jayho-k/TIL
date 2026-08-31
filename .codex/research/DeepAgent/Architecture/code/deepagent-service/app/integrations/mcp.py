from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class McpServerConfig:
    name: str
    transport: str
    endpoint: str

