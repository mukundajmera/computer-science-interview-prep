from collections import Counter


class FreqStack:
    def __init__(self) -> None:
        self.stack = []
        self.frequency = Counter()

    def push(self, val: int) -> None:
        self.stack.append(val)
        self.frequency[val] += 1

    def pop(self) -> int:
        best = max(self.frequency.values())
        for index in range(len(self.stack) - 1, -1, -1):
            value = self.stack[index]
            if self.frequency[value] == best:
                self.stack.pop(index)
                self.frequency[value] -= 1
                if self.frequency[value] == 0:
                    del self.frequency[value]
                return value
        raise IndexError("empty stack")
