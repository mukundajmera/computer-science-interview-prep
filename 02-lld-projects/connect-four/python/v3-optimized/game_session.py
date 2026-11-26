from dataclasses import dataclass

from connect_four_game import Game


@dataclass(frozen=True)
class GameSession:
    session_id: str
    game: Game
