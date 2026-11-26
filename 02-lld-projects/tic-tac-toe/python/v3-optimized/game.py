"""
Game class for Tic-Tac-Toe - v1 Basic
"""
from typing import Optional
from mark import Mark
from position import Position
from board import Board
from player import Player
from game_state import GameState
from win_checker import WinChecker


class Game:
    """Main game controller for Tic-Tac-Toe."""
    
    def __init__(self, player1: Player, player2: Player, board_size: int = Board.DEFAULT_SIZE):
        """
        Initialize the game.
        
        Args:
            player1: First player (X)
            player2: Second player (O)
            board_size: Size of the board (default 3)
        """
        self._board = Board(board_size)
        self._players = [player1, player2]
        self._win_checker = WinChecker()
        self._state = GameState.NOT_STARTED
        self._current_player_index = 0
        self._last_move: Optional[Position] = None
    
    @property
    def board(self) -> Board:
        """Get the game board."""
        return self._board
    
    @property
    def state(self) -> GameState:
        """Get current game state."""
        return self._state
    
    def is_game_over(self) -> bool:
        """Check if game is over."""
        return self._state.is_game_over()
    
    def get_current_player(self) -> Player:
        """Get current player."""
        return self._players[self._current_player_index]
    
    def start(self) -> None:
        """Start the game."""
        self._state = GameState.IN_PROGRESS
        print(f"Game Started! {self._players[0].mark} moves first.")
    
    def make_move(self, position: Position) -> bool:
        """
        Make a move at the specified position.
        
        Args:
            position: Position to place the mark
            
        Returns:
            True if move was successful
        """
        if self._state != GameState.IN_PROGRESS:
            print("Game is not in progress!")
            return False
        
        current_player = self.get_current_player()
        
        if not self._board.place_mark(position, current_player.mark):
            print("Invalid move!")
            return False
        
        self._last_move = position
        
        # Check for win
        if self._win_checker.check_win(self._board, position):
            self._state = GameState.X_WON if current_player.mark == Mark.X else GameState.O_WON
        elif self._board.is_full():
            self._state = GameState.DRAW
        else:
            # Switch to next player
            self._current_player_index = 1 - self._current_player_index
        
        return True
    
    def play(self) -> None:
        """Play a complete game loop."""
        self.start()
        
        while not self.is_game_over():
            self._board.display()
            current_player = self.get_current_player()
            move = current_player.make_move(self._board)
            self.make_move(move)
        
        self._board.display()
        print(self._state.get_message())
    
    def reset(self) -> None:
        """Reset the game."""
        self._board.reset()
        self._state = GameState.NOT_STARTED
        self._current_player_index = 0
        self._last_move = None
