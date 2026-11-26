from board import Board
from bot_move_strategy import BotMoveStrategy
from disc_color import DiscColor


class HeuristicBotMoveStrategy(BotMoveStrategy):
    def select_column(self, board: Board, bot_color: DiscColor) -> int:
        opponent = bot_color.opposite()

        for col in range(board.cols):
            if self._is_winning_move(board, col, bot_color):
                return col

        for col in range(board.cols):
            if self._is_winning_move(board, col, opponent):
                return col

        for col in range(board.cols):
            if board.can_place(col):
                return col

        return -1

    def _is_winning_move(self, board: Board, col: int, color: DiscColor) -> bool:
        if not board.can_place(col):
            return False
        row = board.place_disc(col, color)
        if row < 0:
            return False
        result = board.check_win(row, col, color)
        board.clear_cell(row, col)
        return result
