"""
Movie Ticket Booking System - V1 Basic

Core entities for the booking system.
"""

from enum import Enum
from typing import List, Dict, Optional
from datetime import datetime
import time


class SeatType(Enum):
    """Types of seats with base prices."""
    REGULAR = 10.0
    PREMIUM = 15.0
    VIP = 20.0


class SeatStatus(Enum):
    """Status of a seat for a show."""
    AVAILABLE = "available"
    LOCKED = "locked"
    BOOKED = "booked"


class BookingStatus(Enum):
    """Status of a booking."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class Movie:
    """Represents a movie."""
    
    def __init__(self, movie_id: str, title: str, duration_minutes: int, genre: str):
        self.id = movie_id
        self.title = title
        self.duration_minutes = duration_minutes
        self.genre = genre
    
    def __str__(self) -> str:
        return f"{self.title} ({self.genre}, {self.duration_minutes} min)"


class Seat:
    """Represents a physical seat in a screen."""
    
    def __init__(self, seat_id: str, row: str, number: int, seat_type: SeatType):
        self.id = seat_id
        self.row = row
        self.number = number
        self.type = seat_type
    
    def __str__(self) -> str:
        return f"{self.row}{self.number}"


class ShowSeat:
    """Represents a seat's availability for a specific show."""
    
    LOCK_TIMEOUT_SECONDS = 10 * 60  # 10 minutes
    
    def __init__(self, seat: Seat, price: float):
        self.seat = seat
        self.price = price
        self.status = SeatStatus.AVAILABLE
        self.locked_by: Optional[str] = None
        self.locked_at: float = 0
    
    def is_available(self) -> bool:
        """Check if seat is available, handling lock expiration."""
        if self.status == SeatStatus.LOCKED and self._is_lock_expired():
            self.unlock()
        return self.status == SeatStatus.AVAILABLE
    
    def _is_lock_expired(self) -> bool:
        return time.time() - self.locked_at > self.LOCK_TIMEOUT_SECONDS
    
    def lock(self, user_id: str) -> bool:
        """Lock the seat for a user."""
        if self.is_available():
            self.status = SeatStatus.LOCKED
            self.locked_by = user_id
            self.locked_at = time.time()
            return True
        return False
    
    def unlock(self) -> None:
        """Unlock the seat."""
        self.status = SeatStatus.AVAILABLE
        self.locked_by = None
        self.locked_at = 0
    
    def book(self, user_id: str) -> bool:
        """Book the seat (must be locked by same user)."""
        if self.status == SeatStatus.LOCKED and self.locked_by == user_id:
            self.status = SeatStatus.BOOKED
            return True
        return False
    
    def __str__(self) -> str:
        status_mark = {
            SeatStatus.AVAILABLE: "[ ]",
            SeatStatus.LOCKED: "[L]",
            SeatStatus.BOOKED: "[X]"
        }
        return f"{self.seat}{status_mark[self.status]}"


class Screen:
    """Represents a screen in a theater."""
    
    def __init__(self, screen_id: str, name: str):
        self.id = screen_id
        self.name = name
        self.seats: List[Seat] = []
    
    def add_seat(self, seat: Seat) -> None:
        self.seats.append(seat)
    
    @property
    def capacity(self) -> int:
        return len(self.seats)
    
    @staticmethod
    def create_standard_screen(screen_id: str, name: str,
                               vip_rows: int, premium_rows: int, regular_rows: int,
                               seats_per_row: int) -> 'Screen':
        """Create a standard screen with rows of different seat types."""
        screen = Screen(screen_id, name)
        row_char = ord('A')
        
        for _ in range(vip_rows):
            row = chr(row_char)
            for s in range(1, seats_per_row + 1):
                screen.add_seat(Seat(f"{row}{s}", row, s, SeatType.VIP))
            row_char += 1
        
        for _ in range(premium_rows):
            row = chr(row_char)
            for s in range(1, seats_per_row + 1):
                screen.add_seat(Seat(f"{row}{s}", row, s, SeatType.PREMIUM))
            row_char += 1
        
        for _ in range(regular_rows):
            row = chr(row_char)
            for s in range(1, seats_per_row + 1):
                screen.add_seat(Seat(f"{row}{s}", row, s, SeatType.REGULAR))
            row_char += 1
        
        return screen


