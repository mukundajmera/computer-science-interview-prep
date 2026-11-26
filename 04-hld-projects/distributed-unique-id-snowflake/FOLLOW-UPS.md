# Distributed Unique ID Generator (Snowflake) - Follow-up Questions

1. **What happens in 69 years when the timestamp bits overflow?**
   - *Answer:* The system will fail to generate new IDs (or generate negative/invalid IDs). A migration strategy to a new ID format or shifting the custom epoch would be required beforehand.

2. **How do you handle JavaScript clients?**
   - *Answer:* JS uses double-precision floats for numbers, losing precision above $2^{53}-1$. The API must serialize the 64-bit ID as a `string` in JSON responses.

3. **How does the system ensure a unique Worker ID is acquired dynamically?**
   - *Answer:* By using ZooKeeper ephemeral sequential nodes. A new node creates a session and claims an available ID. If the node dies, the session expires, the ephemeral node drops, and the ID returns to the available pool.

4. **What is the trade-off if the NTP daemon shifts the clock backwards by a few milliseconds?**
   - *Answer:* We trade availability for strict consistency. To prevent collisions, the ID generator thread must sleep and block incoming requests until the physical clock catches up to the last recorded timestamp.
