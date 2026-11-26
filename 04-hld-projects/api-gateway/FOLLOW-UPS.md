# API Gateway Follow-ups

## Follow-up Questions
1. How do you handle configuration updates without restarting nodes?
2. How do we prevent 'retry storms' across the entire gateway?

## Design Contract
- Explores extensions to the design contract in [DESIGN.md](./DESIGN.md).

## Failure Trace
- Discusses advanced failure scenarios like cascading failures due to retry storms.

## Beginner vs Staff
### Beginner
- Might answer configuration updates with simple polling.
### Staff
- Would propose event-driven push mechanisms for config updates and circuit breakers to prevent retry storms.
