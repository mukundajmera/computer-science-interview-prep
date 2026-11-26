# Finite State Machine - Interview Scoring Rubric

## Scoring Dimensions

| Dimension | Weight | Strong signal |
| --- | --- | --- |
| **API Design & Generics** | 25% | Uses fluent interfaces (Builder), applies generics appropriately for the context without domain leakage, code reads cleanly. |
| **State Management** | 25% | Correctly handles the transition lifecycle (Exit -> Transition Actions -> State Update -> Entry). Prevents invalid transitions. |
| **Extensibility** | 20% | Open-closed principle is respected; adding states or transitions does not require modifying core logic classes. |
| **Testing & Robustness** | 20% | Thoroughly tests guards, multiple actions, missing states, and terminal condition boundaries. |
| **Clean Code** | 10% | Readable, DRY, good naming conventions, avoids massive nested conditionals. |

## Performance Bands

- **Strong Hire**: Implements a robust Builder pattern, handles generics flawlessly, correctly orchestrates entry/exit/transition actions, and includes comprehensive tests covering edge cases.
- **Hire**: Meets core functional requirements, uses an object-oriented approach, but API might be slightly clunky or missing fluent chaining. Generics might be loosely typed (e.g. `Object` instead of `<C>`).
- **Lean No Hire**: Core transitions work but code tightly couples the FSM to a specific domain model. Misses execution of actions during the correct lifecycle phase.
- **No Hire**: Fails to implement dynamic state additions (hardcodes transitions). 

## Hard Failure Gates
- **Non-atomic state transitions**: Updating the internal `currentState` pointer before running exit actions or guard evaluations.
- **Terminal state violation**: Allowing a transition to fire when the engine is already in a terminal state.
- **Ignoring guard failures**: Executing state changes even when `evaluateGuard` returns false.

## Cross-links
- [Code Walkthrough](./CODE-WALKTHROUGH.md)
- [Pitfalls](./PITFALLS.md)
