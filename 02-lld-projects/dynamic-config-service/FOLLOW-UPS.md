# Follow-Ups (Optional Staff Extensions)

1. **How would you support JSON payloads in your variants?**
   - We would use an object or dictionary representation (like `Map<String, Object>` in Java) and rely on the client to cast or deserialize.

2. **How would you synchronize state across multiple server instances without restarting?**
   - We could use a distributed key-value store (like Redis or etcd) and have each instance subscribe to Pub/Sub events to update their in-memory caches dynamically.

3. **How do you handle schema changes to the flag rules safely?**
   - Implement versioning on the flag objects. The evaluation engine can check the version to parse rules appropriately.

4. **How would you handle Reverse Indexing for targeted invalidations?**
   - If we need a "which flags affect this user?" reverse lookup, we would introduce an inverted index mapping attributes to flags. This introduces a heavy write/memory penalty. The engine is intentionally forward-only to optimize for reads.
