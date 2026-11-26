import re
from typing import List, Tuple
from chunker import ChunkingStrategy

class SimpleTokenizer:
    """A dummy tokenizer for environments restricted to the standard library.

    Splits text on whitespace and punctuation to approximate tokenization.
    """

    def encode(self, text: str) -> List[str]:
        """Encode text into a list of string 'tokens'."""
        # Simple regex to capture words as tokens. For a dummy tokenizer,
        # we can just split on whitespace and punctuation properly.
        # But for 'max_tokens=4' to mean 4 words, we need to treat spaces as non-tokens
        # or handle them differently. Let's just consider non-whitespace chunks as tokens.
        # This simplifies the char offset logic as well.
        words = []
        for match in re.finditer(r'\S+', text):
            words.append((match.group(), match.start(), match.end()))
        return words

    def decode(self, tokens: List[Tuple[str, int, int]]) -> str:
        """Decode a list of tokens back into text."""
        return " ".join(t[0] for t in tokens)

class TokenChunker(ChunkingStrategy):
    """Chunking strategy based on token counts rather than character lengths.

    Args:
        max_tokens: The maximum number of tokens per chunk.
        overlap_tokens: The number of tokens to overlap between chunks.
        tokenizer: An object with encode() and decode() methods. If None, uses SimpleTokenizer.
    """

    def __init__(self, max_tokens: int = 100, overlap_tokens: int = 0, tokenizer=None) -> None:
        if max_tokens <= 0:
            raise ValueError("max_tokens must be positive")
        if overlap_tokens < 0:
            raise ValueError("overlap_tokens must be non-negative")
        if overlap_tokens >= max_tokens:
            raise ValueError("overlap_tokens must be less than max_tokens")

        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens
        self.tokenizer = tokenizer if tokenizer is not None else SimpleTokenizer()

    def _split_text(self, text: str) -> List[Tuple[str, int, int]]:
        tokens = self.tokenizer.encode(text)
        if not tokens:
            return []

        step = self.max_tokens - self.overlap_tokens
        segments = []
        start_idx = 0

        while start_idx < len(tokens):
            end_idx = min(start_idx + self.max_tokens, len(tokens))
            chunk_tokens = tokens[start_idx:end_idx]

            # Extract actual substring from original text using token offsets
            start_pos = chunk_tokens[0][1]
            end_pos = chunk_tokens[-1][2]
            chunk_text = text[start_pos:end_pos]

            segments.append((chunk_text.strip(), start_pos, end_pos))

            start_idx += step
            if start_idx < len(tokens) and start_idx + self.overlap_tokens >= len(tokens):
                break

        return segments
