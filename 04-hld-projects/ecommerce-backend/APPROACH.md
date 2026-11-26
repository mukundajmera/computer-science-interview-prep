# E-commerce Backend - Approach

## 1. Requirements Clarification

### Functional Requirements
| Requirement | Priority | Notes |
|-------------|----------|-------|
| Product Catalog | P0 | Search, browse, product details |
| Shopping Cart | P0 | Persistent, cross-device |
| Order Placement | P0 | Checkout, payment |
| Inventory | P0 | Real-time, prevent overselling |
| User Auth | P0 | Registration, login, sessions |
| Order Tracking | P1 | Status updates, history |
| Reviews | P2 | Ratings, text reviews |

### Non-Functional Requirements
| Metric | Target | Rationale |
|--------|--------|-----------|
| Availability | 99.99% | Revenue critical |
| Search Latency | < 200ms P99 | User experience |
| Checkout Latency | < 500ms P99 | Cart abandonment |
| Inventory Consistency | Strong | Prevent overselling |
| Order Consistency | Eventual (< 1s) | Acceptable trade-off |

---

## 2. Back-of-the-Envelope Estimation

### Traffic Calculations
```
DAU: 50 million
Average sessions/user/day: 3
Average actions/session: 20

Daily requests: 50M × 3 × 20 = 3 billion
Requests per second (average): 3B / 86400 = 35,000 RPS
Peak RPS (3x): 100,000 RPS
Flash sale peak: 500,000 RPS
```

### Order Volume
```
Orders per day: 10 million
Orders per second (avg): 115 OPS
Peak OPS (10x): 1,150 OPS
Flash sale peak: 50,000 OPS
```

### Storage Calculations
```
Products: 100M × 10KB = 1 TB
Users: 200M × 2KB = 400 GB
Orders: 10M/day × 5KB × 365 = 18 TB/year
Order items: 10M/day × 4 items × 1KB × 365 = 15 TB/year
Cart data: 50M × 5 items × 500B = 125 GB (active)
```

### Database Requirements
```
Product reads: 100,000 RPS (cacheable)
Inventory writes: 50,000 OPS (peak)
Order writes: 50,000 OPS (peak)
Search queries: 10,000 QPS
```

---

## 3. API Design

### Product APIs
```
GET /api/v1/products/{product_id}
Response:
{
  "product_id": "prod_123",
  "name": "Wireless Headphones",
  "description": "High-quality wireless headphones...",
  "price": 79.99,
  "currency": "USD",
  "images": ["url1", "url2"],
  "category": "Electronics > Audio",
  "attributes": {"color": "Black", "brand": "TechAudio"},
  "rating": 4.5,
  "review_count": 1250,
  "in_stock": true,
  "estimated_delivery": "Dec 25-27"
}

GET /api/v1/products/search?q=headphones&category=electronics&page=1
Response:
{
  "results": [...],
  "total_count": 5420,
  "page": 1,
  "facets": {
    "brand": [{"name": "TechAudio", "count": 120}],
    "price_range": [{"name": "50-100", "count": 450}]
  }
}
```

### Cart APIs
```
GET /api/v1/cart
Response:
{
  "cart_id": "cart_abc",
  "items": [
    {
      "product_id": "prod_123",
      "quantity": 2,
      "unit_price": 79.99,
      "subtotal": 159.98
    }
  ],
  "subtotal": 159.98,
  "estimated_tax": 12.80,
  "estimated_total": 172.78
}

POST /api/v1/cart/items
Request:
{
  "product_id": "prod_123",
  "quantity": 1
}

PUT /api/v1/cart/items/{product_id}
Request:
{
  "quantity": 3
}

DELETE /api/v1/cart/items/{product_id}
```

### Order APIs
```
POST /api/v1/orders
Request:
{
  "shipping_address_id": "addr_123",
  "payment_method_id": "pm_456",
  "items": [
    {"product_id": "prod_123", "quantity": 2}
  ]
}

Response:
{
  "order_id": "ord_789",
  "status": "pending_payment",
  "total": 172.78,
  "payment_url": "https://..."
}

GET /api/v1/orders/{order_id}
Response:
{
  "order_id": "ord_789",
  "status": "shipped",
  "items": [...],
  "tracking_number": "1Z999AA...",
  "estimated_delivery": "2024-01-05"
}

GET /api/v1/orders?user_id={user_id}&page=1
```

### Inventory APIs (Internal)
```
POST /api/v1/inventory/reserve
Request:
{
  "reservation_id": "res_123",
  "items": [
    {"product_id": "prod_123", "quantity": 2}
  ],
  "ttl_seconds": 600
}

POST /api/v1/inventory/commit
Request:
{
  "reservation_id": "res_123"
}

POST /api/v1/inventory/release
Request:
{
  "reservation_id": "res_123"
}
```

