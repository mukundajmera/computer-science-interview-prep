# Distributed Email Service - Follow-Up Questions

## Follow-up questions

### 1. Real-Time Notifications
**Question:** How does the frontend client know when a new email arrives without polling the server constantly?
**Discussion:**
- Implementing a lightweight WebSocket or Server-Sent Events (SSE) connection from the client to a Notification Service.
- When the internal Mail Delivery Agent (MDA) finishes processing an inbound message and writes it to Cassandra, it publishes an event (e.g., via Redis Pub/Sub) to the Notification Service.
- The Notification Service pushes a small payload (e.g., `{ "type": "NEW_MAIL", "folder": "Inbox", "unread_count": 5 }`) to the client, prompting the client to make a standard HTTP GET request to fetch the new data.

### 2. Spam and Abuse Prevention
**Question:** What happens if a bad actor tries to send millions of spam emails through our outbound API?
**Discussion:**
- Implementing strict rate limiting at the API Gateway based on `user_id` and IP address.
- Analyzing outbound patterns asynchronously. If a user exceeds a threshold of bounces, spam complaints from external providers, or suspicious content matching, their account sending privileges are temporarily suspended.
- Discussing reputation management for our own outbound IP addresses (avoiding getting blacklisted by other major providers).

### 3. Handling Kafka Outages
**Question:** Your inbound SMTP worker relies on Kafka to process emails asynchronously. What happens if the Kafka cluster goes down entirely?
**Discussion:**
- The Inbound SMTP Worker must fail closed. If it cannot enqueue the message to Kafka, it must **not** return a `250 OK` to the sender.
- Instead, it should return a transient error code (e.g., `4xx`). The external MTA (the sender) is built to handle this and will automatically queue the message on their side and retry periodically.

### 4. Enterprise Archiving / e-Discovery
**Question:** A corporate client requires the ability for administrators to search across *all* employee mailboxes simultaneously for legal compliance. How does this impact your user-partitioned search design?
**Discussion:**
- User-partitioned search is highly optimized for single-user queries but terrible for cross-user queries.
- For enterprise clients, you would introduce an independent, secondary ingest pipeline that writes to a central Elasticsearch cluster specifically provisioned for that tenant's e-discovery needs, trading off higher infrastructure cost for administrative capability.

## Variants and extensions

### Offline Support
How would you design the system to allow a user to read their recent emails and compose drafts while on an airplane with no internet connection?
*(Focuses on local client-side databases like SQLite/IndexedDB, conflict resolution upon reconnection, and an outbox queue).*

### End-to-End Encryption
How do you modify the architecture if the product requirement is that the server absolutely cannot read the contents of the emails (e.g., ProtonMail)?
*(Focuses on client-side key generation, encrypting payloads before the HTTP POST, and the massive trade-off that server-side full-text search becomes impossible).*

## Interviewer probes to prepare

- "Why did you choose Cassandra over a relational database like PostgreSQL?"
- "Walk me through exactly what happens when I click 'Send' with a 20MB PDF attached."
- "How do you handle a scenario where an email has 50 recipients? Do you store 50 copies of the attachment?"

## Cross-links

- [PROBLEM](./PROBLEM.md)
- [DESIGN](./DESIGN.md)
- [APPROACH](./APPROACH.md)