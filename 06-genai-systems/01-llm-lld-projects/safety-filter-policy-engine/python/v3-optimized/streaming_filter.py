"""
Streaming safety filter optimized for early cancellation.
"""

from typing import Iterator

class PolicyViolationError(Exception):
    """Raised when a streamed chunk violates a safety policy."""
    pass

class StreamingSafetyInspector:
    """Evaluates text streams chunk-by-chunk for early cancellation."""

    def __init__(self, block_patterns: list[str]):
        """Initialize with a list of simple block patterns/keywords."""
        self.block_patterns = block_patterns
        self._buffer = ""

    def inspect_stream(self, token_stream: Iterator[str]) -> Iterator[str]:
        """
        Yields tokens if they are safe. Raises PolicyViolationError if a block pattern
        is detected in the accumulated buffer, allowing for early cancellation.
        """
        for token in token_stream:
            self._buffer += token
            # Check for block patterns in the current buffer
            for pattern in self.block_patterns:
                # Basic string matching for demonstration
                # (In a real system, this could use compiled regex or Aho-Corasick)
                if pattern.lower() in self._buffer.lower():
                    raise PolicyViolationError(f"Safety violation detected: '{pattern}'")
            yield token
