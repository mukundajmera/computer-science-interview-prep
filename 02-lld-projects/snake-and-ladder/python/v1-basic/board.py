"""
Snake and Ladder Game - V1 Basic

Board class.
"""
from typing import Dict


class Board:
    """Game board with snakes and ladders."""
    
    def __init__(self, size: int = 100):
        if size < 10:
            raise ValueError("Board size must be at least 10")
        self._size = size
        self._snakes: Dict[int, int] = {}  # head -> tail
        self._ladders: Dict[int, int] = {}  # bottom -> top
    
    def add_snake(self, head: int, tail: int) -> None:
        """Add a snake to the board."""
        if head <= tail:
            raise ValueError("Snake head must be greater than tail")
        if head > self._size or tail < 1:
            raise ValueError("Invalid snake positions")
        self._snakes[head] = tail
    
    def add_ladder(self, bottom: int, top: int) -> None:
        """Add a ladder to the board."""
        if bottom >= top:
            raise ValueError("Ladder bottom must be less than top")
        if bottom < 1 or top > self._size:
            raise ValueError("Invalid ladder positions")
        self._ladders[bottom] = top
    
    def get_next_position(self, current_position: int, dice_roll: int) -> int:
        """Calculate next position after dice roll."""
        new_position = current_position + dice_roll
        
        if new_position > self._size:
            return current_position
        
        if new_position in self._snakes:
            snake_tail = self._snakes[new_position]
            print(f"  Oops! Snake at {new_position} → slides down to {snake_tail}")
            return snake_tail
        
        if new_position in self._ladders:
            ladder_top = self._ladders[new_position]
            print(f"  Yay! Ladder at {new_position} → climbs up to {ladder_top}")
            return ladder_top
        
        return new_position
    
    def has_snake_at(self, position: int) -> bool:
        return position in self._snakes
    
    def has_ladder_at(self, position: int) -> bool:
        return position in self._ladders
    
    def is_winning_position(self, position: int) -> bool:
        return position == self._size
    
    @property
    def size(self) -> int:
        return self._size
    
    @classmethod
    def create_standard_board(cls) -> 'Board':
        """Create a standard 100-square board."""
        board = cls(100)
        
        # Add snakes
        snakes = [(16, 6), (47, 26), (49, 11), (56, 53), (62, 19),
                  (64, 60), (87, 24), (93, 73), (95, 75), (98, 78)]
        for head, tail in snakes:
            board.add_snake(head, tail)
        
        # Add ladders
        ladders = [(1, 38), (4, 14), (9, 31), (21, 42), (28, 84),
                   (36, 44), (51, 67), (71, 91), (80, 100)]
        for bottom, top in ladders:
            board.add_ladder(bottom, top)
        
        return board
