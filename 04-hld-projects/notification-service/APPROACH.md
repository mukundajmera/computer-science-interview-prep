# Design Approach for Notification Service

A step-by-step thought process for designing a scalable notification system.

---

## 1. Requirements Clarification

### Functional vs Non-Functional

**Functional (What the system does):**
- Send notifications via email, SMS, push
- Template-based message rendering
- Bulk notification support (fan-out)
- Scheduling and priority levels
- Delivery tracking and retry

**Non-Functional (How the system behaves):**
- High availability (99.9%)
- At-least-once delivery guarantee
- Low latency for critical notifications
- Horizontal scalability
- Eventually consistent delivery status

### Assumptions with Numbers

| Metric | Value | Reasoning |
|--------|-------|-----------|
| Daily Notifications | 100M | Large user base |
| Peak Notifications/Hour | 10M | Flash sales, campaigns |
| User Base | 500M | Global service |
| Channels | 3 | Email, SMS, Push |
| Templates | 1,000 | Various notification types |

---

## 2. Back-of-the-Envelope Estimation

### Traffic Calculations

```
Daily Volume:
- 100M notifications/day
- = 100M / (24 * 3600) = ~1,150 notifications/second (average)
- Peak: 10M/hour = ~2,800 notifications/second

By Channel (at peak):
- Push (50%): 1,400/sec
- Email (30%): 840/sec
- SMS (20%): 560/sec
```

### Storage Calculations

```
Per Notification Record:
- Notification ID: 16 bytes
- User ID: 16 bytes
- Template ID: 8 bytes
- Channel: 1 byte
- Status: 1 byte
- Created/Updated: 16 bytes
- Metadata: ~200 bytes
- Total: ~260 bytes

Daily Storage:
- 100M * 260 bytes = 26 GB/day
- Monthly: ~780 GB
- Yearly: ~9.5 TB

Retention: 90 days = ~2.4 TB active storage
```

### Queue Depth

```
At peak (2,800/sec):
- If processing takes 100ms average
- Queue depth = 2,800 * 0.1 = 280 messages in flight
- Buffer for spikes: 10x = 2,800 messages
- With retries: 3x = 8,400 messages max

Memory for queue: 8,400 * 1KB = ~8.4 MB (trivial)
```

---

## 3. API Design

### Endpoint 1: Send Single Notification

```
POST /api/v1/notifications

Request:
{
    "userId": "user-123",
    "templateId": "order-confirmation",
    "channel": "email",
    "priority": "high",
    "variables": {
        "orderNumber": "ORD-001",
        "customerName": "John Doe",
        "amount": "$99.99"
    },
    "scheduledAt": null,
    "idempotencyKey": "order-confirmation-ORD-001"
}

Response (202 Accepted):
{
    "notificationId": "notif-abc123",
    "status": "queued",
    "estimatedDelivery": "2024-12-15T10:00:05Z"
}

Errors:
- 400: Invalid request (bad template, missing variables)
- 404: User not found or template not found
- 429: Rate limit exceeded
```

### Endpoint 2: Send Bulk Notification

```
POST /api/v1/notifications/bulk

Request:
{
    "templateId": "flash-sale",
    "channel": "push",
    "priority": "normal",
    "variables": {
        "discountPercent": "50%",
        "validUntil": "2024-12-16"
    },
    "targetAudience": {
        "type": "segment",
        "segmentId": "active-users-30-days"
    },
    "scheduledAt": "2024-12-15T10:00:00Z",
    "idempotencyKey": "flash-sale-dec-2024"
}

Response (202 Accepted):
{
    "batchId": "batch-xyz789",
    "estimatedRecipients": 5000000,
    "status": "processing",
    "trackingUrl": "/api/v1/batches/batch-xyz789"
}
```

### Endpoint 3: Get Notification Status

```
GET /api/v1/notifications/{notificationId}/status

Response:
{
    "notificationId": "notif-abc123",
    "userId": "user-123",
    "channel": "email",
    "status": "delivered",
    "createdAt": "2024-12-15T10:00:00Z",
    "deliveredAt": "2024-12-15T10:00:05Z",
    "attempts": 1
}

Status values: queued, processing, sent, delivered, failed, bounced
```

### Endpoint 4: Manage Templates

```
POST /api/v1/templates

Request:
{
    "templateId": "order-confirmation",
    "channel": "email",
    "subject": "Order {{orderNumber}} Confirmed",
    "body": "Hi {{customerName}}, your order for {{amount}} is confirmed.",
    "variables": ["orderNumber", "customerName", "amount"]
}

Response:
{
    "templateId": "order-confirmation",
    "version": 1,
    "createdAt": "2024-12-15T09:00:00Z"
}
```

### Idempotency

- All send endpoints require `idempotencyKey`
- Duplicate requests within 24 hours return existing notification
- Prevents duplicate sends during retries

---

## 4. Data Model

