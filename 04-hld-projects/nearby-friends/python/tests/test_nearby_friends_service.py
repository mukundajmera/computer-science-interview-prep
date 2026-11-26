import time
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))
from nearby_friends_service import PubSubBus, NearbyFriendsService, LocationUpdate

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
