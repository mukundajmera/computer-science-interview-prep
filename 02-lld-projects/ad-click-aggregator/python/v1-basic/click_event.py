"""ClickEvent for ad-click-aggregator (v1-basic)."""


class ClickEvent:
    def __init__(self, event_id: str, ad_id: str, user_id: str, timestamp: int) -> None:
        self.event_id = event_id
        self.ad_id = ad_id
        self.user_id = user_id
        self.timestamp = timestamp
