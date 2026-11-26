"""
Tests for Chunker–Metadata–Indexer Pipeline (v1-basic).
"""
import unittest
import sys
import os

# Add v1-basic to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v1-basic'))


class TestFixedSizeChunker(unittest.TestCase):
    """Tests for FixedSizeChunker strategy."""

    def setUp(self):
        from chunker import Document, FixedSizeChunker
        self.Document = Document
        self.FixedSizeChunker = FixedSizeChunker

    def test_basic_splitting(self):
        """Fixed-size chunker should split text into equal-sized pieces."""
        doc = self.Document(text="a" * 100, source="test.txt")
        chunker = self.FixedSizeChunker(chunk_size=30)
        chunks = chunker.chunk(doc)
        # 100 / 30 = 4 chunks (30+30+30+10)
        self.assertEqual(len(chunks), 4)

    def test_overlap_produces_more_chunks(self):
        """Overlap should produce more chunks than no-overlap."""
        doc = self.Document(text="a" * 100, source="test.txt")
        no_overlap = self.FixedSizeChunker(chunk_size=50, overlap=0)
        with_overlap = self.FixedSizeChunker(chunk_size=50, overlap=25)
        self.assertGreater(
            len(with_overlap.chunk(doc)),
            len(no_overlap.chunk(doc)),
        )

    def test_overlap_content_shared(self):
        """Overlapping chunks should share characters at boundaries."""
        doc = self.Document(text="abcdefghij", source="test.txt")
        chunker = self.FixedSizeChunker(chunk_size=6, overlap=2)
        chunks = chunker.chunk(doc)
        # First chunk: abcdef, second chunk: efghij (overlap on 'ef')
        self.assertTrue(chunks[0].text.endswith("ef"))
        self.assertTrue(chunks[1].text.startswith("ef"))

    def test_document_shorter_than_chunk_size(self):
        """Document shorter than chunk_size should produce a single chunk."""
        doc = self.Document(text="short", source="test.txt")
        chunker = self.FixedSizeChunker(chunk_size=100)
        chunks = chunker.chunk(doc)
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0].text, "short")

    def test_invalid_chunk_size_raises(self):
        """Chunk size <= 0 should raise ValueError."""
        with self.assertRaises(ValueError):
            self.FixedSizeChunker(chunk_size=0)

    def test_overlap_exceeds_size_raises(self):
        """Overlap >= chunk_size should raise ValueError."""
        with self.assertRaises(ValueError):
            self.FixedSizeChunker(chunk_size=10, overlap=10)

    def test_chunk_positions_are_correct(self):
        """start_pos and end_pos should map back to the original text."""
        text = "Hello, world! This is a test document."
        doc = self.Document(text=text, source="test.txt")
        chunker = self.FixedSizeChunker(chunk_size=15)
        for chunk in chunker.chunk(doc):
            self.assertEqual(
                chunk.text,
                text[chunk.start_pos:chunk.end_pos],
            )


class TestSentenceChunker(unittest.TestCase):
    """Tests for SentenceChunker strategy."""

    def setUp(self):
        from chunker import Document, SentenceChunker
        self.Document = Document
        self.SentenceChunker = SentenceChunker

    def test_groups_sentences(self):
        """Sentences should be grouped according to max_sentences."""
        text = "First. Second. Third. Fourth."
        doc = self.Document(text=text, source="test.txt")
        chunker = self.SentenceChunker(max_sentences=2, overlap=0)
        chunks = chunker.chunk(doc)
        self.assertEqual(len(chunks), 2)

    def test_sentence_overlap(self):
        """Overlapping sentence chunks should repeat boundary sentences."""
        text = "One. Two. Three. Four."
        doc = self.Document(text=text, source="test.txt")
        chunker = self.SentenceChunker(max_sentences=2, overlap=1)
        chunks = chunker.chunk(doc)
        # With overlap=1: [One,Two], [Two,Three], [Three,Four]
        self.assertGreaterEqual(len(chunks), 3)

    def test_single_sentence(self):
        """A single sentence should produce one chunk."""
        doc = self.Document(text="Only one sentence.", source="test.txt")
        chunker = self.SentenceChunker(max_sentences=3)
        chunks = chunker.chunk(doc)
        self.assertEqual(len(chunks), 1)

    def test_no_sentence_boundaries(self):
        """Text without punctuation should produce a single chunk."""
        doc = self.Document(text="No punctuation here", source="test.txt")
        chunker = self.SentenceChunker(max_sentences=2)
        chunks = chunker.chunk(doc)
        self.assertEqual(len(chunks), 1)


