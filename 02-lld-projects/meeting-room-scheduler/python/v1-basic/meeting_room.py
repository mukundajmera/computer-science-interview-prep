from typing import List
import threading
from meeting import Meeting

class MeetingRoom:
    def __init__(self, id: str, capacity: int, amenities: List[str]):
        self.id = id
        self.capacity = capacity
        self.amenities = list(amenities)
        self._booked_meetings = []
        self._lock = threading.Lock()

    def get_booked_meetings(self) -> List[Meeting]:
        with self._lock:
            return list(self._booked_meetings)

    def book_meeting(self, meeting: Meeting) -> bool:
        with self._lock:
            for existing in self._booked_meetings:
                if existing.interval.overlaps(meeting.interval):
                    return False
            self._booked_meetings.append(meeting)
            return True
