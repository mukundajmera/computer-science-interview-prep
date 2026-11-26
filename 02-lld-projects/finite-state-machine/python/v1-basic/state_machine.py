from typing import TypeVar, Generic, Dict, List, Optional
from state import State
from transition import Transition
from listeners import StateChangeListener

C = TypeVar('C')

class StateMachine(Generic[C]):
    def __init__(self, 
                 states: Dict[str, State[C]], 
                 transitions: Dict[str, List[Transition[C]]], 
                 initial_state: str,
                 global_listeners: List[StateChangeListener],
                 global_notifications_enabled: bool):
        self._states = states
        self._transitions = transitions
        self._initial_state = initial_state
        self._global_listeners = global_listeners
        self._global_notifications_enabled = global_notifications_enabled
        self._current_state: Optional[State[C]] = states.get(initial_state)

    def start(self, context: C) -> None:
        if self._current_state is not None:
            self._current_state.on_entry(context)

    def fire(self, event: str, context: C) -> bool:
        if self._current_state is None or self._current_state.is_terminal:
            return False

        available_transitions = self._transitions.get(self._current_state.name, [])
        for transition in available_transitions:
            if transition.event == event and transition.evaluate_guard(context):
                next_state = self._states.get(transition.to_state)
                if next_state:
                    # Execute exit actions
                    self._current_state.on_exit(context)
                    
                    # Execute transition actions
                    transition.execute_actions(context)
                    
                    # Notify listeners
                    if self._global_notifications_enabled and self._current_state.notifications_enabled:
                        for listener in self._global_listeners:
                            listener(self._current_state.name, next_state.name, event)
                            
                    # Update state
                    self._current_state = next_state
                    
                    # Execute entry actions
                    self._current_state.on_entry(context)
                    return True
        return False

    @property
    def current_state(self) -> Optional[str]:
        return self._current_state.name if self._current_state else None

    @property
    def is_terminal(self) -> bool:
        return self._current_state.is_terminal if self._current_state else False
