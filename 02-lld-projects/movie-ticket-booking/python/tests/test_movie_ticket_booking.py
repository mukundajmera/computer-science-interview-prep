#!/usr/bin/env python3
"""
Tests for Movie Ticket Booking System
"""

import unittest
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

import sys
import os

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v1-basic'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'v3-optimized'))


class TestV1BasicEntities(unittest.TestCase):
    """Tests for V1 Basic entities."""
    
    def test_movie_creation(self):
        """Test movie creation with correct properties."""
        from booking_entities import Movie
        
        movie = Movie("M1", "Avengers", 180, "Action")
        
        self.assertEqual(movie.id, "M1")
        self.assertEqual(movie.title, "Avengers")
        self.assertEqual(movie.duration_minutes, 180)
        self.assertEqual(movie.genre, "Action")
    
    def test_screen_creation(self):
        """Test standard screen creation with correct seat layout."""
        from booking_entities import Screen, SeatType
        
        screen = Screen.create_standard_screen("S1", "Screen 1", 1, 2, 3, 5)
        
        self.assertEqual(screen.id, "S1")
        self.assertEqual(screen.name, "Screen 1")
        self.assertEqual(screen.capacity, 30)  # 6 rows * 5 seats
        
        seats = screen.seats
        # Check VIP row
        self.assertEqual(seats[0].type, SeatType.VIP)
        # Check Premium rows
        self.assertEqual(seats[5].type, SeatType.PREMIUM)
        # Check Regular rows
        self.assertEqual(seats[15].type, SeatType.REGULAR)
    
    def test_seat_locking_and_booking(self):
        """Test seat locking and booking."""
        from booking_entities import Seat, ShowSeat, SeatType, SeatStatus
        
        seat = Seat("A1", "A", 1, SeatType.VIP)
        show_seat = ShowSeat(seat, 20.0)
        
        self.assertTrue(show_seat.is_available())
        
        # Lock seat
        self.assertTrue(show_seat.lock("user1"))
        self.assertEqual(show_seat.status, SeatStatus.LOCKED)
        self.assertFalse(show_seat.is_available())
        
        # Cannot lock again
        self.assertFalse(show_seat.lock("user2"))
        
        # Book seat
        self.assertTrue(show_seat.book("user1"))
        self.assertEqual(show_seat.status, SeatStatus.BOOKED)
    
    def test_booking_by_wrong_user(self):
        """Test that wrong user cannot book locked seat."""
        from booking_entities import Seat, ShowSeat, SeatType, SeatStatus
        
        seat = Seat("A1", "A", 1, SeatType.VIP)
        show_seat = ShowSeat(seat, 20.0)
        
        show_seat.lock("user1")
        self.assertFalse(show_seat.book("user2"))
        self.assertEqual(show_seat.status, SeatStatus.LOCKED)
    
    def test_show_creation(self):
        """Test show creation with seats from screen."""
        from booking_entities import Movie, Screen, Show
        
        movie = Movie("M1", "Test", 120, "Drama")
        screen = Screen.create_standard_screen("S1", "Screen 1", 1, 1, 1, 5)
        show = Show("SH1", movie, screen, datetime.now())
        
        self.assertEqual(len(show.get_available_seats()), 15)
        self.assertIsNotNone(show.get_show_seat("A1"))
    
    def test_multiple_seat_locking(self):
        """Test locking multiple seats atomically."""
        from booking_entities import Movie, Screen, Show, SeatStatus
        
        movie = Movie("M1", "Test", 120, "Drama")
        screen = Screen.create_standard_screen("S1", "Screen 1", 1, 1, 1, 5)
        show = Show("SH1", movie, screen, datetime.now())
        
        seat_ids = ["A1", "A2", "A3"]
        self.assertTrue(show.lock_seats(seat_ids, "user1"))
        
        # All seats should be locked
        for seat_id in seat_ids:
            self.assertEqual(show.get_show_seat(seat_id).status, SeatStatus.LOCKED)
        
        # Cannot lock same seats again
        self.assertFalse(show.lock_seats(["A2", "A3"], "user2"))
    
    def test_booking_total(self):
        """Test booking total calculation."""
        from booking_entities import Movie, Screen, Show, Booking
        
        movie = Movie("M1", "Test", 120, "Drama")
        screen = Screen.create_standard_screen("S1", "Screen 1", 1, 1, 0, 3)
        show = Show("SH1", movie, screen, datetime.now())
        
        show.lock_seats(["A1", "B1"], "user1")
        
        seats = [show.get_show_seat("A1"), show.get_show_seat("B1")]
        booking = Booking("BK1", show, "user1", seats)
        
        # VIP (20) + Premium (15) = 35
        self.assertAlmostEqual(booking.total_amount, 35.0, places=2)



