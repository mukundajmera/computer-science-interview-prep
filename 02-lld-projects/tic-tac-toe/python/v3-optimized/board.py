"""
Board class for Tic-Tac-Toe - v1 Basic
"""
from typing import List
from mark import Mark
from position import Position


class Board:
    """Represents the Tic-Tac-Toe game board."""
    
    DEFAULT_SIZE = 3
    
    def __init__(self, size: int = DEFAULT_SIZE):
        """Initialize the board with given size."""
        if size < 1:
            raise ValueError("Board size must be at least 1")
        self._size = size
        self._cells: List[List[Mark]] = []
        self._empty_cells = 0
        self.reset()
    
    @property
    def size(self) -> int:
        """Get the board size."""
        return self._size
    
    @property
    def empty_cells(self) -> int:
        """Get count of empty cells."""
        return self._empty_cells
    
    def place_mark(self, position: Position, mark: Mark) -> bool:
        """
        Place a mark on the board.
        
        Args:
            position: Position to place the mark
            mark: Mark to place
            
        Returns:
            True if successful, False if invalid
        """
        if not self.is_valid_move(position):
            return False
        
        self._cells[position.row][position.col] = mark
        self._empty_cells -= 1
        return True
    
    def remove_mark(self, position: Position) -> None:
        """Remove a mark from the board (for undo)."""
        if position.is_valid(self._size) and self._cells[position.row][position.col] != Mark.EMPTY:
            self._cells[position.row][position.col] = Mark.EMPTY
            self._empty_cells += 1
    
    def get_mark(self, position: Position) -> Mark:
        """Get the mark at a position."""
        if not position.is_valid(self._size):
            raise ValueError(f"Invalid position: {position}")
        return self._cells[position.row][position.col]
    
    def is_empty(self, position: Position) -> bool:
        """Check if a position is empty."""
        return position.is_valid(self._size) and self._cells[position.row][position.col] == Mark.EMPTY
    
    def is_valid_move(self, position: Position) -> bool:
        """Check if a move is valid."""
        return position is not None and position.is_valid(self._size) and self.is_empty(position)
    
    def is_full(self) -> bool:
        """Check if the board is full."""
        return self._empty_cells == 0
    
    def reset(self) -> None:
        """Reset the board to initial state."""
        self._cells = [[Mark.EMPTY for _ in range(self._size)] for _ in range(self._size)]
        self._empty_cells = self._size * self._size
    
    def display(self) -> None:
        """Display the board."""
        print()
        for i in range(self._size):
            row_str = "  "
            for j in range(self._size):
                mark = self._cells[i][j]
                if mark == Mark.EMPTY:
                    # Show position number (1-indexed)
                    row_str += str(i * self._size + j + 1)
                else:
                    row_str += str(mark)
                
                if j < self._size - 1:
                    row_str += " | "
            
            print(row_str)
            
            if i < self._size - 1:
                separator = " " + "---+" * (self._size - 1) + "---"
                print(separator)
        print()