class Show:
    """Represents a movie show."""
    
    def __init__(self, show_id: str, movie: Movie, screen: Screen, start_time: datetime):
        self.id = show_id
        self.movie = movie
        self.screen = screen
        self.start_time = start_time
        self.show_seats: Dict[str, ShowSeat] = {}
        
        # Initialize show seats from screen seats
        for seat in screen.seats:
            self.show_seats[seat.id] = ShowSeat(seat, seat.type.value)
    
    def get_show_seat(self, seat_id: str) -> Optional[ShowSeat]:
        return self.show_seats.get(seat_id)
    
    def get_available_seats(self) -> List[ShowSeat]:
        return [ss for ss in self.show_seats.values() if ss.is_available()]
    
    def lock_seats(self, seat_ids: List[str], user_id: str) -> bool:
        """Lock multiple seats atomically."""
        # First check all seats are available
        for seat_id in seat_ids:
            show_seat = self.show_seats.get(seat_id)
            if show_seat is None or not show_seat.is_available():
                return False
        
        # Lock all seats
        for seat_id in seat_ids:
            self.show_seats[seat_id].lock(user_id)
        
        return True
    
    def unlock_seats(self, seat_ids: List[str]) -> None:
        """Unlock multiple seats."""
        for seat_id in seat_ids:
            show_seat = self.show_seats.get(seat_id)
            if show_seat:
                show_seat.unlock()
    
    def book_seats(self, seat_ids: List[str], user_id: str) -> bool:
        """Book multiple seats."""
        for seat_id in seat_ids:
            show_seat = self.show_seats.get(seat_id)
            if show_seat is None or not show_seat.book(user_id):
                return False
        return True
    
    def display_seats(self) -> None:
        """Display seat map."""
        print(f"\n=== Seat Map for {self.movie.title} ===")
        by_row: Dict[str, List[ShowSeat]] = {}
        
        for show_seat in self.show_seats.values():
            row = show_seat.seat.row
            if row not in by_row:
                by_row[row] = []
            by_row[row].append(show_seat)
        
        for row in sorted(by_row.keys()):
            row_seats = sorted(by_row[row], key=lambda s: s.seat.number)
            seats_str = " ".join(str(s) for s in row_seats)
            seat_type = row_seats[0].seat.type.name
            print(f"{row}: {seats_str} ({seat_type})")
        
        print("Legend: [ ] = Available, [L] = Locked, [X] = Booked")
    
    def __str__(self) -> str:
        return f"{self.movie.title} at {self.screen.name} - {self.start_time}"


class Booking:
    """Represents a booking."""
    
    def __init__(self, booking_id: str, show: Show, user_id: str, seats: List[ShowSeat]):
        self.id = booking_id
        self.show = show
        self.user_id = user_id
        self.seats = seats
        self.seat_ids = [s.seat.id for s in seats]
        self.status = BookingStatus.PENDING
        self.total_amount = sum(s.price for s in seats)
        self.created_at = datetime.now()
    
    def confirm(self) -> None:
        """Confirm the booking."""
        self.status = BookingStatus.CONFIRMED
    
    def cancel(self) -> None:
        """Cancel the booking and unlock seats."""
        self.status = BookingStatus.CANCELLED
        for seat in self.seats:
            seat.unlock()
    
    def __str__(self) -> str:
        seats_str = " ".join(str(s.seat) for s in self.seats)
        return (f"Booking #{self.id}\n"
                f"Movie: {self.show.movie.title}\n"
                f"Show: {self.show.start_time}\n"
                f"Seats: {seats_str}\n"
                f"Total: ${self.total_amount:.2f}\n"
                f"Status: {self.status.value}")


class BookingSystem:
    """Main booking system."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.movies: Dict[str, Movie] = {}
        self.screens: Dict[str, Screen] = {}
        self.shows: Dict[str, Show] = {}
        self.bookings: Dict[str, Booking] = {}
        self._booking_counter = 0
    
    @classmethod
    def reset_instance(cls) -> None:
        """Reset singleton instance for testing."""
        cls._instance = None
    
    # Movie Management
    def add_movie(self, movie: Movie) -> None:
        self.movies[movie.id] = movie
    
    def get_movie(self, movie_id: str) -> Optional[Movie]:
        return self.movies.get(movie_id)
    
    def search_movies(self, query: str) -> List[Movie]:
        query_lower = query.lower()
        return [m for m in self.movies.values() 
                if query_lower in m.title.lower() or query_lower in m.genre.lower()]
    
    # Screen Management
    def add_screen(self, screen: Screen) -> None:
        self.screens[screen.id] = screen
    
    def get_screen(self, screen_id: str) -> Optional[Screen]:
        return self.screens.get(screen_id)
    
    # Show Management
    def add_show(self, show: Show) -> None:
        self.shows[show.id] = show
    
    def get_show(self, show_id: str) -> Optional[Show]:
        return self.shows.get(show_id)
    
    def get_shows_for_movie(self, movie_id: str) -> List[Show]:
        return sorted([s for s in self.shows.values() if s.movie.id == movie_id],
                     key=lambda s: s.start_time)
    
    # Booking Operations
    def create_booking(self, user_id: str, show_id: str, seat_ids: List[str]) -> Optional[Booking]:
        """Create a booking by locking seats."""
        show = self.shows.get(show_id)
        if show is None:
            raise ValueError(f"Show not found: {show_id}")
        
        if not seat_ids:
            raise ValueError("No seats selected")
        
        # Try to lock the seats
        if not show.lock_seats(seat_ids, user_id):
            return None
        
        # Create booking
        seats = [show.get_show_seat(sid) for sid in seat_ids]
        self._booking_counter += 1
        booking_id = f"BK{self._booking_counter}"
        booking = Booking(booking_id, show, user_id, seats)
        self.bookings[booking_id] = booking
        
        return booking
    
    def confirm_booking(self, booking_id: str, payment_method: str) -> bool:
        """Confirm a booking with payment."""
        booking = self.bookings.get(booking_id)
        if booking is None:
            return False
        
        # Book the seats
        if not booking.show.book_seats(booking.seat_ids, booking.user_id):
            return False
        
        booking.confirm()
        return True
    
    def cancel_booking(self, booking_id: str, user_id: str) -> bool:
        """Cancel a booking."""
        booking = self.bookings.get(booking_id)
        if booking is None or booking.user_id != user_id:
            return False
        
        booking.cancel()
        return True
    
    def get_booking(self, booking_id: str) -> Optional[Booking]:
        return self.bookings.get(booking_id)
    
    def get_user_bookings(self, user_id: str) -> List[Booking]:
        return sorted([b for b in self.bookings.values() if b.user_id == user_id],
                     key=lambda b: b.created_at, reverse=True)
