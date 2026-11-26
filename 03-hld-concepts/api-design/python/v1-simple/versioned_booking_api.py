"""Resource-oriented API simulation with idempotent create and pagination samples."""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class Booking:
    booking_id: str
    event_id: str
    user_id: str


class VersionedBookingApi:
    def __init__(self) -> None:
        self._bookings: List[Booking] = []
        self._idempotency_to_booking: Dict[str, str] = {}
        self._sequence = 1

    def post_v1_events_event_id_bookings(self, event_id: str, user_id: str, idempotency_key: str) -> Booking:
        existing_id = self._idempotency_to_booking.get(idempotency_key)
        if existing_id:
            return self._get_by_id(existing_id)

        booking = Booking(
            booking_id=f"b-{self._sequence}",
            event_id=event_id,
            user_id=user_id,
        )
        self._sequence += 1
        self._bookings.append(booking)
        self._idempotency_to_booking[idempotency_key] = booking.booking_id
        return booking

    def get_v1_bookings_offset(self, offset: int, limit: int) -> List[Booking]:
        start = max(0, min(offset, len(self._bookings)))
        end = max(start, min(start + limit, len(self._bookings)))
        return self._bookings[start:end]

    def get_v1_bookings_cursor(self, cursor: Optional[str], limit: int) -> Tuple[List[Booking], Optional[str], bool]:
        start = int(cursor) if cursor is not None else 0
        end = max(start, min(start + limit, len(self._bookings)))

        items = self._bookings[start:end]
        has_more = end < len(self._bookings)
        next_cursor = str(end) if has_more else None
        return items, next_cursor, has_more

    def _get_by_id(self, booking_id: str) -> Booking:
        for booking in self._bookings:
            if booking.booking_id == booking_id:
                return booking
        raise KeyError(f"unknown booking_id={booking_id}")


if __name__ == "__main__":
    api = VersionedBookingApi()

    print("Create 1:", api.post_v1_events_event_id_bookings("e-100", "u-1", "req-1"))
    print("Create 1 retry:", api.post_v1_events_event_id_bookings("e-100", "u-1", "req-1"))
    print("Create 2:", api.post_v1_events_event_id_bookings("e-101", "u-2", "req-2"))
    print("Create 3:", api.post_v1_events_event_id_bookings("e-102", "u-3", "req-3"))

    print("Offset page:", api.get_v1_bookings_offset(0, 2))
    print("Cursor page 1:", api.get_v1_bookings_cursor(None, 2))
    print("Cursor page 2:", api.get_v1_bookings_cursor("2", 2))
