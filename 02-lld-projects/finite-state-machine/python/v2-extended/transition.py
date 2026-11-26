from typing import TypeVar, Generic, List, Optional

C = TypeVar('C')
P = TypeVar('P')
from guards import TransitionGuard


class Transition(Generic[C, P]):
    def __init__(self, from_state: str, to_state: str, event: str, guard: Optional[TransitionGuard[C, P]] = None):
        self._from_state = from_state
        self._to_state = to_state
        self._event = event
        self._guard = guard
        self._transition_actions: List[StateAction[C, P]] = []

    @property
    def from_state(self) -> str:
        return self._from_state

    @property
    def to_state(self) -> str:
        return self._to_state

    @property
    def event(self) -> str:
        return self._event

    def add_transition_action(self, action: 'StateAction[C, P]') -> None:
        self._transition_actions.append(action)

    def evaluate_guard(self, context: C, payload: P = None) -> bool:
        if self._guard is None:
            return True
        return self._guard(context, payload)

    def execute_actions(self, context: C, payload: P = None) -> None:
        for action in self._transition_actions:
            action(context, payload)
