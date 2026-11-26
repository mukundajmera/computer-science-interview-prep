from typing import List, Protocol


class CommentReplayStore(Protocol):
    def replay(self, stream_id: str, cursor: str, limit: int) -> List[str]: ...
