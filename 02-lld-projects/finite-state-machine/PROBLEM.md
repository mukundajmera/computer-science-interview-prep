# Finite State Machine - Problem Statement

## Functional Requirements
- **Single start state**: The FSM must initiate from a designated start state.
- **Multiple terminal states**: The FSM should support ending execution upon reaching one of the configured terminal states.
- **Extensible dynamic additions**: Allow dynamic registration of new states and transitions via a robust API (such as a Builder).
- **Transition guards**: Support for conditional evaluation using predicates (e.g., `Predicate<Context>` in Java, `Callable[[Context], bool]` in Python) before a transition is allowed.
- **Entry, Exit, and Transition actions**: Support configurable actions (e.g., `Consumer<Context>`, `Callable[[Context], None]`) that execute on entering a state, exiting a state, or during a transition.
- **Notification controls**: Offer both a global and per-state mechanism to toggle transition notifications.
- **Event firing API**: A structured API to trigger state transitions by passing an event identifier and a domain-specific context.

## Non-functional Requirements
- **Thread Safety**: Core components might need to handle concurrent state evaluation/transitions depending on the execution model, but the primary focus is on object-oriented encapsulation and correct transitions.
- **Extensibility**: It should be simple to add new states and transition definitions without modifying the core StateMachine engine (Open-Closed Principle).
- **Robustness**: Failure to evaluate guards or unexpected errors in action executions should not leave the StateMachine in an inconsistent, partial state.

## Constraints
- Minimal standard library usage (Java 11+ and Python 3.8+). No external dependencies beyond unit testing frameworks.
- Core logic needs to remain purely focused on the FSM engine, unpolluted by any specific business domain code.

## Clarifying Questions
- Q: What happens when an event matches multiple transitions from the current state?
  A: The first matching transition with a satisfied guard condition should be selected.
- Q: Should the engine support historical transitions or state rollbacks?
  A: No, standard FSM behavior focuses on forward progression only. Errors in transitions typically just refuse to change the state.

## Core Entities
- **State**: Represents a node in the state machine, can have entry/exit actions, and can be marked terminal.
- **Transition**: Connects states based on a trigger event, holds an optional guard and a set of transition actions.
- **StateMachine**: The central engine maintaining current state, processing events, and handling notifications.
- **StateMachineBuilder**: Fluent API for constructing states, transitions, and assembling the engine.
- **Context**: A generic generic domain object passed through all guards and actions.
