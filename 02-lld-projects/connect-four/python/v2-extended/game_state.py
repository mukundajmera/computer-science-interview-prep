from enum import Enum


class GameState(Enum):
    IN_PROGRESS = "IN_PROGRESS"
    RED_WON = "RED_WON"
    YELLOW_WON = "YELLOW_WON"
    DRAW = "DRAW"

    def is_terminal(self) -> bool:
        return self in {GameState.RED_WON, GameState.YELLOW_WON, GameState.DRAW}
