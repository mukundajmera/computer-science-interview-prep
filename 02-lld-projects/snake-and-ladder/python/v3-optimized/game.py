"""
Snake and Ladder Game - V3 Optimized

Main Game class with turn timeout rules.
"""
from typing import List, Optional
import time
from game_entities import Player, Dice, GameStatus
from board import Board


class TurnTimeoutError(Exception):
    """Raised when a player takes too long to play their turn."""
    pass


class Game:
    """Main game controller with turn timeouts."""
    
    def __init__(self, board: Board = None, turn_timeout_seconds: float = 5.0):
        self._board = board or Board.create_standard_board()
        self._players: List[Player] = []
        self._dice = Dice()
        self._current_player_index = 0
        self._status = GameStatus.NOT_STARTED
        self._winner: Optional[Player] = None
        self._turn_timeout_seconds = turn_timeout_seconds
        
    def add_player(self, name: str) -> Player:
        """Add a player to the game."""
        if self._status != GameStatus.NOT_STARTED:
            raise RuntimeError("Cannot add players after game has started")
        
        player_id = f"P{len(self._players) + 1}"
        player = Player(player_id, name)
        self._players.append(player)
        print(f"Added player: {name}")
        return player
    
    def start_game(self) -> None:
        """Start the game."""
        if len(self._players) < 2:
            raise RuntimeError("Need at least 2 players to start")
        self._status = GameStatus.IN_PROGRESS
        self._current_player_index = 0
        print(f"\n=== Game Started! ===")
        print(f"Players: {len(self._players)}")
    
    def _execute_turn_logic(self, current_player: Player, forced_roll: Optional[int] = None) -> None:
        """Internal logic for executing a turn."""
        roll = forced_roll if forced_roll is not None else self._dice.roll()
        old_position = current_player.position
        new_position = self._board.get_next_position(old_position, roll)
        
        print(f"\n{current_player.name} rolls {roll}")
        print(f"  Position: {old_position} → {new_position}")
        
        current_player.move_to(new_position)
        
        if self._board.is_winning_position(new_position):
            self._status = GameStatus.FINISHED
            self._winner = current_player
            print(f"\n🎉 {current_player.name} WINS! 🎉")
            return
            
        self._current_player_index = (self._current_player_index + 1) % len(self._players)

    def play_turn(self, delay: float = 0.0) -> None:
        """Play the current player's turn, simulating delay."""
        if self._status != GameStatus.IN_PROGRESS:
            raise RuntimeError("Game is not in progress")
            
        current_player = self.current_player
        
        start_time = time.time()
        
        if delay > 0:
            time.sleep(delay)
            
        elapsed_time = time.time() - start_time
        
        if elapsed_time > self._turn_timeout_seconds:
            print(f"\n{current_player.name} took too long! Turn skipped.")
            self._current_player_index = (self._current_player_index + 1) % len(self._players)
            return
            
        self._execute_turn_logic(current_player)
    
    @property
    def current_player(self) -> Player:
        return self._players[self._current_player_index]
    
    @property
    def is_game_over(self) -> bool:
        return self._status == GameStatus.FINISHED
    
    @property
    def winner(self) -> Optional[Player]:
        return self._winner
    
    @property
    def status(self) -> GameStatus:
        return self._status
    
    @property
    def players(self) -> List[Player]:
        return list(self._players)
    
    @property
    def board(self) -> Board:
        return self._board
        
    @property
    def turn_timeout_seconds(self) -> float:
        return self._turn_timeout_seconds
    
    def play_game(self) -> Optional[Player]:
        """Play until someone wins."""
        self.start_game()
        max_turns = 1000
        turn_count = 0
        
        while not self.is_game_over and turn_count < max_turns:
            self.play_turn()
            turn_count += 1
        
        return self.winner
