from typing import TypeVar, Generic, List, Optional
from actions import StateAction

C = TypeVar('C')

class State(Generic[C]):
    def __init__(self, name: str, is_terminal: bool):
        self._name = name
        self._is_terminal = is_terminal
        self._entry_actions: List[StateAction[C]] = []
        self._exit_actions: List[StateAction[C]] = []
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

    def add_entry_action(self, action: StateAction[C]) -> None:
        self._entry_actions.append(action)

    def add_exit_action(self, action: StateAction[C]) -> None:
        self._exit_actions.append(action)

    def on_entry(self, context: C) -> None:
        for action in self._entry_actions:
            action(context)

    def on_exit(self, context: C) -> None:
        for action in self._exit_actions:
            action(context)
