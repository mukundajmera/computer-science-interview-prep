# Distributed Email Service - Comparison

## Email vs. Real-Time Chat (WhatsApp/Slack)

Both systems deliver messages from one user to another, but their underlying architectures are driven by fundamentally different product requirements and legacy constraints.

| Concern | Distributed Email Service | Real-Time Chat System |
|---|---|---|
| **Primary Protocol** | HTTP for clients, SMTP for federation. | WebSockets or long-polling HTTP for clients. Proprietary protocols for federation (if any). |
| **Latency Expectation** | Seconds to minutes (asynchronous). | Milliseconds (synchronous feel). |
| **State Management** | Mostly stateless backend for clients; state is pulled on demand. | Highly stateful; servers maintain active connections for every online user to push data instantly. |
| **Message Size** | Large (up to 25MB attachments, rich HTML bodies). | Small (plain text, JSON metadata; attachments are usually uploaded out-of-band). |
| **Federation** | Global and mandatory (must talk to Yahoo, Microsoft, etc.). | Usually closed ecosystems (Slack only talks to Slack). |
| **Search** | Deep, full-text search over years of history is a core feature. | Search is secondary; real-time delivery is the priority. |

## Email Provider vs. SMTP Relay Service (SendGrid/Mailgun)

While both handle email, a full provider (like Gmail) manages user state, whereas a relay service is primarily a transactional pipeline.

| System | Similarity | Key difference |
|---|---|---|
| **Distributed Email Service** | Processes outbound SMTP, handles bounces, requires spam filtering. | Must maintain billions of permanent user mailboxes, manage folder state, and provide high-performance search indexes. |
| **SMTP Relay Service** | Processes outbound SMTP, handles bounces, requires spam filtering. | Stateless regarding the message after delivery. Does not provide an "Inbox" or long-term searchable storage for the end-user. |

## Reuse Guidance

- **Attachment Storage:** The pattern of separating large blobs (S3) from metadata (Cassandra) used here is identical to how you should design a **Chat Service** for image uploads or a **Social Media Feed** for video posts.
- **User-Partitioned Data:** The strategy of partitioning databases and search indexes strictly by `user_id` is highly reusable for any personal-dashboard application (e.g., Personal Finance Trackers, File Storage/Google Drive).

## Cross-links

- [PROBLEM](./PROBLEM.md)
- [DESIGN](./DESIGN.md)
- [APPROACH](./APPROACH.md)