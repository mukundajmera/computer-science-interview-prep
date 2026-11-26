#!/usr/bin/env python3
"""Hotel Reservation Demo - v3 Optimized."""
import sys
sys.path.insert(0, '.')
from datetime import date, timedelta
from enums import RoomType
from models import Guest, Room
from hotel import Hotel


def main():
    print("=== Hotel Reservation Demo - v3 Optimized ===\n")
    
    hotel = Hotel("Grand Hotel")
    hotel.add_room(Room("101", RoomType.SINGLE, 1))
    hotel.add_room(Room("201", RoomType.DELUXE, 2))
    hotel.add_room(Room("202", RoomType.DELUXE, 2))
    
    guest = Guest("G001", "John Doe", "john@email.com", "555-1234")
    hotel.register_guest(guest)
    
    check_in = date.today() + timedelta(days=1)
    check_out = date.today() + timedelta(days=4)
    
    available = hotel.search_available(check_in, check_out, RoomType.DELUXE)
    print(f"Available DELUXE rooms: {len(available)}")
    
    if len(available) >= 2:
        rooms_to_book = available[:2]
        print(f"Booking {len(rooms_to_book)} rooms atomically...")
        res = hotel.make_reservation(guest, rooms_to_book, check_in, check_out)
        res.confirm()
        hotel.check_in(res.reservation_id)
        hotel.check_out(res.reservation_id)
    
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    main()
