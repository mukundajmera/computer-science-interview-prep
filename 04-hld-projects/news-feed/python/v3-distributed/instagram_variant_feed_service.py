
from typing import List, Optional, Protocol


class InstagramVariantFeedService(Protocol):
    """Instagram-oriented contract for media-heavy feed serving."""

    def get_home_feed(self, user_id: str, cursor: Optional[str], limit: int) -> List[str]: ...
    def create_media_post(self, user_id: str, media_key: str, caption: str) -> str: ...
    def register_media_derivative(self, post_id: str, derivative_key: str) -> None: ...
