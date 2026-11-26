from typing import TypeVar, Generic, List, Optional
from actions import StateAction
from guards import TransitionGuard

C = TypeVar('C')

class Transition(Generic[C]):
    def __init__(self, from_state: str, to_state: str, event: str, guard: Optional[TransitionGuard[C]] = None):
        self._from_state = from_state
        self._to_state = to_state
        self._event = event
        self._guard = guard
        self._transition_actions: List[StateAction[C]] = []

    @property
    def from_state(self) -> str:
        return self._from_state

    @property
    def to_state(self) -> str:
        return self._to_state

    @property
    def event(self) -> str:
        return self._event

    def add_transition_action(self, action: StateAction[C]) -> None:
        self._transition_actions.append(action)

    def evaluate_guard(self, context: C) -> bool:
        if self._guard is None:
            return True
        return self._guard(context)

    def execute_actions(self, context: C) -> None:
        for action in self._transition_actions:
            action(context)
