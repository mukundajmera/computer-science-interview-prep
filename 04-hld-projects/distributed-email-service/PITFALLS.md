# Distributed Email Service - Common Pitfalls

## 1. Using IMAP for Web and Mobile Clients

*   **Failure Signal:** The candidate proposes that the frontend web app and mobile apps communicate with the backend using the IMAP protocol.
*   **Root Cause:** Misunderstanding the difference between standard email protocols (designed for standalone desktop clients) and modern web architectures. IMAP requires maintaining a long-lived, stateful TCP connection for every active user.
*   **Mitigation:** Use a stateless REST/HTTP API for all client actions (reading, sending, organizing). Use WebSockets or Server-Sent Events (SSE) strictly for lightweight push notifications ("You have a new message").
*   **Validation:** Check if the candidate's API design is HTTP-based and stateless.

## 2. Global Search Index Bottleneck

*   **Failure Signal:** Proposing a single, monolithic Elasticsearch (or similar) cluster to handle all email search queries across the entire user base.
*   **Root Cause:** Failing to account for the inbound throughput math ($460,000\text{ QPS}$). A global index will suffer severe write contention and indexer lag at this scale.
*   **Mitigation:** Recognize that email search is almost exclusively single-tenant. Partition the search indexes by `user_id`. Each user's index can be stored locally (e.g., embedded RocksDB, or a partitioned Lucene cluster) alongside their metadata.
*   **Validation:** Ask the candidate: "How does your search cluster handle 460k index updates per second?"

## 3. Synchronous Ingestion Pipeline

*   **Failure Signal:** The inbound SMTP worker performs spam filtering, antivirus scanning, and database writing *before* acknowledging the email to the external sender.
*   **Root Cause:** Treating the external SMTP connection as a synchronous web request. External MTAs (Mail Transfer Agents) have strict timeouts and may retry aggressively if delayed, amplifying load.
*   **Mitigation:** The inbound worker should stream the payload to durable object storage (S3), place a pointer on a message queue (Kafka), and immediately return `250 OK`. All processing happens asynchronously.
*   **Validation:** Ask the candidate to walk through the exact steps taken while the external SMTP connection is open.

## 4. Storing Attachments in the Database

*   **Failure Signal:** The schema includes a `BLOB` column for attachments or raw email bodies within the main relational or NoSQL database.
*   **Root Cause:** Overlooking the size disparity between metadata (kilobytes) and attachments (megabytes). Storing binaries in databases causes severe performance degradation, memory pressure, and compaction issues (e.g., in Cassandra).
*   **Mitigation:** Store raw bodies and attachments in an Object Store (like S3). Store only the S3 URIs/pointers in the metadata database.
*   **Validation:** Review the data schema for clear separation of metadata and large blobs.

## 5. Brittle Conversation Threading

*   **Failure Signal:** Grouping replies by string-matching the `Subject` line (e.g., stripping "Re:", "Fwd:") or relying on exact timestamp heuristics.
*   **Root Cause:** Lack of domain knowledge regarding standard email structures.
*   **Mitigation:** Utilize RFC 5322 headers specifically designed for this purpose: `Message-ID`, `In-Reply-To`, and `References`.
*   **Validation:** Ask the candidate: "How exactly do you know that an incoming email from Yahoo is a reply to an email the user sent yesterday?"