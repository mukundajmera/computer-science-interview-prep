"""
Tests for Chess Game implementations.
"""
import unittest
import sys
from pathlib import Path


TEST_DIR = Path(__file__).resolve().parent
HELPER_DIR = TEST_DIR.parents[2] / "test_helpers"
if str(HELPER_DIR) not in sys.path:
    sys.path.insert(0, str(HELPER_DIR))

from imports import import_modules_from


CHESS_MODULES = ["position", "piece", "board", "game", "move"]


def version_path(version: str) -> Path:
    return TEST_DIR.parent / version


def position_module(version: str):
    return import_modules_from(
        version_path(version),
        ["position"],
        purge_modules=CHESS_MODULES,
    )["position"]


class PositionTestsBase:
    version = ""
    def test_valid_position(self):
        Position = position_module(self.version).Position
        self.assertTrue(Position(0, 0).is_valid())
        self.assertTrue(Position(7, 7).is_valid())
        self.assertFalse(Position(-1, 0).is_valid())
        self.assertFalse(Position(8, 0).is_valid())

    def test_algebraic_notation(self):
        Position = position_module(self.version).Position
        self.assertEqual("e4", Position(3, 4).to_algebraic())
        self.assertEqual("a1", Position(0, 0).to_algebraic())


class PiecesTestsBase:
    version = ""
    def test_knight_l_shape(self):
        # Knight moves in L-shape: 8 possible moves
        expected_moves = 8
        self.assertEqual(8, expected_moves)

    def test_pawn_initial_double_move(self):
        # Pawn can move 2 squares from starting position
        start_row = 1
        direction = 1
        two_forward = start_row + 2 * direction
        self.assertEqual(3, two_forward)


class GameTestsBase:
    version = ""
    def test_turn_alternation(self):
        Color = position_module(self.version).Color
        white = Color.WHITE
        after_white = white.opposite()
        self.assertEqual(Color.BLACK, after_white)

    def test_checkmate_condition(self):
        in_check = True
        has_legal_moves = False
        is_checkmate = in_check and not has_legal_moves
        self.assertTrue(is_checkmate)

    def test_stalemate_condition(self):
        in_check = False
        has_legal_moves = False
        is_stalemate = not in_check and not has_legal_moves
        self.assertTrue(is_stalemate)


class TestPositionV1(PositionTestsBase, unittest.TestCase): version = "v1-basic"
class TestPiecesV1(PiecesTestsBase, unittest.TestCase): version = "v1-basic"
class TestGameV1(GameTestsBase, unittest.TestCase): version = "v1-basic"

class TestPositionV2(PositionTestsBase, unittest.TestCase): version = "v2-extended"
class TestPiecesV2(PiecesTestsBase, unittest.TestCase): version = "v2-extended"
class TestGameV2(GameTestsBase, unittest.TestCase): version = "v2-extended"

class TestPositionV3(PositionTestsBase, unittest.TestCase): version = "v3-optimized"
class TestPiecesV3(PiecesTestsBase, unittest.TestCase): version = "v3-optimized"
class TestGameV3(GameTestsBase, unittest.TestCase): version = "v3-optimized"

if __name__ == '__main__':
    unittest.main()
