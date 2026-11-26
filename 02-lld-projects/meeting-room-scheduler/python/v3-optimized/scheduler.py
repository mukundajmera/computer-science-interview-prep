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

    def book_meeting(self, title: str, capacity: int, interval: Interval, amenities: List[str], attendees: List[User], recurrence: str = None, count: int = 1) -> List[Meeting]:
        booked_meetings = []
        current_interval = interval
        
        for i in range(count):
            booked_successfully = False
            max_retries = 3
            retries = 0
            
            while not booked_successfully and retries < max_retries:
                with self._rooms_lock:
                    selected_room = self._allocation_strategy.allocate_room(self._rooms, capacity, current_interval, amenities)
    
                if not selected_room:
                    # If we can't book one instance, we stop booking further or maybe handle differently.
                    # For this implementation, let's just skip this instance or return what we have.
                    break
    
                with self._rooms_lock:
                    meeting_id = f"M{self._meeting_id_counter}"
                    self._meeting_id_counter += 1
                    
                meeting = Meeting(meeting_id, title, current_interval, attendees, selected_room)
    
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
                        
                    booked_meetings.append(meeting)
                    booked_successfully = True
                else:
                    retries += 1
            
            if not booked_successfully:
                break

            if recurrence == "daily":
                current_interval = Interval(current_interval.start_time + 86400, current_interval.end_time + 86400)
            elif recurrence == "weekly":
                current_interval = Interval(current_interval.start_time + 7 * 86400, current_interval.end_time + 7 * 86400)
            else:
                break

        return booked_meetings

    def cancel_meeting(self, meeting_id: str) -> bool:
        target_meeting = None
        with self._rooms_lock:
            for room in self._rooms:
                m = room.cancel_meeting(meeting_id)
                if m:
                    target_meeting = m
                    break
        
        if target_meeting:
            with self._user_meetings_lock:
                for user in target_meeting.attendees:
                    if user.id in self._user_meetings:
                        self._user_meetings[user.id] = [m for m in self._user_meetings[user.id] if m.id != meeting_id]

            with self._listeners_lock:
                listeners = list(self._notification_listeners)
            
            for listener in listeners:
                listener.on_meeting_cancelled(target_meeting)
            
            return True
            
        return False
        
    def reschedule_meeting(self, meeting_id: str, new_interval: Interval) -> Optional[Meeting]:
        target_meeting = None
        with self._rooms_lock:
            for room in self._rooms:
                meetings = room.get_booked_meetings()
                for m in meetings:
                    if m.id == meeting_id:
                        target_meeting = m
                        break
                if target_meeting:
                    break
                    
        if not target_meeting:
            return None
            
        self.cancel_meeting(meeting_id)
        
        # Now try to re-book. Re-use old attendees, amenities etc if we stored them (amenities not in meeting tho, so we pass empty here or we'd need to store them. Since not stored, we pass [] or re-use existing room if possible).
        # We can just attempt to allocate a new room with capacity=len(attendees)
        new_meetings = self.book_meeting(target_meeting.title, len(target_meeting.attendees), new_interval, [], target_meeting.attendees)
        
        if new_meetings:
            with self._listeners_lock:
                listeners = list(self._notification_listeners)
            for listener in listeners:
                listener.on_meeting_rescheduled(new_meetings[0])
            return new_meetings[0]
            
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
