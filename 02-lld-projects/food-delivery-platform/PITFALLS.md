# Pitfalls: Food Delivery Platform

## 1. Invalid State Transitions
Failing to enforce a strict order state machine. For instance, allowing an order to jump from `CREATED` directly to `DELIVERED`, or allowing a `DELIVERED` order to be marked as `PREPARING`. This leads to inconsistent system state and incorrect billing.
*Failure Trace:* Thread 1 (Restaurant) transitions order to `PREPARING`. Thread 2 (Network delay from driver app) simultaneously attempts to force transition to `DELIVERED`. Without state assertions (`compareAndSet` or `_lock`), the order skips intermediate billing states and inventory checks.

## 2. Driver Double-Booking
In a concurrent environment, finding an available driver and assigning them must be an atomic operation (or involve optimistic locking). A common pitfall is a race condition where a search phase identifies driver A as available, and two concurrent order dispatchers assign driver A simultaneously.
*Failure Trace:* Order 1 requests closest driver and gets Driver A. Order 2 simultaneously requests closest driver, getting Driver A before Order 1 has marked Driver A as unavailable. Driver A is now assigned two incompatible orders.

## 3. Hardcoded Dispatch/Pricing Logic
Embedding the surge pricing multiplier or the nearest-driver calculation directly inside the `Order` or `DriverManager` classes. This violates the Open/Closed Principle and makes it hard to A/B test new strategies.

## 4. Floating Point Inaccuracies
Using `float` or `double` naively for currency calculations can lead to precision issues. While acceptable in basic LLD interviews, in production, a dedicated `Money` type or integer representation of cents is necessary.
