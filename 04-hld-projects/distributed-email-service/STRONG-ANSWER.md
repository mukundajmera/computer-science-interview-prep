# Distributed Email Service - Strong Answer Script

## 1. Requirements & Back-of-the-Envelope

**Say:** "To design a distributed email service like Gmail, I’ll focus on allowing users to send, receive, and search emails with high availability and extreme durability. We'll need a modern HTTP API for the web clients and SMTP integration for the outside world."

**Say:** "Let's assume $1\text{ Billion}$ DAU. If they receive 40 emails a day, that's $40\text{ Billion}$ inbound messages daily, which is about $460,000\text{ incoming requests per second}$. Metadata for these (at $50\text{ KB}$ each) requires roughly $730\text{ PB}$ a year, while attachments will push into the Exabyte range. This scale tells me immediately that we cannot use a single global database or a single search index—everything must be partitioned by user."

## 2. High-Level Architecture & Protocol Mismatch

**Say:** "The first major architectural decision is decoupling the client experience from the legacy email protocols. I will not build a stateful IMAP server, as maintaining a billion long-lived TCP connections just for email syncing is an infrastructure nightmare."

**Say:** "Instead, the frontend will communicate via a stateless REST API—for example, `GET /api/v1/folders/inbox/messages`. For new mail notifications, clients will maintain a lightweight WebSocket or SSE connection that simply says 'You have new mail,' prompting the client to fetch via HTTP."

## 3. The Ingestion Pipeline

**Say:** "Handling $460,000\text{ QPS}$ of inbound SMTP traffic requires a highly decoupled ingestion pipeline. When an external server (like Yahoo) connects to our inbound SMTP worker, we cannot do spam filtering or database writes synchronously while they wait."

**Say:** "Instead, the inbound worker takes the raw email payload, streams it directly to an S3 object store, and immediately returns a `250 OK` to the sender. This guarantees durability instantly. The worker then drops an event onto a Kafka queue. Internal Mail Delivery Agents (MDAs) pull from Kafka, run the heavy spam and antivirus checks, and then write the parsed metadata to our database."

## 4. Data Storage and Partitioning

**Say:** "For storage, I'll separate the heavy blobs from the metadata. Attachments and raw email bodies stay in S3. For the metadata, I'll use a wide-column store like Cassandra, strictly partitioned by `user_id`."

**Say:** "Our table `emails_by_folder` will have a composite primary key of `(user_id, folder_id)` and cluster by `email_id` descending. This makes fetching the first 50 emails of an inbox an extremely fast $O(1)$ partition lookup."

## 5. Deep Dive: Search Indexing

**Say:** "A system of this size will completely break a centralized Elasticsearch cluster. You can't write 460k documents per second to a global index efficiently. However, email search is purely single-tenant—I only search my own emails."

**Say:** "Therefore, the search index must also be partitioned by `user_id`. We can use embedded RocksDB or partitioned Lucene indexes stored alongside the user's database shard. When the async MDA processes a new email, it updates that specific user's local index."

## 6. Wrap Up: Conversation Threading

**Say:** "Finally, to handle conversation threading without complex relational joins or fragile subject-line parsing, the MDA will rely on standard RFC 5322 headers. It extracts `Message-ID`, `In-Reply-To`, and `References`. It looks up those parent IDs in the database, grabs their internal `Thread-ID`, and assigns it to the new message, allowing the UI to easily group them."

## Cross-links

- [PROBLEM](./PROBLEM.md)
- [DESIGN](./DESIGN.md)
- [APPROACH](./APPROACH.md)