class TestV2Extended(unittest.TestCase):
    """Tests for V2 Extended features like pricing and payments."""
    
    def test_differentiated_pricing(self):
        """Test that different seat types and times affect pricing."""
        import os, sys
        v2_path = os.path.join(os.path.dirname(__file__), '..', 'v2-extended')
        sys.path.insert(0, v2_path)
        if 'booking_entities' in sys.modules:
            del sys.modules['booking_entities']
        
        from booking_entities import Movie, Screen, Show, SeatType, TimeBasedPricingStrategy
        
        movie = Movie("M1", "Test", 120, "Drama")
        screen = Screen.create_standard_screen("S1", "Screen 1", 1, 1, 1, 5)
        
        # Morning show
        morning_time = datetime.now().replace(hour=10)
        show_morning = Show("SH1", movie, screen, morning_time, TimeBasedPricingStrategy())
        
        vip_morning = show_morning.get_show_seat("A1")
        self.assertAlmostEqual(vip_morning.price, 20.0 * 0.8)
        
        # Evening show
        evening_time = datetime.now().replace(hour=19)
        show_evening = Show("SH2", movie, screen, evening_time, TimeBasedPricingStrategy())
        
        vip_evening = show_evening.get_show_seat("A1")
        self.assertAlmostEqual(vip_evening.price, 20.0 * 1.2)
        
        sys.path.pop(0)

    def test_payment_provider_callback(self):
        """Test payment callback updates booking status."""
        import os, sys, time
        v2_path = os.path.join(os.path.dirname(__file__), '..', 'v2-extended')
        sys.path.insert(0, v2_path)
        if 'booking_entities' in sys.modules:
            del sys.modules['booking_entities']
        
        from booking_entities import BookingSystem, Movie, Screen, Show, SimulatedPaymentProvider, BookingStatus
        
        BookingSystem.reset_instance()
        system = BookingSystem()
        system.set_payment_provider(SimulatedPaymentProvider())
        
        movie = Movie("M1", "Test", 120, "Drama")
        screen = Screen.create_standard_screen("S1", "Screen 1", 1, 1, 1, 5)
        show = Show("SH1", movie, screen, datetime.now())
        
        system.add_movie(movie)
        system.add_screen(screen)
        system.add_show(show)
        
        booking = system.create_booking("user1", "SH1", ["A1", "A2"])
        
        # Test successful payment
        self.assertTrue(system.confirm_booking(booking.id, {"method": "CREDIT_CARD", "valid": True}))
        time.sleep(0.5) # Wait for callback
        self.assertEqual(booking.status, BookingStatus.CONFIRMED)
        
        # Test failed payment
        booking2 = system.create_booking("user1", "SH1", ["B1", "B2"])
        self.assertTrue(system.confirm_booking(booking2.id, {"method": "INVALID"}))
        time.sleep(0.5) # Wait for callback
        self.assertEqual(booking2.status, BookingStatus.CANCELLED)
        
        sys.path.pop(0)


