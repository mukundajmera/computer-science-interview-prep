# Rideshare Matching Engine - Problem Statement

## Problem
Design and implement a Rideshare Driver-Rider Matching & Dispatch Engine. The engine needs to manage the driver state lifecycle, handle rider requests concurrently without duplicate driver assignment, efficiently calculate nearest drivers spatially, and adjust pricing dynamically through a surge multiplier.

## Requirements
1. **Driver Lifecycle FSM**: 
   Transitions: IDLE -> ACCEPTED -> ARRIVED -> IN_TRIP -> COMPLETED -> IDLE.
2. **Atomic Driver Allocation**: 
   When multiple riders request rides concurrently, ensure that a driver is uniquely assigned to at most one rider. No double-assignments.
3. **Nearest-Neighbor Spatial Ranking**: 
   Find and rank the nearest drivers to the rider based on Euclidean distance.
4. **Supply/Demand Surge Pricing**: 
   Dynamic surge pricing multiplier based on available supply of drivers and active ride demand.

## Constraints
* No external frameworks or databases (use in-memory data structures).
* Thread-safe behavior.
* Standard libraries only.
