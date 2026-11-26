# Interview Questions: DynamoDB

## Basic Questions

### 1. What is DynamoDB and what are its primary use cases?
**Q**: Explain what DynamoDB is and when you would use it.

**A**: DynamoDB is Amazon's fully managed, serverless NoSQL database that provides consistent single-digit millisecond latency at any scale.

**Primary characteristics:**
- **Fully managed**: No server provisioning, patching, or maintenance
- **Serverless**: Auto-scales from zero to millions of requests per second
- **Low latency**: Single-digit millisecond P99 latency
- **Key-value + document**: Flexible data model with JSON support
- **Global tables**: Multi-region replication with one click

**Primary use cases:**
1. **User sessions**: Web/mobile app session storage
2. **Gaming**: Player profiles, leaderboards, game state
3. **IoT**: Device data collection and telemetry
4. **Shopping carts**: E-commerce cart and order data
5. **Real-time analytics**: Clickstream, user behavior tracking
6. **Serverless applications**: Perfect fit for Lambda-based apps

**Why DynamoDB over alternatives:**
- Simpler than Cassandra (no cluster management)
- More scalable than PostgreSQL (serverless auto-scaling)
- Better AWS integration than MongoDB
- More durable than Redis (persistent, replicated)

---

### 2. Explain DynamoDB's data model
**Q**: What are partition keys and sort keys?

**A**: **DynamoDB uses a key-value model with two types of primary keys:**

**1. Simple Primary Key** (partition key only):
```
Table: Users
┌────────────────┬──────────────────────┐
│ user_id (PK)   │ Attributes           │
├────────────────┼──────────────────────┤
│ user_123       │ name: "Alice"        │
│                │ email: "alice@..."   │
└────────────────┴──────────────────────┘

Query: Get item by user_id only
```

**2. Composite Primary Key** (partition key + sort key):
```
Table: UserOrders
┌──────────────┬─────────────────┬─────────────────┐
│ user_id (PK) │ order_date (SK) │ Attributes      │
├──────────────┼─────────────────┼─────────────────┤
│ user_123     │ 2024-01-15      │ order_id: "o1"  │
│              │                 │ total: $50      │
├──────────────┼─────────────────┼─────────────────┤
│ user_123     │ 2024-01-20      │ order_id: "o2"  │
│              │                 │ total: $75      │
└──────────────┴─────────────────┴─────────────────┘

Query: Get all orders for user_id, optionally filter by date range
```

**Key characteristics:**

**Partition Key (PK)**:
- Determines which partition stores the data
- Must have high cardinality (many unique values)
- Distributes data across partitions for scalability

**Sort Key (SK)**:
- Optional second part of composite key
- Sorts items within same partition key
- Enables range queries (`>`, `<`, `BETWEEN`)

**Example API calls:**
```python
 # GetItem (direct key lookup)
response = table.get_item(
    Key={
        'user_id': 'user_123',
        'order_date': '2024-01-15'
    }
)

 # Query (partition key + optional sort key filter)
response = table.query(
    KeyConditionExpression=Key('user_id').eq('user_123') &
                           Key('order_date').between('2024-01-01', '2024-01-31')
)
```

**Important**: PK + SK together must be unique!

---

### 3. What's the difference between Query and Scan?
**Q**: When would you use Query vs Scan operations?

**A**: **Query** and **Scan** are fundamentally different operations:

**Query** (efficient, recommended):
```python
 # Query by partition key
response = table.query(
    KeyConditionExpression=Key('user_id').eq('user_123')
)

 # With sort key range
response = table.query(
    KeyConditionExpression=Key('user_id').eq('user_123') &
                           Key('timestamp').between(start, end)
)
```

**Characteristics:**
- **Requires partition key**: Must specify exact partition key value
- **Efficient**: Reads only items in specific partition
- **Cost**: Pay only for items examined (not whole table)
- **Performance**: O(log N + M), M = items returned
- **Use case**: Retrieve user's orders, recent activities, etc.

**Scan** (inefficient, avoid):
```python
 # Scan entire table with filter
response = table.scan(
    FilterExpression=Attr('status').eq('active')
)
```

**Characteristics:**
- **No key required**: Reads entire table
- **Inefficient**: Examines every item in table
- **Cost**: Pay for all items read, even if filtered out
- **Performance**: O(N), N = total items in table
- **Use case**: Analytics, migrations, backups (not real-time queries)