class TestParagraphChunker(unittest.TestCase):
    """Tests for ParagraphChunker strategy."""

    def setUp(self):
        from chunker import Document, ParagraphChunker
        self.Document = Document
        self.ParagraphChunker = ParagraphChunker

    def test_splits_on_double_newline(self):
        """Paragraphs separated by blank lines should become separate chunks."""
        text = "Para one.\n\nPara two.\n\nPara three."
        doc = self.Document(text=text, source="test.txt")
        chunker = self.ParagraphChunker()
        chunks = chunker.chunk(doc)
        self.assertEqual(len(chunks), 3)

    def test_no_paragraphs(self):
        """Text without double newlines should produce a single chunk."""
        doc = self.Document(text="Single paragraph only.", source="test.txt")
        chunker = self.ParagraphChunker()
        chunks = chunker.chunk(doc)
        self.assertEqual(len(chunks), 1)

    def test_empty_paragraphs_skipped(self):
        """Multiple consecutive blank lines should not create empty chunks."""
        text = "First.\n\n\n\nSecond."
        doc = self.Document(text=text, source="test.txt")
        chunker = self.ParagraphChunker()
        chunks = chunker.chunk(doc)
        self.assertEqual(len(chunks), 2)


class TestMetadataExtractor(unittest.TestCase):
    """Tests for MetadataExtractor."""

    def setUp(self):
        from chunker import Document, FixedSizeChunker
        from metadata import MetadataExtractor
        self.doc = Document(text="Hello world. Foo bar.", source="test.md")
        chunker = FixedSizeChunker(chunk_size=50)
        self.chunks = chunker.chunk(self.doc)
        self.extractor = MetadataExtractor()

    def test_standard_tags_present(self):
        """Every chunk should have all standard metadata tags."""
        enriched = self.extractor.extract(self.chunks, self.doc)
        expected_keys = {"source", "doc_id", "position", "word_count",
                         "char_count", "start_pos", "end_pos"}
        for chunk in enriched:
            keys = {t.key for t in chunk.metadata}
            self.assertTrue(expected_keys.issubset(keys))

    def test_word_count_accuracy(self):
        """word_count tag should reflect actual word count."""
        enriched = self.extractor.extract(self.chunks, self.doc)
        for chunk in enriched:
            tag = next(t for t in chunk.metadata if t.key == "word_count")
            self.assertEqual(int(tag.value), len(chunk.text.split()))

    def test_source_matches_document(self):
        """source tag should match the document's source."""
        enriched = self.extractor.extract(self.chunks, self.doc)
        for chunk in enriched:
            tag = next(t for t in chunk.metadata if t.key == "source")
            self.assertEqual(tag.value, "test.md")

    def test_position_format(self):
        """position tag should follow 'chunk N of M' format."""
        enriched = self.extractor.extract(self.chunks, self.doc)
        total = len(enriched)
        for idx, chunk in enumerate(enriched):
            tag = next(t for t in chunk.metadata if t.key == "position")
            self.assertEqual(tag.value, f"chunk {idx + 1} of {total}")

    def test_preserves_custom_metadata(self):
        """Pre-existing custom metadata should be preserved after extraction."""
        from chunker import MetadataTag
        self.chunks[0].metadata = [MetadataTag(key="custom", value="keep_me")]
        enriched = self.extractor.extract(self.chunks, self.doc)
        keys = [t.key for t in enriched[0].metadata]
        self.assertIn("custom", keys)
        self.assertIn("source", keys)


