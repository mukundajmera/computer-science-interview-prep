"""
GameState enum for Tic-Tac-Toe - v1 Basic
"""
from enum import Enum


class GameState(Enum):
    """Represents the state of the game."""
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    X_WON = "X_WON"
    O_WON = "O_WON"
    DRAW = "DRAW"
    
    def is_game_over(self) -> bool:
        """Check if game is over."""
        return self in (GameState.X_WON, GameState.O_WON, GameState.DRAW)
    
    def get_message(self) -> str:
        """Get human-readable message for the state."""
        messages = {
            GameState.X_WON: "Player X wins!",
            GameState.O_WON: "Player O wins!",
            GameState.DRAW: "It's a draw!",
            GameState.IN_PROGRESS: "Game in progress...",
            GameState.NOT_STARTED: "Game not started"
        }
        return messages[self]
