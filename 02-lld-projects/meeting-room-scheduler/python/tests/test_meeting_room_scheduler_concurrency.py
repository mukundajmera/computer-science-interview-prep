import pytest
import threading
import sys
import os
import random
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v3-optimized')))

from interval import Interval
from user import User
from meeting_room import MeetingRoom
from allocation_strategy import BestFitAllocationStrategy
from scheduler import MeetingRoomScheduler

def test_concurrent_booking_stress_test():
    scheduler = MeetingRoomScheduler(BestFitAllocationStrategy())
    
    # Add a single room with enough capacity
    room = MeetingRoom("R1", 100, ["Projector"])
    scheduler.add_room(room)
    
    # We want to book the exact same time slot concurrently
    # The room is only available for 1 meeting at that time slot
    # So only 1 thread should succeed, others should fail
    
    num_threads = 16
    success_count = 0
    success_lock = threading.Lock()
    
    users = [User(f"U{i}", f"User {i}", f"u{i}@example.com") for i in range(num_threads)]
    
    def book_worker(worker_id):
        nonlocal success_count
        # All workers try to book exactly [100, 200)
        meetings = scheduler.book_meeting(
            title=f"Concurrent Meeting {worker_id}",
            capacity=5,
            interval=Interval(100, 200),
            amenities=["Projector"],
            attendees=[users[worker_id]]
        )
        if meetings:
            with success_lock:
                success_count += 1
                
    # Run threads concurrently
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(book_worker, i) for i in range(num_threads)]
        for f in futures:
            f.result()  # raise exceptions if any
            
    # Assert exactly 1 meeting was booked for this specific timeslot
    assert success_count == 1, f"Expected exactly 1 success, got {success_count}"
    
    # Check that room has exactly 1 meeting
    booked_meetings = room.get_booked_meetings()
    assert len(booked_meetings) == 1

def test_concurrent_independent_bookings():
    scheduler = MeetingRoomScheduler(BestFitAllocationStrategy())
    
    # Add multiple rooms
    scheduler.add_room(MeetingRoom("R1", 100, ["Projector"]))
    scheduler.add_room(MeetingRoom("R2", 100, ["Projector"]))
    
    num_threads = 16
    success_count = 0
    success_lock = threading.Lock()
    
    def book_worker(worker_id):
        nonlocal success_count
        # Each worker books a disjoint time slot, e.g. [worker_id*100, worker_id*100 + 50)
        # They should all succeed without deadlocks or race conditions
        interval = Interval(worker_id * 100, worker_id * 100 + 50)
        meetings = scheduler.book_meeting(
            title=f"Independent Meeting {worker_id}",
            capacity=5,
            interval=interval,
            amenities=[],
            attendees=[]
        )
        if meetings:
            with success_lock:
                success_count += 1
                
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(book_worker, i) for i in range(num_threads)]
        for f in futures:
            f.result()
            
    # All non-overlapping bookings should succeed
    assert success_count == num_threads
