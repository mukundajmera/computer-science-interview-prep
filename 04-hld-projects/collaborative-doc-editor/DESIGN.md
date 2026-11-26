# 📋 Collaborative Document Editor — High-Level Design

Use this design as a framework for answering the collaborative document editor system design interview.

---

## 1. 📝 Requirements and Constraints

### Problem Statement
- System to design: A browser-based real-time collaborative document editing application (similar to Google Docs).
- Core user value: Allow multiple users to seamlessly edit a text document simultaneously, maintaining a consistent view across all clients without locking, while persisting the final document state durably.

### Functional Requirements
- [x] FR1: Real-time Editing: Multiple users must be able to view and edit the same document concurrently in near real time.
- [x] FR2: Cursor/Presence Tracking: Users should be able to see who else is in the document and the live positions of their cursors.
- [x] FR3: Offline Editing & Reconnection: Users experiencing temporary network disconnects can continue making local edits, which are seamlessly merged upon reconnection.
- [x] FR4: Undo/Redo: Users can perform local undo/redo operations without reverting other concurrent users' operations.
- [x] FR5: Document Persistence: Document state must be durably persisted, enabling reliable loading of historical snapshots.

### Non-Functional Requirements

| Requirement | Target |
|---|---|
| Availability | 99.99% for reads and collaboration sessions |
| Read latency | < 500 ms to initially load the document |
| Edit propagation latency | < 50 ms P99 for real-time collaboration updates |
| Throughput | Up to 20 ops/sec/doc active burst during intense collaboration |
| Consistency | Strong Eventual Consistency (Convergence): All clients applying the same set of operations must converge to identical states. |
| Durability | Strong durability; no acknowledged edit should ever be lost |

### Constraints
- Regulatory/compliance: Standard data retention policies and access control requirements (not the primary focus of this design).
- Budget/cost preference: Optimize connection gateway memory and cross-AZ data transfer costs.
- Team/operational constraints: Standard stateless microservices, supplemented by stateful connection nodes for WebSockets.
- Region/geography constraints: Multi-region deployment required to support globally distributed users with low latency.

### Out of Scope
- Full rich-text formatting (we assume a linear text model or a simplified rich-text delta model).
- Granular permission matrix and folder structures.
- Video or voice chat integration.
- Full branchable version history UI.

---

## 2. 📊 Back-of-Envelope Estimation (Only What Changes Design)

*Note: The values below (e.g., 50M DAU, 10M concurrent sockets, 20 ops/sec/doc, 10 KB/socket) represent a named illustrative scenario and are not universal production facts.*

### Traffic

| Metric | Value | Formula/Derivation |
|---|---|---|
| DAU | 50M | Scenario Assumption (Input) |
| Peak Concurrent WebSocket Connections | 10M | Scenario Assumption (Input, e.g., 20% of DAU) |
| Active Document Burst Ops | 20 ops/sec/doc | Scenario Assumption (Input) |
| Peak Concurrent Active Documents | 200,000 | Assumes active editing docs are a small fraction of all open sockets (derived assumption) |
| Average Viewers/Editors per Active Doc | 50 | 10M sockets / 200K active docs (fanout derived from distribution assumption) |

### Server Capacity Planning (Stateful Gateways)

| Metric | Value | Detail |
|---|---|---|
| Payload RAM per socket connection | 10 KB | Scenario assumption for application payload mapping state. |
| Overhead per socket connection | 30 KB | Kernel socket buffers, TCP/TLS state, process replication headroom (Explicitly tracked above the 10KB payload). |
| Total RAM for 10M connections | 100 GB | 10M × 10 KB = 100 GB decimal (Payload only assumption). |
| Total Expected RAM with Overhead | 400 GB | 10M × (10 KB + 30 KB). |
| Required Connection Servers | 25 - 30 | 400 GB total RAM / 16 GB usable memory per node. |

### Bandwidth Egress Calculation

