"""
Snake and Ladder Game - V1 Basic

Core game entities.
"""
import random
from enum import Enum


class GameStatus(Enum):
    """Game status enumeration."""
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    FINISHED = "FINISHED"


class Dice:
    """Dice for generating random rolls."""
    
    def __init__(self, min_value: int = 1, max_value: int = 6):
        self._min_value = min_value
        self._max_value = max_value
    
    def roll(self) -> int:
        return random.randint(self._min_value, self._max_value)
    
    @property
    def min_value(self) -> int:
        return self._min_value
    
    @property
    def max_value(self) -> int:
        return self._max_value


class Player:
    """Represents a player in the game."""
    
    def __init__(self, player_id: str, name: str):
        if not player_id:
            raise ValueError("Player ID cannot be empty")
        if not name:
            raise ValueError("Player name cannot be empty")
        self._id = player_id
        self._name = name
        self._position = 0
    
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def position(self) -> int:
        return self._position
    
    def move_to(self, new_position: int) -> None:
        self._position = new_position
    
    def __str__(self) -> str:
        return f"{self._name} (Position: {self._position})"


class Snake:
    """Represents a snake on the board."""
    
    def __init__(self, head: int, tail: int):
        if head <= tail:
            raise ValueError("Snake head must be higher than tail")
        self._head = head
        self._tail = tail
    
    @property
    def head(self) -> int:
        return self._head
    
    @property
    def tail(self) -> int:
        return self._tail


class Ladder:
    """Represents a ladder on the board."""
    
    def __init__(self, bottom: int, top: int):
        if bottom >= top:
            raise ValueError("Ladder bottom must be lower than top")
        self._bottom = bottom
        self._top = top
    
    @property
    def bottom(self) -> int:
        return self._bottom
    
    @property
    def top(self) -> int:
        return self._top
