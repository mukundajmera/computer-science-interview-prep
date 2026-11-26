import uuid
from typing import List, Dict, Any, Optional
from chunker import Document, Chunk, ChunkingStrategy, DocumentChunker, MetadataTag
from index import IndexBackend, InMemoryIndex

class DummySummarizer:
    """A dummy summarizer that just takes the first N words of the text."""

    def summarize(self, text: str, max_words: int = 20) -> str:
        words = text.split()
        if len(words) <= max_words:
            return text
        return " ".join(words[:max_words]) + "..."

class HierarchicalIndexer:
    """Indexes documents at multiple levels of granularity: Document, Section, and Chunk.

    Args:
        section_chunker: Strategy to split documents into sections (e.g., ParagraphChunker).
        chunk_chunker: Strategy to split sections into chunks (e.g., SemanticChunker).
        index_backend: The backend to store the chunks.
    """

    def __init__(self, section_chunker: ChunkingStrategy, chunk_chunker: ChunkingStrategy, index_backend: Optional[IndexBackend] = None):
        self.section_orchestrator = DocumentChunker(section_chunker)
        self.chunk_orchestrator = DocumentChunker(chunk_chunker)
        self.index = index_backend or InMemoryIndex()
        self.summarizer = DummySummarizer()

    def index_document(self, document: Document) -> Dict[str, List[Chunk]]:
        """Process a document and add it to the index at multiple levels.

        Returns:
            A dictionary grouping the created chunks by level ('document', 'section', 'chunk').
        """
        created_chunks = {
            'document': [],
            'section': [],
            'chunk': []
        }

        # 1. Document Level
        doc_summary = self.summarizer.summarize(document.text, max_words=50)
        doc_chunk = Chunk(
            chunk_id=document.doc_id, # Use doc_id as chunk_id for the document level
            text=doc_summary,
            doc_id=document.doc_id,
            start_pos=0,
            end_pos=len(document.text),
            metadata=[
                MetadataTag(key="level", value="document"),
                MetadataTag(key="source", value=document.source)
            ]
        )
        self._add_to_index(doc_chunk)
        created_chunks['document'].append(doc_chunk)

        # 2. Section Level
        sections = self.section_orchestrator.chunk(document)
        for i, section in enumerate(sections):
            section_summary = self.summarizer.summarize(section.text, max_words=30)

            # We create a new chunk for the section summary
            section_chunk = Chunk(
                chunk_id=section.chunk_id,
                text=section_summary,
                doc_id=document.doc_id,
                start_pos=section.start_pos,
                end_pos=section.end_pos,
                metadata=[
                    MetadataTag(key="level", value="section"),
                    MetadataTag(key="parent_id", value=document.doc_id),
                    MetadataTag(key="section_index", value=str(i))
                ]
            )
            self._add_to_index(section_chunk)
            created_chunks['section'].append(section_chunk)

            # 3. Chunk Level
            # We need to treat the section as a document to chunk it further
            section_doc = Document(text=section.text, source=document.source, doc_id=document.doc_id)
            sub_chunks = self.chunk_orchestrator.chunk(section_doc)

            for j, sub_chunk in enumerate(sub_chunks):
                # Adjust offsets relative to the original document
                actual_start = section.start_pos + sub_chunk.start_pos
                actual_end = section.start_pos + sub_chunk.end_pos

                final_chunk = Chunk(
                    chunk_id=sub_chunk.chunk_id,
                    text=sub_chunk.text,
                    doc_id=document.doc_id,
                    start_pos=actual_start,
                    end_pos=actual_end,
                    metadata=[
                        MetadataTag(key="level", value="chunk"),
                        MetadataTag(key="parent_id", value=section.chunk_id),
                        MetadataTag(key="chunk_index", value=str(j))
                    ]
                )
                self._add_to_index(final_chunk)
                created_chunks['chunk'].append(final_chunk)

        return created_chunks

    def _add_to_index(self, chunk: Chunk) -> None:
        # Generate dummy embedding based on string length and ascii values to be somewhat deterministic
        # For a real implementation, an embedding model would be used.
        vec = [float(ord(c)) / 255.0 for c in chunk.text[:10]]
        # pad to 10
        while len(vec) < 10:
            vec.append(0.0)
        self.index.add(chunk, vec)

    def search(self, query_text: str, top_k: int = 3, level: str = None) -> List[Any]:
        """Search the index, optionally filtering by level."""
        vec = [float(ord(c)) / 255.0 for c in query_text[:10]]
        while len(vec) < 10:
            vec.append(0.0)

        results = self.index.search(vec, top_k * 5) # Retrieve more to filter

        if level:
            filtered = []
            for res in results:
                for tag in res.chunk.metadata:
                    if tag.key == "level" and tag.value == level:
                        filtered.append(res)
                        break
            return filtered[:top_k]

        return results[:top_k]
