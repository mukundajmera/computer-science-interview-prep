# Ride Sharing — Common Interview Pitfalls

## 1. No Geospatial Indexing
Brute-force distance scans do not scale for millions of drivers.

## 2. Naive Nearest-Driver Assignment
Ignoring accept/decline loops causes fragile matching behavior.

## 3. Location and Command Path Coupling
High location-write load can starve assignment correctness path.

## 4. Missing Ride State Machine
Ad-hoc status writes allow illegal transitions.

## 5. No Driver Availability Index
Online and available states must be separated to avoid bad offers.

## 6. No Idempotency for Request/Accept
Retries can trigger duplicate trips or inconsistent ownership.

## 7. No Surge/ETA Feedback Loop
Pricing and ETA quality degrade without supply-demand and traffic updates.

---

## Quick Self-Check

- Did I model assignment consistency strongly?
- Did I separate location ingestion from ride lifecycle?
- Did I define legal state transitions?
