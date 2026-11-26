# Ride Sharing System (Uber/Ola)

## Problem Statement

Design a ride-sharing system similar to Uber or Ola that allows riders to request rides and drivers to accept them. The system should handle ride matching, fare calculation, trip management, and driver ratings.

## Functional Requirements

1. **User Management**
   - Riders can register and request rides
   - Drivers can register and update their availability
   - Track driver location and status

2. **Ride Request**
   - Riders specify pickup and drop-off locations
   - Support different vehicle types (Car, Auto, Bike)
   - Real-time ride request handling

3. **Driver Matching**
   - Match nearest available driver to rider
   - Support multiple matching algorithms
   - Driver can accept or reject ride requests

4. **Trip Management**
   - Track trip states (Requested → Matched → Started → Completed)
   - Real-time location updates
   - Trip history for riders and drivers

5. **Fare Calculation**
   - Base fare + distance-based + time-based pricing
   - Support surge pricing during peak hours
   - Different rates for vehicle types

6. **Ratings & Reviews**
   - Riders can rate drivers after trip completion
   - Drivers can rate riders
   - Maintain average ratings

## Non-Functional Requirements

1. **Scalability**: Handle thousands of concurrent ride requests
2. **Low Latency**: Quick driver matching (within seconds)
3. **Reliability**: No lost ride requests
4. **Concurrency**: Handle concurrent driver assignments
5. **Real-time**: Live location tracking

## Constraints & Assumptions

- Single city operation initially
- GPS coordinates represented as (latitude, longitude)
- Distance calculated using Euclidean distance (simplified)
- Drivers manually update availability
- Payment processing is out of scope

## Sample Interactions

```
=== Ride Sharing Demo ===

1. Driver Registration:
   Driver D1 (John) registered with CAR at location (12.9, 77.6)
   Driver D2 (Mike) registered with BIKE at location (12.8, 77.5)

2. Rider requests ride:
   Rider R1 requests ride from (12.85, 77.55) to (12.95, 77.65)
   Vehicle type: CAR

3. System matches driver:
   Matched with Driver D1 (John) - 0.5 km away
   Estimated fare: $15.50

4. Trip lifecycle:
   Trip REQUESTED → MATCHED → IN_PROGRESS → COMPLETED

5. Fare breakdown:
   Base fare: $5.00
   Distance (10 km): $10.00
   Time (15 min): $2.25
   Surge (1.0x): $0.00
   Total: $17.25

6. Rating:
   Rider rated driver 5 stars
   Driver's new average: 4.8
```

## Key Design Challenges

1. **Real-time Matching**: Efficiently find nearest available driver
2. **Concurrency**: Multiple riders requesting same driver
3. **State Management**: Handle trip state transitions
4. **Pricing**: Dynamic surge pricing based on demand
5. **Location Updates**: Frequent location tracking
