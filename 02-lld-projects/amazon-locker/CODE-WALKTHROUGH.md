# Amazon Locker Code Walkthrough

## Deposit flow (v1)
1. Validate requested package size.
2. Find an available matching compartment.
3. Mark compartment occupied.
4. Generate token with expiry.
5. Persist token in in-memory mapping.

## Pickup flow
1. Lookup token.
2. Reject if missing or expired.
3. Open/release mapped compartment.
4. Remove token from mapping.

## v2 extension flow
- Allocation now delegates to `AllocationPolicy`.
- `OUT_OF_SERVICE` compartments are skipped automatically.

## v3 reservation flow
1. `reserveCompartment(size)` marks selected compartment as `RESERVED`.
2. `confirmDeposit(reservationId)` transitions to `OCCUPIED` and emits token.
3. timed-out reservations are auto-expired via sweep.