| Metric | Value | Detail |
|---|---|---|
| Avg Operation Payload Size | 50 Bytes | Delta-encoded JSON (position, chars, user info). Scenario Assumption. |
| Total Peak Egress Bandwidth | 10 GB/s | Derived as: (200,000 active docs) × (20 successful ops/sec/doc) × (50 concurrent doc connections fanout) × (50 Bytes/op) = 10,000,000,000 Bytes/s. NOTE: We do not multiply by 10M DAU/connections, only by active documents. Attempts are ~25 ops/sec/doc with 20% validation failure rate, meaning 5 ops/sec/doc are rejected before broadcast, yielding 20 successful operations broadcasted. |

### Decision Notes
- **Scaling Limit**: The requirement to support 10M concurrent WebSocket connections dictates a stateful connection gateway layer decoupled from the operation processing layer.
- **Uncertainty & Load**: The burst rate of 20 ops/sec/doc across massive fanouts (e.g., 50 viewers) creates significant CPU overhead on the fanout gateways, not just network bandwidth.

---

## 3. 🔌 API / System Interface

### External Contract
- Protocol choice: REST for CRUD metadata; WebSockets for real-time operation streaming and presence.
- Auth model: OAuth 2.0 / JWT for REST API; JWT passed during WebSocket handshake.
- Rate limiting policy: Client-side operation batching is enforced. The server disconnects clients exceeding 50 ops/sec to protect against malicious behavior.

### Core Endpoints
```http
POST /api/v1/documents
GET /api/v1/documents/{documentId}
GET /api/v1/documents/{documentId}/snapshots?version=latest
```

### WebSocket Framing Schema

Clients connect via `wss://api.example.com/v1/documents/{documentId}/session`.

**Client-to-Server Edit Frame:**
```json
{
  "type": "client_edit",
  "documentId": "doc-789",
  "clientId": "client-123",
  "baseVersion": 105,
  "operations": [
    {
      "action": "insert",
      "position": 14,
      "text": "Hello"
    }
  ],
  "timestamp": 1698765432000
}
```

**Server-to-Client Broadcast Frame:**
```json
{
  "type": "server_ack_broadcast",
  "documentId": "doc-789",
  "clientId": "client-123",
  "version": 106,
  "operations": [
    {
      "action": "insert",
      "position": 14,
      "text": "Hello"
    }
  ],
  "presence": {
    "client-123": { "cursor": 19, "lastSeen": 1698765432000 }
  }
}
```

### Error Model
- `400` invalid input payload
- `401/403` auth/authz failure
- `404` missing document
- `409` conflict/concurrency (handled transparently by OT/CRDT, rarely exposed as HTTP 409)
- `429` throttled / rate limited
- `5xx` internal dependency failure

---

## 4. 🗄️ Core Entities and Data Model

### Core Entities
- Entity A: `Document Metadata` (id, title, owner, access controls)
- Entity B: `Operation Log` (immutable sequence of applied transformations)
- Entity C: `Snapshot` (periodically materialized document state)

### Storage Choices
- Primary DB (Metadata & Snapshots): PostgreSQL. Relational consistency is ideal for access controls and metadata.
- Operation Log DB: Apache Cassandra or DynamoDB. The append-only, high-write-throughput nature of the operation log perfectly matches wide-column stores.
- Cache / Presence / PubSub: Redis. Used for fast cursor updates, active document connection routing, and Pub/Sub mesh.

### Detailed PostgreSQL / Cassandra Schema

**PostgreSQL: Document Metadata Table**
```sql
CREATE TABLE documents (
    document_id UUID PRIMARY KEY,
    owner_id UUID NOT NULL,
    title VARCHAR(255),
    latest_version BIGINT DEFAULT 0,
    latest_snapshot_id UUID,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
CREATE INDEX idx_owner_updated ON documents (owner_id, updated_at);
```

**PostgreSQL: Snapshots Table**
```sql
CREATE TABLE snapshots (
    snapshot_id UUID PRIMARY KEY,
    document_id UUID REFERENCES documents(document_id),
    version BIGINT NOT NULL,
    content_s3_url VARCHAR(512),
    created_at TIMESTAMP
);
CREATE INDEX idx_doc_version ON snapshots (document_id, version DESC);
```

