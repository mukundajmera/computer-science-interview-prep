from typing import List, Optional
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
        self._lock = threading.RLock()

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

    def cancel_meeting(self, meeting_id: str) -> Optional[Meeting]:
        with self._lock:
            meetings = self._interval_tree.get_all_meetings()
            target_meeting = None
            for m in meetings:
                if m.id == meeting_id:
                    target_meeting = m
                    break
            
            if target_meeting:
                self._interval_tree.remove(target_meeting)
            return target_meeting