class TestInMemoryIndex(unittest.TestCase):
    """Tests for InMemoryIndex backend."""

    def setUp(self):
        from chunker import Chunk
        from index import InMemoryIndex
        self.InMemoryIndex = InMemoryIndex
        self.Chunk = Chunk
        self.index = InMemoryIndex()

    def _make_chunk(self, text: str = "test") -> "Chunk":
        import uuid
        return self.Chunk(
            chunk_id=str(uuid.uuid4()),
            text=text,
            doc_id="doc-1",
            start_pos=0,
            end_pos=len(text),
        )

    def test_add_and_size(self):
        """Adding entries should increase index size."""
        c = self._make_chunk()
        self.index.add(c, [1.0, 0.0, 0.0])
        self.assertEqual(self.index.size(), 1)

    def test_search_returns_sorted(self):
        """Search should return results sorted by descending similarity."""
        c1 = self._make_chunk("close")
        c2 = self._make_chunk("far")
        self.index.add(c1, [1.0, 0.0])
        self.index.add(c2, [0.0, 1.0])
        results = self.index.search([1.0, 0.0], top_k=2)
        self.assertGreater(results[0].score, results[1].score)

    def test_search_top_k_limits_results(self):
        """Search should return at most top_k entries."""
        for i in range(10):
            self.index.add(self._make_chunk(f"c{i}"), [float(i), 1.0])
        results = self.index.search([5.0, 1.0], top_k=3)
        self.assertEqual(len(results), 3)

    def test_delete_existing(self):
        """Deleting an existing entry should return True and reduce size."""
        c = self._make_chunk()
        self.index.add(c, [1.0])
        self.assertTrue(self.index.delete(c.chunk_id))
        self.assertEqual(self.index.size(), 0)

    def test_delete_nonexistent(self):
        """Deleting a non-existent chunk_id should return False."""
        self.assertFalse(self.index.delete("no-such-id"))

    def test_empty_embedding_raises(self):
        """Adding an empty embedding should raise ValueError."""
        c = self._make_chunk()
        with self.assertRaises(ValueError):
            self.index.add(c, [])

    def test_dimension_mismatch_raises(self):
        """Searching with mismatched dimensions should raise ValueError."""
        c = self._make_chunk()
        self.index.add(c, [1.0, 2.0])
        with self.assertRaises(ValueError):
            self.index.search([1.0, 2.0, 3.0], top_k=1)

    def test_search_empty_index(self):
        """Searching an empty index should return an empty list."""
        results = self.index.search([1.0, 0.0], top_k=5)
        self.assertEqual(results, [])

    def test_add_overwrites_existing(self):
        """Re-adding the same chunk_id should overwrite the entry."""
        c = self._make_chunk()
        self.index.add(c, [1.0, 0.0])
        self.index.add(c, [0.0, 1.0])
        self.assertEqual(self.index.size(), 1)
        results = self.index.search([0.0, 1.0], top_k=1)
        self.assertAlmostEqual(results[0].score, 1.0, places=5)


class TestChunkingStrategyValidation(unittest.TestCase):
    """Tests for shared validation in ChunkingStrategy base class."""

    def test_empty_document_raises(self):
        """Chunking an empty document should raise ValueError."""
        from chunker import Document, FixedSizeChunker
        doc = Document(text="", source="empty.txt")
        with self.assertRaises(ValueError):
            FixedSizeChunker(chunk_size=10).chunk(doc)

    def test_whitespace_only_document_raises(self):
        """Chunking a whitespace-only document should raise ValueError."""
        from chunker import Document, ParagraphChunker
        doc = Document(text="   \n\n  ", source="blank.txt")
        with self.assertRaises(ValueError):
            ParagraphChunker().chunk(doc)


if __name__ == "__main__":
    unittest.main()
