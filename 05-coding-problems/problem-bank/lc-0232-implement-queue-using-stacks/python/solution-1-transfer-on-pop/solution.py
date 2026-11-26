from __future__ import annotations


class MyQueue:
    def __init__(self) -> None:
        self.input_stack: list[int] = []
        self.output_stack: list[int] = []

    def push(self, x: int) -> None:
        self.input_stack.append(x)

    def pop(self) -> int:
        self._move_if_needed()
        return self.output_stack.pop()

    def peek(self) -> int:
        self._move_if_needed()
        return self.output_stack[-1]

    def empty(self) -> bool:
        return not self.input_stack and not self.output_stack

    def _move_if_needed(self) -> None:
        if self.output_stack:
            return
        while self.input_stack:
            self.output_stack.append(self.input_stack.pop())
