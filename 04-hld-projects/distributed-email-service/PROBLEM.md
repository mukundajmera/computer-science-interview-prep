# Distributed Email Service (Gmail)

## Problem Statement

Design a distributed email service similar to Gmail that allows users to send, receive, search, and manage emails via a modern HTTP-based web application while also handling traditional SMTP interchanges with external domains and IMAP for third-party email clients.

---

## Requirements and Constraints

### Functional Requirements

1. **Send Email:** Send email via HTTP API and SMTP, supporting `To`, `CC`, and `BCC` fields.
2. **Receive Email:** Inbound email ingestion via SMTP from external domains, including spam and antivirus filtering.
3. **Folder Management / Client Access:** Support folder views (Inbox, Sent, Drafts, Trash) with pagination via HTTP API and synchronize state via IMAP for third-party clients.
4. **Conversation Threading:** Group messages dynamically by tracking RFC 5322 headers (`Message-ID`, `In-Reply-To`, `References`).
5. **Attachments & Search:** Handle attachments up to 25MB and support full-text search over email metadata and bodies.

### Non-Functional Requirements

| Requirement | Target |
|---|---|
| Reliability | Extreme (Zero email loss once accepted) |
| Availability | 99.99% |
| Consistency | Strong consistency for user mailbox views |
| Outbound Scale | ~100,000 QPS (1 Billion users) |
| Inbound Scale | ~460,000 QPS |
| Storage (Metadata) | ~730 PB / year |
| Storage (Attachments) | ~1,460 PB / year |

### Capacity Assumptions

- **Users:** 1 Billion DAU.
- **Outbound Traffic:** 10 emails sent per user per day.
  - $1\text{B users} \times 10\text{ emails/day} = 10\text{B sent/day} \approx 100,000\text{ QPS}$
- **Inbound Traffic:** 40 emails received per user per day.
  - $1\text{B users} \times 40\text{ emails/day} = 40\text{B received/day} \approx 460,000\text{ QPS}$
- **Storage Profile:**
  - **Metadata:** Average 50 KB per email.
    - $40\text{B} \times 50\text{ KB} = 2\text{ PB/day} = 730\text{ PB/year}$
  - **Attachments:** 20% of emails have attachments; average 500 KB per attachment.
    - $8\text{B attachments/day} \times 500\text{ KB} = 4\text{ PB/day} = 1,460\text{ PB/year}$ in object storage.

### Out of Scope

- Client-side offline caching architectures.
- Advanced AI auto-reply generation.
- Detailed spam filtering ML model internals.

---

## High-Level Design Outline

### Core Services

- **WebMail HTTP API / Gateway:** Serves the frontend client applications.
- **IMAP Gateway:** Terminates long-lived TCP connections for third-party email clients (e.g., Apple Mail, Outlook) translating IMAP commands into internal API calls.
- **Inbound SMTP Workers:** Receive emails from external domains, process them through security filters, and enqueue for delivery.
- **Outbound SMTP Workers:** Deliver outgoing messages to external mail exchanges (MX).
- **Mail Delivery Agent (MDA):** Routes internally parsed emails into the appropriate user mailbox partitions.
- **Search Indexer:** Asynchronously indexes incoming email for fast text search.

### Storage and Cache

- **Primary DB (Metadata):** Wide-column store (e.g., Cassandra) or distributed SQL database partitioned by user.
- **Object Store:** S3-compatible blob storage for raw email bodies and attachments.
- **Search Index:** User-partitioned LSM trees or local inverted indexes (e.g., RocksDB or Lucene per user).

### API Surface (Illustrative)

```http
POST /api/v1/messages/send
GET /api/v1/folders/{folderId}/messages?page=...
GET /api/v1/messages/{messageId}
GET /api/v1/search?q=...
```

---

## Scoring Rubric

Strong answers explicitly cover:
1. Handling the protocol translation (WebMail HTTP to External SMTP).
2. Justifying the user-partitioned data model for metadata and search.
3. Achieving conversation threading without rigid database locking.

See [RUBRIC](./RUBRIC.md).

---

## Common Pitfalls

- Defaulting to a global Elasticsearch cluster for search, which bottlenecks under heavy ingest.
- Mishandling the stateful, long-lived nature of IMAP connections (e.g., memory bloat on gateways) when supporting third-party clients, or failing to decouple the stateful gateway from stateless internal services.
- Storing large attachments directly in the metadata database.

See [PITFALLS](./PITFALLS.md).

---

## Follow-Up Questions

- How do you guarantee zero message loss during inbound processing?
- How does the system handle real-time notifications for incoming mail?

See [FOLLOW-UPS](./FOLLOW-UPS.md).

---

## Related Links

- [APPROACH](./APPROACH.md)
- [DESIGN](./DESIGN.md)
- [COMPARISON](./COMPARISON.md)
- [STRONG-ANSWER](./STRONG-ANSWER.md)
