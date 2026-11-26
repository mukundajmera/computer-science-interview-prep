import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v2-extended'))
# Avoid cross-version module cache collisions when running full test suite.
for module_name in ["connect_four_game", "disc_color", "game_state", "player", "board", "move"]:
    sys.modules.pop(module_name, None)

from board import Board
from connect_four_game import Game
from disc_color import DiscColor
from game_state import GameState
from player import Player


class ConnectFourV2Test(unittest.TestCase):
    def test_undo_restores_state(self):
        red = Player("Red", DiscColor.RED)
        yellow = Player("Yellow", DiscColor.YELLOW)
        game = Game(red, yellow, Board(6, 7))

        self.assertTrue(game.make_move(red, 2))
        self.assertTrue(game.make_move(yellow, 3))
        self.assertEqual(2, len(game.get_move_history()))

        self.assertTrue(game.undo_last_move())
        self.assertEqual(yellow, game.get_current_player())
        self.assertEqual(GameState.IN_PROGRESS, game.get_game_state())


if __name__ == '__main__':
    unittest.main()
