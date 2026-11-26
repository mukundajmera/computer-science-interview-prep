# Chat/Messaging Service - Approach

## 1. Requirements Clarification

### Functional Requirements
- One-on-one real-time messaging
- Group chat (up to 256 members)
- Message delivery status (sent → delivered → read)
- Offline message queueing
- Conversation history with pagination
- Typing indicators and presence status

### Non-Functional Requirements
- **Latency**: < 100ms for message delivery
- **Availability**: 99.99% uptime
- **Consistency**: Eventual for receipts, causal for message ordering
- **Durability**: Zero message loss
- **Scale**: 500M DAU, 20B messages/day

### Assumptions with Concrete Numbers
- **DAU**: 500 million
- **Messages per user/day**: 40
- **Total messages/day**: 20 billion
- **Peak QPS**: 500,000 messages/second
- **Concurrent connections**: 50 million
- **Average message size**: 100 bytes
- **Group size**: avg 10, max 256

---

## 2. Back-of-the-envelope Estimation

### Messages Per Second
- Total daily messages: 500M users × 40 messages = 20B messages/day
- Average QPS: 20B / 86,400 ≈ 230,000 messages/second
- Peak QPS (3x): 700,000 messages/second

### Storage Requirements
- Message size: 100 bytes average
- Daily storage: 20B × 100 bytes = 2TB/day
- Yearly storage: 2TB × 365 = 730TB/year
- With replication (3x): 2.2PB/year

### Connection Requirements
- Concurrent connections: 50M
- WebSocket memory per connection: ~10KB
- Total memory for connections: 50M × 10KB = 500GB
- Servers needed (16GB each): ~40 WebSocket servers

### Bandwidth
- Incoming: 700K messages × 100 bytes = 70MB/s
- Outgoing (1:1 ratio): 70MB/s
- With group fan-out (avg 5x): 350MB/s outgoing

---

## 3. API Design

### REST APIs

```
POST /api/v1/messages
- Create and send a new message
- Request: { conversationId, content, type, replyToId? }
- Response: { messageId, status, timestamp }

GET /api/v1/conversations/{conversationId}/messages
- Get message history with pagination
- Query: limit, before, after
- Response: { messages[], hasMore, nextCursor }

PUT /api/v1/messages/{messageId}/read
- Mark message as read
- Response: { status, readAt }

POST /api/v1/conversations
- Create new conversation (1:1 or group)
- Request: { participantIds[], name?, type }
- Response: { conversationId, participants[], createdAt }

GET /api/v1/conversations
- List user's conversations
- Response: { conversations[], unreadCounts }

PUT /api/v1/conversations/{conversationId}/participants
- Add/remove participants from group
- Request: { add: [], remove: [] }
```

### WebSocket Events

```
Client → Server:
- connect: { userId, deviceId, authToken }
- send_message: { conversationId, content, clientMsgId }
- typing: { conversationId, isTyping }
- ack: { messageId }

Server → Client:
- new_message: { conversationId, message }
- message_delivered: { messageId, deliveredAt }
- message_read: { messageId, readBy, readAt }
- typing_indicator: { conversationId, userId, isTyping }
- presence_update: { userId, status, lastSeen }
```

---

## 4. Data Model

### Messages Table (Cassandra/ScyllaDB)
```sql
CREATE TABLE messages (
    conversation_id UUID,
    message_id TIMEUUID,  -- Time-based for ordering
    sender_id UUID,
    content TEXT,
    message_type TEXT,    -- text, image, video
    reply_to_id UUID,
    created_at TIMESTAMP,
    PRIMARY KEY (conversation_id, message_id)
) WITH CLUSTERING ORDER BY (message_id DESC);
```

### Conversations Table
```sql
CREATE TABLE conversations (
    conversation_id UUID PRIMARY KEY,
    type TEXT,            -- direct, group
    name TEXT,
    created_by UUID,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### User Conversations (for inbox)
```sql
CREATE TABLE user_conversations (
    user_id UUID,
    conversation_id UUID,
    last_message_id TIMEUUID,
    unread_count INT,
    muted BOOLEAN,
    PRIMARY KEY (user_id, last_message_id)
) WITH CLUSTERING ORDER BY (last_message_id DESC);
```

### Message Status (Redis)
```
Key: msg:{messageId}:status
Value: { sent: [], delivered: [], read: [] }
TTL: 7 days
```

### User Presence (Redis)
```
Key: presence:{userId}
Value: { status: online|offline, lastSeen: timestamp, deviceIds: [] }
TTL: 5 minutes (refresh on heartbeat)
```

### SQL vs NoSQL Decision
- **Cassandra for Messages**: Write-heavy, time-series data, partition by conversation
- **Redis for Status/Presence**: High-speed reads, ephemeral data, pub/sub support
- **PostgreSQL for User/Group metadata**: Relational data, ACID for group operations

### Sharding Strategy
- **Messages**: Partition by conversation_id
- **User Conversations**: Partition by user_id
- **Presence**: Consistent hashing across Redis cluster

---

## 5. High-Level Architecture

### Logical Components

```
┌─────────────┐     ┌─────────────────┐     ┌──────────────────┐
│   Clients   │────▶│   API Gateway   │────▶│  WebSocket LB    │
└─────────────┘     └─────────────────┘     └──────────────────┘
                                                      │
                    ┌─────────────────────────────────┴────────────┐
                    │                                              │
              ┌─────▼─────┐                               ┌────────▼───────┐
              │  REST API │                               │  WS Connection │
              │  Servers  │                               │    Managers    │
              └─────┬─────┘                               └────────┬───────┘
                    │                                              │
              ┌─────▼─────────────────────────────────────────────▼─────┐
              │                    Message Service                       │
              └─────┬─────────────────────────────────────────────┬─────┘
                    │                                             │
         ┌──────────┴──────────┐                    ┌─────────────┴─────────────┐
         │                     │                    │                           │
   ┌─────▼─────┐        ┌──────▼──────┐      ┌──────▼──────┐            ┌───────▼───────┐
   │ Cassandra │        │    Redis    │      │   Message   │            │   Presence    │
   │ (Messages)│        │  (Presence) │      │    Queue    │            │    Service    │
   └───────────┘        └─────────────┘      └──────┬──────┘            └───────────────┘
                                                    │
                                             ┌──────▼──────┐
                                             │   Delivery  │
                                             │   Workers   │
                                             └─────────────┘
