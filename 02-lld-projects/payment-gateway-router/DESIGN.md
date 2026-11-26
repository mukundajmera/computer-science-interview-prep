# Payment Gateway Router - Design

## Cross-links
- [Problem Statement](PROBLEM.md)
- [Approach](APPROACH.md)
- [Code Walkthrough](CODE-WALKTHROUGH.md)
- [Rubric](RUBRIC.md)
- [Pitfalls](PITFALLS.md)
- [Follow-Ups](FOLLOW-UPS.md)

## System Architecture

The Gateway Router acts as a proxy between incoming payment requests and third-party gateways. Requests flow through the router, pass idempotency checks, get assigned a gateway via the routing strategy, and are monitored by circuit breakers.

## Class Diagram

```mermaid
classDiagram
    class GatewayRouter {
        -List~PaymentGateway~ gateways
        -RoutingStrategy routingStrategy
        -IdempotencyStore idempotencyStore
        +routePayment(PaymentRequest) PaymentResponse
    }
    class PaymentGateway {
        <<interface>>
        +processPayment(PaymentRequest) PaymentResponse
        +getSuccessRate() double
        +recordMetrics(boolean)
    }
    class RoutingStrategy {
        <<interface>>
        +route(List~PaymentGateway~, PaymentRequest) PaymentGateway
    }
    class IdempotencyStore {
        +lockOrCheck(String) boolean
        +getState(String) State
        +update(String, State, PaymentResponse)
    }
    class CircuitBreaker {
        +allowRequest() boolean
        +recordSuccess()
        +recordFailure()
    }
    GatewayRouter --> PaymentGateway
    GatewayRouter --> RoutingStrategy
    GatewayRouter --> IdempotencyStore
    PaymentGateway --> CircuitBreaker
```

## Sequence Diagram: Payment Routing with Fallback

```mermaid
sequenceDiagram
    participant Client
    participant Router
    participant IdempotencyStore
    participant RoutingStrategy
    participant Gateway1
    participant Gateway2

    Client->>Router: routePayment(PaymentRequest)
    Router->>IdempotencyStore: lockOrCheck(idempotencyKey)
    IdempotencyStore-->>Router: locked (IN_PROGRESS)
    
    Router->>RoutingStrategy: route([Gateway1, Gateway2])
    RoutingStrategy-->>Router: Gateway1

    Router->>Gateway1: processPayment()
    Gateway1-->>Router: TIMEOUT
    
    Router->>RoutingStrategy: route([Gateway2])
    RoutingStrategy-->>Router: Gateway2
    
    Router->>Gateway2: processPayment()
    Gateway2-->>Router: SUCCESS
    
    Router->>IdempotencyStore: update(COMPLETED, Response)
    Router-->>Client: PaymentResponse(SUCCESS, Gateway2)
```

## Circuit Breaker State Machine

```mermaid
stateDiagram-v2
    [*] --> CLOSED
    CLOSED --> OPEN : failures >= threshold
    OPEN --> HALF_OPEN : time >= resetTimeout
    HALF_OPEN --> CLOSED : success
    HALF_OPEN --> OPEN : failure
```
