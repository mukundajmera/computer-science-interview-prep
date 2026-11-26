import pytest
import sys
import os
import importlib.util

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))
from chunker import Document

v4_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v4-advanced'))
sys.path.insert(0, v4_dir)

# Load metadata module directly from v4
spec = importlib.util.spec_from_file_location("v4_metadata", os.path.join(v4_dir, "metadata.py"))
v4_meta = importlib.util.module_from_spec(spec)
sys.modules["v4_metadata"] = v4_meta
spec.loader.exec_module(v4_meta)

import chunkers

def test_token_chunker():
    doc = Document(text="This is a simple test document for token chunker")
    chunker_obj = chunkers.TokenChunker(chunk_size=4, overlap=1)
    chunks = chunker_obj.chunk(doc)
    
    assert len(chunks) == 3
    assert chunks[0].text == "This is a simple"
    assert chunks[1].text == "simple test document for"
    assert chunks[2].text == "for token chunker"

def test_recursive_character_chunker_basic():
    doc = Document(text="Word "*50) # 250 chars
    chunker_obj = chunkers.RecursiveCharacterChunker(chunk_size=100, overlap=10)
    chunks = chunker_obj.chunk(doc)
    
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk.text) <= 100

def test_recursive_character_chunker_paragraphs():
    doc = Document(text="Paragraph 1.\n\nParagraph 2.\n\nParagraph 3.")
    chunker_obj = chunkers.RecursiveCharacterChunker(chunk_size=20, overlap=0)
    chunks = chunker_obj.chunk(doc)
    
    assert len(chunks) >= 3
    # The length of "Paragraph 1." is 12, so it fits in 20.
    assert "Paragraph 1." in chunks[0].text

def test_markdown_header_chunker():
    text = "# Title\nSome content.\n## Subtitle\nMore content."
    doc = Document(text=text)
    chunker_obj = chunkers.MarkdownHeaderChunker()
    chunks = chunker_obj.chunk(doc)
    
    assert len(chunks) == 2
    
    assert "Some content." in chunks[0].text
    assert any(tag.key == "Header 1" and tag.value == "Title" for tag in chunks[0].metadata)
    
    assert "More content." in chunks[1].text
    assert any(tag.key == "Header 1" and tag.value == "Title" for tag in chunks[1].metadata)
    assert any(tag.key == "Header 2" and tag.value == "Subtitle" for tag in chunks[1].metadata)

def test_advanced_metadata_extractor():
    text = "Hello world!"
    doc = Document(text=text, source="test.md", doc_id="doc1")
    
    chunker_obj = chunkers.TokenChunker(chunk_size=10, overlap=0)
    chunks = chunker_obj.chunk(doc)
    
    extractor = v4_meta.AdvancedMetadataExtractor()
    enriched = extractor.extract(chunks, doc)
    
    assert len(enriched) == 1
    meta = {t.key: t.value for t in enriched[0].metadata}
    
    assert meta["source"] == "test.md"
    assert meta["doc_id"] == "doc1"
    assert "position" in meta
    assert meta["word_count"] == "2"
    assert meta["token_estimate"] == "2"
    
    byte_start = int(meta["byte_start"])
    byte_end = int(meta["byte_end"])
    assert byte_end > byte_start
    assert byte_start == 0
