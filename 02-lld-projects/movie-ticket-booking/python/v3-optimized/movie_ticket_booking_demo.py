#!/usr/bin/env python3
"""
Movie Ticket Booking System - V1 Basic Demo

Demonstrates basic booking functionality.
"""

from datetime import datetime, timedelta
from booking_entities import (
    Movie, Screen, Show,
    BookingSystem
)


def main():
    print("=== Movie Ticket Booking System V1 - Basic Demo ===\n")
    
    # Reset singleton for fresh start
    BookingSystem.reset_instance()
    system = BookingSystem()
    
    # Setup movies
    avengers = Movie("M1", "Avengers: Endgame", 181, "Action/Sci-Fi")
    inception = Movie("M2", "Inception", 148, "Sci-Fi/Thriller")
    system.add_movie(avengers)
    system.add_movie(inception)
    print(f"Added movies: {avengers}, {inception}")
    
    # Setup screens
    screen1 = Screen.create_standard_screen("S1", "Screen 1", 
                                           vip_rows=1, premium_rows=2, regular_rows=3,
                                           seats_per_row=8)
    system.add_screen(screen1)
    print(f"Added screen: {screen1.name} with {screen1.capacity} seats")
    
    # Setup shows
    show_time = datetime.now() + timedelta(hours=2)
    show1 = Show("SH1", avengers, screen1, show_time)
    system.add_show(show1)
    print(f"Added show: {show1}")
    
    # Display seat map
    show1.display_seats()
    
    # Search for movies
    print("\n--- Searching for 'Avengers' ---")
    results = system.search_movies("Avengers")
    for movie in results:
        print(f"  Found: {movie}")
    
    # Create a booking
    print("\n--- Creating Booking ---")
    seat_ids = ["B3", "B4"]
    booking = system.create_booking("user1", "SH1", seat_ids)
    
    if booking:
        print(f"Booking created successfully!")
        print(booking)
        
        # Show locked seats
        show1.display_seats()
        
        # Confirm with payment
        print("\n--- Processing Payment ---")
        if system.confirm_booking(booking.id, "CREDIT_CARD"):
            print("Payment successful! Booking confirmed.")
            print(booking)
        else:
            print("Payment failed!")
        
        # Show booked seats
        show1.display_seats()
    else:
        print("Failed to create booking - seats not available")
    
    # Try booking same seats again (should fail)
    print("\n--- Trying to book same seats again ---")
    booking2 = system.create_booking("user2", "SH1", seat_ids)
    if booking2:
        print("Booking created (unexpected)")
    else:
        print("Cannot book - seats already taken ✓")
    
    # Book different seats
    print("\n--- User2 booking different seats ---")
    booking3 = system.create_booking("user2", "SH1", ["C1", "C2", "C3"])
    if booking3:
        print(f"Booking created: {booking3.id}")
        system.confirm_booking(booking3.id, "DEBIT_CARD")
        print("Confirmed!")
    
    # Final seat map
    show1.display_seats()
    
    # Show user bookings
    print("\n--- User1's Bookings ---")
    for b in system.get_user_bookings("user1"):
        print(f"  {b.id}: {b.status.value}")
    
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    main()
