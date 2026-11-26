from typing import TypeVar, Callable

C = TypeVar('C')

TransitionGuard = Callable[[C], bool]
