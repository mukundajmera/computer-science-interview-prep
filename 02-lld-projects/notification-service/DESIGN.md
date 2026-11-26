# Design

The Notification Dispatcher consists of several core components coordinating to ensure messages are delivered efficiently and reliably.

## Class Diagram

```mermaid
classDiagram
    class NotificationDispatcher {
        +dispatch(Notification)
    }
    class Channel {
        <<interface>>
        +send(Message)
    }
    class EmailChannel {
        +send(Message)
    }
    class SMSChannel {
        +send(Message)
    }
    class PushChannel {
        +send(Message)
    }
    class SlackChannel {
        +send(Message)
    }
    class QueueManager {
        +enqueue(Notification, Priority)
        +dequeue() Notification
    }
    class RateLimiter {
        +acquire(ChannelType) bool
    }
    class RetryEngine {
        +scheduleRetry(Notification, Attempt)
    }
    class IntentStore {
        +recordIntent(IdempotencyKey, IntentState)
        +getIntent(IdempotencyKey) IntentState
    }
    
    NotificationDispatcher --> QueueManager
    NotificationDispatcher --> Channel
    NotificationDispatcher --> RateLimiter
    NotificationDispatcher --> RetryEngine
    NotificationDispatcher --> IntentStore
    Channel <|-- EmailChannel
    Channel <|-- SMSChannel
    Channel <|-- PushChannel
    Channel <|-- SlackChannel
```

## Flow Diagram

```mermaid
graph TD
    A["Intake (API with Idempotency Key)"] --> IC{"Idempotency Check"}
    IC -- Exists --> DU["Drop / Return Existing Intent"]
    IC -- New --> IS["Record Delivery Intent"]
    IS --> PREF{"Preference & Routing Check"}
    PREF -- Unsubscribed --> IGN["Ignore / Record Suppressed"]
    PREF -- Subscribed --> QF{"Queue Full?"}
    QF -- Yes --> QOF["Overflow (Record Failed Intent)"]
    QF -- No --> B["Priority Queue (Memory)"]
    B --> C["Worker Threads (Consumers)"]
    C --> D{"Rate Limiter (Check)"}
    D -- Allowed --> E["Dispatch (Channel)"]
    D -- Blocked --> F["Retry Engine (Backoff)"]
    E -- Success --> G["Done (Update Intent: Sent)"]
    E -- Timeout/Unknown --> F
    E -- Permanent Failure --> PF["Done (Update Intent: Failed)"]
    F --> B
```

## Flow
1. **Intake:** The dispatcher receives a notification request with an idempotency key.
2. **Idempotency Check:** Checks `IntentStore` to ensure at most one delivery intent is recorded. Duplicates are dropped.
3. **Routing & Preferences:** Evaluates recipient preferences, channels, and unsubscribe rules explicitly.
4. **Queueing:** If the queue is not full, the request is queued based on priority. Bounded queue overflow preserves the intent state as a failure.
5. **Processing:** Worker threads pull from the queue.
6. **Rate Checking:** Before sending, the rate limiter is checked for the target channel.
7. **Dispatch:** The message is sent to the target channel. It does not promise external exactly-once delivery.
8. **Retry & Failures:** If dispatch fails (e.g., rate limit, fake provider timeout), the retry engine schedules it for later using exponential backoff. Permanent failures and duplicate callbacks update the intent state appropriately.
