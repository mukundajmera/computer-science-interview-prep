"""
Chess Game - V1 Basic

Chess pieces with movement rules.
"""
from abc import ABC, abstractmethod
from typing import List, TYPE_CHECKING
from position import Position, Color

if TYPE_CHECKING:
    from board import Board


class Piece(ABC):
    """Abstract base class for all chess pieces."""
    
    def __init__(self, color: Color, position: Position):
        self.color = color
        self.position = position
        self.has_moved = False

    def set_position(self, position: Position):
        self.position = position
        self.has_moved = True

    @abstractmethod
    def get_valid_moves(self, board: 'Board') -> List[Position]:
        """Get all valid move destinations."""
        pass

    @abstractmethod
    def get_symbol(self) -> str:
        """Get the symbol for display."""
        pass

    def can_move_to(self, board: 'Board', target: Position) -> bool:
        return target in self.get_valid_moves(board)

    def is_valid_target(self, board: 'Board', target: Position) -> bool:
        """Check if target is valid (empty or opponent's piece)."""
        if not target.is_valid():
            return False
        piece_at_target = board.get_piece(target)
        return piece_at_target is None or piece_at_target.color != self.color

    def __str__(self) -> str:
        return f"{self.color.value}{self.__class__.__name__}@{self.position}"


class King(Piece):
    DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def get_valid_moves(self, board: 'Board') -> List[Position]:
        moves = []
        for dr, dc in self.DIRECTIONS:
            target = Position(self.position.row + dr, self.position.col + dc)
            if self.is_valid_target(board, target):
                moves.append(target)
        return moves

    def get_symbol(self) -> str:
        return 'K' if self.color == Color.WHITE else 'k'


class Queen(Piece):
    DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

    def get_valid_moves(self, board: 'Board') -> List[Position]:
        moves = []
        for dr, dc in self.DIRECTIONS:
            self._add_moves_in_direction(board, moves, dr, dc)
        return moves

    def _add_moves_in_direction(self, board: 'Board', moves: List[Position], dr: int, dc: int):
        row, col = self.position.row + dr, self.position.col + dc
        while 0 <= row < 8 and 0 <= col < 8:
            target = Position(row, col)
            piece = board.get_piece(target)
            if piece is None:
                moves.append(target)
            else:
                if piece.color != self.color:
                    moves.append(target)
                break
            row, col = row + dr, col + dc

    def get_symbol(self) -> str:
        return 'Q' if self.color == Color.WHITE else 'q'


class Rook(Piece):
    DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def get_valid_moves(self, board: 'Board') -> List[Position]:
        moves = []
        for dr, dc in self.DIRECTIONS:
            self._add_moves_in_direction(board, moves, dr, dc)
        return moves

    def _add_moves_in_direction(self, board: 'Board', moves: List[Position], dr: int, dc: int):
        row, col = self.position.row + dr, self.position.col + dc
        while 0 <= row < 8 and 0 <= col < 8:
            target = Position(row, col)
            piece = board.get_piece(target)
            if piece is None:
                moves.append(target)
            else:
                if piece.color != self.color:
                    moves.append(target)
                break
            row, col = row + dr, col + dc

    def get_symbol(self) -> str:
        return 'R' if self.color == Color.WHITE else 'r'


class Bishop(Piece):
    DIRECTIONS = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

    def get_valid_moves(self, board: 'Board') -> List[Position]:
        moves = []
        for dr, dc in self.DIRECTIONS:
            self._add_moves_in_direction(board, moves, dr, dc)
        return moves

    def _add_moves_in_direction(self, board: 'Board', moves: List[Position], dr: int, dc: int):
        row, col = self.position.row + dr, self.position.col + dc
        while 0 <= row < 8 and 0 <= col < 8:
            target = Position(row, col)
            piece = board.get_piece(target)
            if piece is None:
                moves.append(target)
            else:
                if piece.color != self.color:
                    moves.append(target)
                break
            row, col = row + dr, col + dc

    def get_symbol(self) -> str:
        return 'B' if self.color == Color.WHITE else 'b'


class Knight(Piece):
    MOVES = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]

    def get_valid_moves(self, board: 'Board') -> List[Position]:
        moves = []
        for dr, dc in self.MOVES:
            target = Position(self.position.row + dr, self.position.col + dc)
            if self.is_valid_target(board, target):
                moves.append(target)
        return moves

    def get_symbol(self) -> str:
        return 'N' if self.color == Color.WHITE else 'n'


class Pawn(Piece):
    def get_valid_moves(self, board: 'Board') -> List[Position]:
        moves = []
        direction = 1 if self.color == Color.WHITE else -1
        start_row = 1 if self.color == Color.WHITE else 6

        # Forward move
        one_forward = Position(self.position.row + direction, self.position.col)
        if one_forward.is_valid() and board.get_piece(one_forward) is None:
            moves.append(one_forward)
            
            # Double move from starting position
            if self.position.row == start_row:
                two_forward = Position(self.position.row + 2 * direction, self.position.col)
                if board.get_piece(two_forward) is None:
                    moves.append(two_forward)

        # Diagonal captures
        for col_offset in [-1, 1]:
            capture_pos = Position(self.position.row + direction, self.position.col + col_offset)
            if capture_pos.is_valid():
                target_piece = board.get_piece(capture_pos)
                if target_piece and target_piece.color != self.color:
                    moves.append(capture_pos)

        return moves

    def get_symbol(self) -> str:
        return 'P' if self.color == Color.WHITE else 'p'
