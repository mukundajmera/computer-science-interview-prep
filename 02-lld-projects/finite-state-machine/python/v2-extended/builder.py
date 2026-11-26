from typing import TypeVar, Generic, Dict, List, Optional
from state import State
from transition import Transition
from actions import StateAction
from guards import TransitionGuard
from state_machine import StateMachine
from listeners import StateChangeListener
C = TypeVar('C')
P = TypeVar('P')

class StateMachineBuilder(Generic[C, P]):
    def __init__(self):
        self._states: Dict[str, State[C, P]] = {}
        self._transitions: Dict[str, List[Transition[C, P]]] = {}
        self._initial_state: Optional[str] = None
        self._listeners: List[StateChangeListener] = []
        self._global_notifications_enabled: bool = True

    def with_state(self, name: str, is_terminal: bool = False) -> 'StateMachineBuilder[C, P]':
        if name not in self._states:
            self._states[name] = State(name, is_terminal)
        return self

    def with_initial_state(self, name: str) -> 'StateMachineBuilder[C, P]':
        self.with_state(name, False)
        self._initial_state = name
        return self

    def with_entry_action(self, state_name: str, action: StateAction[C, P]) -> 'StateMachineBuilder[C, P]':
        state = self._states.get(state_name)
        if state:
            state.add_entry_action(action)
        else:
            raise ValueError(f"State {state_name} does not exist.")
        return self

    def with_exit_action(self, state_name: str, action: StateAction[C, P]) -> 'StateMachineBuilder[C, P]':
        state = self._states.get(state_name)
        if state:
            state.add_exit_action(action)
        else:
            raise ValueError(f"State {state_name} does not exist.")
        return self

    def with_transition(self) -> 'TransitionBuilder[C]':
        return TransitionBuilder(self)

    def with_global_listener(self, listener: StateChangeListener) -> 'StateMachineBuilder[C, P]':
        self._listeners.append(listener)
        return self

    def set_notifications_enabled(self, enabled: bool) -> 'StateMachineBuilder[C, P]':
        self._global_notifications_enabled = enabled
        return self
        
    def set_state_notifications_enabled(self, state_name: str, enabled: bool) -> 'StateMachineBuilder[C, P]':
        state = self._states.get(state_name)
        if state:
            state.set_notifications_enabled(enabled)
        else:
            raise ValueError(f"State {state_name} does not exist.")
        return self

    def build(self) -> StateMachine[C, P]:
        if not self._initial_state or self._initial_state not in self._states:
            raise ValueError("Initial state must be set and valid.")
        return StateMachine(self._states, self._transitions, self._initial_state, self._listeners, self._global_notifications_enabled)


class TransitionBuilder(Generic[C, P]):
    def __init__(self, builder: StateMachineBuilder[C, P]):
        self._builder = builder
        self._from_state: Optional[str] = None
        self._to_state: Optional[str] = None
        self._event: Optional[str] = None
        self._guard: Optional[TransitionGuard[C, P]] = None
        self._actions: List[StateAction[C, P]] = []

    def from_state(self, state: str) -> 'TransitionBuilder[C]':
        self._from_state = state
        return self

    def to_state(self, state: str) -> 'TransitionBuilder[C]':
        self._to_state = state
        return self

    def on_event(self, event: str) -> 'TransitionBuilder[C]':
        self._event = event
        return self

    def with_guard(self, guard: TransitionGuard[C, P]) -> 'TransitionBuilder[C]':
        self._guard = guard
        return self

    def with_action(self, action: StateAction[C, P]) -> 'TransitionBuilder[C]':
        self._actions.append(action)
        return self

    def create(self) -> StateMachineBuilder[C, P]:
        if not self._from_state or not self._to_state or not self._event:
            raise ValueError("Transition must have from_state, to_state, and event.")
        if self._from_state not in self._builder._states or self._to_state not in self._builder._states:
            raise ValueError("Both from_state and to_state must exist in the StateMachine.")
        
        transition = Transition(self._from_state, self._to_state, self._event, self._guard)
        for action in self._actions:
            transition.add_transition_action(action)
            
        if self._from_state not in self._builder._transitions:
            self._builder._transitions[self._from_state] = []
        self._builder._transitions[self._from_state].append(transition)
        
        return self._builder
