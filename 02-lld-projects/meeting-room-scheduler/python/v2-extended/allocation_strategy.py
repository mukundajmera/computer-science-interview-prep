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
                    if not room.has_overlap(interval):
                        suitable_rooms.append(room)
        
        if not suitable_rooms:
            return None
            
        suitable_rooms.sort(key=lambda r: r.capacity)
        return suitable_rooms[0]
