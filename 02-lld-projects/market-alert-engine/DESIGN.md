# Market Alert Engine - Design

## Architecture

The system consists of three primary components:
1.  **Tick Ingestion**: Handles incoming data and routes it to the evaluation engine.
2.  **Rule Engine**: Stores registered rules, evaluates conditions (Composite pattern), and manages cooldowns.
3.  **Notification Sinks**: Dispatches alerts to configured channels (Observer pattern).

## Class Diagram

```mermaid
classDiagram
    class Tick {
        +String symbol
        +double price
        +int volume
        +long timestamp
    }

    class Condition {
        <<interface>>
        +evaluate(Tick tick) boolean
    }

    class PriceCondition {
        +double threshold
        +Operator operator
        +evaluate(Tick tick) boolean
    }

    class AndCondition {
        +Condition left
        +Condition right
        +evaluate(Tick tick) boolean
    }

    class OrCondition {
        +Condition left
        +Condition right
        +evaluate(Tick tick) boolean
    }

    class NotCondition {
        +Condition condition
        +evaluate(Tick tick) boolean
    }

    class AlertRule {
        +String ruleId
        +String symbol
        +Condition condition
        +long cooldownMs
        +List~Sink~ sinks
    }

    class Sink {
        <<interface>>
        +send(AlertRule rule, Tick tick)
    }

    class AlertEngine {
        -Map~String, List~AlertRule~~ rulesBySymbol
        -Map~String, Long~ lastAlertTimes
        +addRule(AlertRule rule)
        +processTick(Tick tick)
    }

    Condition <|-- PriceCondition
    Condition <|-- AndCondition
    Condition <|-- OrCondition
    Condition <|-- NotCondition
    AlertEngine --> AlertRule
    AlertRule --> Condition
    AlertRule --> Sink
    AlertEngine --> Tick
```

## Cross-links
- [Problem Statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Rubric](./RUBRIC.md)
- [Pitfalls](./PITFALLS.md)
- [Follow-ups](./FOLLOW-UPS.md)
