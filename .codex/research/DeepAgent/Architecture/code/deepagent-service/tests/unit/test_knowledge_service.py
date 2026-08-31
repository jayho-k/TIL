from app.models.document import Document
from app.repositories.document_repository import InMemoryDocumentRepository
from app.services.knowledge_service import KnowledgeService


def test_search_normalizes_query_and_delegates_to_repository():
    repository = InMemoryDocumentRepository(
        [Document(id="1", title="SOLID", content="Single responsibility principle")]
    )
    service = KnowledgeService(repository)

    results = service.search("  solid  ")

    assert [document.title for document in results] == ["SOLID"]
    assert repository.last_query == "solid"


def test_search_rejects_blank_query():
    service = KnowledgeService(InMemoryDocumentRepository())

    try:
        service.search("   ")
    except ValueError as exc:
        assert str(exc) == "query must not be blank"
    else:
        raise AssertionError("blank query must fail")

