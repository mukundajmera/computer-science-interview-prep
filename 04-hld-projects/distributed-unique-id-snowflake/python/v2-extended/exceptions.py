class ClockMovedBackwardsException(Exception):
    pass


class TimestampOverflowException(Exception):
    """Raised when the timestamp no longer fits the 41-bit delta field
    (v2 improvement #3, FOLLOW-UPS.md #1)."""
    pass


class WorkerIdPoolExhaustedError(Exception):
    """Raised when no worker ID lease is available (v2 improvement #2,
    FOLLOW-UPS.md #3)."""
    pass
