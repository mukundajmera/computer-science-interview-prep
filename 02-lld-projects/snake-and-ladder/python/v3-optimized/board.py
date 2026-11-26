"""
Snake and Ladder Game - V2 Extended

Board class.
"""
from typing import Dict
from game_entities import TileEffectStrategy, SnakeEffectStrategy, LadderEffectStrategy


class Board:
    """Game board with tile effect strategies."""
    
    def __init__(self, size: int = 100):
        if size < 10:
            raise ValueError("Board size must be at least 10")
        self._size = size
        self._effects: Dict[int, TileEffectStrategy] = {}
    
    def add_snake(self, head: int, tail: int) -> None:
        """Add a snake to the board."""
        if head > self._size or tail < 1:
            raise ValueError("Invalid snake positions")
        self._effects[head] = SnakeEffectStrategy(head, tail)
    
    def add_ladder(self, bottom: int, top: int) -> None:
        """Add a ladder to the board."""
        if bottom < 1 or top > self._size:
            raise ValueError("Invalid ladder positions")
        self._effects[bottom] = LadderEffectStrategy(bottom, top)
        
    def add_effect(self, position: int, strategy: TileEffectStrategy) -> None:
        """Add a generic tile effect strategy."""
        if position < 1 or position > self._size:
            raise ValueError("Invalid effect position")
        self._effects[position] = strategy
    
    def get_next_position(self, current_position: int, dice_roll: int) -> int:
        """Calculate next position after dice roll using strategies."""
        new_position = current_position + dice_roll
        
        if new_position > self._size:
            return current_position
            
        if new_position in self._effects:
            new_position = self._effects[new_position].apply_effect(new_position)
            
        return new_position
    
    def has_snake_at(self, position: int) -> bool:
        return position in self._effects and isinstance(self._effects[position], SnakeEffectStrategy)
    
    def has_ladder_at(self, position: int) -> bool:
        return position in self._effects and isinstance(self._effects[position], LadderEffectStrategy)
    
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
