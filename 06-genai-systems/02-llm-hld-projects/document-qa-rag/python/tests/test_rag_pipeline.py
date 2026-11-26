import pytest
import sys
import os

# Add to path to allow dynamic imports per instructions
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))

from rag_pipeline import DocumentProcessor, HybridRetriever, Chunk, PromptBuilder, RAGPipeline

def test_chunking_with_overlap():
    processor = DocumentProcessor(chunk_size=5, overlap=2)
    text = "The quick brown fox jumps over the lazy dog."
    metadata = {"doc_title": "Test Doc", "page_num": 1}

    chunks = processor.chunk_document("doc_1", text, metadata)

    # words: ["The", "quick", "brown", "fox", "jumps", "over", "the", "lazy", "dog."]
    # chunk 1: 0-5 -> "The quick brown fox jumps"
    # chunk 2: 3-8 -> "fox jumps over the lazy"
    # chunk 3: 6-9 -> "the lazy dog."

    assert len(chunks) == 3
    assert chunks[0].text == "The quick brown fox jumps"
    assert chunks[1].text == "fox jumps over the lazy"
    assert chunks[2].text == "the lazy dog."

    assert chunks[0].metadata["doc_id"] == "doc_1"
    assert chunks[0].metadata["doc_title"] == "Test Doc"
    assert chunks[0].metadata["chunk_index"] == 0

def test_hybrid_retrieval_rrf():
    retriever = HybridRetriever()

    chunk1 = Chunk(id="c1", text="Machine learning algorithms build a model based on training data.", metadata={})
    chunk2 = Chunk(id="c2", text="The weather today is sunny and warm.", metadata={})
    chunk3 = Chunk(id="c3", text="Deep learning is a subset of machine learning.", metadata={})

    retriever.ingest(chunk1)
    retriever.ingest(chunk2)
    retriever.ingest(chunk3)

    results = retriever.search("machine learning model", top_k=2)

    assert len(results) == 2
    # Expect c1 and c3 to be the top results due to relevance
    result_ids = [c.id for c in results]
    assert "c1" in result_ids
    assert "c3" in result_ids
    assert "c2" not in result_ids

def test_prompt_context_truncation():
    builder = PromptBuilder(max_context_tokens=60)

    # 5 words
    chunk1 = Chunk(id="c1", text="This is a short chunk.", metadata={"doc_title": "Doc A", "page_num": 1})
    # 20 words
    chunk2 = Chunk(id="c2", text="This is a much longer chunk that will definitely exceed the token limit when combined with the other text.", metadata={"doc_title": "Doc B", "page_num": 2})

    query = "What is this?"

    prompt = builder.build_prompt(query, [chunk1, chunk2])

    assert "[Source 1]" in prompt
    assert "Doc A" in prompt
    # Since max_context_tokens is 30, and the system prompt + query + chunk 1 citations takes up about 25-30 tokens,
    # chunk 2 should be excluded.
    assert "[Source 2]" not in prompt
    assert "Doc B" not in prompt

def test_end_to_end_rag_pipeline():
    pipeline = RAGPipeline(chunk_size=10, overlap=2, max_context_tokens=100)

    doc_text = "Python is a high-level, general-purpose programming language. Its design philosophy emphasizes code readability with the use of significant indentation. Python is dynamically typed and garbage-collected."
    pipeline.ingest_document("doc_py", doc_text, metadata={"doc_title": "Python Wiki", "page_num": 1})

    prompt = pipeline.query("Is Python dynamically typed?", top_k=1)

    assert "Python is dynamically typed" in prompt
    assert "[Source 1] Python Wiki - Page 1" in prompt
    assert "QUESTION: Is Python dynamically typed?" in prompt
