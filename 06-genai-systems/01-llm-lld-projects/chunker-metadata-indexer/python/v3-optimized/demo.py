import asyncio
import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))
from index import InMemoryIndex
from chunker import Document

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from streaming_chunker import StreamingChunker
from async_batch_indexer import AsyncBatchIndexer

def generate_large_document_stream():
    """Simulate a large document streaming in chunks (e.g., from network or disk)."""
    sentences = [
        "This is the first sentence of our very large document. ",
        "It talks about AI and machine learning. ",
        "Streaming chunking allows us to process this without loading it all at once. ",
        "Here is another sentence to add to the bulk. ",
        "We are generating multiple chunks of text. "
    ]
    # Simulate a stream by yielding sentences repeatedly
    for _ in range(20):
        for sentence in sentences:
            yield sentence

async def main():
    print("=== Chunker & Metadata Indexer Pipeline v3-Optimized Demo ===")

    # 1. Setup backend and indexer
    backend = InMemoryIndex()
    indexer = AsyncBatchIndexer(backend, batch_size=5, max_concurrency=2)

    # 2. Setup streaming chunker
    chunker = StreamingChunker(chunk_size=50, overlap=10)

    # 3. Get document stream
    print("Starting stream generation...")
    stream = generate_large_document_stream()

    # 4. Chunk stream
    # Note: doc_id could be passed explicitly
    chunk_stream = chunker.chunk_stream(stream, doc_id="demo-doc-123")

    print("Processing and indexing chunks asynchronously...")
    start_time = time.time()

    # 5. Process stream with async batch indexer
    await indexer.process_stream(chunk_stream)

    elapsed = time.time() - start_time
    print(f"Indexing completed in {elapsed:.2f} seconds.")
    print(f"Total entries in index: {backend.size()}")

    # 6. Test search
    print("\nTesting search for a query embedding...")
    # Dummy embedding for testing
    query_emb = [0.5] * 10
    results = backend.search(query_emb, top_k=3)

    print(f"Top 3 results:")
    for res in results:
        print(f"Score {res.score:.4f}: {res.chunk.text[:40]}...")

if __name__ == "__main__":
    asyncio.run(main())
