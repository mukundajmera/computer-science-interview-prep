# Follow-ups

- **Distributed Brokers:** How would you replace the in-memory `PriorityQueue` with a distributed queue like Kafka or RabbitMQ to scale out worker nodes?
- **Dead Letter Queues (DLQ):** Where should messages go when `attempts > max_retries`? (Store them in a DLQ for manual inspection or redrive).
- **Idempotency:** How to prevent sending duplicate notifications if the process crashes just after sending but before committing the status?
