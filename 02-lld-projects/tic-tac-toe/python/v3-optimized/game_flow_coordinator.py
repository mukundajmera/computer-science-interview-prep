"""Interview-focused coordinator contracts for tic-tac-toe game flow."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class TurnPolicy(Protocol):
    """Computes next turn from current game context."""

    def next_turn(self, game_state: object) -> object:
        ...


class WinResolutionPolicy(Protocol):
    """Determines whether a move creates a winning terminal state."""

    def is_winning_move(self, game_state: object, position: object) -> bool:
        ...


@dataclass(frozen=True)
class GameStateTransition:
    """Lightweight transition object used in interview walkthroughs."""

    next_turn: object
    has_winner: bool


class GameFlowCoordinator:
    """Coordinates turn and win-resolution policies."""

    def __init__(self, turn_policy: TurnPolicy, win_resolution_policy: WinResolutionPolicy) -> None:
        self._turn_policy = turn_policy
        self._win_resolution_policy = win_resolution_policy

    def on_move(self, game_state: object, position: object) -> GameStateTransition:
        return GameStateTransition(
            next_turn=self._turn_policy.next_turn(game_state),
            has_winner=self._win_resolution_policy.is_winning_move(game_state, position),
        )
