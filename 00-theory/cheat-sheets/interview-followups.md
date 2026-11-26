# Common Interview Follow-up Questions

## By LLD Problem

### Parking Lot
1. "How to handle electric vehicle charging spots?"
2. "How to make it thread-safe?"
3. "How to implement dynamic pricing?"
4. "Multiple entry/exit points?"
5. "How to find nearest available spot?"

### Elevator System
1. "Add weight capacity?"
2. "How to handle rush hour?"
3. "Multiple elevator banks?"
4. "Emergency stop?"
5. "Compare FCFS vs SCAN vs LOOK?"

### LRU Cache
1. "Why HashMap + DLL, not just one?"
2. "Make it thread-safe?"
3. "Add TTL (expiration)?"
4. "How does Redis do it?"
5. "LRU vs LFU?"

### Rate Limiter
1. "Token Bucket vs Leaky Bucket?"
2. "Distributed rate limiting?"
3. "Different limits per user tier?"
4. "Sliding window vs fixed window?"
5. "How to handle bursts?"

### Vending Machine
1. "Why State Pattern?"
2. "Add multiple payment methods?"
3. "Handle out of change?"
4. "Concurrent users?"
5. "Add new product types?"

---

## Generic Follow-ups

### Scalability
- "How would you scale this to 10x users?"
- "What's the bottleneck?"
- "How to shard the data?"

### Concurrency
- "What happens with concurrent requests?"
- "How to prevent race conditions?"
- "What locks would you use?"

### Failure Handling
- "What if X component fails?"
- "How to handle partial failures?"
- "Retry strategy?"

### Testing
- "How would you test this?"
- "What edge cases?"
- "How to mock dependencies?"

---

## Pattern-Specific Questions

### Singleton
- "How to prevent reflection attacks?"
- "Lazy vs eager initialization?"
- "Thread-safe without synchronized?"

### Factory
- "When Factory Method vs Abstract Factory?"
- "How to add new types?"
- "Registry pattern for extensibility?"

### Strategy
- "How to select strategy at runtime?"
- "Default strategy?"
- "Strategy vs State difference?"

---

## Quick Answers Template

**"How would you improve this?"**
1. Add caching for frequent queries
2. Async processing for heavy operations
3. Better error handling
4. Metrics and monitoring

**"What would you do differently?"**
1. Use interface over concrete classes
2. Add dependency injection
3. Better separation of concerns
4. More comprehensive tests
