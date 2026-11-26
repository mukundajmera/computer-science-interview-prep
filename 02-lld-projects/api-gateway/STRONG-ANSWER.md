# Strong Answer: API Gateway

## Core Architecture and Principles

**Say:** "To design the API Gateway, I've structured it around three main responsibilities: Request Routing, a Filter Chain for cross-cutting concerns, and Circuit Breaking for resiliency. 

The core flow is built around a Chain of Responsibility pattern. When a request arrives, it first traverses a list of Pre-Filters. This allows us to handle concerns like Authentication and Rate Limiting centrally. If any Pre-Filter fails the request—for instance, returning a 429 Too Many Requests—the gateway short-circuits, skipping backend dispatch entirely. Crucially, I've designed the `handle` method to apply Post-Filters in reverse order regardless of whether the request succeeded or short-circuited. This ensures that features like request duration logging are accurately captured for all traffic. Note that this implementation represents an interview proof-sketch/simulation and is not a deployment-ready system."

## Resiliency and State Management

**Say:** "For resiliency, I integrated a Circuit Breaker pattern directly at the dispatch layer. The Circuit Breaker tracks consecutive failures and flips to an OPEN state to protect struggling backends. 

A critical design decision I made here is isolating gateway-generated errors from backend errors. If the Rate Limiting filter rejects a request, that 429 response does not increment the backend's failure count. We only want to penalize the backend for actual dispatch failures like 500 errors or timeouts. 

To handle concurrency, especially in the Rate Limiter and Circuit Breaker, I utilized thread-safe primitives. The Circuit Breaker uses atomic variables to manage its state transitions safely, ensuring that when the reset timeout expires, an atomic compare-and-set allows exactly one request through in the HALF_OPEN state, preventing a thundering herd against a recovering backend. This creates a coherent path from simple beginner routing to staff-level concurrent state management."
