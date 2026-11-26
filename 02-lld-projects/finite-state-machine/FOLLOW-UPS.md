# Finite State Machine - Follow-Up Questions

## Follow-up questions

1. **How would you support "any" state transitions? (e.g., transition to ERROR from ANY state)**
   - *Answer strategy*: Discuss adding a special wildcard `*` state identifier to the transitions map, and updating the `fire` method to check wildcard transitions if no specific transition matches the event.

2. **How do you handle cyclic transitions where a state transitions to itself?**
   - *Answer strategy*: Explain that cyclic transitions are just standard transitions where `toState` == `fromState`. The FSM should normally run `onExit` and `onEntry` for these, unless explicitly configured as an "internal transition" which skips entry/exit actions.

## Variants and extensions

- **Hierarchical / Nested State Machines (Statecharts)**
  - Extend the design so that a `State` can internally contain an entire `StateMachine`. If an event is not handled by the nested state machine, it bubbles up to the parent machine.
- **Asynchronous Event Queues**
  - Wrap the StateMachine in an Actor pattern. Instead of `fire` executing synchronously on the caller's thread, events are placed in an inbox queue and processed strictly sequentially by a background worker, preventing concurrency issues natively.
- **Serialization and Persistent Hydration**
  - Discuss how to serialize a live state machine. Usually, you only need to serialize the `currentState` string and the `Context` data. The state machine topology (states, transitions, actions) is stateless code configuration built at startup.

## Interviewer probes to prepare

- *Probe*: "What happens if a transition action throws a runtime exception?"
  - *Response*: It disrupts the execution flow. Depending on requirements, we might want to catch these and trigger an automatic transition to an `ERROR` state, or let it bubble up, meaning the state remains unchanged (as the `currentState` pointer updates at the end).

## Cross-links
- [Problem Statement](./PROBLEM.md)
- [Pitfalls](./PITFALLS.md)
