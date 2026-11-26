# Webhook Dispatcher - Problem Statement

## Overview
Design and implement a Reliable Webhook Dispatcher & Event Delivery Engine. The system accepts events and dispatches them as webhooks to registered subscribers via HTTP. It must handle delivery failures, secure payloads with signatures, and protect destination endpoints from being overwhelmed.

## Requirements

### Core Capabilities
1. **Subscription Management:** Subscribers can be added or removed at runtime. Subscribers listen to specific event topics or patterns.
2. **Security:** Payloads must be signed using RFC 2104 HMAC-SHA256 signature generation. The signature should be included in the `X-Hub-Signature-256` header.
3. **Async Dispatch:** Events should be delivered via an async worker pool dispatch mechanism.
4. **Retry & Backoff:** If a delivery fails, it must be retried using exponential backoff with full jitter to avoid thundering herd problems.
5. **Dead Letter Queue (DLQ):** After exhaustion of the retry budget, failed deliveries must be routed to a DLQ for manual inspection or later reprocessing.
6. **Concurrency Control:** The system must enforce per-destination concurrency throttling/semaphores to prevent overwhelming downstream endpoints.

### Constraints
* Implementation must rely solely on the standard library (no external frameworks or libraries for core logic).
* The solution should include an in-memory queue for task buffering.
