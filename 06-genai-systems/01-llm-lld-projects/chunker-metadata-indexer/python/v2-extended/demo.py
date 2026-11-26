"""Demo for v2-extended components."""

from chunker import Document, DocumentChunker, ParagraphChunker
from token_chunker import TokenChunker
from semantic_chunker import SemanticChunker
from hierarchical_indexer import HierarchicalIndexer

def main():
    print("=== Chunker & Metadata Indexer Pipeline v2 Demo ===")

    text = (
        "The quick brown fox jumps over the lazy dog. "
        "This is an entirely different sentence with unrelated meaning. "
        "We are talking about something else now.\n\n"
        "Here is a new paragraph. It discusses topics like AI and machine learning. "
        "LLMs are large language models. They can generate text. "
        "Tokenization is the process of breaking text into pieces. "
        "Chunking is important for retrieval augmented generation."
    )

    doc = Document(text=text, source="demo.txt")

    print("\n--- Token Chunker ---")
    token_chunker = DocumentChunker(TokenChunker(max_tokens=10, overlap_tokens=2))
    token_chunks = token_chunker.chunk(doc)
    for i, chunk in enumerate(token_chunks):
        print(f"Chunk {i+1} [{chunk.start_pos}:{chunk.end_pos}]: {repr(chunk.text)}")

    print("\n--- Semantic Chunker ---")
    semantic_chunker = DocumentChunker(SemanticChunker(similarity_threshold=0.1, max_sentences_per_chunk=3))
    semantic_chunks = semantic_chunker.chunk(doc)
    for i, chunk in enumerate(semantic_chunks):
        print(f"Chunk {i+1} [{chunk.start_pos}:{chunk.end_pos}]: {repr(chunk.text)}")

    print("\n--- Hierarchical Indexer ---")
    indexer = HierarchicalIndexer(
        section_chunker=ParagraphChunker(),
        chunk_chunker=SemanticChunker(similarity_threshold=0.1)
    )

    hierarchy = indexer.index_document(doc)
    print(f"Indexed: {len(hierarchy['document'])} document level, {len(hierarchy['section'])} section level, {len(hierarchy['chunk'])} chunk level.")

    print("\nSearching for 'AI and machine learning' at Section level:")
    results = indexer.search("AI and machine learning", top_k=2, level="section")
    for res in results:
        print(f"Score: {res.score:.4f} | Chunk text: {repr(res.chunk.text)}")

if __name__ == "__main__":
    main()
