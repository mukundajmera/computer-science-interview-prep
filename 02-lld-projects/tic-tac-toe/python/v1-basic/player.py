"""
Player classes for Tic-Tac-Toe - v1 Basic
"""
from abc import ABC, abstractmethod
from mark import Mark
from position import Position
from board import Board


class Player(ABC):
    """Abstract base class for players."""
    
    def __init__(self, name: str, mark: Mark):
        """Initialize a player."""
        if mark == Mark.EMPTY:
            raise ValueError("Player cannot have EMPTY mark")
        self._name = name
        self._mark = mark
    
    @property
    def name(self) -> str:
        """Get player name."""
        return self._name
    
    @property
    def mark(self) -> Mark:
        """Get player mark."""
        return self._mark
    
    @abstractmethod
    def make_move(self, board: Board) -> Position:
        """
        Get the next move from this player.
        
        Args:
            board: Current board state
            
        Returns:
            Position to place mark
        """
        pass
    
    def __str__(self) -> str:
        return f"{self._name} ({self._mark})"


class HumanPlayer(Player):
    """Human player that gets moves from console input."""
    
    def make_move(self, board: Board) -> Position:
        """Get move from user input."""
        size = board.size
        max_pos = size * size
        
        while True:
            try:
                input_str = input(f"{self.name} ({self.mark}), enter position (1-{max_pos}): ")
                pos = int(input_str.strip())
                
                if pos < 1 or pos > max_pos:
                    print(f"Invalid position! Enter a number between 1 and {max_pos}")
                    continue
                
                # Convert 1-indexed position to row, col
                row = (pos - 1) // size
                col = (pos - 1) % size
                position = Position(row, col)
                
                if not board.is_empty(position):
                    print("That cell is already occupied! Try again.")
                    continue
                
                return position
                
            except ValueError:
                print("Invalid input! Please enter a number.")
