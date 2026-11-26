class Logger:
    def __init__(self) -> None:
        self.next_allowed = {}

    def shouldPrintMessage(self, timestamp: int, message: str) -> bool:
        if timestamp < self.next_allowed.get(message, 0):
            return False
        self.next_allowed[message] = timestamp + 10
        return True
