import math
import time
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v2-extended')))
from nearby_friends_service_v2 import PubSubBus, NearbyFriendsService, LocationUpdate

# ---------------------------------------------------------------------------
# v1 parity tests: same scenarios as tests/test_nearby_friends_service.py,
# run against v2.
# ---------------------------------------------------------------------------

def test_location_update_dispatched():
    pub_sub_bus = PubSubBus()
    service = NearbyFriendsService(pub_sub_bus)

    now = time.time()
    service.update_location("UserA", 40.7128, -74.0060, now)

    received_updates = []
    service.subscribe_to_friend("UserA", "FriendB", lambda update: received_updates.append(update))

    service.update_location("FriendB", 40.7150, -74.0050, now)

    assert len(received_updates) == 1
    assert received_updates[0].user_id == "FriendB"

def test_distance_cutoff():
    pub_sub_bus = PubSubBus()
    service = NearbyFriendsService(pub_sub_bus)

    now = time.time()
    service.update_location("UserA", 40.7128, -74.0060, now)

    received_updates = []
    service.subscribe_to_friend("UserA", "FriendB", lambda update: received_updates.append(update))

    # LA coordinates (very far from NY)
    service.update_location("FriendB", 34.0522, -118.2437, now)

    assert len(received_updates) == 0

def test_user_ttl_expiry():
    pub_sub_bus = PubSubBus()
    service = NearbyFriendsService(pub_sub_bus)

    now = time.time()
    service.update_location("UserA", 40.7128, -74.0060, now)

    received_updates = []
    service.subscribe_to_friend("UserA", "FriendB", lambda update: received_updates.append(update))

    # Update is 11 minutes old
    old_timestamp = now - (11 * 60)
    service.update_location("FriendB", 40.7150, -74.0050, old_timestamp)

    assert len(received_updates) == 0

def test_subscribe_unsubscribe_friend():
    pub_sub_bus = PubSubBus()
    service = NearbyFriendsService(pub_sub_bus)

    now = time.time()
    service.update_location("UserA", 40.7128, -74.0060, now)

    received_updates = []
    handler = service.subscribe_to_friend("UserA", "FriendB", lambda update: received_updates.append(update))

    service.update_location("FriendB", 40.7150, -74.0050, now)
    assert len(received_updates) == 1

    service.unsubscribe_from_friend("FriendB", handler)
    service.update_location("FriendB", 40.7150, -74.0050, now)
    assert len(received_updates) == 1  # Should not increase

def test_offline_friend_not_notified():
    pub_sub_bus = PubSubBus()
    service = NearbyFriendsService(pub_sub_bus)

    now = time.time()
    # User A doesn't have an active location in cache

    received_updates = []
    service.subscribe_to_friend("UserA", "FriendB", lambda update: received_updates.append(update))

    service.update_location("FriendB", 40.7150, -74.0050, now)

    assert len(received_updates) == 0

# ---------------------------------------------------------------------------
# v2-only tests: one or more per improvement.
# ---------------------------------------------------------------------------

# Improvement #1: offline-to-online initial state (FOLLOW-UPS.md #2).

def test_initial_state_delivered_on_subscribe():
    pub_sub_bus = PubSubBus()
    service = NearbyFriendsService(pub_sub_bus)

    now = time.time()
    service.update_location("UserA", 40.7128, -74.0060, now)
    service.update_location("FriendB", 40.7150, -74.0050, now)

    received_updates = []
    # FriendB already has a fresh in-range location before UserA subscribes.
    service.subscribe_to_friend("UserA", "FriendB", lambda update: received_updates.append(update))

    assert len(received_updates) == 1, "subscriber gets the last known location immediately"
    assert received_updates[0].user_id == "FriendB"

    service.update_location("FriendB", 40.7152, -74.0052, time.time())
    assert len(received_updates) == 2, "live updates keep flowing after the snapshot"

def test_initial_state_not_delivered_when_out_of_range():
    pub_sub_bus = PubSubBus()
    service = NearbyFriendsService(pub_sub_bus)

    now = time.time()
    service.update_location("UserA", 40.7128, -74.0060, now)
    service.update_location("FriendB", 34.0522, -118.2437, now)  # LA

    received_updates = []
    service.subscribe_to_friend("UserA", "FriendB", lambda update: received_updates.append(update))

    assert len(received_updates) == 0

