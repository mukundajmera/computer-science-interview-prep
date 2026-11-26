# Distributed Email Service - Interview Scoring Rubric

## Scoring rubric

| Dimension | Weight | Strong signal |
|---|---|---|
| **Protocol Understanding** | 20% | Clearly distinguishes between HTTP APIs for internal clients and SMTP for external federation. Justifies avoiding stateful IMAP connections for the web/mobile app. |
| **Ingestion Pipeline** | 20% | Designs an asynchronous, durable ingestion pipeline. Stores raw blobs immediately upon SMTP receipt before returning `250 OK`, deferring spam/AV checks to background workers via a message queue. |
| **Data Partitioning** | 25% | Identifies the necessity of strict `user_id` partitioning for both the metadata database (Cassandra) and the search indexes. Explains why a global search index fails at 460k QPS. |
| **Data Modeling** | 15% | Separates large blobs (attachments, raw bodies) into object storage (S3) while keeping metadata and text snippets in the fast database. Provides a workable schema. |
| **Conversation Threading** | 10% | Leverages RFC 5322 headers (`Message-ID`, `In-Reply-To`, `References`) rather than brittle subject-line parsing or complex DB locks. |
| **Trade-offs & Resilience** | 10% | Articulates failure modes (e.g., what happens if Kafka is down? Answer: Inbound SMTP workers return transient error 4xx). |

## Performance bands

- **Strong Hire (5):** Candidate drives the architecture, immediately recognizing the protocol mismatch and the scale of the inbound write path. They propose a robust async ingestion pipeline, strict user partitioning for data and search, and elegantly handle conversation threading via standard headers.
- **Hire (4):** Candidate provides a solid, scalable design with separated storage (DB vs S3) and an async pipeline, but might need minor hints regarding the search index bottlenecks or exactly how threading is accomplished.
- **Lean Hire (3):** Candidate designs a workable system but relies too heavily on synchronous operations or unpartitioned data stores (e.g., suggesting a single global Elasticsearch cluster without acknowledging the scaling pain).
- **No Hire (1-2):** Candidate attempts to build a stateful IMAP server for a billion users, stores large attachments directly in a relational database, or fails to provide a mechanism for inter-domain SMTP communication.

## Cross-links

- [PROBLEM](./PROBLEM.md)
- [DESIGN](./DESIGN.md)
- [PITFALLS](./PITFALLS.md)