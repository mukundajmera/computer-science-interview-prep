# Amazon Locker — Common Interview Pitfalls

## 1) Treating token as plain string only
Token should own expiry semantics, not just act as an ID.

## 2) Mixing physical state and relationship state casually
Keep compartment state transitions explicit and auditable.

## 3) Allocating out-of-service compartments
Maintenance status must be respected in all allocation paths.

## 4) Time-dependent tests using sleeps
Inject time source in advanced version.

## 5) Generating token before confirming deposit in reserve-confirm flow
Reservation and confirmation should be distinct operations.
