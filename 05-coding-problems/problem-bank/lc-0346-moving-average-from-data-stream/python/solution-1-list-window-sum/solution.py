class MovingAverage:
    def __init__(self, size: int):
        self.size = size
        self.values = []

    def next(self, val: int) -> float:
        self.values.append(val)
        window = self.values[-self.size:]
        return sum(window) / len(window)
