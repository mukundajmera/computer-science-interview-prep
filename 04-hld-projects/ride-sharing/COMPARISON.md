# Ride Sharing — Comparison

## Ride Sharing vs Ticketing Platform

| Concern | Ride Sharing | Ticketing Platform |
|---|---|---|
| Inventory model | Dynamic driver availability | Static seat inventory |
| Assignment pressure | Continuous realtime | Event-driven burst windows |
| Consistency target | Driver assignment correctness | Seat hold/booking correctness |

## Ride Sharing vs Quick Commerce Delivery

| Concern | Ride Sharing | Quick Commerce |
|---|---|---|
| Routing basis | Driver proximity and ETA | Fulfillment center proximity and stock |
| Lifecycle | Trip state transitions | Order and reservation states |
| Realtime stream | Driver location | Availability and delivery status |

## Ride Sharing vs Collaborative Editor

| Concern | Ride Sharing | Collaborative Editor |
|---|---|---|
| Realtime payload | Geolocation + status | Operations + presence |
| Conflict model | Assignment contention | Concurrent edit convergence |
| Session affinity | Geo zone and ride ID | Document ID |
