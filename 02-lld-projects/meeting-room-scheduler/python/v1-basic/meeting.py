from typing import List
from interval import Interval
from user import User

class Meeting:
    def __init__(self, id: str, title: str, interval: Interval, attendees: List[User], room: 'MeetingRoom'):
        self.id = id
        self.title = title
        self.interval = interval
        self.attendees = list(attendees)
        self.room = room
