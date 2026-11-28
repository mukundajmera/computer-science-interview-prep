"""
v2-extended nearby friends service.

Improvements over v1-basic (each has dedicated tests):

1. Offline-to-online initial state (FOLLOW-UPS.md #2): subscribing to a
   friend immediately delivers the friend's last known location when it
   is fresh and in range, so a user who opens the app after being
   offline sees the map without waiting for the friend's next move.

2. Fan-out throttling with per-channel publish metrics (FOLLOW-UPS.md #3
   celebrity problem, PITFALLS.md #3 fan-out multiplier): PubSubBus
   counts publishes per channel so the read-to-write ratio is
   observable, and the service can throttle a friend's updates to at
   most one delivery per interval per subscriber, always delivering the
   first update after a quiet period.

3. Out-of-order and invalid update hardening (FOLLOW-UPS.md #4 reconnect
   storms): a location update older than the stored one is ignored
   instead of regressing the user's position, and coordinates are
   validated so NaN or out-of-range values never enter the system.
"""

import math
import time
from threading import Lock
from typing import Callable, Dict, List, Optional, Set

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
    """v1 parity plus per-channel publish metrics (improvement #2)."""

    def __init__(self):
        self.channel_subscribers: Dict[str, Set[Callable[[LocationUpdate], None]]] = {}
        self.publish_counts: Dict[str, int] = {}
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
            self.publish_counts[channel] = self.publish_counts.get(channel, 0) + 1
            if channel in self.channel_subscribers:
                subscribers = set(self.channel_subscribers[channel])
        for subscriber in subscribers:
            subscriber(message)

    def get_publish_count(self, channel: str) -> int:
        """Fan-out metric: total publishes on a channel (PITFALLS.md #3)."""
        with self.lock:
            return self.publish_counts.get(channel, 0)


class NearbyFriendsService:
    def __init__(self, pub_sub_bus: PubSubBus, throttle_interval_seconds: Optional[float] = None):
        self.pub_sub_bus = pub_sub_bus
        self.throttle_interval_seconds = throttle_interval_seconds
        self.active_user_locations: Dict[str, LocationUpdate] = {}
        self.lock = Lock()

    @staticmethod
    def _validate_coordinates(latitude: float, longitude: float):
        # Improvement #3: invalid coordinates never enter the system.
        if math.isnan(latitude) or math.isnan(longitude):
            raise ValueError("coordinates must not be NaN")
        if not -90.0 <= latitude <= 90.0:
            raise ValueError("latitude out of range: %r" % (latitude,))
        if not -180.0 <= longitude <= 180.0:
            raise ValueError("longitude out of range: %r" % (longitude,))

    def update_location(self, user_id: str, latitude: float, longitude: float, timestamp: float):
        self._validate_coordinates(latitude, longitude)
        update = LocationUpdate(user_id, latitude, longitude, timestamp)
        with self.lock:
            existing = self.active_user_locations.get(user_id)
            # Improvement #3: an older update (reconnect-storm duplicate or
            # delayed packet) must not regress the stored position.
            if existing is not None and update.timestamp < existing.timestamp:
                return
            self.active_user_locations[user_id] = update
        self.pub_sub_bus.publish(user_id, update)

    def subscribe_to_friend(self, user_id: str, friend_id: str, client_callback: Callable[[LocationUpdate], None]) -> Callable[[LocationUpdate], None]:
        last_delivery = {"time": None}
        delivery_lock = Lock()

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
                        # Improvement #2: throttle a chatty friend to one
                        # delivery per interval per subscriber.
                        with delivery_lock:
                            now = time.time()
                            if (self.throttle_interval_seconds is not None
                                    and last_delivery["time"] is not None
                                    and now - last_delivery["time"] < self.throttle_interval_seconds):
                                return
                            last_delivery["time"] = now
                        client_callback(friend_update)

        self.pub_sub_bus.subscribe(friend_id, friend_update_handler)

        # Improvement #1: deliver the friend's last known location right
        # away when it is fresh and in range (offline-to-online catch-up).
        with self.lock:
            friend_location = self.active_user_locations.get(friend_id)
            user_location = self.active_user_locations.get(user_id)
        if friend_location is not None and user_location is not None:
            current_time = time.time()
            if friend_location.timestamp >= current_time - TTL_SECONDS:
                distance = self.calculate_haversine_distance(
                    user_location.latitude, user_location.longitude,
                    friend_location.latitude, friend_location.longitude
                )
                if distance <= MAX_DISTANCE_MILES:
                    with delivery_lock:
                        last_delivery["time"] = time.time()
                    client_callback(friend_location)

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

    def get_user_location(self, user_id: str) -> Optional[LocationUpdate]:
        with self.lock:
            return self.active_user_locations.get(user_id)
