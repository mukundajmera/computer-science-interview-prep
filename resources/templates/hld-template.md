# 📝 HLD Practice Template

Use this template to practice High-Level Design problems.

---

## System: [System Name]

**Date:** ___  
**Time spent:** ___

---

## 1. 📝 Requirements Clarification

### Functional Requirements
*What should the system do?*

- [ ] FR1: ___
- [ ] FR2: ___
- [ ] FR3: ___
- [ ] FR4: ___

### Non-Functional Requirements

| Requirement | Target |
|-------------|--------|
| Availability | ___% |
| Latency (read) | ___ ms |
| Latency (write) | ___ ms |
| Throughput | ___ QPS |
| Consistency | Strong / Eventual |

### Assumptions
- 
- 

### Out of Scope
- 
- 

### Clarifying Questions Asked
1. Q: ___  A: ___
2. Q: ___  A: ___

---

## 2. 📊 Capacity Estimation

### Users & Traffic

| Metric | Value | Calculation |
|--------|-------|-------------|
| Total users | ___ | |
| DAU | ___ | |
| Requests/user/day | ___ | |
| Daily requests | ___ | DAU × req/user |
| QPS | ___ | daily / 86400 |
| Peak QPS | ___ | QPS × 2-3 |

### Storage

| Data Type | Size | Count/Day | Daily | 5-Year |
|-----------|------|-----------|-------|--------|
| ___ | ___ | ___ | ___ | ___ |
| ___ | ___ | ___ | ___ | ___ |
| **Total** | | | ___ | ___ |

### Bandwidth

| Direction | Formula | Result |
|-----------|---------|--------|
| Incoming | ___ | ___ MB/s |
| Outgoing | ___ | ___ MB/s |

---

## 3. 🔌 API Design

### API 1: ___
```
POST /api/v1/___

Request:
{
    "field": "value"
}

Response: 200 OK
{
    "data": {}
}
```

### API 2: ___
```
GET /api/v1/___/{id}

Response: 200 OK
{
    "data": {}
}
```

### API 3: ___
```
DELETE /api/v1/___/{id}

Response: 204 No Content
```

---

## 4. 🗄️ Data Model

### Database Choice
- **Type:** SQL / NoSQL
- **Technology:** ___
- **Reasoning:** ___

### Schema

**Table 1: ___**
```
{
    id:         string (PK)
    field1:     type
    field2:     type
    created_at: timestamp
    updated_at: timestamp
}

Indexes: id, field1
```

**Table 2: ___**
```
{
    id:         string (PK)
    foreign_id: string (FK)
    field1:     type
}

Indexes: id, foreign_id
```

---

## 5. 🏗️ High-Level Architecture

### Diagram

```
┌─────────────────────────────────────────┐
│               Clients                   │
└───────────────────┬─────────────────────┘
                    │
                    ▼
           ┌────────────────┐
           │  Load Balancer │
           └───────┬────────┘
                   │
      ┌────────────┼────────────┐
      ▼            ▼            ▼
 ┌────────┐   ┌────────┐   ┌────────┐
 │ Server │   │ Server │   │ Server │
 └───┬────┘   └───┬────┘   └───┬────┘
     │            │            │
     └────────────┼────────────┘
                  │
         ┌────────┴────────┐
         ▼                 ▼
    ┌─────────┐       ┌─────────┐
    │  Cache  │       │   DB    │
    └─────────┘       └─────────┘
```

### Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| Load Balancer | ___ | ___ |
| Application | ___ | ___ |
| Cache | ___ | ___ |
| Database | ___ | ___ |
| Message Queue | ___ | ___ |

### Data Flow

**Read Path:**
1. ___
2. ___
3. ___

**Write Path:**
1. ___
2. ___
3. ___

---

## 6. 🔍 Deep Dives

### 6.1 Scaling Strategy

**Horizontal Scaling:**
- ___

**Database Scaling:**
- Sharding key: ___
- Replication: ___

### 6.2 Caching

| Layer | What | TTL | Invalidation |
|-------|------|-----|--------------|
| ___ | ___ | ___ | ___ |

### 6.3 Key Algorithm/Component

```
How it works:
1. ___
2. ___
3. ___
```

---

## 7. ⚖️ Trade-offs

### Decision 1: ___

| Option A | Option B |
|----------|----------|
| Pros: | Pros: |
| Cons: | Cons: |

**Chose:** ___ because ___

---

## 8. 🔮 Follow-up Questions

**Q:** What if traffic 10x?
**A:** ___

**Q:** What if ___goes down?
**A:** ___

**Q:** How to add ___?
**A:** ___

---

## 9. 🔄 Self-Review

### What went well?
- 

### What could be improved?
- 

### Time allocation:
| Phase | Planned | Actual |
|-------|---------|--------|
| Requirements | 5 min | ___ |
| Estimation | 5 min | ___ |
| API | 5 min | ___ |
| Design | 15 min | ___ |
| Deep Dive | 10 min | ___ |
| Trade-offs | 5 min | ___ |

---

*Compare with solution and note differences!*
