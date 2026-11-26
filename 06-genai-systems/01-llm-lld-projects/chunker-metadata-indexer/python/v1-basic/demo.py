"""
Chunker–Metadata–Indexer demo — v1 basic.

Walks through the full pipeline:
    1. Create a document
    2. Chunk with each strategy
    3. Extract metadata
    4. Index chunks with stub embeddings
    5. Perform a similarity search
    6. Delete an entry

Run:
    python demo.py
"""

from chunker import (
    Document,
    DocumentChunker,
    FixedSizeChunker,
    ParagraphChunker,
    SentenceChunker,
)
from index import InMemoryIndex
from metadata import MetadataExtractor

SAMPLE_TEXT = (
    "Retrieval-Augmented Generation (RAG) combines a retrieval step with a "
    "generative model. The retriever fetches relevant passages from a corpus. "
    "These passages are then fed to a large language model as context. "
    "The model generates an answer grounded in the retrieved evidence.\n\n"
    "Chunking is a critical preprocessing step. Documents must be split into "
    "manageable pieces so that embeddings capture focused semantics. Overlap "
    "between chunks helps preserve context across boundaries.\n\n"
    "An index stores the chunk embeddings and supports fast similarity search. "
    "Common backends include FAISS, Pinecone, and Weaviate."
)


def _stub_embedding(text: str, dim: int = 8) -> list:
    """Generate a deterministic stub embedding based on text content.

    Uses SHA-256 for cross-run determinism (unlike ``hash()`` which is
    randomised per interpreter invocation).

    This is NOT a real embedding model — it exists only to demonstrate
    the pipeline without external dependencies.
    """
    import hashlib
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    return [b / 255.0 for b in digest[:dim]]


def main() -> None:
    doc = Document(text=SAMPLE_TEXT, source="rag-overview.md")

    print("=" * 60)
    print("CHUNKER–METADATA–INDEXER DEMO (v1-basic)")
    print("=" * 60)

    # ------------------------------------------------------------------
    # 1. Fixed-size chunking
    # ------------------------------------------------------------------
    print("\n--- Fixed-Size Chunking (size=150, overlap=30) ---")
    chunker = DocumentChunker(FixedSizeChunker(chunk_size=150, overlap=30))
    chunks = chunker.chunk(doc)
    for c in chunks:
        print(f"  [{c.start_pos}:{c.end_pos}] {c.text[:60]}...")

    # ------------------------------------------------------------------
    # 2. Sentence-based chunking
    # ------------------------------------------------------------------
    print("\n--- Sentence Chunking (max_sentences=2, overlap=1) ---")
    chunker.set_strategy(SentenceChunker(max_sentences=2, overlap=1))
    chunks = chunker.chunk(doc)
    for c in chunks:
        print(f"  [{c.start_pos}:{c.end_pos}] {c.text[:60]}...")

    # ------------------------------------------------------------------
    # 3. Paragraph-based chunking
    # ------------------------------------------------------------------
    print("\n--- Paragraph Chunking ---")
    chunker.set_strategy(ParagraphChunker())
    chunks = chunker.chunk(doc)
    for c in chunks:
        print(f"  [{c.start_pos}:{c.end_pos}] {c.text[:60]}...")

    # ------------------------------------------------------------------
    # 4. Metadata extraction
    # ------------------------------------------------------------------
    print("\n--- Metadata Extraction ---")
    extractor = MetadataExtractor()
    chunks = extractor.extract(chunks, doc)
    for c in chunks:
        tags = {t.key: t.value for t in c.metadata}
        print(f"  Chunk {tags.get('position', '?')}: "
              f"words={tags.get('word_count')}, chars={tags.get('char_count')}")

    # ------------------------------------------------------------------
    # 5. Indexing + search
    # ------------------------------------------------------------------
    print("\n--- Indexing & Search ---")
    index = InMemoryIndex()
    for c in chunks:
        emb = _stub_embedding(c.text)
        index.add(c, emb)
    print(f"  Indexed {index.size()} chunks")

    query = _stub_embedding("How does RAG work?")
    results = index.search(query, top_k=2)
    print(f"  Top-2 search results:")
    for entry in results:
        print(f"    score={entry.score:.4f}  text={entry.chunk.text[:50]}...")

    # ------------------------------------------------------------------
    # 6. Deletion
    # ------------------------------------------------------------------
    print("\n--- Delete ---")
    target_id = chunks[0].chunk_id
    deleted = index.delete(target_id)
    print(f"  Deleted chunk {target_id[:8]}...: {deleted}")
    print(f"  Index size after delete: {index.size()}")

    print("\n" + "=" * 60)
    print("Demo complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
