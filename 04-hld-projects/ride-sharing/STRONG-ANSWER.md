# Ride Sharing — Strong Interview Answer (45 Minutes)

Say: "I will keep matching, trip state, pricing, and location ingestion separate so the system can make fast dispatch decisions without corrupting the trip lifecycle."

## 0-5 min: Requirements
- Prioritize fare estimate, ride request, driver match, lifecycle tracking.
- Set hard consistency for assignment.

## 5-10 min: Estimates
- Calculate location ingest write pressure.
- Estimate peak request bursts and candidate-query load.

## 10-15 min: API + Entities
- Present rider and driver contracts.
- Define state machine and availability semantics.

## 15-30 min: Architecture
- Show split between location ingestion and assignment/lifecycle path.
- Add geo index, availability index, and notification stream.

## 30-40 min: Deep Dives
1. Candidate ranking and offer loop.
2. Geospatial boundary handling.
3. Surge and ETA update strategy.

## 40-45 min: Trade-offs + Wrap
- Chosen now: strong assignment consistency, eventual location consistency.
- Revisit trigger: match latency tail or offer retry depth exceeds SLO.
