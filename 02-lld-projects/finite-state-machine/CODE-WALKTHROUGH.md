# Finite State Machine - Code Walkthrough

This document outlines the core components implemented in both the Java and Python implementations.

## Interfaces / Type Definitions
- **StateAction / TransitionGuard / StateChangeListener**: In Java, these are interfaces (or functional interfaces). In Python, they are defined using `typing.Callable` to keep the API pythonic and lightweight.
- They all operate on a generic `Context` object `C`, passing domain-specific data transparently.

## StateMachineBuilder
Provides a Fluent API to aggregate `State` and `Transition` objects.
- `withState()`: Registers an available node.
- `withInitialState()`: Sets the anchor state.
- `withEntryAction() / withExitAction()`: Modifies state behavior.
- `withTransition()`: Returns a scoped `TransitionBuilder` which validates its configuration before inserting the configured `Transition` back into the main builder's maps.
- `build()`: Emits a fully assembled `StateMachine`.

## StateMachine
The orchestrator at runtime.
- Holds maps of `states` and `transitions`.
- Tracks the `currentState`.
- `fire(event, context)`: The core evaluation loop. It pulls transitions associated with the `currentState`. It evaluates the guard, and if met, runs `onExit`, transition actions, changes state, runs `onEntry`, and notifies listeners.

## State
Encapsulates metadata (name, is_terminal) and a list of entry and exit actions. Iterates through actions sequentially when invoked by the engine.

## Transition
A connective edge defining source, destination, event trigger, and conditional guard logic.

## Cross-links
- [Design](./DESIGN.md)
- [Rubric](./RUBRIC.md)
