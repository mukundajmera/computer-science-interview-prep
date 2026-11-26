# Strong Answer: Live Comments

**Pacing Target:** 45 minutes

## 1. Introduction and Requirements Gathering (5 mins)
**Say:** "To design the Live Comments, I'll start by clarifying the core requirements, both functional and non-functional, before diving into the component architecture. We want to ensure the system is extensible, highly concurrent, and fault-tolerant."

## 2. Entity Modeling (10 mins)
**Say:** "Let's define the primary entities and their relationships. For this system, the domain models encapsulate the core business rules."
The system relies on `Comment`, `User`, `Post`, `CommentThread`, and `Media`. The `CommentThread` acts as the aggregate root for a single post's comment section, encapsulating all nested comments.

## 3. Data Structure Rationale (10 mins)
**Say:** "Choosing the right data structures is critical for meeting our latency and throughput requirements."
I model the threaded comments using an N-ary tree. To achieve O(1) lookups, a flat `ConcurrentHashMap` links a `CommentID` directly to its `Comment` node. Additionally, a `ConcurrentSkipListMap` sorted by timestamp allows for fetching the most recent comments in logarithmic time.

To handle recent events and stream buffers optimally, we can rely on a bounded replay ring that emits a documented sequence gap on overflow.

**Java Implementation Snippet:**
```java
// java/v2-extended/CircularRingBufferReplayStore.java snippet
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

**Python Implementation Snippet:**
```python
# python/v2-extended/circular_ring_buffer.py snippet
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

## 4. Design Pattern Justifications (5 mins)
**Say:** "To keep the system modular and maintainable, I've applied specific design patterns."
The **Composite Pattern** elegantly represents the recursive tree structure of comments and nested replies. I also utilized a **Factory Pattern** to dynamically instantiate different types of comments, such as plain text, gifs, or image attachments.

## 5. Concurrency Defense & Thread-Safety Details (10 mins)
**Say:** "Given that this system will be accessed by multiple threads concurrently, ensuring thread safety without creating bottlenecks is a priority."
To ensure high concurrency, I applied `ReentrantReadWriteLock`s on the `CommentThread`. This allows thousands of concurrent readers to view the comments, while isolating writes. Furthermore, fine-grained locking is applied on specific parent comments when adding a child reply, avoiding a global lock on the entire post.

For real-time fanout, we avoid halting loops. A subscriber disconnect cannot block unrelated subscribers indefinitely.

**Java Implementation Snippet:**
```java
// java/v2-extended/WebSocketSessionPubSub.java snippet
@Override
public void fanout(String streamId, String commentPayload, long eventTimeMs) {
    Set<String> sessions = streamSubscriptions.get(streamId);
    if (sessions != null) {
        for (String sessionId : sessions) {
            WebSocketConnection conn = activeConnections.get(sessionId);
            if (conn != null) {
                try {
                    conn.send(commentPayload);
                } catch (Exception e) {
                    // ensure subscriber disconnect cannot block unrelated subscribers indefinitely
                    continue;
                }
            }
        }
    }
}
```

**Python Implementation Snippet:**
```python
# python/v2-extended/websocket_pubsub.py snippet
def fanout(self, stream_id: str, comment_payload: str, event_time_ms: int) -> None:
    with self.lock:
        sessions = self.stream_subscriptions.get(stream_id, set()).copy()
        conns = [self.active_connections.get(sid) for sid in sessions]
        
    for conn in conns:
        if conn is not None:
            try:
                conn.send(comment_payload)
            except Exception:
                # ensure subscriber disconnect cannot block unrelated subscribers indefinitely
                continue
```

## 6. Fake Transport Testing (5 mins)
**Say:** "We decoupled our core business logic from real WebSocket implementations by ensuring our duplicates, reconnect cursor, moderation rejection and cancellation are tested through fake transports, not live WebSocket services."