**Cassandra: Immutable Op-Log Table**
```cql
CREATE TABLE operation_logs (
    document_id uuid,
    version bigint,
    client_id text,
    operation_payload text,
    created_at timestamp,
    PRIMARY KEY (document_id, version)
) WITH CLUSTERING ORDER BY (version ASC);
```

### Key Access Patterns
1. Read path query: Fetch `documents` metadata -> Fetch latest `snapshots` URL -> Fetch missed `operation_logs` (version > snapshot.version).
2. Write path mutation: Append to `operation_logs`, update in-memory model, broadcast.
3. Secondary lookup: Periodic worker scans `operation_logs` length. If length > 1000, trigger snapshot generation.

### Partition and Index Notes
- Partition key: `document_id`. Operations are tightly bound to a single document.
- Hot key risk: Highly active public documents (e.g., an AMA or live broadcast). Mitigated by batching operations at the connection gateway.
- Required indexes: `(document_id, version)` clustering order in Cassandra to efficiently slice the delta log for reconnecting clients.

---

## 5. 🏗️ High-Level Architecture

### System Architecture Diagram

```mermaid
flowchart TD
    C[Clients] --> LB[Load Balancer]
    LB --> WS[WebSocket Connection Gateway]
    LB --> API[REST API Servers]
    
    API --> PG[(PostgreSQL - Metadata/Snapshots)]
    API --> S3[(S3 - Object Storage)]
    
    WS <--> RedisPubSub((Redis Pub/Sub Mesh))
    WS --> CollabEngine[Collaboration Engine Node]
    
    CollabEngine --> Cass[(Cassandra - Op Log)]
    CollabEngine --> PG
    
    Cass --> SnapWorker[Snapshot Generation Worker]
    SnapWorker --> S3
    SnapWorker --> PG
```

### Component List
- Load Balancer: Terminates TLS, routes REST traffic statelessly, and maps WebSocket traffic.
- WebSocket Connection Gateway: Holds persistent TCP connections. Extremely lightweight, buffering I/O.
- Collaboration Engine Node: Stateful actor processing incoming operations using OT or CRDT algorithms.
- Redis Pub/Sub: Routes operations between Connection Gateways and Collaboration Engines.
- Snapshot Worker: Background daemon compacting the immutable op-log into S3 objects.

### Read Path (Document Initialization)
1. Client makes REST request to get document metadata and the latest `snapshot` URL.
2. Client downloads the snapshot from S3.
3. Client establishes a WebSocket connection, providing `last_seen_op_id` (the version of the snapshot).
4. Server fetches any trailing operations from Cassandra (version > `last_seen_op_id`) and streams them to the client.

### Write Path (Real-time Editing)
1. Client generates local edits and sends them via WebSocket to the Connection Gateway.
2. Connection Gateway routes the message to the specific Collaboration Engine Node responsible for `documentId` via Consistent Hashing.
3. Collaboration Node applies concurrency conflict resolution, assigns a monotonically increasing global version number.
4. Collaboration Node durably appends the operation to Cassandra (WAL).
5. Collaboration Node publishes the accepted operation to Redis Pub/Sub.
6. Connection Gateways subscribed to that document broadcast the operation to all connected clients.

### Failure-aware Path
- Client disconnection: Client buffers local operations. Upon reconnection, replays missing gaps using `last_seen_op_id`.
- Node crash recovery: If a Collaboration Engine Node crashes, the Consistent Hashing ring reassigns the `documentId` to a new node. The new node rebuilds its in-memory state by loading the latest snapshot and replaying the Cassandra WAL.
- Network Partition: If Redis Pub/Sub partitions, clients fall back to periodic polling against Cassandra until connectivity is restored.

---

## 6. 🔍 Deep Dives (Pick 1-2)

### Deep Dive A: Concurrency Conflict Resolution (OT vs CRDT)

Collaborative editing requires a mathematical foundation to ensure all clients converge to the same text state despite receiving concurrent edits in different orders.

