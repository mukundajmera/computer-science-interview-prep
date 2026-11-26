"""
Chess Game - V1 Basic

Chess board representation.
"""
from typing import Optional, List
from position import Position, Color
from piece import Piece, King, Queen, Rook, Bishop, Knight, Pawn


class Board:
    """Chess board - 8x8 grid of squares."""
    
    def __init__(self):
        self.squares: List[List[Optional[Piece]]] = [[None] * 8 for _ in range(8)]

    def get_piece(self, pos: Position) -> Optional[Piece]:
        if not pos.is_valid():
            return None
        return self.squares[pos.row][pos.col]

    def set_piece(self, pos: Position, piece: Optional[Piece]):
        if pos.is_valid():
            self.squares[pos.row][pos.col] = piece
            if piece:
                piece.position = pos

    def remove_piece(self, pos: Position) -> Optional[Piece]:
        piece = self.get_piece(pos)
        if piece:
            self.squares[pos.row][pos.col] = None
        return piece

    def move_piece(self, from_pos: Position, to_pos: Position) -> Optional[Piece]:
        piece = self.remove_piece(from_pos)
        captured = self.remove_piece(to_pos)
        self.set_piece(to_pos, piece)
        if piece:
            piece.set_position(to_pos)
        return captured

    def find_king(self, color: Color) -> Optional[Position]:
        for row in range(8):
            for col in range(8):
                piece = self.squares[row][col]
                if isinstance(piece, King) and piece.color == color:
                    return Position(row, col)
        return None

    def setup_initial_position(self):
        """Set up the initial chess position."""
        # Clear board
        for row in range(8):
            for col in range(8):
                self.squares[row][col] = None

        # White pieces
        self._setup_back_rank(0, Color.WHITE)
        for col in range(8):
            self.set_piece(Position(1, col), Pawn(Color.WHITE, Position(1, col)))

        # Black pieces
        self._setup_back_rank(7, Color.BLACK)
        for col in range(8):
            self.set_piece(Position(6, col), Pawn(Color.BLACK, Position(6, col)))

    def _setup_back_rank(self, row: int, color: Color):
        pieces = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for col, piece_class in enumerate(pieces):
            pos = Position(row, col)
            self.set_piece(pos, piece_class(color, pos))

    def display(self):
        print("  a b c d e f g h")
        print("  ----------------")
        for row in range(7, -1, -1):
            print(f"{row + 1}|", end="")
            for col in range(8):
                piece = self.squares[row][col]
                symbol = piece.get_symbol() if piece else '.'
                print(f"{symbol} ", end="")
            print(f"|{row + 1}")
        print("  ----------------")
        print("  a b c d e f g h")
