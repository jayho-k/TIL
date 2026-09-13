import json
from collections.abc import Iterable, Iterator
from typing import Any

import httpx


def parse_sse_lines(lines: Iterable[str]) -> Iterator[tuple[str, dict[str, Any]]]:
    event = "message"
    data: list[str] = []
    for line in lines:
        if not line:
            if data:
                yield event, json.loads("\n".join(data))
            event, data = "message", []
        elif line.startswith("event:"):
            event = line.removeprefix("event:").strip()
        elif line.startswith("data:"):
            data.append(line.removeprefix("data:").strip())
    if data:
        yield event, json.loads("\n".join(data))


class AgentApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def start(self, filename: str, content: bytes):
        with httpx.stream(
            "POST",
            f"{self.base_url}/runs",
            files={"file": (filename, content, "text/plain")},
            timeout=300,
        ) as response:
            response.raise_for_status()
            yield from parse_sse_lines(response.iter_lines())

    def resume(self, run_id: str, decision: dict[str, Any]):
        with httpx.stream(
            "POST",
            f"{self.base_url}/runs/{run_id}/resume",
            json=decision,
            timeout=300,
        ) as response:
            response.raise_for_status()
            yield from parse_sse_lines(response.iter_lines())

    def status(self, run_id: str) -> dict[str, Any]:
        response = httpx.get(f"{self.base_url}/runs/{run_id}", timeout=30)
        response.raise_for_status()
        return response.json()

    def download(self, run_id: str) -> bytes:
        response = httpx.get(f"{self.base_url}/runs/{run_id}/download", timeout=30)
        response.raise_for_status()
        return response.content
