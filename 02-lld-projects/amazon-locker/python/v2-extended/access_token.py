from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class AccessToken:
    code: str
    compartment_id: str
    expires_at: datetime

    def is_expired(self, now: datetime) -> bool:
        return now > self.expires_at
