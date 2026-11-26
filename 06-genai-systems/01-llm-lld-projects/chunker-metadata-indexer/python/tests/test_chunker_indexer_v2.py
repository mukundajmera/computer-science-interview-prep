import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v2-extended')))
from chunker import Document, ParagraphChunker
from token_chunker import TokenChunker
from semantic_chunker import SemanticChunker
from hierarchical_indexer import HierarchicalIndexer

def test_token_chunker():
    doc = Document(text="One two three four five six seven eight nine ten")
    chunker = TokenChunker(max_tokens=4, overlap_tokens=1)

    chunks = chunker.chunk(doc)
    # The words: "One", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"
    # Chunk 1: 0,1,2,3 -> One two three four
    # Chunk 2: 3,4,5,6 -> four five six seven
    # Chunk 3: 6,7,8,9 -> seven eight nine ten
    assert len(chunks) == 3
    assert chunks[0].text == "One two three four"
    assert chunks[1].text == "four five six seven"
    assert chunks[2].text == "seven eight nine ten"

    # Check offsets
    assert doc.text[chunks[0].start_pos:chunks[0].end_pos] == "One two three four"

def test_semantic_chunker():
    # First two sentences are similar (mention apple), third is different.
    text = "I like to eat apple. The apple is very sweet. Cars are fast and drive on roads."
    doc = Document(text=text)

    # threshold > 0.0 means the first two might be grouped if they share words.
    # Actually, jaccard("i like to eat apple", "the apple is very sweet") = "apple" is shared.
    chunker = SemanticChunker(similarity_threshold=0.1)
    chunks = chunker.chunk(doc)

    # Verify we get two chunks based on similarity
    # Chunk 1: "I like to eat apple. The apple is very sweet."
    # Chunk 2: "Cars are fast and drive on roads."
    assert len(chunks) >= 2
    assert "apple" in chunks[0].text.lower()
    assert "Cars" in chunks[-1].text

def test_hierarchical_indexer_levels():
    doc = Document(text="Paragraph one.\n\nParagraph two.\n\nParagraph three.")

    indexer = HierarchicalIndexer(
        section_chunker=ParagraphChunker(),
        chunk_chunker=SemanticChunker()
    )

    hierarchy = indexer.index_document(doc)

    assert len(hierarchy['document']) == 1
    assert len(hierarchy['section']) == 3
    # at least 3 chunks
    assert len(hierarchy['chunk']) >= 3

    doc_chunk = hierarchy['document'][0]
    assert doc_chunk.metadata[0].value == "document"

    section_chunk = hierarchy['section'][0]
    assert section_chunk.metadata[0].value == "section"

    chunk_chunk = hierarchy['chunk'][0]
    assert chunk_chunk.metadata[0].value == "chunk"

def test_hierarchical_indexer_search_filter():
    doc = Document(text="Paragraph one.\n\nParagraph two.")

    indexer = HierarchicalIndexer(
        section_chunker=ParagraphChunker(),
        chunk_chunker=SemanticChunker()
    )

    indexer.index_document(doc)

    section_results = indexer.search("Paragraph one", level="section")
    for res in section_results:
        assert any(t.key == "level" and t.value == "section" for t in res.chunk.metadata)

    doc_results = indexer.search("Paragraph one", level="document")
    for res in doc_results:
        assert any(t.key == "level" and t.value == "document" for t in res.chunk.metadata)
