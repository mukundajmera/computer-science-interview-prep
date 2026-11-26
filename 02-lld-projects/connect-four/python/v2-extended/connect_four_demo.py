from board import Board
from connect_four_game import Game
from disc_color import DiscColor
from player import Player


if __name__ == "__main__":
    red = Player("Red", DiscColor.RED)
    yellow = Player("Yellow", DiscColor.YELLOW)
    game = Game(red, yellow, Board(6, 7))

    game.make_move(red, 0)
    game.make_move(yellow, 1)
    game.make_move(red, 0)

    print("History size:", len(game.get_move_history()))
    game.undo_last_move()
    print("History size after undo:", len(game.get_move_history()))
