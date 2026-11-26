from enum import Enum


class DiscColor(Enum):
    RED = "RED"
    YELLOW = "YELLOW"
    EMPTY = "EMPTY"

    def opposite(self) -> "DiscColor":
        if self == DiscColor.RED:
            return DiscColor.YELLOW
        if self == DiscColor.YELLOW:
            return DiscColor.RED
        return DiscColor.EMPTY
