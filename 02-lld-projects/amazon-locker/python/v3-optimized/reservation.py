from dataclasses import dataclass
from datetime import datetime

from reservation_status import ReservationStatus


@dataclass
class Reservation:
    reservation_id: str
    compartment_id: str
    expires_at: datetime
    status: ReservationStatus = ReservationStatus.RESERVED

    def is_expired(self, now: datetime) -> bool:
        return now > self.expires_at
