from connect_four_game import Game
from disc_color import DiscColor
from game_session import GameSession
from player import Player


if __name__ == "__main__":
    red = Player("Red", DiscColor.RED)
    yellow = Player("Yellow", DiscColor.YELLOW)
    game = Game(red, yellow)
    session = GameSession("session-1", game)

    print("Suggested column:", session.game.suggest_bot_move())
