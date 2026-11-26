# Finite State Machine - Design

## System Architecture

The FSM Engine utilizes the Builder Pattern to construct the state transitions and encapsulate the runtime state inside a `StateMachine` instance. The design heavily relies on parameterized Generics (e.g. `<C> Context`) to remain domain-agnostic. 

We utilize the Observer Pattern to push transition notifications via `StateChangeListener`.

## Class Diagram

```mermaid
classDiagram
    class StateMachine~C~ {
        -Map states
        -Map transitions
        -State currentState
        -List listeners
        +start(context: C)
        +fire(event: String, context: C) boolean
        +getCurrentState() String
        +isTerminal() boolean
    }
    
    class StateMachineBuilder~C~ {
        -Map states
        -Map transitions
        +withState(name: String, isTerminal: boolean)
        +withTransition() TransitionBuilder
        +build() StateMachine
    }
    
    class State~C~ {
        -String name
        -boolean isTerminal
        -List entryActions
        -List exitActions
        +onEntry(context: C)
        +onExit(context: C)
    }
    
    class Transition~C~ {
        -String fromState
        -String toState
        -String event
        -TransitionGuard guard
        +evaluateGuard(context: C) boolean
        +executeActions(context: C)
    }
    
    StateMachineBuilder --> StateMachine : creates
    StateMachine "1" *-- "many" State : manages
    StateMachine "1" *-- "many" Transition : manages
    Transition --> State : transitions between
```

## Sequence Diagram: Event Firing Lifecycle

```mermaid
sequenceDiagram
    participant Client
    participant FSM as StateMachine
    participant CurrentState as State (From)
    participant Trans as Transition
    participant NextState as State (To)
    
    Client->>FSM: fire("EVENT", context)
    FSM->>Trans: evaluateGuard(context)
    alt Guard allows
        Trans-->>FSM: true
        FSM->>CurrentState: onExit(context)
        FSM->>Trans: executeActions(context)
        FSM->>NextState: onEntry(context)
        FSM-->>Client: true (Transition successful)
    else Guard rejects
        Trans-->>FSM: false
        FSM-->>Client: false (Transition rejected)
    end
```

## Cross-links
- [Problem Statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Code Walkthrough](./CODE-WALKTHROUGH.md)
