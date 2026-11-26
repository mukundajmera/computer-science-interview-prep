from enum import Enum, auto

class LogLevel(Enum):
    TRACE = 1
    DEBUG = 2
    INFO = 3
    WARN = 4
    ERROR = 5
    FATAL = 6

    def is_greater_or_equal(self, other: 'LogLevel') -> bool:
        return self.value >= other.value

