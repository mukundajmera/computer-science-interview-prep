# Distributed Email Service - Approach

## Initial Analysis & Requirements Breakdown

When approaching a system like Gmail, the problem domain spans two different worlds:
1.  **The Client World (Web/Mobile):** Modern, fast, state-driven user interfaces.
2.  **The Federation World (SMTP):** Legacy, robust, loosely coupled protocols for routing mail between domains across the internet.

### 1. Protocol Impedance Mismatch
The biggest initial realization is that we cannot just build an "IMAP server." Traditional IMAP servers maintain a long-lived, stateful TCP connection for every active client. At 1 Billion DAU, maintaining 1 Billion persistent stateful connections specifically for mail protocol parsing is an immense infrastructure burden.

**The approach:** Decouple the frontend from the backend protocols.
*   Clients communicate via stateless REST/HTTP APIs for fetching mail and sending actions.
*   Clients use WebSockets or Server-Sent Events (SSE) solely for lightweight notifications of new mail.
*   The backend handles standard SMTP only when talking to *other* mail providers (e.g., Yahoo, Outlook).

### 2. The Scale of Ingestion
With 460,000 QPS of inbound emails, the write volume is staggering. 
*   If we try to write these synchronously to a relational database, we will hit connection limits and locking bottlenecks.
*   If we try to index them synchronously into a global Elasticsearch cluster, the indexers will constantly fall behind.

**The approach:** Asynchronous, durable ingestion.
1.  **Accept & Store:** The inbound SMTP worker receives the raw `.eml` file, streams it directly to S3 (object storage), and returns a `250 OK` to the sender. This guarantees durability immediately.
2.  **Queue:** The S3 pointer is placed on a durable message queue (Kafka).
3.  **Process:** Internal workers (Mail Delivery Agents) pull from the queue, run spam/AV checks, extract metadata, and write to the database and search indexes.

### 3. Data Partitioning Strategy
Email is an inherently isolated dataset. User A almost never needs to query User B's mailbox (unless they are sharing an enterprise inbox, which is an edge case we handle separately).

**The approach:** Strict `user_id` partitioning.
*   We use a wide-column store like Cassandra. The partition key is `user_id`.
*   All queries for folder lists, pagination, and message retrieval hit exactly one node (or replica set) in the database.
*   We apply the same logic to search. Instead of a massive global search index, we use user-partitioned indexes (e.g., embedded RocksDB or partitioned Lucene).

### 4. Conversation Threading
How do we know that Email C is a reply to Email B, which was a reply to Email A? 
*   We could try matching the `Subject:` string (e.g., stripping "Re:"), but this is fragile and error-prone.
*   We could require the database to maintain strict parent-child foreign keys, but this creates lock contention and complexity during concurrent deliveries.

**The approach:** Rely on RFC 5322 Standards.
Email clients inject specific headers:
*   `Message-ID`: `<1234@sender.com>`
*   `In-Reply-To`: `<1234@sender.com>`
*   `References`: `<1234@sender.com> <5678@sender.com>`

When the backend processes a new email, it extracts these headers. It queries the database for the referenced IDs. If it finds them, it pulls their existing internal `Thread-ID` and assigns it to the new message. The frontend groups by `Thread-ID`.

## Evolution of the Design

1.  **Phase 1: Naive DB Storage:** Initially, one might think to store the entire email (metadata + body) in a SQL database.
    *   *Correction:* Email bodies and attachments can be huge. Storing them in DB causes massive page thrashing and bloat. Shift bodies and attachments to S3; keep only metadata and snippets in the DB.
2.  **Phase 2: Synchronous Processing:** An initial design might process spam and AV checks while the external sender is waiting on the SMTP connection.
    *   *Correction:* External senders will time out. Spam checks (especially ML-based ones) can be slow. Ingest the raw payload first, ack the connection, and process asynchronously.

## Summary

The design boils down to an event-driven, aggressively partitioned architecture that bridges legacy SMTP standards with modern, scalable web patterns.