**Performance comparison:**
```
Table: 1 million items

Query with partition key:
- Reads: 10 items from 1 partition
- Cost: 10 items charged
- Latency: ~10ms

Scan with filter:
- Reads: 1 million items, returns 10
- Cost: 1 million items charged
- Latency: ~10 seconds (with pagination)
```

**Best practice**: Always use Query; design data model to avoid Scans

---

### 4. What are capacity modes in DynamoDB?
**Q**: Explain On-Demand vs Provisioned capacity.

**A**: **DynamoDB offers two capacity modes:**

**On-Demand Mode**:
```python
table = dynamodb.create_table(
    TableName='Users',
    BillingMode='PAY_PER_REQUEST',
    ...
)
```

**Pricing**: Pay per request
- Writes: $1.25 per million (1KB writes)
- Reads: $0.25 per million (4KB eventually consistent reads)

**Characteristics:**
- **Auto-scaling**: Instant, unlimited scaling
- **No planning**: No capacity units to specify
- **Unpredictable costs**: Varies with traffic

**Best for:**
- New applications (unknown traffic patterns)
- Spiky/unpredictable workloads
- Development/testing environments
- Serverless applications with variable traffic

**Provisioned Mode**:
```python
table = dynamodb.create_table(
    TableName='Users',
    BillingMode='PROVISIONED',
    ProvisionedThroughput={
        'ReadCapacityUnits': 100,
        'WriteCapacityUnits': 50
    },
    ...
)
```

**Pricing**: Pay per hour for provisioned capacity
- Writes: $0.47 per WCU-hour
- Reads: $0.09 per RCU-hour

**Characteristics:**
- **Fixed capacity**: Specify RCU/WCU
- **Throttling**: Requests rejected if exceeding capacity
- **Auto-scaling**: Optional, scales within min/max
- **Predictable costs**: Fixed monthly bill

**Best for:**
- Predictable workloads
- Cost optimization (up to 50% cheaper than on-demand)
- Consistent traffic patterns
- Production applications with known load

**Capacity units explained:**
```
RCU (Read Capacity Unit):
- 1 RCU = 1 strongly consistent read/sec (4KB)
         OR 2 eventually consistent reads/sec (4KB)

WCU (Write Capacity Unit):
- 1 WCU = 1 write/sec (1KB)

Example calculation:
- Read 100 items/sec (4KB each, eventually consistent)
- Write 50 items/sec (2KB each)

RCUs needed: 100 / 2 = 50 RCUs
WCUs needed: 50 × (2KB / 1KB) = 100 WCUs
```

**Switching between modes**: Allowed once every 24 hours

---

### 5. What are Global Secondary Indexes (GSI)?
**Q**: Explain GSIs and when to use them.

**A**: **GSI enables querying on attributes other than primary key:**

**Without GSI** (limited queries):
```python
 # Base table
Table: Users
PK: user_id
SK: (none)

 # Can only query by user_id
response = table.get_item(Key={'user_id': 'user_123'})

 # Cannot query by email directly!
 # Would need expensive Scan operation
```

**With GSI** (flexible queries):
```python
 # Create GSI on email
GSI: EmailIndex
PK: email
SK: user_id (optional)

 # Now can query by email efficiently
response = table.query(
    IndexName='EmailIndex',
    KeyConditionExpression=Key('email').eq('alice@example.com')
)
```

**GSI characteristics:**

**1. Separate partition key**:
```
Base Table: PK=user_id
GSI:        PK=email (different attribute)
```

**2. Eventual consistency**:
- GSI updated asynchronously after base table write
- Slight delay (typically milliseconds)
- Cannot use strongly consistent reads

**3. Separate capacity**:
```python
 # GSI has its own throughput
dynamodb.update_table(
    TableName='Users',
    GlobalSecondaryIndexUpdates=[{
        'Update': {
            'IndexName': 'EmailIndex',
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 50,  # Independent of base table
                'WriteCapacityUnits': 25
            }
        }
    }]
)
```

**4. Projection** (which attributes to include):
```python
GlobalSecondaryIndexes=[{
    'IndexName': 'EmailIndex',
    'KeySchema': [
        {'AttributeName': 'email', 'KeyType': 'HASH'}
    ],
    'Projection': {
        'ProjectionType': 'INCLUDE',
        'NonKeyAttributes': ['name', 'created_at']  # Only include these
    }
}]
```

