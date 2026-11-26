"""
Chess Game - V1 Basic

Position and enums for chess game.
"""
from enum import Enum
from dataclasses import dataclass


class Color(Enum):
    WHITE = "WHITE"
    BLACK = "BLACK"

    def opposite(self):
        return Color.BLACK if self == Color.WHITE else Color.WHITE


class GameState(Enum):
    ACTIVE = "ACTIVE"
    CHECK = "CHECK"
    CHECKMATE = "CHECKMATE"
    STALEMATE = "STALEMATE"
    RESIGNED = "RESIGNED"


@dataclass(frozen=True)
class Position:
    """Position on the chess board."""
    row: int  # 0-7 (rank 1-8)
    col: int  # 0-7 (file a-h)

    def is_valid(self) -> bool:
        return 0 <= self.row < 8 and 0 <= self.col < 8

    def to_algebraic(self) -> str:
        """Convert to algebraic notation (e.g., 'e4')."""
        file = chr(ord('a') + self.col)
        rank = self.row + 1
        return f"{file}{rank}"

    @classmethod
    def from_algebraic(cls, notation: str) -> 'Position':
        """Create position from algebraic notation."""
        if len(notation) != 2:
            raise ValueError(f"Invalid notation: {notation}")
        
        file = notation[0]
        rank = notation[1]
        
        col = ord(file) - ord('a')
        row = int(rank) - 1
        
        pos = cls(row, col)
        if not pos.is_valid():
            raise ValueError(f"Invalid position: {notation}")
        return pos

    def __str__(self) -> str:
        return self.to_algebraic()
