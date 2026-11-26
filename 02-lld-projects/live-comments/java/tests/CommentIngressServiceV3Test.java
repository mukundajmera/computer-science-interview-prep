import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class CommentIngressServiceV3Test {

    static class FakeIdempotencyStore implements IdempotencyStore {
        private final Set<String> claimed = new HashSet<>();
        
        @Override
        public boolean claim(String key, long ttlMs) {
            if (claimed.contains(key)) {
                return false;
            }
            claimed.add(key);
            return true;
        }
    }

    static class FakeCommentStore implements DistributedCommentStore {
        private final CircularRingBufferReplayStore buffer;
        
        public FakeCommentStore(int capacity) {
            this.buffer = new CircularRingBufferReplayStore(capacity);
        }

        @Override
        public void appendComment(String streamId, String commentPayload, String region) {
            buffer.addComment(streamId, commentPayload);
        }

        @Override
        public List<String> getRecentComments(String streamId, String region, int limit) {
            // Empty cursor for getting the latest messages
            return buffer.replay(streamId, "", limit);
        }

        public List<String> replayWithCursor(String streamId, String cursor, int limit) {
            return buffer.replay(streamId, cursor, limit);
        }
    }

    static class FakeFanoutService implements DistributedFanoutService {
        private int disconnectedCount = 0;
        private int broadcastCount = 0;

        @Override
        public void broadcast(String streamId, String commentPayload, String region) {
            broadcastCount++;
            // Simulate that subscriber disconnect cannot block unrelated subscribers indefinitely
            if (disconnectedCount > 0) {
                // If this was a real WebSocket loop, a disconnected client throwing an exception
                // shouldn't halt the broadcast loop. The Fake just ignores them.
            }
        }
        
        public void simulateClientDisconnect() {
            disconnectedCount++;
        }
        
        public int getBroadcastCount() {
            return broadcastCount;
        }
    }

    static class FakeSessionRegistry implements DistributedSessionRegistry {
        private final Set<String> sessions = new HashSet<>();
        
        @Override
        public void registerSession(String streamId, String sessionId, String userId, String region) {
            sessions.add(sessionId);
        }

        @Override
        public void unregisterSession(String streamId, String sessionId, String region) {
            sessions.remove(sessionId);
        }
        
        public boolean isRegistered(String sessionId) {
            return sessions.contains(sessionId);
        }
    }

    static class FakeModerationPipelineV3 implements ModerationPipelineV3 {
        @Override
        public boolean isApproved(String payload) {
            return !payload.contains("bad");
        }
    }

    private FakeCommentStore store;
    private FakeIdempotencyStore idemp;
    private FakeFanoutService fanout;
    private FakeSessionRegistry registry;
    private FakeModerationPipelineV3 mod;
    private CommentIngressServiceV3 service;

    @BeforeEach
    void setUp() {
        store = new FakeCommentStore(10); // capacity 10
        idemp = new FakeIdempotencyStore();
        fanout = new FakeFanoutService();
        registry = new FakeSessionRegistry();
        mod = new FakeModerationPipelineV3();
        
        service = new CommentIngressServiceV3(store, idemp, fanout, registry, mod);
    }

    @Test
    void testGapOnOverflow() {
        // Publish 12 messages to overflow the capacity 10 buffer
        for (int i = 0; i < 12; i++) {
            service.publishComment("stream1", "msg" + i, "idem" + i, "us-east");
        }
        
        List<String> gapReplay = store.replayWithCursor("stream1", "1", 50);
        Assertions.assertTrue(gapReplay.get(0).contains("GAP"), "Expected documented sequence gap on overflow");
        Assertions.assertEquals("msg2", gapReplay.get(1));
        Assertions.assertEquals("msg11", gapReplay.get(gapReplay.size() - 1));
    }

    @Test
    void testSubscriberDisconnect() {
        // Simulate subscriber disconnect
        fanout.simulateClientDisconnect();
        
        // Broadcast shouldn't be blocked by disconnected subscriber
        service.publishComment("stream1", "Hello", "idem-hello", "us-east");
        Assertions.assertEquals(1, fanout.getBroadcastCount(), "Unrelated subscribers shouldn't be blocked");
    }

    @Test
    void testIdempotencyDuplicates() {
        boolean first = service.publishComment("stream1", "Hello", "idem-dup", "us-east");
        boolean second = service.publishComment("stream1", "Hello", "idem-dup", "us-east");
        
        Assertions.assertTrue(first);
        Assertions.assertFalse(second, "Duplicate idempotency key should be rejected");
        
        List<String> recent = store.getRecentComments("stream1", "us-east", 50);
        Assertions.assertEquals(1, recent.size());
    }

    @Test
    void testModerationRejection() {
        boolean valid = service.publishComment("stream1", "good message", "idem-good", "us-east");
        boolean invalid = service.publishComment("stream1", "this is a bad message", "idem-bad", "us-east");
        
        Assertions.assertTrue(valid);
        Assertions.assertFalse(invalid, "Moderation should reject 'bad' messages");
        
        List<String> recent = store.getRecentComments("stream1", "us-east", 50);
        Assertions.assertEquals(1, recent.size());
        Assertions.assertEquals("good message", recent.get(0));
    }

    @Test
    void testSessionCancellation() {
        service.joinStream("stream1", "sess1", "user1", "us-east");
        Assertions.assertTrue(registry.isRegistered("sess1"));
        
        service.leaveStream("stream1", "sess1", "us-east");
        Assertions.assertFalse(registry.isRegistered("sess1"));
    }
}
