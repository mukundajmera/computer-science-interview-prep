"""Token rate limiter tracking RPM and TPM budgets."""

import time
import threading

class TokenRateLimiter:
    """Thread-safe rate limiter for Requests Per Minute and Tokens Per Minute."""

    def __init__(self, max_rpm: int, max_tpm: int):
        self.max_rpm = max_rpm
        self.max_tpm = max_tpm

        self.rpm_tokens = max_rpm
        self.tpm_tokens = max_tpm

        self.last_refill_time = time.monotonic()
        self._lock = threading.Lock()

    def _refill(self):
        """Refills tokens based on time elapsed."""
        now = time.monotonic()
        elapsed = now - self.last_refill_time

        if elapsed > 0:
            # Calculate tokens to add (rate per second)
            rpm_to_add = (self.max_rpm / 60.0) * elapsed
            tpm_to_add = (self.max_tpm / 60.0) * elapsed

            self.rpm_tokens = min(self.max_rpm, self.rpm_tokens + rpm_to_add)
            self.tpm_tokens = min(self.max_tpm, self.tpm_tokens + tpm_to_add)

            self.last_refill_time = now

    def acquire(self, estimated_tokens: int) -> bool:
        """
        Attempt to acquire 1 request token and 'estimated_tokens' token budget.
        Returns True if successful, False if rate limited.
        """
        with self._lock:
            self._refill()

            if self.rpm_tokens >= 1 and self.tpm_tokens >= estimated_tokens:
                self.rpm_tokens -= 1
                self.tpm_tokens -= estimated_tokens
                return True
            return False

    def refund(self, tokens: int) -> None:
        """Refund tokens if the actual usage was less than estimated."""
        with self._lock:
            self.tpm_tokens = min(self.max_tpm, self.tpm_tokens + tokens)
