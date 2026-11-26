# Design Trade-offs Matrix

## Data Structure Trade-offs

| Need | Use | Trade-off |
|------|-----|-----------|
| Fast lookup | HashMap | No ordering |
| Sorted + fast | TreeMap | O(log n) vs O(1) |
| Unique values | Set | No duplicates |
| Order preserved | LinkedHashMap | Extra memory |
| Thread-safe | ConcurrentHashMap | Slight overhead |

---

## Pattern Trade-offs

| Pattern | Pros | Cons |
|---------|------|------|
| **Singleton** | Single instance, global access | Testing hard, hidden deps |
| **Factory** | Decoupled creation | Extra classes |
| **Strategy** | Swappable algorithms | More interfaces |
| **State** | Clean state logic | More classes |
| **Observer** | Loose coupling | Memory leaks possible |

---

## Database Trade-offs

| Choice | Pros | Cons |
|--------|------|------|
| SQL | ACID, joins, mature | Scale limits |
| NoSQL | Scale, flexible | No joins, eventual consistency |
| Sharding | Horizontal scale | Complex queries |
| Replication | Read scale, HA | Write bottleneck |
| Caching | Speed | Staleness, consistency |

---

## Consistency Trade-offs

| Approach | Consistency | Availability | Use Case |
|----------|-------------|--------------|----------|
| Strong | ✅ Always latest | ❌ May block | Banking |
| Eventual | ⚠️ Eventually | ✅ Always up | Social media |
| Read-your-writes | ✅ Own writes | ✅ Good | User sessions |

---

## Caching Trade-offs

| Strategy | Freshness | Complexity | Use Case |
|----------|-----------|------------|----------|
| Write-through | ✅ Fresh | Medium | Critical data |
| Write-behind | ⚠️ Lag | High | High write load |
| Cache-aside | ⚠️ Miss penalty | Low | Read-heavy |
| Read-through | ✅ Transparent | Medium | General |

---

## Interview Trade-off Questions

**"Singleton vs Dependency Injection?"**
- Singleton: Simple, global access
- DI: Testable, flexible, preferred

**"HashMap vs TreeMap?"**
- HashMap: O(1), no order
- TreeMap: O(log n), sorted, range queries

**"SQL vs NoSQL?"**
- SQL: Relationships, ACID
- NoSQL: Scale, flexible schema

**"Sync vs Async processing?"**
- Sync: Simple, blocking
- Async: Scale, complex error handling