**Java Fake Transport Test Snippet:**
```java
// java/tests/CommentIngressServiceV2Test.java snippet
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

@Test
void testReplayWithCursorAndGap() {
    Set<String> blockedWords = new HashSet<>();
    blockedWords.add("spam");
    BasicModerationPipeline moderation = new BasicModerationPipeline(blockedWords);
    FakeTransport pubSub = new FakeTransport();
    CircularRingBufferReplayStore buffer = new CircularRingBufferReplayStore(10);
    
    CommentIngressServiceV2 service = new CommentIngressServiceV2(
            pubSub, pubSub, buffer, moderation
    );
    
    service.joinStream("stream2", "sess3", "user3");
    
    for (int i = 0; i < 12; i++) {
        service.publishComment("stream2", "user3", "msg" + i, 1000 + i);
    }
    
    List<String> gapReplay = buffer.replay("stream2", "1", 50);
    Assertions.assertTrue(gapReplay.get(0).contains("GAP"), "Should emit documented sequence gap on overflow");
    Assertions.assertEquals("msg2", gapReplay.get(1));
}

@Test
void testDuplicates() {
    BasicModerationPipeline moderation = new BasicModerationPipeline(new HashSet<>());
    FakeTransport pubSub = new FakeTransport();
    CircularRingBufferReplayStore buffer = new CircularRingBufferReplayStore(10);
    CommentIngressServiceV2 service = new CommentIngressServiceV2(pubSub, pubSub, buffer, moderation);

    service.publishComment("stream1", "user1", "duplicate msg", 1000);
    service.publishComment("stream1", "user1", "duplicate msg", 1001);

    Assertions.assertEquals(2, pubSub.broadcasted.size());
    List<String> replay = buffer.replay("stream1", "", 10);
    Assertions.assertEquals(2, replay.size());
}

@Test
void testModerationRejection() {
    Set<String> blocked = new HashSet<>();
    blocked.add("bad");
    BasicModerationPipeline moderation = new BasicModerationPipeline(blocked);
    FakeTransport fakeTransport = new FakeTransport();
    CircularRingBufferReplayStore buffer = new CircularRingBufferReplayStore(10);
    CommentIngressServiceV2 service = new CommentIngressServiceV2(fakeTransport, fakeTransport, buffer, moderation);

    service.publishComment("s1", "u1", "good message", 100);
    service.publishComment("s1", "u1", "bad message", 101);

    Assertions.assertEquals(1, fakeTransport.broadcasted.size());
    Assertions.assertEquals("good message", fakeTransport.broadcasted.get(0));
}

@Test
void testCancellation() {
    FakeTransport fakeTransport = new FakeTransport();
    CommentIngressServiceV2 service = new CommentIngressServiceV2(fakeTransport, fakeTransport, new CircularRingBufferReplayStore(10), new BasicModerationPipeline(new HashSet<>()));

    service.joinStream("s1", "sess1", "u1");
    Assertions.assertTrue(fakeTransport.registered.contains("sess1"));

    service.leaveStream("s1", "sess1");
    Assertions.assertFalse(fakeTransport.registered.contains("sess1"));
}
```

**Python Fake Transport Test Snippet:**
```python
# python/tests/test_v2_v3.py snippet
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

class TestV2LiveComments(unittest.TestCase):
    def setUp(self):
        self.pubsub = FakeTransport()
        self.moderation = v2_moderation.BasicModerationPipeline({"badword", "spam"})
        self.buffer = v2_buffer.CircularRingBufferReplayStore(10)
        self.service = v2_ingress.CommentIngressServiceV2(
            fanout_service=self.pubsub,
            session_registry=self.pubsub,
            replay_store=self.buffer,
            moderation_pipeline=self.moderation
        )

    def test_replay_with_cursor_and_gap(self):
        self.service.join_stream("stream2", "sess3", "user3")
        for i in range(12):
            self.service.publish_comment("stream2", "user3", f"msg{i}", 1000 + i)
            
        gap_replay = self.buffer.replay("stream2", "1", 50)
        self.assertTrue("GAP" in gap_replay[0], "Should emit documented sequence gap on overflow")
        self.assertEqual(gap_replay[1], "msg2")

    def test_leave_stream(self):
        self.service.join_stream("s1", "session_1", "u1")
        self.assertIn("session_1", self.pubsub.registered, "Should register through fake transport")
        
        self.service.leave_stream("s1", "session_1")
        self.assertNotIn("session_1", self.pubsub.registered, "Should cancel through fake transport")

    def test_duplicates(self):
        self.service.publish_comment("s1", "u1", "duplicate msg", 1000)
        self.service.publish_comment("s1", "u1", "duplicate msg", 1001)
        self.assertEqual(len(self.pubsub.broadcasted), 2)
        
        recent = self.buffer.replay("s1", "", 10)
        self.assertEqual(len(recent), 2)

    def test_moderation(self):
        self.service.publish_comment("stream1", "user1", "Hello world!", 1000)
        self.service.publish_comment("stream1", "user1", "badword test", 1001) # Should be moderated
        self.service.publish_comment("stream1", "user1", "spam test", 1002) # Should be moderated
        
        recent = self.buffer.replay("stream1", "", 50)
        self.assertEqual(len(recent), 1)
        self.assertEqual(recent[0], "Hello world!")
```

## 7. Failure Handling (3 mins)
**Say:** "Systems fail, so we need to anticipate and handle failures gracefully at the lowest level."
The system is designed for graceful degradation. If media attachments fail to load or process, the UI falls back to showing only the text part of the comment. Comments are persisted asynchronously; if the background persistence fails, a local cache maintains state and flags the comment for retry.

## 8. Production Trade-offs (2 mins)
**Say:** "In a real production environment, this in-memory or single-node design would require certain trade-offs and adaptations."
Storing the entire comment tree in memory provides immediate rendering but fails to scale for viral posts with millions of replies. Deeply nested pagination requires complex state management. In production, we'd offload to a document store and cache only the top N active comments in Redis.
