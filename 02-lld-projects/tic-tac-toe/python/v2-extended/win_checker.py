"""
WinChecker for Tic-Tac-Toe - v1 Basic
"""
from mark import Mark
from position import Position
from board import Board


class WinChecker:
    """Checks for win conditions on the board."""
    
    def check_win(self, board: Board, last_move: Position) -> bool:
        """
        Check if the last move resulted in a win.
        
        Args:
            board: The game board
            last_move: The last move made
            
        Returns:
            True if the player who made the move won
        """
        if last_move is None:
            return False
        
        mark = board.get_mark(last_move)
        if mark == Mark.EMPTY:
            return False
        
        row = last_move.row
        col = last_move.col
        size = board.size
        
        # Check row
        if self._check_row(board, row, mark):
            return True
        
        # Check column
        if self._check_column(board, col, mark):
            return True
        
        # Check main diagonal (if applicable)
        if row == col and self._check_main_diagonal(board, mark):
            return True
        
        # Check anti-diagonal (if applicable)
        if row + col == size - 1 and self._check_anti_diagonal(board, mark):
            return True
        
        return False
    
    def _check_row(self, board: Board, row: int, mark: Mark) -> bool:
        """Check if entire row has the same mark."""
        for col in range(board.size):
            if board.get_mark(Position(row, col)) != mark:
                return False
        return True
    
    def _check_column(self, board: Board, col: int, mark: Mark) -> bool:
        """Check if entire column has the same mark."""
        for row in range(board.size):
            if board.get_mark(Position(row, col)) != mark:
                return False
        return True
    
    def _check_main_diagonal(self, board: Board, mark: Mark) -> bool:
        """Check main diagonal (top-left to bottom-right)."""
        for i in range(board.size):
            if board.get_mark(Position(i, i)) != mark:
                return False
        return True
    
    def _check_anti_diagonal(self, board: Board, mark: Mark) -> bool:
        """Check anti-diagonal (top-right to bottom-left)."""
        size = board.size
        for i in range(size):
            if board.get_mark(Position(i, size - 1 - i)) != mark:
                return False
        return True
