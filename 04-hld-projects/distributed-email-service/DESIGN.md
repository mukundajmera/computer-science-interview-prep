# 📋 HLD Design Template: Distributed Email Service (Gmail)

Use this template as a framework for practicing system design interviews.

---

## 1. 📝 Requirements and Constraints

### Problem Statement
- System to design: Distributed Email Service
- Core user value: Allow users to send, receive, organize, and search emails with extreme reliability and low latency, using modern web protocols and IMAP for third-party clients, while interoperating with legacy SMTP mail servers globally.

### Functional Requirements
- [x] FR1: Send email via HTTP API (recipients in To, CC, BCC).
- [x] FR2: Inbound email ingestion via SMTP with spam/antivirus filter.
- [x] FR3: Folder views (Inbox, Sent, Drafts, Trash) with pagination via HTTP API and synchronize state via IMAP.
- [x] FR4: Conversation threading via RFC 5322 headers (`Message-ID`, `In-Reply-To`, `References`).
- [x] FR5: Attachment handling (up to 25MB) and email full-text search.

### Non-Functional Requirements

| Requirement | Target |
|---|---|
| Availability | 99.99% |
| Read latency | < 200 ms for folder views |
| Write latency | Asynchronous processing; quick ack on send |
| Throughput | 100,000 outbound QPS; 460,000 inbound QPS |
| Consistency | Strong consistency for user mailbox views |
| Durability | Extreme reliability (zero email loss once accepted) |

### Constraints
- Global user base requiring geo-distribution.
- Need to interoperate with external mail servers that may be slow or temporarily unavailable.
- Need to support long-lived stateful IMAP connections for third-party clients.

### Out of Scope
- Full spam/ML model implementation details.
- Offline client-side caching mechanisms (e.g., IMAP local sync).

---

## 2. 📊 Back-of-Envelope Estimation

### Traffic

| Metric | Value | Formula |
|---|---|---|
| DAU | 1 Billion | input |
| Sent/user/day | 10 | input |
| Received/user/day | 40 | input |
| Daily Outbound | 10 Billion | 1B × 10 |
| Outbound QPS | ~100,000 | 10B / 86400 |
| Daily Inbound | 40 Billion | 1B × 40 |
| Inbound QPS | ~460,000 | 40B / 86400 |

### Storage

| Data Type | Avg Size | Daily Volume | 1-Year |
|---|---|---|---|
| Metadata | 50 KB | 2 PB | 730 PB |
| Attachments | 500 KB (for 20% of msgs) | 4 PB | 1,460 PB |

### Decision Notes
- Which estimate forces a design choice? The sheer volume of incoming messages (460,000 QPS) makes a single global search index or a monolithic relational database unviable. Data and indexes must be strictly partitioned by user.
- What assumption is most uncertain? The distribution of email sizes and attachment usage, which dictates our blob storage vs. metadata storage split.

---

## 3. 🔌 API / System Interface

### External Contract
- Protocol choice: REST / HTTP for web clients; IMAP for third-party desktop/mobile clients; SMTP for inter-domain mail transfer.
- Auth model: OAuth 2.0 / JWT for API clients.

### Core Endpoints

```http
POST /api/v1/messages/send
Content-Type: multipart/form-data
(Accepts message body, To/CC/BCC, and attachments)

GET /api/v1/folders/{folder_id}/messages?page_token=...&limit=50
Response: List of emails with snippets and read status.

GET /api/v1/messages/{message_id}
Response: Full email body and attachment links.

GET /api/v1/search?q={query}&limit=50
Response: List of emails matching the query.
```

### Error Model
- `400` invalid input (e.g., malformed email address)
- `401/403` auth/authz failures
- `404` folder or message not found
- `413` Payload Too Large (attachment > 25MB)
- `5xx` internal dependency failure

---

## 4. 🗄️ Core Entities and Data Model

### Data Schemas

Using Cassandra or a similar wide-column store, partitioned tightly around the `user_id`:

```sql
-- Cassandra user-partitioned mailbox tables
CREATE TABLE folders (
    user_id UUID,
    folder_id UUID,
    folder_name VARCHAR(64),
    unread_count INT,
    PRIMARY KEY (user_id, folder_id)
);

CREATE TABLE emails_by_folder (
    user_id UUID,
    folder_id UUID,
    email_id TIMEUUID,
    from_addr VARCHAR(255),
    to_addrs LIST<VARCHAR(255)>,
    subject VARCHAR(512),
    body_snippet VARCHAR(255),
    is_read BOOLEAN,
    has_attachment BOOLEAN,
    PRIMARY KEY ((user_id, folder_id), email_id)
) WITH CLUSTERING ORDER BY (email_id DESC);

CREATE TABLE email_attachments (
    attachment_id UUID PRIMARY KEY,
    email_id TIMEUUID,
    filename VARCHAR(255),
    size_bytes BIGINT,
    s3_uri VARCHAR(1024)
);
```

### Storage Choices
- Primary DB: Cassandra (Wide-Column) or partitioned distributed SQL. Reason: Excellent write throughput, and query patterns are always scoped to a single user.
- Object Storage: S3 or equivalent blob store. Reason: Cost-effective scaling for 1,460 PB/year of attachments and large raw email bodies.
- Search Index: Local Lucene/RocksDB indexes partitioned by `user_id`.

### Key Access Patterns
1. Read path query: Load the first 50 emails in the Inbox (`emails_by_folder`).
2. Write path mutation: Insert an incoming email into `emails_by_folder`, update `unread_count` in `folders`.
3. Secondary lookup: Resolve `attachment_id` to `s3_uri` when a user downloads an attachment.