```

### HLD Concepts Used
- **WebSocket**: Real-time bidirectional communication
- **Message Queue**: Decoupling, reliable delivery, offline queueing
- **Redis Pub/Sub**: Real-time event distribution
- **Consistent Hashing**: Connection server routing
- **Cache**: User sessions, presence, recent messages

### Write Path
1. Client sends message via WebSocket
2. WS Manager validates and forwards to Message Service
3. Message Service persists to Cassandra
4. Message queued for delivery
5. Delivery Worker looks up recipient's WS connection
6. Pushes message to recipient via their WS Manager
7. Updates delivery status in Redis

### Read Path
1. Client requests history via REST API
2. API Server queries Cassandra by conversation_id
3. Returns paginated results
4. Hot conversations may be served from cache

---

## 6. Deep Dives

### Deep Dive 1: Message Ordering and ID Generation

**Challenge**: Ensure messages appear in correct order across distributed systems.

**Solution**: TIMEUUID for message IDs
- Based on timestamp + unique node ID
- Guarantees ordering within same millisecond
- No coordination needed between servers

**Vector Clocks for Conflict Detection**:
- Each client maintains a vector clock
- Server detects concurrent edits
- Useful for edit/delete operations

```
Message ID Structure:
| Timestamp (48 bits) | Node ID (16 bits) | Sequence (16 bits) |
|---------------------|-------------------|---------------------|
```

### Deep Dive 2: Delivery Guarantees for Offline Users

**Challenge**: Ensure messages reach users who are offline.

**Solution**: Message Queue + Persistent Storage

1. **Online Delivery**:
   - Check presence service
   - Push via WebSocket
   - If ACK received → mark delivered

2. **Offline Queueing**:
   - If user offline → queue in Kafka
   - Partition by user_id for ordering
   - When user reconnects → drain queue

3. **Multi-Device Sync**:
   - Each device has device_id
   - Track delivery per device
   - Sync cursor for history

**Retry Strategy**:
```
Attempt 1: Immediate push
Attempt 2: 1 second delay
Attempt 3: 5 second delay
Attempt 4: Move to offline queue
```

### Deep Dive 3: Scaling WebSocket Connections

**Challenge**: Millions of concurrent persistent connections.

**Solution**: Horizontally Scaled Connection Layer

1. **Connection Managers**:
   - Stateful servers managing WebSocket connections
   - Each server handles ~100K connections
   - Connected to Redis for session state

2. **Connection Routing**:
   - Consistent hashing by user_id
   - Sticky sessions via load balancer
   - Registry stores user→server mapping

3. **Cross-Server Communication**:
   - Use Redis Pub/Sub or Kafka
   - Message Service publishes to topic
   - Correct Connection Manager receives and delivers

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Conn Mgr 1 │     │  Conn Mgr 2 │     │  Conn Mgr N │
│ (Users A-H) │     │ (Users I-P) │     │ (Users Q-Z) │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       └───────────────────┴───────────────────┘
                           │
                    ┌──────▼──────┐
                    │ Redis Pub/  │
                    │    Sub      │
                    └─────────────┘
```

---

## 7. Bottlenecks and Mitigations

| Bottleneck | Mitigation |
|------------|------------|
| WebSocket server memory | Horizontal scaling, efficient memory per connection |
| Hot conversations (celebrity groups) | Partition large groups, dedicated servers |
| Message database writes | Cassandra's write-optimized design, compaction |
| Presence updates flooding | Batch updates, rate limiting, presence sharding |
| Group message fan-out | Async fan-out workers, lazy delivery |
| Redis pub/sub overload | Sharded Redis, topic partitioning |

---

## 8. Evolution Plan

### v1 → v2: Adding Scale
- Add message queue for reliable delivery
- Implement group chat with fan-out workers
- Add read receipts and delivery status
- Presence service with Redis

### v2 → v3: Planet Scale
- Multi-region deployment with geo-routing
- Message ordering with vector clocks
- Multi-device synchronization
- Conflict resolution for concurrent operations
- Global message ID generation with Snowflake
