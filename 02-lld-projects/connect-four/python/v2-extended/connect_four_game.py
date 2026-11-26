from typing import List

from board import Board
from disc_color import DiscColor
from game_state import GameState
from move import Move
from player import Player


class Game:
    def __init__(self, player1: Player, player2: Player, board: Board = None):
        self.board = board or Board()
        self.player1 = player1
        self.player2 = player2
        self.current_player = player1
        self.state = GameState.IN_PROGRESS
        self.winner = None
        self.history: List[Move] = []

    def make_move(self, player: Player, column: int) -> bool:
        if self.state.is_terminal():
            return False
        if player is None or player != self.current_player:
            return False
        if not self.board.can_place(column):
            return False

        row = self.board.place_disc(column, player.color)
        if row < 0:
            return False

        self.history.append(Move(player, row, column))

        if self.board.check_win(row, column, player.color):
            self.winner = player
            self.state = GameState.RED_WON if player.color == DiscColor.RED else GameState.YELLOW_WON
            return True

        if self.board.is_full():
            self.state = GameState.DRAW
            return True

        self.current_player = self.player2 if self.current_player == self.player1 else self.player1
        return True

    def undo_last_move(self) -> bool:
        if not self.history:
            return False
        move = self.history.pop()
        self.board.clear_cell(move.row, move.column)
        self.current_player = move.player
        self.winner = None
        self.state = GameState.IN_PROGRESS
        return True

    def get_move_history(self) -> List[Move]:
        return list(self.history)

    def get_current_player(self) -> Player:
        return self.current_player

    def get_game_state(self) -> GameState:
        return self.state

    def get_winner(self):
        return self.winner
