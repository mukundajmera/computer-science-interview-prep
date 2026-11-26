import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v1-basic'))
for module_name in ["connect_four_game", "disc_color", "game_state", "player", "board"]:
    sys.modules.pop(module_name, None)
# Avoid cross-version module cache collisions when running full test suite.
for module_name in ["connect_four_game", "disc_color", "game_state", "player", "board", "move"]:
    sys.modules.pop(module_name, None)

from connect_four_game import Game
from disc_color import DiscColor
from game_state import GameState
from player import Player


class ConnectFourV1Test(unittest.TestCase):
    def setUp(self):
        self.red = Player("Red", DiscColor.RED)
        self.yellow = Player("Yellow", DiscColor.YELLOW)
        self.game = Game(self.red, self.yellow)

    def test_invalid_turn_and_column(self):
        self.assertFalse(self.game.make_move(self.red, -1))
        self.assertFalse(self.game.make_move(self.yellow, 0))

    def test_vertical_win(self):
        self.assertTrue(self.game.make_move(self.red, 0))
        self.assertTrue(self.game.make_move(self.yellow, 1))
        self.assertTrue(self.game.make_move(self.red, 0))
        self.assertTrue(self.game.make_move(self.yellow, 1))
        self.assertTrue(self.game.make_move(self.red, 0))
        self.assertTrue(self.game.make_move(self.yellow, 1))
        self.assertTrue(self.game.make_move(self.red, 0))

        self.assertEqual(GameState.RED_WON, self.game.get_game_state())
        self.assertEqual(self.red, self.game.get_winner())


if __name__ == '__main__':
    unittest.main()
