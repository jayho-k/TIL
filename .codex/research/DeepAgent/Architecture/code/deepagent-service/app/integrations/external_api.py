from typing import Protocol


class ExternalApiClient(Protocol):
    async def get_json(self, path: str) -> dict[str, object]: ...

