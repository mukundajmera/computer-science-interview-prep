from dataclasses import dataclass
from player import Player


@dataclass(frozen=True)
class Move:
    player: Player
    row: int
    column: int