Projection types:
- **KEYS_ONLY**: Only key attributes (smallest, cheapest)
- **INCLUDE**: Key + specified attributes
- **ALL**: All attributes (largest, most expensive)

**Limitations:**
- Maximum 20 GSIs per table
- Eventually consistent only (no strong consistency)
- Costs apply for storage and throughput
- Sparse indexes: Items without GSI key are not in GSI

**LSI vs GSI:**

| Aspect | LSI (Local Secondary Index) | GSI (Global Secondary Index) |
|--------|------------------------------|------------------------------|
| **Partition key** | Same as base table | Different from base table |
| **Sort key** | Different from base table | Can be different |
| **Creation** | At table creation only | Anytime |
| **Consistency** | Strong or eventual | Eventual only |
| **Capacity** | Shares with base table | Separate capacity |
| **Limit** | 5 per table | 20 per table |

---

## Intermediate Questions

### 1. How do you design a good partition key?
**Q**: What makes a good partition key in DynamoDB?

**A**: **Partition key determines data distribution and query performance:**

**Good partition key characteristics:**

**1. High cardinality** (many unique values):
```python
 # Bad: Status (only 3 values)
PK: status  # "active", "inactive", "pending"
 # 90% of users "active" → hot partition

 # Good: User ID (millions of values)
PK: user_id
 # Evenly distributed across partitions
```

**2. Uniform access patterns**:
```python
 # Bad: Date (today gets all writes)
PK: order_date  # "2024-01-31"
 # All today's orders go to same partition

 # Good: Customer ID + date as sort key
PK: customer_id
SK: order_date
 # Writes distributed across all customers
```

**3. Even distribution**:
```python
 # Bad: Product category
PK: category  # "Electronics", "Books", ...
 # Popular categories become hot partitions

 # Good: Product ID
PK: product_id
 # Each product evenly distributed
```

**Design patterns:**

**Pattern 1: Composite attributes**
```python
 # Combine attributes for uniqueness
PK: f"{tenant_id}#{user_id}"
 # Example: "tenant_abc#user_123"
```

**Pattern 2: Adding randomness**
```python
import random

 # Add random suffix to distribute writes
PK: f"{date}#{random.randint(0, 99)}"
 # Example: "2024-01-31#42"

 # Query: Must query all 100 suffixes and merge results
```

**Pattern 3: Hash-based distribution**
```python
import hashlib

def get_partition_key(user_id, shard_count=100):
    hash_value = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
    shard = hash_value % shard_count
    return f"user#{shard}"

 # Distributes users across 100 partitions
PK: get_partition_key("user_123")  # "user#42"
```

**Monitoring hot partitions:**
```python
 # CloudWatch metrics
cloudwatch.get_metric_statistics(
    MetricName='UserErrors',
    Dimensions=[
        {'Name': 'TableName', 'Value': 'Orders'}
    ]
)

 # Check for ThrottledRequests
 # High throttling on specific partitions indicates hot partition
```

---

### 2. How would you implement pagination in DynamoDB?
**Q**: Explain pagination patterns.

**A**: **DynamoDB uses LastEvaluatedKey for pagination:**

**Basic pagination**:
```python
def get_all_items(table, user_id):
    items = []
    last_key = None

    while True:
        if last_key:
            response = table.query(
                KeyConditionExpression=Key('user_id').eq(user_id),
                ExclusiveStartKey=last_key
            )
        else:
            response = table.query(
                KeyConditionExpression=Key('user_id').eq(user_id)
            )

        items.extend(response['Items'])

        # Check if more results exist
        last_key = response.get('LastEvaluatedKey')
        if not last_key:
            break

    return items
```

**Page size limit**:
```python
response = table.query(
    KeyConditionExpression=Key('user_id').eq('user_123'),
    Limit=25  # Return max 25 items per page
)

 # DynamoDB may return fewer than Limit due to:
 # 1. Result set size limit (1 MB)
 # 2. Filter expressions reducing results
```

**Cursor-based pagination** (for APIs):
```python
import base64
import json

def encode_cursor(last_key):
    """Encode LastEvaluatedKey as cursor for API"""
    return base64.b64encode(json.dumps(last_key).encode()).decode()

def decode_cursor(cursor):
    """Decode cursor back to LastEvaluatedKey"""
    return json.loads(base64.b64decode(cursor))

 # API endpoint
@app.route('/api/orders')
def get_orders():
    cursor = request.args.get('cursor')
    start_key = decode_cursor(cursor) if cursor else None

    response = table.query(
        KeyConditionExpression=Key('user_id').eq(user_id),
        Limit=20,
        ExclusiveStartKey=start_key if start_key else None
    )

    return {
        'items': response['Items'],
        'next_cursor': encode_cursor(response['LastEvaluatedKey'])
                       if 'LastEvaluatedKey' in response else None
    }
```