**Operational Transformation (OT)**
OT requires a centralized server to serialize operations and transform conflicting client edits.
- Transformation Function `T(op1, op2) -> op1'`: If client 1 inserts 'x' at position 5 (`ins(p1=5, c1='x')`), and client 2 concurrently inserts 'y' at position 2 (`ins(p2=2, c2='y')`), the server transforms client 1's operation against client 2's: `T(ins(5, 'x'), ins(2, 'y')) = ins(6, 'x')`.
- TP1/TP2 Divergence Criteria: To be mathematically correct, OT must satisfy two properties.
  - Transformation Property 1 (TP1): `op1 + T(op2, op1) ≡ op2 + T(op1, op2)`. This ensures that applying two concurrent operations in any order yields the same document state.
  - Transformation Property 2 (TP2): Transforming an operation against a sequence of concurrent operations must be independent of the order they are evaluated. Proving TP2 for string manipulation with rich text is notoriously difficult, leading to complex and error-prone server implementations.
- **Worked OT Trace**: Client A and B start with string "abc".
  - A executes `O_A = insert(pos=1, 'x')` generating local state "axbc".
  - B concurrently executes `O_B = insert(pos=2, 'y')` generating local state "abyc".
  - Server orders A before B.
  - Server broadcasts `O_A` to B. B applies it: `pos(O_A) < pos(O_B)`, so B gets "axbyc".
  - Server receives `O_B`, transforms it against `O_A`: `T(O_B, O_A) = insert(pos=2+1, 'y') = insert(pos=3, 'y')`.
  - Server broadcasts transformed `O_B'` to A. A applies `insert(pos=3, 'y')` to "axbc" -> "axbyc". State converges.

**Conflict-Free Replicated Data Types (CRDTs)**
CRDTs distribute the conflict resolution by mathematically ensuring commutative and associative operations. They eliminate positional index shifting by assigning universally unique, immutable identifiers to every character. Simply naming Yjs, RGA, or Automerge does not constitute a universal convergence proof; we must explicitly define the merge behavior.
- RGA (Replicated Growable Array): An early sequence CRDT that uses a linked list of characters with logical timestamps to order concurrent insertions deterministically without server transformation.
- Automerge: A popular JSON-like CRDT framework. It maintains an internal operation log and logical vector clocks, merging concurrent mutations by applying deterministic ordering rules (e.g., tie-breaking by client ID).
- Yjs (Item structures, left/right origins, ver. 13.x): Yjs is heavily optimized for text. It represents the document as a doubly-linked list of `Item` structs. Each Item explicitly tracks its `left` and `right` neighbor origins (using unique client/sequence IDs).
- **Worked CRDT Trace**: Client A and B insert concurrently.
  - Both know character 'b' (ID: `[c0, 2]`) and 'c' (ID: `[c0, 3]`).
  - Client A inserts 'x' between 'b' and 'c'. Its ID is `[c1, 1]`, `left=[c0, 2]`, `right=[c0, 3]`.
  - Client B concurrently inserts 'y' between 'b' and 'c'. Its ID is `[c2, 1]`, `left=[c0, 2]`, `right=[c0, 3]`.
  - When the peers sync, they see two items with identical left/right origins. Yjs breaks the tie consistently using the globally unique client ID (`c1` vs `c2`), ensuring deterministic ordering (e.g., 'b', 'x', 'y', 'c').
- **Explicit Reference Contracts for CRDT Resolution Boundary**:
  ```java
  // Java CRDT Tie-Breaking
  public class CrdtItem implements Comparable<CrdtItem> {
      String clientId;
      long clock;
      String character;
      
      @Override
      public int compareTo(CrdtItem other) {
          // Both items share the same left/right origins.
          // Tie-break securely and consistently.
          return this.clientId.compareTo(other.clientId);
      }
  }
  ```
  ```python
  # Python CRDT Tie-Breaking
  class CrdtItem:
      def __init__(self, client_id: str, clock: int, character: str):
          self.client_id = client_id
          self.clock = clock
          self.character = character
          
      def __lt__(self, other: 'CrdtItem') -> bool:
          # Both items share the same left/right origins.
          # Tie-break securely and consistently.
          return self.client_id < other.client_id
  ```
- **Decision:** While CRDTs require more memory (metadata per character), they simplify server architecture immensely. The server becomes a dumb relayer of binary blobs. We select Yjs for its superior memory compaction and performance in text editing.

