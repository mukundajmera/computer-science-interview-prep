# Finite State Machine - Approach

## Entity Identification
The core logic of an FSM naturally maps to states, transitions, and the overarching machine. We identified the need for `State`, `Transition`, `StateMachine`, and a corresponding generic `Context`.

## State Pattern vs Table-driven Transition Matrix
- **State Pattern**: Implements polymorphic state behaviors but often scatters transition logic. Adding a new transition requires altering existing state classes, violating the Open-Closed Principle for the overall orchestration.
- **Table-Driven / Builder Approach**: Centralizes the configuration map (states and transitions) into the FSM. This makes it far easier to define complex, dynamic flows at runtime. We use a **Builder** to construct the internal tables (maps of states and transitions), allowing an immutable or tightly controlled StateMachine to evaluate the rules.

## Fluent Builder API Design
A Fluent Builder makes the engine much simpler to consume. We chain configuration steps like `withState()`, `withEntryAction()`, and provide an inner `TransitionBuilder` via `withTransition().from().to().on().create()`. This API design prevents partial or invalid configuration.

## Atomic State Transition Semantics
State transitions should be treated sequentially:
1. Validate event and guard conditions.
2. If valid, execute the current state's `onExit` actions.
3. Execute the `Transition` actions.
4. Update the current state to the new state.
5. Execute the new state's `onEntry` actions.
6. Notify listeners.

## Error Handling & Rollback on Guard/Action Failure
If a guard fails, the transition is simply rejected (`fire` returns false). If an exception occurs during an exit, transition, or entry action, the engine must either bubble the exception up immediately or employ a try-catch mechanism. In this basic design, exceptions will bubble up naturally to notify the calling thread, meaning domain code must ensure action resilience to avoid disrupting the thread.

## Cross-links
- [Problem Statement](./PROBLEM.md)
- [Design](./DESIGN.md)
