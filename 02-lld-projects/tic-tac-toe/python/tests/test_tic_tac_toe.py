"""
Tests for Tic-Tac-Toe Python implementations.
"""
import unittest
import sys
import os

# Add v1-basic to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v1-basic'))

from mark import Mark
from position import Position
from game_state import GameState
from board import Board
from win_checker import WinChecker


class TestBoard(unittest.TestCase):
    def setUp(self):
        self.board = Board(3)

    def test_initialization(self):
        self.assertEqual(9, self.board.empty_cells)
        for i in range(3):
            for j in range(3):
                self.assertEqual(Mark.EMPTY, self.board.get_mark(Position(i, j)))

    def test_place_mark(self):
        pos = Position(0, 0)
        self.assertTrue(self.board.place_mark(pos, Mark.X))
        self.assertEqual(Mark.X, self.board.get_mark(pos))
        self.assertEqual(8, self.board.empty_cells)

    def test_place_mark_on_occupied(self):
        pos = Position(0, 0)
        self.board.place_mark(pos, Mark.X)
        self.assertFalse(self.board.place_mark(pos, Mark.O))
        self.assertEqual(Mark.X, self.board.get_mark(pos))

    def test_remove_mark(self):
        pos = Position(1, 1)
        self.board.place_mark(pos, Mark.X)
        self.assertEqual(8, self.board.empty_cells)
        self.board.remove_mark(pos)
        self.assertEqual(Mark.EMPTY, self.board.get_mark(pos))
        self.assertEqual(9, self.board.empty_cells)

    def test_is_full(self):
        self.assertFalse(self.board.is_full())
        for i in range(3):
            for j in range(3):
                self.board.place_mark(Position(i, j), Mark.X)
        self.assertTrue(self.board.is_full())


class TestPosition(unittest.TestCase):
    def test_validity(self):
        self.assertTrue(Position(0, 0).is_valid(3))
        self.assertTrue(Position(2, 2).is_valid(3))
        self.assertFalse(Position(-1, 0).is_valid(3))
        self.assertFalse(Position(3, 0).is_valid(3))

    def test_equality(self):
        p1 = Position(1, 2)
        p2 = Position(1, 2)
        p3 = Position(2, 1)
        self.assertEqual(p1, p2)
        self.assertNotEqual(p1, p3)


class TestWinChecker(unittest.TestCase):
    def setUp(self):
        self.board = Board(3)
        self.checker = WinChecker()

    def test_row_win(self):
        self.board.place_mark(Position(0, 0), Mark.X)
        self.board.place_mark(Position(0, 1), Mark.X)
        win_pos = Position(0, 2)
        self.board.place_mark(win_pos, Mark.X)
        self.assertTrue(self.checker.check_win(self.board, win_pos))

    def test_column_win(self):
        self.board.place_mark(Position(0, 1), Mark.O)
        self.board.place_mark(Position(1, 1), Mark.O)
        win_pos = Position(2, 1)
        self.board.place_mark(win_pos, Mark.O)
        self.assertTrue(self.checker.check_win(self.board, win_pos))

    def test_diagonal_win(self):
        self.board.place_mark(Position(0, 0), Mark.X)
        self.board.place_mark(Position(1, 1), Mark.X)
        win_pos = Position(2, 2)
        self.board.place_mark(win_pos, Mark.X)
        self.assertTrue(self.checker.check_win(self.board, win_pos))

    def test_anti_diagonal_win(self):
        self.board.place_mark(Position(0, 2), Mark.O)
        self.board.place_mark(Position(1, 1), Mark.O)
        win_pos = Position(2, 0)
        self.board.place_mark(win_pos, Mark.O)
        self.assertTrue(self.checker.check_win(self.board, win_pos))

    def test_no_win(self):
        self.board.place_mark(Position(0, 0), Mark.X)
        self.board.place_mark(Position(0, 1), Mark.O)
        last_pos = Position(0, 2)
        self.board.place_mark(last_pos, Mark.X)
        self.assertFalse(self.checker.check_win(self.board, last_pos))


class TestGameState(unittest.TestCase):
    def test_is_game_over(self):
        self.assertFalse(GameState.NOT_STARTED.is_game_over())
        self.assertFalse(GameState.IN_PROGRESS.is_game_over())
        self.assertTrue(GameState.X_WON.is_game_over())
        self.assertTrue(GameState.O_WON.is_game_over())
        self.assertTrue(GameState.DRAW.is_game_over())


if __name__ == '__main__':
    unittest.main()
