"""
Chess Game - V2 Extended

Move class with command pattern for undo support.
See v1-basic for Position, Piece, Board classes.
"""
from enum import Enum
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from position import Position
    from piece import Piece
    from board import Board


class MoveType(Enum):
    NORMAL = "NORMAL"
    CAPTURE = "CAPTURE"
    CASTLING_KINGSIDE = "CASTLING_KINGSIDE"
    CASTLING_QUEENSIDE = "CASTLING_QUEENSIDE"
    EN_PASSANT = "EN_PASSANT"
    PROMOTION = "PROMOTION"


class Move:
    """Represents a chess move with undo capability."""
    
    def __init__(
        self,
        piece: 'Piece',
        from_pos: 'Position',
        to_pos: 'Position',
        captured_piece: Optional['Piece'],
        move_type: MoveType,
        is_first_move: bool
    ):
        self.piece = piece
        self.from_pos = from_pos
        self.to_pos = to_pos
        self.captured_piece = captured_piece
        self.move_type = move_type
        self.is_first_move = is_first_move

    def execute(self, board: 'Board'):
        """Execute the move on the board."""
        board.move_piece(self.from_pos, self.to_pos)

    def undo(self, board: 'Board'):
        """Undo the move on the board."""
        board.move_piece(self.to_pos, self.from_pos)
        
        if self.captured_piece:
            board.set_piece(self.to_pos, self.captured_piece)
        
        if self.is_first_move:
            self.piece.has_moved = False

    def to_algebraic(self) -> str:
        """Convert to algebraic notation."""
        from piece import Pawn
        
        if self.move_type == MoveType.CASTLING_KINGSIDE:
            return "O-O"
        elif self.move_type == MoveType.CASTLING_QUEENSIDE:
            return "O-O-O"
        
        notation = ""
        
        # Piece symbol (except pawn)
        if not isinstance(self.piece, Pawn):
            notation += self.piece.get_symbol().upper()
        
        # Capture notation
        if self.captured_piece:
            if isinstance(self.piece, Pawn):
                notation += chr(ord('a') + self.from_pos.col)
            notation += "x"
        
        notation += str(self.to_pos)
        
        return notation

    def __str__(self) -> str:
        return self.to_algebraic()
