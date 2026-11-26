import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v3-optimized'))
for module_name in [
    "connect_four_game",
    "disc_color",
    "game_state",
    "player",
    "board",
    "move",
    "bot_move_strategy",
    "heuristic_bot_move_strategy",
    "game_session",
]:
    sys.modules.pop(module_name, None)
# Avoid cross-version module cache collisions when running full test suite.
for module_name in [
    "connect_four_game",
    "disc_color",
    "game_state",
    "player",
    "board",
    "move",
    "bot_move_strategy",
    "heuristic_bot_move_strategy",
    "game_session",
]:
    sys.modules.pop(module_name, None)

from connect_four_game import Game
from disc_color import DiscColor
from game_session import GameSession
from player import Player


class ConnectFourV3Test(unittest.TestCase):
    def test_bot_suggestion_is_legal(self):
        red = Player("Red", DiscColor.RED)
        yellow = Player("Yellow", DiscColor.YELLOW)
        game = Game(red, yellow)

        col = game.suggest_bot_move()
        self.assertGreaterEqual(col, 0)
        self.assertTrue(game.board.can_place(col))

    def test_session_wrapper(self):
        red = Player("Red", DiscColor.RED)
        yellow = Player("Yellow", DiscColor.YELLOW)
        game = Game(red, yellow)
        session = GameSession("s-1", game)

        self.assertEqual("s-1", session.session_id)
        self.assertIs(game, session.game)


if __name__ == '__main__':
    unittest.main()
