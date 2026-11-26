from dataclasses import dataclass
from disc_color import DiscColor


@dataclass(frozen=True)
class Player:
    name: str
    color: DiscColor