### Deep Dive B: WebSocket Stateful Gateway Architecture

Managing 10M concurrent WebSockets is a classic C10M challenge.

- **Connection Affinity:** WebSockets are stateful by definition. The Load Balancer (e.g., HAProxy or AWS ALB) simply pins the TCP connection to a specific WebSocket Connection Gateway node.
- **Consistent Hashing on documentId & The Hot-Document Bottleneck:** The Connection Gateways must forward edits to the specific Collaboration Engine Node managing that document's state in memory. We use Consistent Hashing on `documentId` so that if a Collaboration Node fails, only a fraction of documents are migrated. *Crucially, documentId affinity alone does not resolve a hot-document bottleneck*. If a massive broadcast doc receives huge traffic, the single Collaboration Engine node holding that `documentId` will melt down under the fan-out overhead. This requires splitting the doc into smaller chunks or adding a tier of aggregation nodes.
- **Redis Pub/Sub vs Cluster Mesh:** Instead of a complex peer-to-peer cluster mesh between all Gateways and Engine Nodes (which suffers from N^2 connection scaling), we utilize Redis Pub/Sub as an intermediary broker. When a Gateway accepts a client for `doc-789`, it subscribes to the Redis channel `doc-789`. The Engine Node publishes accepted edits to this channel. Redis Pub/Sub efficiently handles the fan-out broadcast.
- **Heartbeat Detection & Reconnect/Replay Behavior:** Dead connections (half-open TCP sockets) leak memory. We enforce a strict Ping/Pong protocol at the WebSocket frame level.
  - *Disconnect*: If a client misses two consecutive 30-second ping intervals, the Gateway forcefully terminates the socket and emits a `presence_leave` event.
  - *Gap Replay (last_seen_op_id)*: When the client reconnects, it sends the `last_seen_op_id` in its handshake. The Engine Node fetches only the missing operations from its in-memory buffer (or the Redis/Cassandra backing store) that occurred after that ID, guaranteeing seamless catch-up without full state transfer.

### Deep Dive C: Rich-Text Delta Model & Undo/Redo Semantics

- **Rich-text Delta Model:** Instead of syncing full HTML, we use a Delta representation, consisting of sequential instructions: `retain(5), insert('bold_text', {bold: true}), delete(2)`. This compact format is ideal for computing diffs and transmitting over WebSockets.
- **Distributed Undo/Redo Buffer Semantics:** A naive local undo reverts the exact previous state. In a collaborative environment, if User A deletes text, and User B types inside it, User A's undo should restore the deleted text *and* incorporate User B's new text.
- To achieve this, the undo buffer stores *inverse operations*. When an undo is triggered, the inverse operation is sent to the server and mathematically transformed (via OT or CRDT algorithms) against all operations that occurred *after* the original action. This ensures that a user only undoes their own actions without destroying concurrent, interleaved work from other users.

---


### Deep Dive D: Failure Mode Histories (Illustrative Scenario)

To guarantee correctness during chaotic events, we outline the exact state ownership and recovery traces:

1. **Failure Case 1: Collaboration Engine Node Crash (documentId Hotspot)**
   - **State Owner before crash**: Engine Node X owns the in-memory Yjs structure and the recent un-snapshotted operation buffer. Cassandra owns the durable Operation Log (WAL).
   - **What happens**: Engine Node X OOMs due to a highly active document. Connections to it drop.
   - **Timeout/Replay**: Gateways detect the TCP reset and queue incoming client ops. The Consistent Hashing ring detects Node X's failure (via missing heartbeats in Zookeeper/Consul). The `documentId` hash ring slot maps to a new Engine Node Y. Node Y wakes up, fetches the latest snapshot from S3, then replays the WAL from Cassandra starting from the snapshot's offset.
   - **Guarantee retained**: Strong Eventual Consistency + No Data Loss. Clients replay any operations that failed to acknowledge, ensuring no acknowledged edit is lost during the node transition.

