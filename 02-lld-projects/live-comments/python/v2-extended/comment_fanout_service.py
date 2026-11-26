from typing import Protocol


class CommentFanoutService(Protocol):
    def fanout(self, stream_id: str, comment_payload: str, event_time_ms: int) -> None: ...
