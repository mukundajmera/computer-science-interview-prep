"""
Chess Game - V1 Basic

Main game controller.
"""
from typing import List
from position import Position, Color, GameState
from board import Board


class Player:
    """Player representation."""
    
    def __init__(self, name: str, color: Color):
        self.name = name
        self.color = color

    def __str__(self) -> str:
        return f"{self.name} ({self.color.value})"


class Game:
    """Main chess game controller."""
    
    def __init__(self, white_name: str = "White", black_name: str = "Black"):
        self.board = Board()
        self.white_player = Player(white_name, Color.WHITE)
        self.black_player = Player(black_name, Color.BLACK)
        self.current_turn = Color.WHITE
        self.game_state = GameState.ACTIVE
        
        self.board.setup_initial_position()

    def make_move(self, from_pos: Position, to_pos: Position) -> bool:
        """Make a move from source to destination."""
        if self.game_state in [GameState.CHECKMATE, GameState.STALEMATE]:
            print("Game is over!")
            return False

        piece = self.board.get_piece(from_pos)

        if piece is None:
            print(f"No piece at {from_pos}")
            return False

        if piece.color != self.current_turn:
            print(f"It's {self.current_turn.value}'s turn!")
            return False

        valid_moves = piece.get_valid_moves(self.board)
        if to_pos not in valid_moves:
            print(f"Invalid move for {piece.__class__.__name__}")
            return False

        captured = self.board.move_piece(from_pos, to_pos)
        if captured:
            print(f"Captured {captured}")

        self.current_turn = self.current_turn.opposite()
        return True

    def get_valid_moves(self, pos: Position) -> List[Position]:
        """Get valid moves for piece at position."""
        piece = self.board.get_piece(pos)
        if piece is None:
            return []
        return piece.get_valid_moves(self.board)

    @property
    def current_player(self) -> Player:
        return self.white_player if self.current_turn == Color.WHITE else self.black_player

    def display_board(self):
        self.board.display()

    def resign(self):
        self.game_state = GameState.RESIGNED
        print(f"{self.current_player.name} resigned!")
        print(f"{self.current_turn.opposite().value} wins!")
