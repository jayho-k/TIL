from collections.abc import Sequence
from typing import Any

from app.models.document import Document
from app.services.knowledge_service import KnowledgeService


def _format_documents(documents: Sequence[Document]) -> str:
    if not documents:
        return "No matching documents found."
    return "\n\n".join(
        f"[{document.id}] {document.title}\n{document.content}" for document in documents
    )


def build_knowledge_tools(service: KnowledgeService) -> list[Any]:
    from langchain_core.tools import tool

    @tool
    def search_knowledge(query: str) -> str:
        """Search internal knowledge documents for the supplied query."""
        return _format_documents(service.search(query))

    return [search_knowledge]