---

## 4. Data Model

### Product Catalog (PostgreSQL + Elasticsearch)
```sql
-- PostgreSQL for authoritative data
CREATE TABLE products (
    product_id VARCHAR(32) PRIMARY KEY,
    seller_id VARCHAR(32) NOT NULL,
    name VARCHAR(500) NOT NULL,
    description TEXT,
    base_price DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    category_id VARCHAR(32),
    status ENUM('active', 'inactive', 'deleted'),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_seller (seller_id),
    INDEX idx_category (category_id)
);

CREATE TABLE product_attributes (
    product_id VARCHAR(32),
    attribute_name VARCHAR(100),
    attribute_value VARCHAR(500),
    PRIMARY KEY (product_id, attribute_name)
);

CREATE TABLE product_images (
    product_id VARCHAR(32),
    image_url VARCHAR(1000),
    display_order INT,
    PRIMARY KEY (product_id, display_order)
);
```

### Inventory (PostgreSQL with Row-Level Locking)
```sql
CREATE TABLE inventory (
    product_id VARCHAR(32) PRIMARY KEY,
    available_quantity INT NOT NULL DEFAULT 0,
    reserved_quantity INT NOT NULL DEFAULT 0,
    warehouse_id VARCHAR(32),
    last_updated TIMESTAMP DEFAULT NOW(),
    version INT DEFAULT 0  -- Optimistic locking
);

CREATE TABLE inventory_reservations (
    reservation_id VARCHAR(32) PRIMARY KEY,
    product_id VARCHAR(32) NOT NULL,
    quantity INT NOT NULL,
    status ENUM('active', 'committed', 'released', 'expired'),
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_product (product_id),
    INDEX idx_expires (expires_at)
);
```

### Shopping Cart (Redis + PostgreSQL backup)
```
Redis Hash: cart:{user_id}
  product_123 -> {"quantity": 2, "added_at": "..."}
  product_456 -> {"quantity": 1, "added_at": "..."}
TTL: 30 days

Redis String: cart_version:{user_id} -> version_number
```

### Orders (PostgreSQL)
```sql
CREATE TABLE orders (
    order_id VARCHAR(32) PRIMARY KEY,
    user_id VARCHAR(32) NOT NULL,
    status ENUM('pending_payment', 'paid', 'processing', 
                'shipped', 'delivered', 'cancelled', 'refunded'),
    subtotal DECIMAL(10,2),
    tax DECIMAL(10,2),
    shipping DECIMAL(10,2),
    total DECIMAL(10,2),
    currency VARCHAR(3),
    shipping_address_id VARCHAR(32),
    payment_method_id VARCHAR(32),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_user (user_id),
    INDEX idx_status (status),
    INDEX idx_created (created_at DESC)
);

CREATE TABLE order_items (
    order_id VARCHAR(32),
    product_id VARCHAR(32),
    quantity INT,
    unit_price DECIMAL(10,2),
    subtotal DECIMAL(10,2),
    PRIMARY KEY (order_id, product_id)
);
```

### Database Choice Rationale
| Data Type | Database | Reason |
|-----------|----------|--------|
| Products (source) | PostgreSQL | ACID, relationships |
| Products (search) | Elasticsearch | Full-text, facets, scoring |
| Inventory | PostgreSQL | Strong consistency, transactions |
| Cart | Redis | Low latency, TTL, atomic ops |
| Orders | PostgreSQL | ACID, complex queries |
| Sessions | Redis | Fast, ephemeral |

---

## 5. High-Level Architecture

### Core Components

1. **API Gateway**: Rate limiting, auth, routing
2. **Product Service**: Catalog CRUD, search
3. **Cart Service**: Cart management
4. **Order Service**: Order lifecycle
5. **Inventory Service**: Stock management
6. **Payment Service**: Payment processing
7. **User Service**: Authentication, profiles

### Key Patterns

- **Saga Pattern**: Distributed transactions for checkout
- **CQRS**: Separate read/write models for products
- **Event Sourcing**: Order state changes
- **Circuit Breaker**: Payment provider resilience

### Read Path
```
Client → CDN (static) → API Gateway → Product Service → Cache → DB/Search
```

### Write Path (Order)
```
Client → API Gateway → Order Service 
    → Inventory Service (reserve)
    → Payment Service (charge)
    → Inventory Service (commit)
    → Notification Service
```

---

## 6. Deep Dives

### Deep Dive 1: Inventory Consistency (Prevent Overselling)

**Challenge**: Handle 50K concurrent orders during flash sales without overselling

**Solution**: Two-phase reservation with optimistic locking

