from collections.abc import Sequence

from app.models.document import Document
from app.repositories.document_repository import DocumentRepository


class KnowledgeService:
    def __init__(self, repository: DocumentRepository) -> None:
        self._repository = repository

    def search(self, query: str, *, limit: int = 5) -> Sequence[Document]:
        normalized = query.strip().casefold()
        if not normalized:
            raise ValueError("query must not be blank")
        return self._repository.search(normalized, limit=limit)

