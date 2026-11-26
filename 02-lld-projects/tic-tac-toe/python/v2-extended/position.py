"""
Position class for Tic-Tac-Toe - v1 Basic
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Position:
    """Represents a position on the Tic-Tac-Toe board. Immutable."""
    row: int
    col: int
    
    def is_valid(self, board_size: int) -> bool:
        """Check if position is valid for given board size."""
        return 0 <= self.row < board_size and 0 <= self.col < board_size
    
    def __str__(self) -> str:
        return f"({self.row}, {self.col})"
