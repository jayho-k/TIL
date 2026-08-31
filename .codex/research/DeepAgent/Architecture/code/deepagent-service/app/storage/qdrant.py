from typing import Any


def create_qdrant_client(url: str) -> Any:
    """Create an async Qdrant client for vector repository adapters."""
    from qdrant_client import AsyncQdrantClient

    return AsyncQdrantClient(url=url)