class TestV3Concurrency(unittest.TestCase):
    """Tests for V3 Optimized concurrency features."""
    
    def test_concurrent_seat_locking(self):
        """Test concurrent seat locking."""
        # Import from v3-optimized
        v3_path = os.path.join(os.path.dirname(__file__), '..', 'v3-optimized')
        sys.path.insert(0, v3_path)
        if 'booking_entities' in sys.modules:
            del sys.modules['booking_entities']
        
        from booking_entities import Movie, Screen, Show
        
        movie = Movie("M1", "Test", 120, "Drama", "PG")
        screen = Screen.create_standard_screen("S1", "Screen 1", 1, 0, 0, 5)
        show = Show("SH1", movie, screen, datetime.now())
        
        target_seats = ["A1", "A2"]
        results = []
        barrier = threading.Barrier(10)
        
        def try_lock(user_id: str):
            barrier.wait()
            locked = show.lock_seats(target_seats, user_id)
            results.append(locked)
        
        threads = []
        for i in range(10):
            t = threading.Thread(target=try_lock, args=(f"user{i}",))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join(timeout=5)
        
        # Only one should succeed
        success_count = sum(1 for r in results if r)
        self.assertEqual(success_count, 1)
    
    def test_concurrent_booking_creation(self):
        """Test concurrent booking creation."""
        v3_path = os.path.join(os.path.dirname(__file__), '..', 'v3-optimized')
        sys.path.insert(0, v3_path)
        if 'booking_entities' in sys.modules:
            del sys.modules['booking_entities']
        
        from booking_entities import Movie, Screen, Show, BookingSystem
        
        system = BookingSystem.create_new_instance(booking_expiration=60)
        
        movie = Movie("M1", "Test", 120, "Drama", "PG")
        screen = Screen.create_standard_screen("S1", "Screen 1", 1, 0, 0, 5)
        show = Show("SH1", movie, screen, datetime.now())
        
        system.add_movie(movie)
        system.add_screen(screen)
        system.add_show(show)
        
        target_seats = ["A3", "A4"]
        bookings = []
        barrier = threading.Barrier(5)
        lock = threading.Lock()
        
        def try_book(user_id: str):
            barrier.wait()
            booking = system.create_booking(user_id, "SH1", target_seats)
            if booking:
                with lock:
                    bookings.append(booking)
        
        threads = []
        for i in range(5):
            t = threading.Thread(target=try_book, args=(f"user{i}",))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join(timeout=5)
        
        # Only one booking should be created
        self.assertEqual(len(bookings), 1)
        
        system.shutdown()
    
    def test_booking_cancellation(self):
        """Test booking cancellation."""
        v3_path = os.path.join(os.path.dirname(__file__), '..', 'v3-optimized')
        sys.path.insert(0, v3_path)
        if 'booking_entities' in sys.modules:
            del sys.modules['booking_entities']
        
        from booking_entities import Movie, Screen, Show, BookingSystem, BookingStatus
        
        system = BookingSystem.create_new_instance(booking_expiration=60)
        
        movie = Movie("M1", "Test", 120, "Drama", "PG")
        screen = Screen.create_standard_screen("S1", "Screen 1", 0, 1, 0, 3)
        show = Show("SH1", movie, screen, datetime.now())
        
        system.add_movie(movie)
        system.add_screen(screen)
        system.add_show(show)
        
        booking = system.create_booking("user1", "SH1", ["A1"])
        self.assertIsNotNone(booking)
        
        # Cancel pending booking
        self.assertTrue(system.cancel_booking(booking.id, "user1"))
        self.assertEqual(booking.status, BookingStatus.CANCELLED)
        
        # Seat should be available again
        self.assertTrue(show.get_show_seat("A1").is_available())
        
        system.shutdown()
    
    def test_cancellation_by_wrong_user(self):
        """Test that wrong user cannot cancel booking."""
        v3_path = os.path.join(os.path.dirname(__file__), '..', 'v3-optimized')
        sys.path.insert(0, v3_path)
        if 'booking_entities' in sys.modules:
            del sys.modules['booking_entities']
        
        from booking_entities import Movie, Screen, Show, BookingSystem, BookingStatus
        
        system = BookingSystem.create_new_instance(booking_expiration=60)
        
        movie = Movie("M1", "Test", 120, "Drama", "PG")
        screen = Screen.create_standard_screen("S1", "Screen 1", 0, 1, 0, 3)
        show = Show("SH1", movie, screen, datetime.now())
        
        system.add_movie(movie)
        system.add_screen(screen)
        system.add_show(show)
        
        booking = system.create_booking("user1", "SH1", ["A1"])
        
        # Wrong user cannot cancel
        self.assertFalse(system.cancel_booking(booking.id, "user2"))
        self.assertEqual(booking.status, BookingStatus.PENDING)
        
        system.shutdown()


class TestIntegration(unittest.TestCase):
    """Integration tests."""
    
    def test_complete_booking_flow(self):
        """Test complete booking flow."""
        v3_path = os.path.join(os.path.dirname(__file__), '..', 'v3-optimized')
        sys.path.insert(0, v3_path)
        if 'booking_entities' in sys.modules:
            del sys.modules['booking_entities']
        
        from booking_entities import Movie, Screen, Show, BookingSystem
        
        system = BookingSystem.create_new_instance(booking_expiration=60)
        
        # Setup
        movie = Movie("M1", "Avengers", 180, "Action", "PG-13")
        screen = Screen.create_standard_screen("S1", "Screen 1", 1, 2, 3, 8)
        show = Show("SH1", movie, screen, datetime.now())
        
        system.add_movie(movie)
        system.add_screen(screen)
        system.add_show(show)
        
        # Search movie
        search_results = system.search_movies("Avengers")
        self.assertEqual(len(search_results), 1)
        
        # Get shows
        shows = system.get_shows_for_movie("M1")
        self.assertEqual(len(shows), 1)
        
        # Create booking
        seat_ids = ["B1", "B2", "B3"]
        booking = system.create_booking("user1", "SH1", seat_ids)
        self.assertIsNotNone(booking)
        
        # Total = 3 * Premium ($15) = $45
        self.assertAlmostEqual(booking.total_amount, 45.0, places=2)
        
        system.shutdown()
    
    def test_system_statistics(self):
        """Test system statistics."""
        v3_path = os.path.join(os.path.dirname(__file__), '..', 'v3-optimized')
        sys.path.insert(0, v3_path)
        if 'booking_entities' in sys.modules:
            del sys.modules['booking_entities']
        
        from booking_entities import Movie, Screen, Show, BookingSystem
        
        system = BookingSystem.create_new_instance(booking_expiration=60)
        
        movie = Movie("M1", "Test", 120, "Drama", "PG")
        screen = Screen.create_standard_screen("S1", "Screen 1", 1, 1, 1, 3)
        show = Show("SH1", movie, screen, datetime.now())
        
        system.add_movie(movie)
        system.add_screen(screen)
        system.add_show(show)
        
        stats = system.get_system_stats()
        
        self.assertEqual(stats['total_movies'], 1)
        self.assertEqual(stats['total_screens'], 1)
        self.assertEqual(stats['total_shows'], 1)
        
        system.shutdown()


if __name__ == '__main__':
    unittest.main()
