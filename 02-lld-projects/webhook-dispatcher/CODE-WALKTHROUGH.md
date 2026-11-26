# Webhook Dispatcher - Code Walkthrough

## Python Implementation

- `models.py`: Defines `Event`, `Subscriber`, and `WebhookTask`.
- `crypto.py`: Implements `generate_hmac_signature(secret, payload)`.
- `http_client.py`: An interface/mock for HTTP delivery.
- `dispatcher.py`: The `WebhookDispatcher` class handles pub/sub, queuing tasks, and managing the worker pool.
- `worker.py`: The core logic for processing a task, implementing the semaphore acquisition, HMAC generation, error handling, and backoff/DLQ routing.

## Java Implementation

- `Event.java`, `Subscriber.java`: Core models.
- `WebhookDispatcher.java`: Manages the concurrent task queue and executor service.
- `WebhookTask.java`: Implements `Runnable`, containing the logic for delivery, HMAC calculation, retry (with `Math.random()` jitter), and DLQ logic.
- `DestinationSemaphoreMap.java`: Manages a concurrent map of Semaphores keyed by destination URL to restrict outbound concurrency.
