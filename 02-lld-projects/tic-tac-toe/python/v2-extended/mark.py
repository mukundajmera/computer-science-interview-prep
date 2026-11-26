"""
Mark enum for Tic-Tac-Toe - v1 Basic
"""
from enum import Enum


class Mark(Enum):
    """Represents a mark on the Tic-Tac-Toe board."""
    X = 'X'
    O = 'O'
    EMPTY = ' '
    
    def __str__(self) -> str:
        return self.value
