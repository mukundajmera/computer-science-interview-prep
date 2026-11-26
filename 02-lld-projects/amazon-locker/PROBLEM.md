# Amazon Locker

## Problem Statement
Design a locker system where carriers deposit packages into compartments and customers retrieve them using access tokens.

## Requirements and constraints

### Functional requirements
1. Accept package deposits by size (`SMALL`, `MEDIUM`, `LARGE`).
2. Allocate a compatible compartment and generate one access token per successful deposit.
3. Validate token at pickup and open the mapped compartment.
4. Reject invalid/expired tokens.
5. Support staff cleanup of expired deposits.

### Non-functional requirements
- Deterministic IDs and time behavior in tests.
- Clear ownership boundaries between locker orchestration, token lifecycle, and compartment state.
- Java/Python parity for all versions.
- Standard-library-only implementation.

## Out of scope
- delivery routing
- customer notifications (SMS/email)
- payment processing

## Version roadmap
- **v1-basic:** exact-size allocation + token expiry handling.
- **v2-extended:** fallback allocation and compartment maintenance states.
- **v3-optimized:** reservation-confirm workflow with injectable clock.

## Related content
- [Parking Lot](../parking-lot/)
- [State Pattern](../../01-design-patterns/behavioral/state/)
- [Strategy Pattern](../../01-design-patterns/behavioral/strategy/)
