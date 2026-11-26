from typing import List
import threading
from meeting import Meeting
from interval_tree import IntervalTree
from interval import Interval

class MeetingRoom:
    def __init__(self, id: str, capacity: int, amenities: List[str]):
        self.id = id
        self.capacity = capacity
        self.amenities = list(amenities)
        self._interval_tree = IntervalTree()
        self._lock = threading.Lock()

    def get_booked_meetings(self) -> List[Meeting]:
        with self._lock:
            return self._interval_tree.get_all_meetings()

    def has_overlap(self, interval: Interval) -> bool:
        with self._lock:
            return self._interval_tree.has_overlap(interval)

    def book_meeting(self, meeting: Meeting) -> bool:
        with self._lock:
            if self._interval_tree.has_overlap(meeting.interval):
                return False
            self._interval_tree.insert(meeting)
            return True
