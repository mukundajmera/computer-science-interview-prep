import sys
import os
import pytest

# Add the target module directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v1-simple'))

from versioned_booking_api import VersionedBookingApi

@pytest.fixture
def api():
    return VersionedBookingApi()

def test_idempotent_create_booking(api):
    booking1 = api.post_v1_events_event_id_bookings("event-1", "user-1", "idem-1")
    booking2 = api.post_v1_events_event_id_bookings("event-1", "user-1", "idem-1")

    assert booking1 is not None
    assert booking1 is booking2, "Idempotency key should return the exact same booking object"

    booking3 = api.post_v1_events_event_id_bookings("event-2", "user-2", "idem-2")
    assert booking1 is not booking3, "Different idempotency keys should return different bookings"

    assert booking1.event_id == "event-1"
    assert booking1.user_id == "user-1"

def test_offset_pagination(api):
    for i in range(5):
        api.post_v1_events_event_id_bookings(f"e{i}", f"u{i}", f"req{i}")

    page1 = api.get_v1_bookings_offset(0, 2)
    assert len(page1) == 2

    page2 = api.get_v1_bookings_offset(2, 2)
    assert len(page2) == 2

    page3 = api.get_v1_bookings_offset(4, 2)
    assert len(page3) == 1

    out_of_bounds = api.get_v1_bookings_offset(10, 5)
    assert len(out_of_bounds) == 0

def test_cursor_pagination(api):
    for i in range(3):
        api.post_v1_events_event_id_bookings(f"e{i}", f"u{i}", f"req{i}")

    items1, next_cursor1, has_more1 = api.get_v1_bookings_cursor(None, 2)
    assert len(items1) == 2
    assert next_cursor1 == "2"
    assert has_more1 is True

    items2, next_cursor2, has_more2 = api.get_v1_bookings_cursor(next_cursor1, 2)
    assert len(items2) == 1
    assert next_cursor2 is None
    assert has_more2 is False
