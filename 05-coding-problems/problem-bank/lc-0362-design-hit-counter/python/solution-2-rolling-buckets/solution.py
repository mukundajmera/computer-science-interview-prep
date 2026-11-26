class HitCounter:
    def __init__(self) -> None:
        self.times = [0] * 300
        self.counts = [0] * 300

    def hit(self, timestamp: int) -> None:
        index = timestamp % 300
        if self.times[index] != timestamp:
            self.times[index] = timestamp
            self.counts[index] = 0
        self.counts[index] += 1

    def getHits(self, timestamp: int) -> int:
        return sum(count for time, count in zip(self.times, self.counts) if timestamp - time < 300)
