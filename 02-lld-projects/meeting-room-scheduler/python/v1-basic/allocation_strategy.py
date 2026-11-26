from abc import ABC, abstractmethod
from typing import List, Optional
from meeting_room import MeetingRoom
from interval import Interval

class RoomAllocationStrategy(ABC):
    @abstractmethod
    def allocate_room(self, rooms: List[MeetingRoom], capacity: int, interval: Interval, amenities: List[str]) -> Optional[MeetingRoom]:
        pass

class BestFitAllocationStrategy(RoomAllocationStrategy):
    def allocate_room(self, rooms: List[MeetingRoom], capacity: int, interval: Interval, amenities: List[str]) -> Optional[MeetingRoom]:
        suitable_rooms = []
        for room in rooms:
            if room.capacity >= capacity:
                if all(amenity in room.amenities for amenity in amenities):
                    if self._is_available(room, interval):
                        suitable_rooms.append(room)
        
        if not suitable_rooms:
            return None
            
        suitable_rooms.sort(key=lambda r: r.capacity)
        return suitable_rooms[0]

    def _is_available(self, room: MeetingRoom, interval: Interval) -> bool:
        # Avoid checking-then-acting race outside of lock by returning current snapshot,
        # Scheduler will attempt final book anyway.
        for meeting in room.get_booked_meetings():
            if meeting.interval.overlaps(interval):
                return False
        return True
