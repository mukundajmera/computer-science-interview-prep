import pytest
import threading
from typing import List

import sys
import os
# Since v2 and v3 are mostly supersets, we can test v3 features explicitly and it covers interval trees.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v3-optimized')))

from interval import Interval
from user import User
from meeting_room import MeetingRoom
from allocation_strategy import BestFitAllocationStrategy
from scheduler import MeetingRoomScheduler
from notification import NotificationListener

class MockNotificationListener(NotificationListener):
    def __init__(self):
        self.booked_events = []
        self.cancelled_events = []
        self.rescheduled_events = []
        
    def on_meeting_booked(self, meeting):
        self.booked_events.append(meeting)

    def on_meeting_cancelled(self, meeting):
        self.cancelled_events.append(meeting)

    def on_meeting_rescheduled(self, meeting):
        self.rescheduled_events.append(meeting)

@pytest.fixture
def scheduler():
    return MeetingRoomScheduler(BestFitAllocationStrategy())

@pytest.fixture
def u1():
    return User("U1", "Alice", "alice@example.com")

@pytest.fixture
def u2():
    return User("U2", "Bob", "bob@example.com")

def test_interval_tree_overlap(scheduler, u1):
    # This tests the augmented interval tree indirectly through the scheduler
    r1 = MeetingRoom("R1", 10, ["Projector"])
    scheduler.add_room(r1)
    
    m1_list = scheduler.book_meeting("M1", 5, Interval(100, 200), ["Projector"], [u1])
    assert len(m1_list) == 1
    
    # Overlapping
    m2_list = scheduler.book_meeting("M2", 5, Interval(150, 250), ["Projector"], [u1])
    assert len(m2_list) == 0
    
    # Non-overlapping
    m3_list = scheduler.book_meeting("M3", 5, Interval(200, 300), ["Projector"], [u1])
    assert len(m3_list) == 1
    
    # Contained overlap
    m4_list = scheduler.book_meeting("M4", 5, Interval(120, 150), ["Projector"], [u1])
    assert len(m4_list) == 0

def test_notifications_observer(scheduler, u1):
    r1 = MeetingRoom("R1", 10, ["Projector"])
    scheduler.add_room(r1)
    
    listener = MockNotificationListener()
    scheduler.add_notification_listener(listener)
    
    # Test Booked Notification
    m_list = scheduler.book_meeting("M1", 5, Interval(100, 200), ["Projector"], [u1])
    assert len(m_list) == 1
    meeting = m_list[0]
    
    assert len(listener.booked_events) == 1
    assert listener.booked_events[0].id == meeting.id
    
    # Test Cancelled Notification
    scheduler.cancel_meeting(meeting.id)
    assert len(listener.cancelled_events) == 1
    assert listener.cancelled_events[0].id == meeting.id
    
def test_reschedule_observer(scheduler, u1):
    r1 = MeetingRoom("R1", 10, ["Projector"])
    scheduler.add_room(r1)
    
    listener = MockNotificationListener()
    scheduler.add_notification_listener(listener)
    
    m_list = scheduler.book_meeting("M1", 5, Interval(100, 200), ["Projector"], [u1])
    meeting = m_list[0]
    
    # Test Reschedule Notification
    new_meeting = scheduler.reschedule_meeting(meeting.id, Interval(300, 400))
    assert new_meeting is not None
    assert new_meeting.interval.start_time == 300
    assert len(listener.rescheduled_events) == 1
    assert listener.rescheduled_events[0].id == new_meeting.id

def test_recurring_meetings(scheduler, u1):
    r1 = MeetingRoom("R1", 10, ["Projector"])
    scheduler.add_room(r1)
    
    # Book daily meetings for 3 days
    meetings = scheduler.book_meeting("Daily Standup", 5, Interval(100, 200), ["Projector"], [u1], recurrence="daily", count=3)
    
    assert len(meetings) == 3
    assert meetings[0].interval.start_time == 100
    assert meetings[1].interval.start_time == 100 + 86400
    assert meetings[2].interval.start_time == 100 + 86400 * 2
    
def test_capacity_and_amenities_filtering(scheduler, u1):
    r1 = MeetingRoom("R1", 5, ["Projector"])
    r2 = MeetingRoom("R2", 15, ["Whiteboard"])
    r3 = MeetingRoom("R3", 20, ["Projector", "Whiteboard"])
    
    scheduler.add_room(r1)
    scheduler.add_room(r2)
    scheduler.add_room(r3)
    
    # Needs 10 capacity and Projector -> Only R3 fits
    m1_list = scheduler.book_meeting("M1", 10, Interval(100, 200), ["Projector"], [u1])
    assert len(m1_list) == 1
    assert m1_list[0].room.id == "R3"
    
    # Needs 5 capacity and Projector -> R1 fits best (smallest valid capacity)
    m2_list = scheduler.book_meeting("M2", 5, Interval(300, 400), ["Projector"], [u1])
    assert len(m2_list) == 1
    assert m2_list[0].room.id == "R1"
