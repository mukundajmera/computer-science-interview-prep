# Problem Statement

Design a robust Notification Dispatcher. The system should manage multiple notification channels (Email, SMS, Push, Slack) and handle sending messages to users based on user preferences.

## Requirements

1. **Multi-channel Support:** The system should support sending notifications via Email, SMS, Push, and Slack.
2. **User Preference Matrix:** Users should be able to specify their preferred channel(s) for different types of notifications.
3. **Channel Rate Limits:** The system should respect rate limits for each channel to avoid being blocked by external providers.
4. **Priority Queues:** Notifications should be assigned priorities (e.g., HIGH, MEDIUM, LOW) and processed accordingly.
5. **Retry with Exponential Backoff:** Failed notifications should be retried using exponential backoff to handle transient failures.

## Acceptance criteria
1. Same event/recipient/channel idempotency key produces at most one recorded delivery intent; routing/preference/unsubscribe priorities are explicit.
2. Fake provider timeout/unknown outcome, retry, permanent failure, duplicate callback and bounded queue overflow preserve intent state without promising external exactly-once delivery.
3. Version-specific APIs and deterministic fixture inputs/expected outputs are fixed before implementation; no production/security promise is inferred.
