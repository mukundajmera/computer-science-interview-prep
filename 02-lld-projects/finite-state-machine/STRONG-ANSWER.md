# LLD Solution: Finite State Machine

**Time Target:** 45 minutes

## 1. Requirements Clarification & Boundary Defense
**Say:** "The core requirement is to orchestrate a deterministic flow across a set of states connected by valid transitions. The machine must support a single start state, multiple terminal states, and dynamic extensible additions of states and transitions. I will ensure we can conditionally evaluate transitions via guards and execute side-effects via entry, exit, and transition actions."

## 2. API Design & Generics
**Say:** "To keep the core logic domain-agnostic, I will heavily use parameterized generics (e.g., `<C> Context` in Java) throughout the components. This prevents business models from polluting the FSM engine. I will use a fluent `StateMachineBuilder` API to encapsulate construction, ensuring the engine remains in a valid, immutable configuration at runtime."

## 3. Data Structure & Pattern Rationale
**Say:** "Instead of the classic polymorphic State Pattern—which tightly couples state logic and scatters transition logic, violating the Open-Closed Principle when adding new flows—I will use a Table-Driven Builder approach. The engine centralizes the configuration maps (states and transitions) into the `StateMachine` which evaluates the rules without modifying existing state classes."

## 4. Atomic State Transition Lifecycle
**Say:** "State transitions will follow a strict, sequential lifecycle during the `fire(event, context)` loop:
1. Validate the event matches a transition and evaluate the predicate guard.
2. If allowed, execute the current state's `onExit` actions.
3. Execute the transition's actions.
4. Update the internal `currentState` pointer.
5. Execute the new state's `onEntry` actions.
6. Notify subscribed `StateChangeListener` observers."

## 5. Failure Handling & Concurrency Discussion
**Say:** "If a guard condition fails, the transition simply rejects (`fire` returns false). If a runtime exception occurs during action execution (like an exit or transition action), standard implementations should let it bubble up, disrupting the flow without advancing the machine. Because volatile actions run before updating the `currentState` pointer, the state machine avoids partial rollbacks and remains safely in the original state."
