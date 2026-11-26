from typing import TypeVar, Protocol

C = TypeVar('C')
P = TypeVar('P')

class TransitionGuard(Protocol[C, P]):
    def __call__(self, context: C, payload: P) -> bool: ...