2. **Failure Case 2: Gateway Node Crash during Reconnect Gap**
   - **State Owner before crash**: Client holds local unacknowledged edits (e.g., op IDs 100-105). Gateway holds the physical TCP socket. Redis Pub/Sub routes the broadcast.
   - **What happens**: Gateway Node A reboots abruptly. The client's TCP socket is closed.
   - **Timeout/Replay**: The client's WebSocket library triggers a reconnect with exponential backoff. The Load Balancer routes the client to a new Gateway Node B. The client sends its `last_seen_op_id=99`. Gateway Node B subscribes to the doc's Redis channel, asks the Engine Node for operations > 99. The Engine Node sends ops 100-103 (which were concurrent edits from other users), and the client then pushes its unacknowledged ops 100-105 to the server.
   - **Guarantee retained**: Exactly-once operation application (Idempotency). Because operations carry universally unique CRDT identifiers (client ID + sequence), the Engine Node silently ignores duplicates if the client retries an operation the server actually received right before the crash.

## 7. ⚖️ Trade-offs and Decisions

| Decision | Option Chosen | Alternative | Why Chosen Now | Revisit Trigger |
|---|---|---|---|---|
| Concurrency Model | Yjs CRDT | OT-style transform pipeline | CRDTs eliminate the need for centralized transformation logic, simplifying server scaling and enabling true peer-to-peer offline capabilities. | Mobile client memory constraints limit CRDT metadata size. |
| Session Delivery | WebSocket | Server-Sent Events (SSE) + HTTP POST | WebSockets offer symmetric full-duplex communication with lower header overhead per message, crucial for high-frequency typing events. | Corporate firewalls blocking WSS traffic. |
| Durability Model | Event Sourcing (Op Log) + Periodic Snapshots | In-place Document Updates | Event sourcing guarantees no edits are lost and simplifies building the undo stack and version history. | Storage costs exceed budget, requiring more aggressive log compaction. |
| Presence Storage | Ephemeral Redis | Persistent DB | Presence (cursors) changes constantly and is only relevant to currently active sessions; durability is unnecessary. | Need for historical analytics on user engagement. |

---

## 8. 🔮 Follow-up Questions

1. **How do we scale sessions across many collaboration nodes?**
   - By decoupling the WebSocket termination layer (Connection Gateways) from the processing layer (Collaboration Engines). Connection gateways scale horizontally to handle sheer connection volume, while Collaboration engines scale based on active document throughput, routed via Consistent Hashing.
2. **How do we recover from node loss during active edits?**
   - The Consistent Hashing ring detects node loss. The assigned `documentId` shifts to a new node. The new node halts writes, pulls the latest S3 Snapshot, replays the Cassandra WAL to rebuild in-memory state, and then resumes accepting writes.
3. **What changes if we add full document history playback?**
   - We must permanently retain the Cassandra Operation Log instead of expiring it. We would need to implement an efficient time-travel API that loads a specific snapshot and replays operations up to a requested timestamp.
4. **How do we handle offline divergence resolution?**
   - When a client goes offline, it continues modifying its local CRDT state. Upon reconnection, it performs a state vector sync. The client sends its state vector to the server. The server replies with only the missing CRDT operations, seamlessly merging the heavily diverged offline work.

---

## 9. 🧩 Variants and Extensions

- **Variant 1 (Reader-only overflow mode):** For massive broadcasts (e.g., millions viewing a live transcript), we switch from WebSocket to CDN-backed HTTP Live Streaming (HLS) or short-polling, as WebSockets are too resource-intensive for pure read-only fan-out at that scale.
- **Variant 2 (Offline edit queue and sync reconciliation):** For spotty mobile networks, prioritizing robust CRDT sync protocols allows apps to act seamlessly offline, treating the server simply as another peer in the synchronization mesh.
- **Variant 3 (Granular Field Synchronization):** Extending the system to synchronize structured data (like Notion or Figma) by mapping CRDT principles to JSON trees (Map and Array CRDTs) rather than just linear strings.

---

## 10. 🚨 Common Pitfalls (Self-Check)