**Important notes:**
- LastEvaluatedKey is **not** a row number or offset
- Cannot jump to arbitrary page (no "page 10")
- Must iterate through pages sequentially
- Cursor becomes invalid if table data changes

---

### 3. How do DynamoDB Streams work?
**Q**: Explain DynamoDB Streams and use cases.

**A**: **DynamoDB Streams capture ordered sequence of item-level changes:**

**Architecture**:
```
DynamoDB Table
    ↓ (writes trigger stream records)
DynamoDB Stream
    ├── Record 1: INSERT user_123
    ├── Record 2: MODIFY user_123
    ├── Record 3: REMOVE user_456
    └── Record 4: INSERT user_789
    ↓ (stream records processed by)
Lambda Function / Consumer
```

**Stream record types**:
```python
stream_view_types = {
    'KEYS_ONLY': {
        'Keys': {'user_id': 'user_123'}
    },
    'NEW_IMAGE': {
        'Keys': {'user_id': 'user_123'},
        'NewImage': {'user_id': 'user_123', 'name': 'Alice', ...}
    },
    'OLD_IMAGE': {
        'Keys': {'user_id': 'user_123'},
        'OldImage': {'user_id': 'user_123', 'name': 'Bob', ...}
    },
    'NEW_AND_OLD_IMAGES': {
        'Keys': {'user_id': 'user_123'},
        'OldImage': {...},
        'NewImage': {...}
    }
}
```

**Common use cases:**

**1. Real-time aggregation**:
```python
 # Stream: New order inserted
 # Lambda: Update user's total spending

def lambda_handler(event, context):
    for record in event['Records']:
        if record['eventName'] == 'INSERT':
            order = record['dynamodb']['NewImage']
            user_id = order['user_id']['S']
            total = Decimal(order['total']['N'])

            # Update aggregation table
            summary_table.update_item(
                Key={'user_id': user_id},
                UpdateExpression='ADD total_spent :amount, order_count :one',
                ExpressionAttributeValues={
                    ':amount': total,
                    ':one': 1
                }
            )
```

**2. Cross-region replication** (custom):
```python
 # Stream from us-east-1 table
 # Lambda replicates to eu-west-1 table

def lambda_handler(event, context):
    for record in event['Records']:
        if record['eventName'] == 'INSERT':
            item = record['dynamodb']['NewImage']
            # Write to replica table in different region
            replica_table.put_item(Item=deserialize(item))
```

**3. Change data capture (CDC)**:
```python
 # Stream: DynamoDB changes
 # Lambda: Sync to Elasticsearch for full-text search

def lambda_handler(event, context):
    for record in event['Records']:
        item = record['dynamodb']['NewImage']

        if record['eventName'] == 'INSERT' or record['eventName'] == 'MODIFY':
            # Index in Elasticsearch
            es.index(index='users', id=item['user_id']['S'], body=deserialize(item))
        elif record['eventName'] == 'REMOVE':
            # Delete from Elasticsearch
            es.delete(index='users', id=record['dynamodb']['Keys']['user_id']['S'])
```

**4. Audit logging**:
```python
 # Record all changes to audit table
def lambda_handler(event, context):
    for record in event['Records']:
        audit_table.put_item(Item={
            'audit_id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'event_type': record['eventName'],
            'table_name': record['eventSourceARN'].split('/')[1],
            'old_image': record['dynamodb'].get('OldImage'),
            'new_image': record['dynamodb'].get('NewImage')
        })
```

**Characteristics:**
- 24-hour retention (cannot configure)
- Ordered within shard
- Exactly-once processing (with proper handling)
- Near real-time (typically <1 second delay)

---

## Advanced Questions

### 1. How do you implement optimistic locking in DynamoDB?
**Q**: Prevent concurrent update conflicts.

**A**: **Use conditional writes with version attribute:**