```
Phase 1: Reserve
1. SELECT available_quantity, version FROM inventory WHERE product_id = ?
2. Check: available_quantity >= requested_quantity
3. UPDATE inventory SET 
     reserved_quantity = reserved_quantity + ?,
     available_quantity = available_quantity - ?,
     version = version + 1
   WHERE product_id = ? AND version = ?
4. If update fails (version mismatch), retry

Phase 2: Commit or Release
- Commit: Convert reservation to permanent deduction
- Release: Restore available_quantity (on timeout or cancel)
```

**Optimizations**:
- Pre-allocate inventory chunks to app servers
- Use Redis for hot products (sync to DB async)
- Partition inventory by product category

### Deep Dive 2: Order Workflow (Saga Pattern)

**Challenge**: Coordinate a [distributed transaction](../../03-hld-concepts/distributed-transactions/THEORY.md) across services

**Solution**: Orchestrated saga with compensating transactions

```
Order Saga Steps:
1. Create Order (pending)
2. Reserve Inventory → fail: Cancel Order
3. Process Payment → fail: Release Inventory, Cancel Order
4. Commit Inventory → fail: Refund Payment, Release Inventory, Cancel Order
5. Confirm Order
6. Send Notification

Compensation Actions:
- Cancel Order: Update status to cancelled
- Release Inventory: Restore available_quantity
- Refund Payment: Call payment provider refund API
```

**Implementation**:
```
Order Service (Saga Orchestrator)
    ↓ ReserveInventoryCommand
Inventory Service
    ↓ InventoryReservedEvent / InventoryFailedEvent
Order Service
    ↓ ProcessPaymentCommand
Payment Service
    ↓ PaymentSucceededEvent / PaymentFailedEvent
Order Service
    ↓ CommitInventoryCommand
Inventory Service
    ↓ InventoryCommittedEvent
Order Service
    ↓ ConfirmOrderCommand
```

### Deep Dive 3: Product Search (CQRS + Elasticsearch)

**Challenge**: Fast, relevant search across 100M products

**Solution**: CQRS with Elasticsearch as read model

```
Write Path:
Product Service → PostgreSQL → CDC (Debezium) → Kafka → ES Indexer → Elasticsearch

Read Path:
Search Request → API Gateway → Search Service → Elasticsearch → Aggregated Response
```

**Elasticsearch Index Design**:
```json
{
  "settings": {
    "number_of_shards": 20,
    "number_of_replicas": 2
  },
  "mappings": {
    "properties": {
      "name": {"type": "text", "analyzer": "standard", "boost": 2.0},
      "description": {"type": "text"},
      "category": {"type": "keyword"},
      "brand": {"type": "keyword"},
      "price": {"type": "float"},
      "rating": {"type": "float"},
      "review_count": {"type": "integer"},
      "in_stock": {"type": "boolean"},
      "created_at": {"type": "date"}
    }
  }
}
```

**Search Features**:
- Full-text with typo tolerance
- Faceted filtering (brand, price range, rating)
- Relevance boosting (popularity, conversion rate)
- Spell correction and suggestions

---

## 7. Bottlenecks and Mitigations

### Bottleneck 1: Inventory Hot Spots
| Issue | Mitigation |
|-------|------------|
| Single product high demand | Shard inventory by warehouse |
| Lock contention | Optimistic locking + retry |
| Flash sale surge | Pre-allocate inventory buckets |

### Bottleneck 2: Cart Service Load
| Issue | Mitigation |
|-------|------------|
| 500M cart ops/day | Redis cluster with consistent hashing |
| Large carts | Limit items per cart (100) |
| Cart sync delays | Async persistence to PostgreSQL |

### Bottleneck 3: Order Spikes
| Issue | Mitigation |
|-------|------------|
| 50K OPS peak | Horizontal scaling + queue buffering |
| Payment timeouts | Async payment with webhooks |
| DB write throughput | Sharding by user_id |

### Bottleneck 4: Search Load
| Issue | Mitigation |
|-------|------------|
| 10K QPS | Elasticsearch cluster with replicas |
| Slow queries | Query caching, result pagination |
| Index updates | Batch indexing, async CDC |

---

## 8. Evolution Plan

### v1: Basic (MVP)
- Single region deployment
- PostgreSQL for all data
- Basic search with SQL LIKE
- Synchronous payment
- In-memory cart (session-based)

### v2: Scaled
- Multi-AZ deployment
- Redis for cart and caching
- Elasticsearch for search
- Async order processing with queues
- Inventory reservation system
- Payment webhook integration

### v3: Distributed (Planet-Scale)
- Multi-region with geo-routing
- CQRS for products
- Saga orchestration for orders
- Global inventory coordination
- Real-time sync across regions
- Multi-CDN for static assets
- Edge caching for catalog
