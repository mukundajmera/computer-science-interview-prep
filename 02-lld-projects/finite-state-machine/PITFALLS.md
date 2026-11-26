# Finite State Machine - Common Pitfalls

## 1. Tight coupling of state logic to domain classes
- **Signal**: The StateMachine or State classes directly import domain objects like `Order` or `Payment`.
- **Root Cause**: Failure to use Generics (`<C>`) or a generic interface to abstract the data being passed through the FSM.
- **Mitigation**: Use a parameterized type for the context that is passed to all guards and actions.

## 2. Lack of Context Parameter
- **Signal**: Guards and actions take no arguments and rely on global state or closures.
- **Root Cause**: Designing the FSM in a vacuum without considering how real-world transitions evaluate external dynamic data.
- **Mitigation**: Ensure `fire(event, context)` passes the context object strictly through the lifecycle down to guards and actions.

## 3. Deadlocks during concurrent transition fire
- **Signal**: The system hangs when multiple threads attempt to fire events simultaneously.
- **Root Cause**: Improper use of coarse-grained synchronization blocks around the entire FSM, leading to deadlocks if actions attempt to call back into the state machine.
- **Mitigation**: Standard implementations avoid locking the entire machine, or enforce a strict single-threaded queue/actor model for processing events. 

## 4. Unhandled exceptions in exit actions leaving machine in corrupted state
- **Signal**: An exception in an `onExit` action causes the `fire` method to abort, but the application retries and fails because internal FSM pointers are broken.
- **Root Cause**: Transition lifecycle executes out of order (e.g. updating internal state before running actions).
- **Mitigation**: Always perform volatile actions before updating the hard state pointer, or wrap critical state updates in transactional bounds if supported.

## Cross-links
- [Rubric](./RUBRIC.md)
- [Follow-Ups](./FOLLOW-UPS.md)
