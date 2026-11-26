from typing import List, Optional, Dict
import threading
from meeting_room import MeetingRoom
from meeting import Meeting
from user import User
from interval import Interval
from allocation_strategy import RoomAllocationStrategy
from notification import NotificationListener

class MeetingRoomScheduler:
    def __init__(self, allocation_strategy: RoomAllocationStrategy):
        self._rooms: List[MeetingRoom] = []
        self._allocation_strategy = allocation_strategy
        self._notification_listeners: List[NotificationListener] = []
        self._meeting_id_counter = 1
        
        self._rooms_lock = threading.Lock()
        self._listeners_lock = threading.Lock()
        self._user_meetings_lock = threading.Lock()
        
        self._user_meetings: Dict[str, List[Meeting]] = {}

    def add_room(self, room: MeetingRoom):
        with self._rooms_lock:
            self._rooms.append(room)

    def add_notification_listener(self, listener: NotificationListener):
        with self._listeners_lock:
            self._notification_listeners.append(listener)

    def book_meeting(self, title: str, capacity: int, interval: Interval, amenities: List[str], attendees: List[User]) -> Optional[Meeting]:
        with self._rooms_lock:
            selected_room = self._allocation_strategy.allocate_room(self._rooms, capacity, interval, amenities)

        if not selected_room:
            return None

        with self._rooms_lock:
            meeting_id = f"M{self._meeting_id_counter}"
            self._meeting_id_counter += 1
            
        meeting = Meeting(meeting_id, title, interval, attendees, selected_room)

        if selected_room.book_meeting(meeting):
            with self._user_meetings_lock:
                for user in attendees:
                    if user.id not in self._user_meetings:
                        self._user_meetings[user.id] = []
                    self._user_meetings[user.id].append(meeting)

            with self._listeners_lock:
                listeners = list(self._notification_listeners)
            
            for listener in listeners:
                listener.on_meeting_booked(meeting)
                
            return meeting

        return None

    def get_last_20_meetings_for_user(self, user_id: str) -> List[Meeting]:
        with self._user_meetings_lock:
            meetings = list(self._user_meetings.get(user_id, []))
            meetings.sort(key=lambda m: m.interval.start_time, reverse=True)
            return meetings[:20]

    def get_last_20_meetings_for_room(self, room_id: str) -> List[Meeting]:
        target_room = None
        with self._rooms_lock:
            for room in self._rooms:
                if room.id == room_id:
                    target_room = room
                    break

        if not target_room:
            return []

        meetings = target_room.get_booked_meetings()
        meetings.sort(key=lambda m: m.interval.start_time, reverse=True)
        return meetings[:20]

    def find_common_free_slots(self, users: List[User], search_start: int, search_end: int) -> List[Interval]:
        busy_intervals = []
        
        with self._user_meetings_lock:
            for user in users:
                meetings = self._user_meetings.get(user.id, [])
                for meeting in meetings:
                    busy_intervals.append(meeting.interval)

        if not busy_intervals:
            return [Interval(search_start, search_end)]

        busy_intervals.sort(key=lambda i: i.start_time)
        merged = []
        current = busy_intervals[0]

        for next_interval in busy_intervals[1:]:
            if current.end_time >= next_interval.start_time:
                current = Interval(current.start_time, max(current.end_time, next_interval.end_time))
            else:
                merged.append(current)
                current = next_interval
        merged.append(current)

        free_slots = []
        current_start = search_start

        for busy in merged:
            if busy.start_time > current_start:
                if busy.start_time <= search_end:
                    free_slots.append(Interval(current_start, busy.start_time))
                else:
                    free_slots.append(Interval(current_start, search_end))
                    current_start = search_end
                    break
            current_start = max(current_start, busy.end_time)

        if current_start < search_end:
            free_slots.append(Interval(current_start, search_end))

        return free_slots
