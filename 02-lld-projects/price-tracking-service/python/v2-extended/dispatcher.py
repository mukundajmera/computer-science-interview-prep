import typing
from domain import Channel

class Clock(typing.Protocol):
    def now_sec(self) -> int: ...

class ChannelAdapter(typing.Protocol):
    def send(self, user_id: str, message: str) -> None: ...

class EmailAdapter:
    def send(self, user_id: str, message: str) -> None:
        print(f"Sending Email to {user_id}: {message}")

class SMSAdapter:
    def send(self, user_id: str, message: str) -> None:
        print(f"Sending SMS to {user_id}: {message}")

class PushAdapter:
    def send(self, user_id: str, message: str) -> None:
        print(f"Sending PUSH to {user_id}: {message}")

class RateLimitedDispatcher:
    def __init__(self, adapters: typing.Dict[Channel, ChannelAdapter], clock: Clock, rate_limit_window_sec: int = 60) -> None:
        self.adapters = adapters
        self.clock = clock
        self.rate_limit_window_sec = rate_limit_window_sec
        # subscription_id -> last_sent_timestamp
        self._last_sent: typing.Dict[str, int] = {}

    def dispatch(self, subscription_id: str, user_id: str, channel: Channel, message: str) -> bool:
        now = self.clock.now_sec()
        last_sent = self._last_sent.get(subscription_id)
        
        if last_sent is not None and (now - last_sent) < self.rate_limit_window_sec:
            return False # rate limited
            
        adapter = self.adapters.get(channel)
        if adapter:
            adapter.send(user_id, message)
            self._last_sent[subscription_id] = now
            return True
        return False
