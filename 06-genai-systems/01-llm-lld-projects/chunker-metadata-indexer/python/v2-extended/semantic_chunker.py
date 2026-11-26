import re
import math
from typing import List, Tuple, Set
from chunker import ChunkingStrategy

def get_words(text: str) -> Set[str]:
    """Extract lowercase words from text."""
    return set(re.findall(r'\b\w+\b', text.lower()))

def jaccard_similarity(set1: Set[str], set2: Set[str]) -> float:
    """Calculate Jaccard similarity between two sets."""
    if not set1 and not set2:
        return 1.0
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union > 0 else 0.0

class SemanticChunker(ChunkingStrategy):
    """Chunking strategy that splits text based on semantic boundaries.

    It detects semantic shifts by computing similarity between sliding windows
    of sentences and splitting when similarity drops below a threshold.

    Args:
        similarity_threshold: If similarity between consecutive sentences drops
                              below this, a boundary is created.
        max_sentences_per_chunk: Hard limit on chunk size to prevent huge chunks.
    """

    _SENTENCE_RE = re.compile(r'(?<=[.!?])\s+')

    def __init__(self, similarity_threshold: float = 0.1, max_sentences_per_chunk: int = 10) -> None:
        self.similarity_threshold = similarity_threshold
        self.max_sentences_per_chunk = max_sentences_per_chunk

    def _split_text(self, text: str) -> List[Tuple[str, int, int]]:
        # 1. Split into sentences and record their offsets
        sentences: List[Tuple[str, int, int]] = []
        prev = 0
        for match in self._SENTENCE_RE.finditer(text):
            end = match.start()
            segment = text[prev:end + 1]
            sentences.append((segment, prev, end + 1))
            prev = match.end()

        if prev < len(text):
            segment = text[prev:]
            sentences.append((segment, prev, len(text)))

        if not sentences:
            return []

        # 2. Calculate word sets for each sentence
        sentence_features = [get_words(s[0]) for s in sentences]

        # 3. Group sentences into chunks based on similarity drops
        segments: List[Tuple[str, int, int]] = []

        current_chunk_sentences = [sentences[0]]

        for i in range(1, len(sentences)):
            prev_features = sentence_features[i-1]
            curr_features = sentence_features[i]

            sim = jaccard_similarity(prev_features, curr_features)

            # Boundary condition: similarity drops below threshold, OR max sentences reached
            if sim < self.similarity_threshold or len(current_chunk_sentences) >= self.max_sentences_per_chunk:
                # Finalize current chunk
                combined_text = "".join(s[0] for s in current_chunk_sentences)
                start_pos = current_chunk_sentences[0][1]
                end_pos = current_chunk_sentences[-1][2]
                segments.append((combined_text.strip(), start_pos, end_pos))

                # Start new chunk
                current_chunk_sentences = [sentences[i]]
            else:
                current_chunk_sentences.append(sentences[i])

        # Add the last chunk
        if current_chunk_sentences:
            combined_text = "".join(s[0] for s in current_chunk_sentences)
            start_pos = current_chunk_sentences[0][1]
            end_pos = current_chunk_sentences[-1][2]
            segments.append((combined_text.strip(), start_pos, end_pos))

        return segments
