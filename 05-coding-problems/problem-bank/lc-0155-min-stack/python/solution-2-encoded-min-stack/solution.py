from __future__ import annotations


class MinStack:
    def __init__(self) -> None:
        self.values: list[int] = []
        self.minimum = 0

    def push(self, val: int) -> None:
        if not self.values:
            self.values.append(val)
            self.minimum = val
        elif val < self.minimum:
            self.values.append(2 * val - self.minimum)
            self.minimum = val
        else:
            self.values.append(val)

    def pop(self) -> None:
        removed = self.values.pop()
        if removed < self.minimum:
            self.minimum = 2 * self.minimum - removed

    def top(self) -> int:
        value = self.values[-1]
        if value < self.minimum:
            return self.minimum
        return value

    def getMin(self) -> int:
        return self.minimum
