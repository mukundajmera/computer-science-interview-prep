from typing import TypeVar, Generic, List
from actions import StateAction
C = TypeVar('C')
P = TypeVar('P')

class State(Generic[C, P]):
    def __init__(self, name: str, is_terminal: bool):
        self._name = name
        self._is_terminal = is_terminal
        self._entry_actions: List[StateAction[C, P]] = []
        self._exit_actions: List[StateAction[C, P]] = []
        self._notifications_enabled: bool = True

    @property
    def name(self) -> str:
        return self._name

    @property
    def is_terminal(self) -> bool:
        return self._is_terminal

    @property
    def notifications_enabled(self) -> bool:
        return self._notifications_enabled

    def set_notifications_enabled(self, enabled: bool) -> None:
        self._notifications_enabled = enabled

    def add_entry_action(self, action: 'StateAction[C, P]') -> None:
        self._entry_actions.append(action)

    def add_exit_action(self, action: 'StateAction[C, P]') -> None:
        self._exit_actions.append(action)

    def on_entry(self, context: C, payload: P = None) -> None:
        for action in self._entry_actions:
            action(context, payload)

    def on_exit(self, context: C, payload: P = None) -> None:
        for action in self._exit_actions:
            action(context, payload)
