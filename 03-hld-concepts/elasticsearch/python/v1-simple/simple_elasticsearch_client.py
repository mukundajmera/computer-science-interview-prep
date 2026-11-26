"""Interview-scale in-memory search client with lightweight filtering."""

from dataclasses import dataclass, field
from typing import List, Set


@dataclass(frozen=True)
class Document:
    id: str
    title: str
    body: str
    tags: Set[str] = field(default_factory=set)


class SimpleElasticsearchClient:
    def __init__(self) -> None:
        self._documents: List[Document] = []

    def index(self, document: Document) -> None:
        self._documents.append(document)

    def search_text(self, query: str) -> List[Document]:
        needle = query.lower()
        return [
            document
            for document in self._documents
            if needle in document.title.lower() or needle in document.body.lower()
        ]

    def filter_by_tag(self, tag: str) -> List[Document]:
        return [document for document in self._documents if tag in document.tags]


if __name__ == "__main__":
    client = SimpleElasticsearchClient()
    client.index(Document("1", "Design Search", "Elasticsearch basics", {"distributed", "search"}))
    client.index(Document("2", "Cache Guide", "Redis cache-aside pattern", {"cache"}))
    print("search_text('search') ->", len(client.search_text("search")))
    print("filter_by_tag('distributed') ->", len(client.filter_by_tag("distributed")))
