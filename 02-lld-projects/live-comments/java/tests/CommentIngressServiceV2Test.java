import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.ArrayList;

public class CommentIngressServiceV2Test {

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

    @Test
    void testSubscriberDisconnect() {
        WebSocketSessionPubSub pubSub = new WebSocketSessionPubSub();
        pubSub.register("stream1", "sess1", "user1");
        pubSub.register("stream1", "sess2", "user2");
        
        pubSub.addConnection("sess1", payload -> { throw new RuntimeException("Disconnect"); });
        
        boolean[] sess2Received = {false};
        pubSub.addConnection("sess2", payload -> { sess2Received[0] = true; });
        
        pubSub.fanout("stream1", "hello", 1000L);
        Assertions.assertTrue(sess2Received[0], "Disconnect should not block unrelated subscribers");
    }
}