---

## 5. 🏗️ High-Level Architecture

### Component List
- **Web API Gateway:** Terminates HTTP, handles auth, routes to internal services.
- **IMAP Gateway:** Terminates stateful TCP connections for third-party clients and proxies commands to internal stateless services.
- **Mail Transfer Agents (MTA) / SMTP Workers:** Inbound and Outbound nodes communicating via SMTP.
- **Message Queue:** Kafka or RabbitMQ for durable asynchronous processing.
- **Mail Delivery Agent (MDA):** Internal worker that writes to the database and search index.
- **Storage Tier:** Cassandra (Metadata), S3 (Blobs).

### Read Path (Web Client or IMAP Client viewing Inbox)
1. User requests `/api/v1/folders/inbox/messages` (or issues an IMAP `FETCH` command).
2. API Gateway (or IMAP Gateway) validates auth and routes to the Read Service.
3. Read Service queries Cassandra `emails_by_folder` where `user_id=X` and `folder_id=Inbox`.
4. Returns snippets and metadata to the client.

### Write Path (Inbound SMTP from External)
1. External MTA connects to Inbound SMTP Worker.
2. Worker receives the raw `.eml` payload and immediately persists it to S3 (to guarantee no data loss), returning a `250 OK` to the sender.
3. Worker enqueues a message to Kafka with the S3 path.
4. Spam/Antivirus workers pull from Kafka, process the email, and pass it to the MDA.
5. MDA parses headers, writes metadata to Cassandra (`emails_by_folder`), and updates the user's search index.

---

## 6. 🔍 Deep Dives

### Deep Dive A: Search Indexing at Scale
- **Bottleneck:** Traditional global Elasticsearch index crashes or bottlenecks under 460,000 QPS of incoming email ingestion.
- **Chosen pattern:** User-Partitioned LSM Index. Since users only search their own emails, we partition the inverted index by `user_id`.
- **Implementation:** Use embedded RocksDB or a specialized Lucene cluster where nodes hold specific user partitions. Updates to the index are processed asynchronously by the MDA after writing to Cassandra.

### Deep Dive B: Conversation Threading
- **Challenge:** Grouping replies into a single "conversation" view efficiently.
- **Pattern:** Avoid complex hierarchical SQL joins. Instead, parse standard RFC 5322 headers:
  - `Message-ID`: Unique ID for the email.
  - `In-Reply-To`: The ID of the parent email.
  - `References`: A list of IDs representing the thread history.
- **Implementation:** When the MDA processes an incoming email, it extracts these headers. It looks up the `Thread-ID` associated with the `In-Reply-To` or `References`. If found, it assigns the new email the same `Thread-ID`. The UI simply groups emails by `Thread-ID` and sorts by timestamp.

---

## 7. ⚖️ Trade-offs and Decisions

| Decision | Option Chosen | Alternative | Why Chosen Now |
|---|---|---|---|
| Protocol for Clients | WebMail REST API + IMAP Gateway | Pure IMAP/SMTP | Supporting only IMAP limits modern web capabilities. We use stateless REST for our own clients, but provide an IMAP Gateway to terminate stateful connections for third-party compatibility without polluting internal services. |
| Search Indexing | User-Partitioned Local Indexes | Centralized Elasticsearch | Centralized ES cannot handle 460k writes/sec efficiently. Email search is strictly single-tenant. |
| Attachment Storage | S3 Object Store | Database BLOBs | Storing large binaries in Cassandra causes heap pressure and compaction thrashing. |

---

## 8. 🔮 Follow-up Questions

1. What happens if the internal Kafka queue goes down during an inbound SMTP transfer?
2. How do you push real-time new email notifications to a mobile client?
3. How is the user-partitioned search index rebuilt if a node fails?

---

## 9. 🧩 Variants and Extensions

- **Variant 1 (Enterprise/Corporate Mail):** Needs compliance archiving and e-discovery (cross-user search capabilities for admins).
- **Variant 2 (End-to-End Encryption):** Implementing PGP or similar client-side encryption where the server cannot read the body or index the search terms centrally.

---

## 10. 🚨 Common Pitfalls (Self-Check)

- [x] I justified separating the stateful IMAP gateway from the stateless internal REST services.
- [x] I partitioned the database and search indexes by `user_id`.
- [x] I addressed how conversation threading works via email headers.
- [x] I decoupled the ingestion pipeline using a message queue for high reliability.

---

## 11. 🧮 Scoring Rubric (Self-Evaluation)

| Dimension | 1 (Weak) | 3 (Okay) | 5 (Strong) |
|---|---|---|---|
| Requirements handling | Vague | Mostly clear | Addressed HTTP vs SMTP explicitly |
| Architecture clarity | Boxes only | Basic flow | Detailed pipeline with Kafka and MDA |
| Technical depth | Tool names | Some rationale | Cassandra partitioning & RFC 5322 headers |
| Trade-off quality | None | Some | Global vs Partitioned search explored |

---

## 12. ✅ Wrap-up Summary

1. We designed a distributed email system capable of handling 1 billion DAU and 460k inbound QPS.
2. The core architecture uses stateless HTTP APIs for clients, standard SMTP workers for external federation, and an async Kafka-driven pipeline for mail delivery.
3. A key trade-off was rejecting a global search index in favor of user-partitioned indexes to handle the immense write throughput.
4. We solved conversation threading gracefully by leveraging standard RFC 5322 headers instead of complex database locks.

---
**Real-world reference**: See how WhatsApp solved this in the [WhatsApp case study](../../case-studies/whatsapp-messaging/)
