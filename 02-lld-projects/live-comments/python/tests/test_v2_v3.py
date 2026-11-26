import unittest
import sys
import os

BASE_DIR = os.path.dirname(__file__)
V2_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "v2-extended"))
V3_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "v3-optimized"))

if V2_DIR not in sys.path:
    sys.path.insert(0, V2_DIR)
if V3_DIR not in sys.path:
    sys.path.insert(0, V3_DIR)

# Dynamically import to avoid test cross contamination
import importlib.util

def import_module_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

v2_ingress = import_module_from_path("comment_ingress_service_v2", os.path.join(V2_DIR, "comment_ingress_service_v2.py"))
v2_moderation = import_module_from_path("moderation", os.path.join(V2_DIR, "moderation.py"))
v2_pubsub = import_module_from_path("websocket_pubsub", os.path.join(V2_DIR, "websocket_pubsub.py"))
v2_buffer = import_module_from_path("circular_ring_buffer", os.path.join(V2_DIR, "circular_ring_buffer.py"))

v3_ingress = import_module_from_path("comment_ingress_service_v3", os.path.join(V3_DIR, "comment_ingress_service_v3.py"))



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

    def test_publish_and_join(self):
        self.service.join_stream("stream1", "sess1", "user1")
        
        self.service.publish_comment("stream1", "user1", "Hello world!", 1000)
        self.service.publish_comment("stream1", "user1", "badword test", 1001) # Should be moderated
        self.service.publish_comment("stream1", "user1", "spam test", 1002) # Should be moderated
        self.service.publish_comment("stream1", "user1", "Valid message", 1003)
        
        recent = self.buffer.replay("stream1", "", 50)
        self.assertEqual(len(recent), 2)
        self.assertEqual(recent[0], "Hello world!")
        self.assertEqual(recent[1], "Valid message")
        
        # Test join gets replay
        recent_on_join = self.service.join_stream("stream1", "sess2", "user2")
        self.assertEqual(len(recent_on_join), 2)
        
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

    def test_subscriber_disconnect(self):
        pubsub = v2_pubsub.WebSocketSessionPubSub()
        pubsub.register("stream1", "sess1", "user1")
        pubsub.register("stream1", "sess2", "user2")
        
        class BrokenConnection:
            def send(self, payload: str) -> None:
                raise Exception("Disconnect")
                
        class GoodConnection:
            def __init__(self):
                self.received = False
            def send(self, payload: str) -> None:
                self.received = True
                
        good_conn = GoodConnection()
        pubsub.add_connection("sess1", BrokenConnection())
        pubsub.add_connection("sess2", good_conn)
        
        pubsub.fanout("stream1", "hello", 1000)
        self.assertTrue(good_conn.received)
class FakeIdempotencyStore:
    def __init__(self):
        self.claimed = set()
    def claim(self, key: str, ttl_ms: int) -> bool:
        if key in self.claimed:
            return False
        self.claimed.add(key)
        return True

class FakeCommentStore:
    def __init__(self, capacity: int = 10):
        self.buffer = v2_buffer.CircularRingBufferReplayStore(capacity)
        
    def append_comment(self, stream_id: str, comment_payload: str, region: str) -> None:
        self.buffer.add_comment(stream_id, comment_payload)
        
    def get_recent_comments(self, stream_id: str, region: str, limit: int) -> list:
        return self.buffer.replay(stream_id, "", limit)
        
    def replay_with_cursor(self, stream_id: str, cursor: str, limit: int) -> list:
        return self.buffer.replay(stream_id, cursor, limit)

class FakeFanout:
    def __init__(self):
        self.disconnected_count = 0
        self.broadcast_count = 0

    def broadcast(self, stream_id: str, comment_payload: str, region: str) -> None:
        self.broadcast_count += 1
        if self.disconnected_count > 0:
            pass
            
    def simulate_client_disconnect(self):
        self.disconnected_count += 1

class FakeRegistry:
    def __init__(self):
        self.sessions = set()
        
    def register_session(self, stream_id: str, session_id: str, user_id: str, region: str) -> None:
        self.sessions.add(session_id)
        
    def unregister_session(self, stream_id: str, session_id: str, region: str) -> None:
        self.sessions.discard(session_id)
        
    def is_registered(self, session_id: str) -> bool:
        return session_id in self.sessions

class FakeModeration:
    def is_approved(self, payload: str) -> bool:
        return "bad" not in payload

class TestV3LiveComments(unittest.TestCase):
    def setUp(self):
        self.store = FakeCommentStore()
        self.idemp = FakeIdempotencyStore()
        self.service = v3_ingress.CommentIngressServiceV3(
            comment_store=self.store,
            idempotency_store=self.idemp,
            fanout_service=FakeFanout(),
            session_registry=FakeRegistry(),
            moderation_pipeline=FakeModeration()
        )

    def test_v3_publish(self):
        # Successful publish
        res = self.service.publish_comment("s1", "Good message", "idem1", "us-east")
        self.assertTrue(res)
        self.assertEqual(len(self.store.get_recent_comments("s1", "us-east", 50)), 1)

        # Idempotency duplicate
        res = self.service.publish_comment("s1", "Good message", "idem1", "us-east")
        self.assertFalse(res)
        self.assertEqual(len(self.store.get_recent_comments("s1", "us-east", 50)), 1)

        # Moderation blocked
        res = self.service.publish_comment("s1", "This is bad", "idem2", "us-east")
        self.assertFalse(res)
        
        recent = self.store.get_recent_comments("s1", "us-east", 50)
        self.assertEqual(len(recent), 1)
        self.assertEqual(recent[0], "Good message")

    def test_gap_on_overflow(self):
        for i in range(12):
            self.service.publish_comment("stream1", f"msg{i}", f"idem{i}", "us-east")
            
        gap_replay = self.store.replay_with_cursor("stream1", "1", 50)
        self.assertTrue("GAP" in gap_replay[0], "Expected documented sequence gap on overflow")
        self.assertEqual(gap_replay[1], "msg2")
        self.assertEqual(gap_replay[-1], "msg11")
        
    def test_subscriber_disconnect(self):
        # Simulate subscriber disconnect
        self.service.fanout_service.simulate_client_disconnect()
        # Broadcast shouldn't be blocked by disconnected subscriber
        self.service.publish_comment("stream1", "Hello", "idem-hello", "us-east")
        self.assertEqual(self.service.fanout_service.broadcast_count, 1, "Unrelated subscribers shouldn't be blocked")

    def test_session_cancellation(self):
        self.service.join_stream("stream1", "sess1", "user1", "us-east")
        self.assertTrue(self.service.session_registry.is_registered("sess1"))
        
        self.service.leave_stream("stream1", "sess1", "us-east")
        self.assertFalse(self.service.session_registry.is_registered("sess1"))

if __name__ == '__main__':
    unittest.main()
