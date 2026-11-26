# Hotel Reservation System

## Problem Statement

Design a Hotel Reservation System that allows guests to search for available rooms, make reservations, manage bookings, and handle check-in/check-out processes. The system should support different room types, pricing strategies, and customer management.

## Functional Requirements

1. **Room Management**: Add/remove rooms, manage room types and amenities
2. **Search Availability**: Search for available rooms by date range, room type, and capacity
3. **Make Reservation**: Book rooms for specified dates with guest information
4. **Cancel Reservation**: Cancel existing reservations with refund policy
5. **Check-in/Check-out**: Process guest check-in and check-out
6. **Payment Processing**: Handle deposits, payments, and refunds
7. **Guest Management**: Store guest profiles and booking history
8. **Pricing Management**: Support different pricing strategies (seasonal, weekday/weekend)

## Non-Functional Requirements

1. **Concurrency**: Handle concurrent booking requests without double-booking
2. **Consistency**: Ensure room availability is always accurate
3. **Scalability**: Support multiple hotels and thousands of rooms
4. **Audit Trail**: Log all booking activities

## Constraints & Assumptions

1. Reservations are per-room-night (one room, one night)
2. Check-in time: 3:00 PM, Check-out time: 11:00 AM
3. Cancellation within 24 hours of check-in: 50% charge
4. Cancellation more than 24 hours before: Full refund
5. Maximum stay: 30 nights
6. Room types: SINGLE, DOUBLE, DELUXE, SUITE

## Clarifying Questions for Interview

1. **Q: Should we support multiple hotels?**
   A: Start with single hotel, design for extensibility.

2. **Q: How should we handle overbooking?**
   A: Prevent overbooking with proper locking mechanisms.

3. **Q: What payment methods should we support?**
   A: Abstract payment processing for flexibility.

4. **Q: Should we support group bookings?**
   A: Yes, in v2 we add support for booking multiple rooms.

## Sample Interactions

```
=== Welcome to Grand Hotel ===

Guest: Search for available rooms
Check-in Date: 2024-03-15
Check-out Date: 2024-03-18
Room Type: DOUBLE
Number of Guests: 2

Found 5 available rooms:
1. Room 201 - Double Room - $150/night
2. Room 205 - Double Room - $150/night
3. Room 301 - Double Deluxe - $200/night
...

Guest selects Room 201
Total for 3 nights: $450 + tax = $495.00

Confirm booking? Yes

=== Reservation Confirmed ===
Confirmation #: RES-2024-001234
Guest: John Smith
Room: 201 (Double)
Check-in: March 15, 2024 at 3:00 PM
Check-out: March 18, 2024 at 11:00 AM
Total: $495.00
Deposit Paid: $99.00

Thank you for your reservation!
```
