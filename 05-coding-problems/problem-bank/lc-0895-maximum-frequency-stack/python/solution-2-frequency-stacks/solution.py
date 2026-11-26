from collections import defaultdict


class FreqStack:
    def __init__(self) -> None:
        self.frequency = defaultdict(int)
        self.by_frequency = defaultdict(list)
        self.max_frequency = 0

    def push(self, val: int) -> None:
        self.frequency[val] += 1
        freq = self.frequency[val]
        self.max_frequency = max(self.max_frequency, freq)
        self.by_frequency[freq].append(val)

    def pop(self) -> int:
        value = self.by_frequency[self.max_frequency].pop()
        self.frequency[value] -= 1
        if not self.by_frequency[self.max_frequency]:
            self.max_frequency -= 1
        return value