- [x] I skipped clarifying requirements (Addressed: Defined real-time, offline, and durability requirements).
- [x] I did estimates that did not influence design (Addressed: Connected 10M sockets to memory requirements).
- [x] I assumed single-writer semantics (Addressed: Deep dive on CRDT/OT concurrent writes).
- [x] I treated websocket delivery order as global consistency (Addressed: Explained server sequencing and conflict resolution).
- [x] I missed reconnect replay protocol (Addressed: Included `last_seen_op_id` and State Vector sync).
- [x] I did not mention failure handling (Addressed: Detailed node crash and partition recovery).
- [x] I did not articulate trade-offs explicitly (Addressed: Table provided).

---

## 11. 🧮 Scoring Rubric (Self-Evaluation)

| Dimension | 1 (Weak) | 3 (Okay) | 5 (Strong) | Your Score |
|---|---|---|---|---|
| Requirements handling | Vague | Mostly clear | Prioritized + quantified | 5 |
| Architecture clarity | Boxes only | Basic flow | End-to-end + failure-aware | 5 |
| Technical depth | Tool names | Some rationale | Pattern + metric-driven rationale | 5 |
| Trade-off quality | None | Some | Explicit and contextual | 5 |
| Communication | Disorganized | Understandable | Structured + concise | 5 |

---

## 12. ✅ Wrap-up Summary (Final 60-90 Seconds)

"To summarize, we designed a highly available Collaborative Document Editor supporting 50 million DAU and 10 million concurrent active sessions. We utilized a decoupled architecture, terminating WebSockets on horizontally scalable gateways, while stateful Collaboration Engine nodes handle complex concurrency via CRDTs. We durably persist all edits using an Event Sourcing model in Cassandra, compacted periodically into S3 snapshots. We intentionally traded the memory footprint of CRDTs to drastically simplify server architecture compared to traditional OT. Finally, our design explicitly handles node failures and offline client reconciliations, ensuring robust data integrity and a seamless user experience."

---

## 📌 Final Checklist

- [x] Requirements and constraints captured
- [x] Estimates tied to decisions
- [x] APIs and entities are coherent
- [x] Read/write paths are explicit
- [x] Deep dive completed
- [x] Trade-offs stated
- [x] Follow-ups addressed
- [x] Strong summary delivered

---


---

## 13. 📋 Requirement-to-Section Review

- [x] Capacity planning math: 50M DAU, 10M concurrent WebSocket connections, 20 ops/sec/doc active burst, RAM per socket connection (10 KB per socket = 100 GB RAM across connection gateways), bandwidth egress calculation (Section 2 - Capacity Planning).
- [x] Concurrency conflict resolution mathematical proof: Operational Transformation (OT) transformation functions T(ins(p1, c1), ins(p2, c2)) and TP1/TP2 divergence criteria vs Conflict-Free Replicated Data Types (CRDTs) comparing RGA, Yjs (Item structures, left/right origins), and Automerge (Section 6, Deep Dive A).
- [x] WebSocket stateful gateway architecture: Consistent hashing on documentId, Redis Pub/Sub vs cluster mesh, connection affinity, heartbeat detection (Section 6, Deep Dive B).
- [x] Rich-text delta model and distributed undo/redo buffer semantics (Section 6, Deep Dive C).
- [x] Detailed PostgreSQL / Cassandra schema for documents, snapshots, and immutable op-logs (Section 4 - Data Model).
- [x] Exact JSON API and WebSocket framing schemas (Section 3 - System Interface).
- [x] Failure modes: Client reconnection gap replay with last_seen_op_id, server node crash recovery from snapshot + WAL, offline divergence resolution (Section 6, Deep Dive D).

## Related

- [PROBLEM](./PROBLEM.md)
- [RUBRIC](./RUBRIC.md)
- [FOLLOW-UPS](./FOLLOW-UPS.md)
- [STRONG-ANSWER](./STRONG-ANSWER.md)
- [03-hld-concepts/real-time-updates](../../03-hld-concepts/real-time-updates/)
- [03-hld-concepts/consistent-hashing](../../03-hld-concepts/consistent-hashing/)
- [03-hld-concepts/workflow-orchestration](../../03-hld-concepts/workflow-orchestration/)
