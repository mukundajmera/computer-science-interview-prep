from __future__ import annotations


class MyQueue:
    def __init__(self) -> None:
        self.stack: list[int] = []

    def push(self, x: int) -> None:
        temp: list[int] = []
        while self.stack:
            temp.append(self.stack.pop())
        self.stack.append(x)
        while temp:
            self.stack.append(temp.pop())

    def pop(self) -> int:
        return self.stack.pop()

    def peek(self) -> int:
        return self.stack[-1]

    def empty(self) -> bool:
        return not self.stack
