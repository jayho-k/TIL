from collections.abc import Iterable, Sequence
from typing import Protocol

from app.models.document import Document


class DocumentRepository(Protocol):
    def search(self, query: str, *, limit: int = 5) -> Sequence[Document]: ...


class InMemoryDocumentRepository:
    def __init__(self, documents: Iterable[Document] = ()) -> None:
        self._documents = list(documents)
        self.last_query: str | None = None

    def search(self, query: str, *, limit: int = 5) -> Sequence[Document]:
        self.last_query = query
        lowered = query.casefold()
        matches = [
            document
            for document in self._documents
            if lowered in document.title.casefold() or lowered in document.content.casefold()
        ]
        return matches[:limit]

