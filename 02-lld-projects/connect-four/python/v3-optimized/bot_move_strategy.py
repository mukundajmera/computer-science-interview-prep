from abc import ABC, abstractmethod

from board import Board
from disc_color import DiscColor


class BotMoveStrategy(ABC):
    @abstractmethod
    def select_column(self, board: Board, bot_color: DiscColor) -> int:
        raise NotImplementedError
