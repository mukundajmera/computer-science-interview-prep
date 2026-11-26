class Logger:
    def __init__(self) -> None:
        self.events = []

    def shouldPrintMessage(self, timestamp: int, message: str) -> bool:
        for seen_at, seen_message in reversed(self.events):
            if timestamp - seen_at >= 10:
                break
            if seen_message == message:
                return False
        self.events.append((timestamp, message))
        return True