```python
def update_with_optimistic_locking(table, user_id, new_data):
    """
    Optimistic locking prevents lost updates.

    Scenario:
    - User A reads item (version=1)
    - User B reads item (version=1)
    - User A updates (version=1 → 2) ✓
    - User B updates (version=1 → 2) ✗ (fails, version already 2)
    """
    try:
        # Read current item with version
        response = table.get_item(Key={'user_id': user_id})
        item = response['Item']
        current_version = item['version']

        # Update with condition: version must match
        table.update_item(
            Key={'user_id': user_id},
            UpdateExpression='SET #data = :new_data, #version = :new_version',
            ConditionExpression='#version = :current_version',
            ExpressionAttributeNames={
                '#data': 'data',
                '#version': 'version'
            },
            ExpressionAttributeValues={
                ':new_data': new_data,
                ':new_version': current_version + 1,
                ':current_version': current_version
            }
        )
        return True

    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            # Version mismatch - item was modified by another process
            print("Conflict detected, retry with latest version")
            return False
        raise
```

**Pattern 2: Atomic counters** (for simple increments):
```python
 # No need for optimistic locking with atomic operations
table.update_item(
    Key={'user_id': 'user_123'},
    UpdateExpression='ADD view_count :inc',
    ExpressionAttributeValues={':inc': 1}
)
 # Atomic increment, no conflicts
```

---

### 2. How would you design a multi-tenant application with DynamoDB?
**Q**: Best practices for multi-tenancy.

**A**: **Multiple design patterns based on isolation needs:**

**Pattern 1: Single table with tenant ID in partition key** (most common):
```python
 # Composite partition key
Table: MultiTenantData
PK: "{tenant_id}#{entity_type}"
SK: "{entity_id}"

Examples:
- tenant_abc#user | user_123
- tenant_abc#order | order_456
- tenant_xyz#user | user_789

 # Query single tenant's data
response = table.query(
    KeyConditionExpression=Key('PK').begins_with('tenant_abc#user')
)
```

**Benefits:**
- Cost-effective (single table)
- Easy to manage
- Simple billing per tenant (filter by partition key prefix)

**Pattern 2: Separate table per tenant**:
```python
 # Create table for each tenant
table_name = f"tenant_{tenant_id}_data"
dynamodb.create_table(TableName=table_name, ...)
```

**Benefits:**
- Strong isolation
- Independent backups
- Tenant-specific capacity tuning

**Drawbacks:**
- AWS limits (256 tables per region default)
- Management overhead
- Higher costs

**Pattern 3: Row-level security with attribute-based access**:
```python
 # Use IAM policies with session tags
{
    "Version": "2012-10-17",
    "Statement": [{
        "Effect": "Allow",
        "Action": ["dynamodb:GetItem", "dynamodb:Query"],
        "Resource": "arn:aws:dynamodb:*:*:table/MultiTenantData",
        "Condition": {
            "ForAllValues:StringEquals": {
                "dynamodb:LeadingKeys": ["${aws:PrincipalTag/tenant_id}"]
            }
        }
    }]
}
```

**Recommendation**: Use Pattern 1 (single table) for most cases, Pattern 2 for strict isolation requirements.

---

## Common Follow-ups

- "How do you handle DynamoDB throttling?"
- "What's the difference between DynamoDB and Cassandra?"
- "How do you backup and restore DynamoDB tables?"
- "When would you use DynamoDB transactions?"
- "How do you calculate DynamoDB costs?"

---

## Red Flags to Avoid

❌ **Don't say:**
- "Use Scan for all queries" - Scans are expensive and slow
- "DynamoDB is always cheaper" - Can be very expensive at scale
- "No need for data modeling" - Poor model = poor performance and high costs
- "Use SQL-style joins" - DynamoDB doesn't support joins

❌ **Don't forget:**
- Partition key design is critical (avoid hot partitions)
- GSIs have eventual consistency and separate capacity
- Item size limit (400 KB)
- Query requires partition key (cannot query arbitrary attributes)

---

## How to Explain in 30 Seconds

> "DynamoDB is AWS's fully managed NoSQL database with serverless auto-scaling and single-digit millisecond latency. Key design decisions: choose partition key for even distribution (avoid hot partitions), use sort keys for range queries, create GSIs for flexible querying (separate capacity, eventual consistency), and select capacity mode (on-demand for unpredictable, provisioned for predictable workloads). Use for key-value lookups, user sessions, and IoT data. Avoid for complex queries with joins or full-text search. Monitor partition-level metrics and optimize for cost."