def test_initial_state_not_delivered_when_stale():
    pub_sub_bus = PubSubBus()
    service = NearbyFriendsService(pub_sub_bus)

    now = time.time()
    service.update_location("UserA", 40.7128, -74.0060, now)
    service.update_location("FriendB", 40.7150, -74.0050, now - (11 * 60))  # 11 min old

    received_updates = []
    service.subscribe_to_friend("UserA", "FriendB", lambda update: received_updates.append(update))

    assert len(received_updates) == 0

# Improvement #2: fan-out metrics and throttling (FOLLOW-UPS.md #3,
# PITFALLS.md #3).

def test_publish_count_metric():
    pub_sub_bus = PubSubBus()
    service = NearbyFriendsService(pub_sub_bus)

    now = time.time()
    service.update_location("FriendB", 40.7150, -74.0050, now)
    service.update_location("FriendB", 40.7151, -74.0051, now + 1)
    service.update_location("FriendB", 40.7152, -74.0052, now + 2)
    service.update_location("FriendC", 40.7150, -74.0050, now)

    assert pub_sub_bus.get_publish_count("FriendB") == 3
    assert pub_sub_bus.get_publish_count("FriendC") == 1
    assert pub_sub_bus.get_publish_count("Nobody") == 0

def test_throttle_drops_burst_updates():
    pub_sub_bus = PubSubBus()
    service = NearbyFriendsService(pub_sub_bus, throttle_interval_seconds=0.25)

    now = time.time()
    service.update_location("UserA", 40.7128, -74.0060, now)

    received_updates = []
    service.subscribe_to_friend("UserA", "FriendB", lambda update: received_updates.append(update))

    service.update_location("FriendB", 40.7150, -74.0050, now + 1)   # delivered (first)
    service.update_location("FriendB", 40.7151, -74.0051, now + 2)   # dropped (inside interval)
    time.sleep(0.3)
    service.update_location("FriendB", 40.7152, -74.0052, now + 3)  # delivered (interval passed)

    assert len(received_updates) == 2
    assert received_updates[0].latitude == 40.7150
    assert received_updates[1].latitude == 40.7152

def test_no_throttle_by_default():
    pub_sub_bus = PubSubBus()
    service = NearbyFriendsService(pub_sub_bus)

    now = time.time()
    service.update_location("UserA", 40.7128, -74.0060, now)

    received_updates = []
    service.subscribe_to_friend("UserA", "FriendB", lambda update: received_updates.append(update))

    service.update_location("FriendB", 40.7150, -74.0050, now + 1)
    service.update_location("FriendB", 40.7151, -74.0051, now + 2)

    assert len(received_updates) == 2, "v1 behavior: every update is delivered"

# Improvement #3: out-of-order rejection and input validation
# (FOLLOW-UPS.md #4).

def test_out_of_order_update_ignored():
    pub_sub_bus = PubSubBus()
    service = NearbyFriendsService(pub_sub_bus)

    now = time.time()
    service.update_location("UserA", 40.7128, -74.0060, now)

    received_updates = []
    service.subscribe_to_friend("UserA", "FriendB", lambda update: received_updates.append(update))

    service.update_location("FriendB", 40.7150, -74.0050, now)
    # A delayed duplicate from before the reconnect storm must not regress.
    service.update_location("FriendB", 34.0522, -118.2437, now - 30)

    stored = service.get_user_location("FriendB")
    assert stored.latitude == 40.7150, "newer position is kept"
    assert len(received_updates) == 1, "stale update is not fanned out"

def test_invalid_coordinates_rejected():
    pub_sub_bus = PubSubBus()
    service = NearbyFriendsService(pub_sub_bus)

    now = time.time()
    with pytest.raises(ValueError):
        service.update_location("UserA", 91.0, -74.0060, now)
    with pytest.raises(ValueError):
        service.update_location("UserA", 40.7128, -181.0, now)
    with pytest.raises(ValueError):
        service.update_location("UserA", math.nan, -74.0060, now)

    assert service.get_user_location("UserA") is None, "invalid updates never stored"
