import math
import time
from typing import Callable, Dict, Set, List
from threading import Lock

EARTH_RADIUS_MILES = 3958.8
MAX_DISTANCE_MILES = 5.0
TTL_SECONDS = 10 * 60

class LocationUpdate:
    def __init__(self, user_id: str, latitude: float, longitude: float, timestamp: float):
        self.user_id = user_id
        self.latitude = latitude
        self.longitude = longitude
        self.timestamp = timestamp

class PubSubBus:
    def __init__(self):
        self.channel_subscribers: Dict[str, Set[Callable[[LocationUpdate], None]]] = {}
        self.lock = Lock()

    def subscribe(self, channel: str, subscriber: Callable[[LocationUpdate], None]):
        with self.lock:
            if channel not in self.channel_subscribers:
                self.channel_subscribers[channel] = set()
            self.channel_subscribers[channel].add(subscriber)

    def unsubscribe(self, channel: str, subscriber: Callable[[LocationUpdate], None]):
        with self.lock:
            if channel in self.channel_subscribers:
                self.channel_subscribers[channel].discard(subscriber)
                if not self.channel_subscribers[channel]:
                    del self.channel_subscribers[channel]

    def publish(self, channel: str, message: LocationUpdate):
        subscribers = set()
        with self.lock:
            if channel in self.channel_subscribers:
                subscribers = set(self.channel_subscribers[channel])
        for subscriber in subscribers:
            subscriber(message)


class NearbyFriendsService:
    def __init__(self, pub_sub_bus: PubSubBus):
        self.pub_sub_bus = pub_sub_bus
        self.active_user_locations: Dict[str, LocationUpdate] = {}
        self.lock = Lock()

    def update_location(self, user_id: str, latitude: float, longitude: float, timestamp: float):
        update = LocationUpdate(user_id, latitude, longitude, timestamp)
        with self.lock:
            self.active_user_locations[user_id] = update
        self.pub_sub_bus.publish(user_id, update)

    def subscribe_to_friend(self, user_id: str, friend_id: str, client_callback: Callable[[LocationUpdate], None]) -> Callable[[LocationUpdate], None]:
        def friend_update_handler(friend_update: LocationUpdate):
            with self.lock:
                user_location = self.active_user_locations.get(user_id)
            if user_location:
                current_time = time.time()
                if friend_update.timestamp >= current_time - TTL_SECONDS:
                    distance = self.calculate_haversine_distance(
                        user_location.latitude, user_location.longitude,
                        friend_update.latitude, friend_update.longitude
                    )
                    if distance <= MAX_DISTANCE_MILES:
                        client_callback(friend_update)
        
        self.pub_sub_bus.subscribe(friend_id, friend_update_handler)
        return friend_update_handler
    
    def unsubscribe_from_friend(self, friend_id: str, handler: Callable[[LocationUpdate], None]):
        self.pub_sub_bus.unsubscribe(friend_id, handler)

    @staticmethod
    def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        rlat1 = math.radians(lat1)
        rlat2 = math.radians(lat2)

        a = math.sin(dlat / 2)**2 + math.cos(rlat1) * math.cos(rlat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return EARTH_RADIUS_MILES * c

    def get_user_location(self, user_id: str) -> LocationUpdate:
        with self.lock:
            return self.active_user_locations.get(user_id)
