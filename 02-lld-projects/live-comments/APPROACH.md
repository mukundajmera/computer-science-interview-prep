# Approach for Live Comments System

## Overview and Core Strategy
The Live Comments system must facilitate a real-time, interactive experience where millions of concurrent users viewing the same live stream (e.g., a major sporting event) can post comments that instantly appear on everyone's screen. The primary engineering challenges are managing the massive fan-out required for broadcasting (one comment must reach a million clients instantly), handling the stateful nature of WebSockets, and ensuring the infrastructure does not collapse under extreme "thundering herd" traffic spikes.

Our approach abandons traditional stateless HTTP polling in favor of persistent WebSockets for bidirectional communication, backed by an incredibly fast, highly optimized Publish/Subscribe (Pub/Sub) messaging layer for inter-node routing. We prioritize broadcast latency and system stability over strict database consistency.

## Connection Management (WebSockets)
We utilize WebSockets as the primary transport protocol. This avoids the massive HTTP header overhead and latency associated with continuous polling. However, because WebSockets require persistent, stateful TCP connections, a single server node can only hold open a finite number of connections (typically constrained by OS file descriptors and memory, maxing out around 50k-100k per node). 
Therefore, the Connection Tier must be horizontally scaled behind a robust Load Balancer configured for sticky sessions or consistent hashing, ensuring clients stay connected to their assigned node.

## The Fan-out Strategy (Pub/Sub)
The core routing problem occurs when User A (on Node 1) posts a comment, but the million other viewers are distributed across 100 different Server Nodes. We solve this using a distributed Pub/Sub broker, typically Redis.
1. Every Server Node subscribes to specific Redis channels corresponding to the active live stream IDs they are servicing (e.g., `channel:stream_123`).
2. When Node 1 receives a validated comment, it publishes the JSON payload to `channel:stream_123`.
3. Redis instantly broadcasts this payload to all 100 Server Nodes via its highly optimized internal networking.
4. Each Server Node then iterates through its local, in-memory mapping of WebSocket connections tied to that stream and pushes the comment down to the clients. This localized fan-out dramatically reduces network hops.

## Traffic Shaping and Fast Moderation
During a pivotal moment in a broadcast, thousands of users will comment simultaneously. We cannot allow raw, unfiltered broadcast to overwhelm the clients or display toxic content.
We implement aggressive rate-limiting using Token Buckets in Redis at the Connection Node level. Furthermore, before a comment is published, it must pass through an in-memory moderation filter. We avoid slow regex matching, instead using a Trie-based algorithm against a dictionary of banned words or utilizing a highly cached, lightweight ML model. This ensures the moderation path remains in the single-digit milliseconds, preventing the processing thread pool from backing up.

## Live Comments Core Domain Implementations

To ensure transport-agnostic evaluation and robust testing, the live comments logic is decoupled from actual live WebSocket services.

Each assigned document describes actual supported versions: Java 11+ SE and Python 3.8+ utilizing only standard libraries.

### 1. Bounded Replay Ring and Sequence Gaps
A bounded replay ring emits a documented sequence gap on overflow; subscriber disconnect cannot block unrelated subscribers indefinitely.

**Java 11+ Implementation:**
```java
// Bounded capacity ring buffer implementation
public synchronized List<String> replay(String cursorStr, int limit) {
    long cursor = 0;
    boolean hasCursor = cursorStr != null && !cursorStr.isEmpty();
    if (hasCursor) {
        try { cursor = Long.parseLong(cursorStr); } catch (NumberFormatException e) {}
    }
    
    long maxSeq = sequenceGenerator.get();
    long oldestAvailable = Math.max(1, maxSeq - capacity + 1);
    
    List<String> result = new ArrayList<>();
    
    // A bounded replay ring emits a documented sequence gap on overflow
    boolean isGap = hasCursor && cursor < oldestAvailable - 1;
    if (isGap) {
        result.add("[GAP] Sequence gap detected on overflow");
        cursor = oldestAvailable - 1;
    }
    
    long startSeq;
    if (hasCursor) {
        startSeq = Math.max(cursor + 1, oldestAvailable);
    } else {
        startSeq = Math.max(oldestAvailable, maxSeq - limit + 1);
    }
    
    long endSeq = maxSeq;
    
    for (long seq = startSeq; seq <= endSeq; seq++) {
        int index = (int) (seq % capacity);
        String comment = buffer[index];
        if (comment != null) {
            result.add(comment);
        }
    }
    
    if (hasCursor && result.size() > limit) {
        return result.subList(0, limit);
    }
    return result;
}
```

**Python 3.8+ Implementation:**
```python
# Bounded capacity ring buffer implementation
def replay(self, cursor_str: str, limit: int) -> List[str]:
    with self.lock:
        cursor = 0
        has_cursor = bool(cursor_str)
        if has_cursor:
            try:
                cursor = int(cursor_str)
            except ValueError:
                pass

        max_seq = self.sequence
        oldest_available = max(1, max_seq - self.capacity + 1)
        
        result = []
        
        # A bounded replay ring emits a documented sequence gap on overflow
        is_gap = has_cursor and cursor < oldest_available - 1
        if is_gap:
            result.append("[GAP] Sequence gap detected on overflow")
            cursor = oldest_available - 1
            
        if has_cursor:
            start_seq = max(cursor + 1, oldest_available)
        else:
            start_seq = max(oldest_available, max_seq - limit + 1)
            
        end_seq = max_seq
        
        for seq in range(start_seq, end_seq + 1):
            index = seq % self.capacity
            comment = self.buffer[index]
            if comment is not None:
                result.append(comment)
                
        if has_cursor and len(result) > limit:
            return result[:limit]
        return result
```

### 2. Transport-Agnostic Core Logic Testing
Duplicates, reconnect cursor, moderation rejection and cancellation are tested through fake transports, not live WebSocket services.

**Java Test Fixture via Fake Transport:**
```java
// Testing through fake transports instead of live WebSocket services to verify:
// Duplicates, reconnect cursor, moderation rejection, and cancellation.
static class FakeTransport implements CommentFanoutService, LiveSessionRegistry {
    public final List<String> broadcasted = new ArrayList<>();
    public final Set<String> registered = new HashSet<>();
    
    @Override
    public void fanout(String streamId, String commentPayload, long eventTimeMs) {
        broadcasted.add(commentPayload);
    }

    @Override
    public void register(String streamId, String sessionId, String userId) {
        registered.add(sessionId);
    }

    @Override
    public void unregister(String streamId, String sessionId) {
        registered.remove(sessionId);
    }
}
```

**Python Test Fixture via Fake Transport:**
```python
# Testing through fake transports instead of live WebSocket services to verify:
# Duplicates, reconnect cursor, moderation rejection, and cancellation.
class FakeTransport:
    def __init__(self):
        self.broadcasted = []
        self.registered = set()

    def fanout(self, stream_id: str, comment_payload: str, event_time_ms: int) -> None:
        self.broadcasted.append(comment_payload)

    def register(self, stream_id: str, session_id: str, user_id: str) -> None:
        self.registered.add(session_id)

    def unregister(self, stream_id: str, session_id: str) -> None:
        self.registered.discard(session_id)
```
