from connect_four_game import Game
from disc_color import DiscColor
from player import Player


if __name__ == "__main__":
    red = Player("Red", DiscColor.RED)
    yellow = Player("Yellow", DiscColor.YELLOW)
    game = Game(red, yellow)

    game.make_move(red, 0)
    game.make_move(yellow, 1)
    game.make_move(red, 0)
    game.make_move(yellow, 1)
    game.make_move(red, 0)
    game.make_move(yellow, 1)
    game.make_move(red, 0)

    print("State:", game.get_game_state().value)
    print("Winner:", game.get_winner().name if game.get_winner() else "None")