### Database Choice: Hybrid

| Data Type | Database | Reasoning |
|-----------|----------|-----------|
| Notifications | Cassandra | High write throughput, time-series queries |
| Templates | PostgreSQL | Structured data, low volume |
| User Preferences | Redis + PostgreSQL | Fast reads, reliable storage |
| Delivery Logs | Cassandra | Append-only, time-partitioned |

### Notifications Table (Cassandra)

```
Table: notifications
Partition Key: (user_id, year_month)
Clustering Key: (created_at DESC, notification_id)

{
    user_id:          text
    year_month:       text        // "2024-12" for partitioning
    notification_id:  uuid
    template_id:      text
    channel:          text        // email, sms, push
    priority:         text        // critical, high, normal, low
    status:           text        // queued, sent, delivered, failed
    variables:        map<text, text>
    scheduled_at:     timestamp
    created_at:       timestamp
    updated_at:       timestamp
    delivered_at:     timestamp
    attempt_count:    int
    last_error:       text
}
```

### Templates Table (PostgreSQL)

```sql
CREATE TABLE templates (
    template_id     VARCHAR(100) PRIMARY KEY,
    channel         VARCHAR(20) NOT NULL,
    name            VARCHAR(255) NOT NULL,
    subject         TEXT,
    body            TEXT NOT NULL,
    variables       JSONB,
    version         INT DEFAULT 1,
    is_active       BOOLEAN DEFAULT true,
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_templates_channel ON templates(channel);
```

### User Preferences Table

```sql
CREATE TABLE user_notification_preferences (
    user_id         VARCHAR(50) PRIMARY KEY,
    email_enabled   BOOLEAN DEFAULT true,
    sms_enabled     BOOLEAN DEFAULT true,
    push_enabled    BOOLEAN DEFAULT true,
    quiet_hours     JSONB,  -- {"start": "22:00", "end": "08:00"}
    opted_out_types TEXT[],
    updated_at      TIMESTAMP DEFAULT NOW()
);
```

---

## 5. High-Level Architecture

### Logical Components

```
┌─────────────────────────────────────────────────────────────────┐
│                        API Gateway                               │
│              (Rate Limiting, Authentication)                     │
└─────────────────────────────┬───────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        ┌──────────┐    ┌──────────┐    ┌──────────┐
        │Notif API │    │Template  │    │Preference│
        │ Service  │    │ Service  │    │ Service  │
        └────┬─────┘    └────┬─────┘    └────┬─────┘
             │               │               │
             │     ┌─────────┴───────────────┘
             │     │
             ▼     ▼
        ┌──────────────┐
        │   Priority   │
        │   Router     │
        └──────┬───────┘
               │
    ┌──────────┼──────────┐──────────┐
    ▼          ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│Critical│ │ High   │ │Normal  │ │ Low    │
│ Queue  │ │ Queue  │ │ Queue  │ │ Queue  │
└───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘
    │          │          │          │
    └──────────┼──────────┼──────────┘
               │
               ▼
        ┌──────────────┐
        │   Channel    │
        │   Router     │
        └──────┬───────┘
               │
    ┌──────────┼──────────┐
    ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐
│ Email  │ │  SMS   │ │ Push   │
│Provider│ │Provider│ │Provider│
│ Pool   │ │ Pool   │ │ Pool   │
└───┬────┘ └───┬────┘ └───┬────┘
    │          │          │
    ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐
│SendGrid│ │ Twilio │ │Firebase│
│ SES    │ │Vonage  │ │  APNs  │
│Mailgun │ │        │ │        │
└────────┘ └────────┘ └────────┘
```

### HLD Concepts Used

| Concept | How It's Used |
|---------|---------------|
| **Message Queue** | Priority-based queues for async processing |
| **Worker Pool** | Channel-specific workers for parallel sending |
| **Rate Limiter** | Per-provider rate limiting |
| **Circuit Breaker** | Failover between providers |
| **Dead Letter Queue** | Store failed notifications for retry |
| **Template Engine** | Variable substitution at render time |

### Write Path (Send Notification)

```
1. Client sends POST /notifications
2. API validates request, checks user preferences
3. Fetch and render template with variables
4. Route to priority queue based on priority level
5. Return 202 Accepted with notificationId
6. (Async) Worker picks from queue
7. Route to appropriate channel provider
8. Send via provider (with rate limiting)
9. Update notification status
10. If failed, retry with exponential backoff
```

### Read Path (Check Status)

```
1. Client sends GET /notifications/{id}/status
2. Query Cassandra by notification_id
3. Return current status and delivery info
4. For batch queries, use user_id + time range
```

---

## 6. Deep Dives

### 6.1 Message Queue Design for Retries

**Priority Queue Setup:**
```
Queues (separate topics/queues):
1. critical-notifications (processed first)
2. high-notifications
3. normal-notifications  
4. low-notifications

Worker allocation:
- Critical: 40% of workers
- High: 30% of workers
- Normal: 20% of workers
- Low: 10% of workers
```

