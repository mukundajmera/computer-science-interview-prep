from typing import TypeVar, Generic, Callable

C = TypeVar('C')

StateAction = Callable[[C], None]