**Retry with Exponential Backoff:**
```
Retry Schedule:
- Attempt 1: Immediate
- Attempt 2: 1 minute
- Attempt 3: 5 minutes
- Attempt 4: 15 minutes
- Attempt 5: 1 hour
- Attempt 6: 4 hours
- Max attempts: 6

After max attempts: Move to DLQ
```

**Dead Letter Queue (DLQ):**
```
DLQ Purpose:
- Store permanently failed notifications
- Allow manual investigation
- Support replay after provider issues fixed

DLQ Actions:
- Retry: Manually move back to main queue
- Archive: Move to cold storage after 30 days
- Alert: Notify ops team for high failure rates
```

### 6.2 Rate Limiting and Deduplication

**Provider Rate Limits:**
```
SendGrid: 1000 emails/second
Twilio SMS: 100 messages/second/number
Firebase: 500 messages/second

Implementation:
- Token bucket per provider
- Spillover to secondary provider
- Backpressure to queue when all providers limited
```

**Deduplication Strategy:**
```
1. Idempotency Key stored in Redis
   - Key: idempotency:{key}
   - Value: notification_id
   - TTL: 24 hours

2. Check before queuing:
   IF EXISTS idempotency:{key}
     RETURN existing notification
   ELSE
     CREATE notification
     SET idempotency:{key} = notification_id EX 86400
```

**Content-Based Dedup:**
```
Hash: SHA256(user_id + template_id + channel + variables_json)
Window: 1 hour

Prevents duplicate sends even without idempotency key
```

### 6.3 Template Management

**Template Rendering:**
```
Template: "Hello {{name}}, your order {{orderId}} is confirmed."
Variables: {"name": "John", "orderId": "ORD-001"}
Output: "Hello John, your order ORD-001 is confirmed."

Performance:
- Pre-compile templates on load
- Cache compiled templates in memory
- Variable substitution: O(n) where n = variable count
```

**Template Versioning:**
```
- Each update creates new version
- Notifications reference specific version
- Rollback by activating previous version
- Audit trail for compliance
```

---

## 7. Bottlenecks and Mitigations

### Identified Bottlenecks

| Bottleneck | Impact | Mitigation |
|------------|--------|------------|
| **Bulk Send Fan-out** | Queue overflow | Batch processing, rate limiting |
| **Provider Rate Limits** | Delayed delivery | Multi-provider pool, spillover |
| **Template Rendering** | CPU-bound | Pre-compilation, caching |
| **Database Writes** | High throughput | Cassandra partitioning, batching |
| **User Preference Lookup** | Per-notification overhead | Redis caching |

### Scaling Strategy

```
Level 1 (1M/day):
- Single queue per priority
- One provider per channel
- PostgreSQL for all data

Level 2 (100M/day):
- Kafka for message queuing
- Multiple providers with failover
- Cassandra for notifications
- Redis for caching

Level 3 (1B/day):
- Multi-region deployment
- Sharded queues by user segment
- Dedicated clusters per channel
- Real-time analytics pipeline
```

---

## 8. Evolution Plan

### v1 → v2 → v3 Narrative

**v1-basic: MVP (Week 1-2)**
```
- Single channel (email only)
- Simple in-memory queue
- Basic template substitution
- No retry logic
- PostgreSQL for storage

Handles: ~10,000 notifications/hour
```

**v2-scaled: Production Ready (Month 1-2)**
```
- All three channels (email, SMS, push)
- Kafka for message queuing
- Priority queues (4 levels)
- Retry with exponential backoff
- Dead letter queue
- Multi-provider support
- Cassandra for notifications
- Redis for preferences caching

Handles: ~1 million notifications/hour
```

**v3-distributed: Planet Scale (Month 3-6)**
```
- Multi-region deployment
- Provider failover with circuit breakers
- Advanced routing (A/B testing)
- Real-time delivery analytics
- Compliance features (GDPR, CAN-SPAM)
- Machine learning for send time optimization

Handles: ~100 million notifications/hour
```

---

## Interview Discussion Points

1. **Why Kafka over RabbitMQ?**
   - Higher throughput for our volume
   - Better for event sourcing (replay capability)
   - Consumer groups for parallel processing

2. **How to handle provider outages?**
   - Circuit breaker pattern
   - Fallback to secondary provider
   - Queue backpressure, don't lose messages

3. **Why at-least-once instead of exactly-once?**
   - Exactly-once is expensive
   - Duplicate notifications are less harmful than missed ones
   - Idempotency keys prevent user-facing duplicates

4. **How to ensure delivery order?**
   - Partition by user_id in Kafka
   - Single consumer per partition
   - Sequential processing within user context

5. **How to handle quiet hours?**
   - Check user preferences before send
   - Schedule for next available window
   - Critical notifications bypass quiet hours
