import unittest
import sys
import os
import asyncio

# Add repo root to path to allow importing _testutil
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.insert(0, root_dir)
from _testutil import load_module

v2_mod = load_module(os.path.abspath(os.path.join(os.path.dirname(__file__), "../v2-scaled/scaled_chat_service.py")), "scaled_chat_service")

class MockMessageQueue(v2_mod.MessageQueue):
    def __init__(self):
        self.published = []
        
    def publish(self, topic: str, message: bytes) -> None:
        self.published.append((topic, message))
        
    def subscribe(self, topic: str, consumer) -> None:
        pass

class MockCache(v2_mod.Cache):
    def __init__(self):
        self.store = {}
        self.published = []
        
    def get(self, key: str):
        return self.store.get(key)
        
    def set(self, key: str, value: str, ttl_seconds: int) -> None:
        self.store[key] = value
        
    def delete(self, key: str) -> None:
        self.store.pop(key, None)
        
    def publish(self, channel: str, message: str) -> None:
        self.published.append((channel, message))
        
    def subscribe(self, channel: str, callback) -> None:
        pass

class MockPresenceService(v2_mod.PresenceService):
    def __init__(self):
        self.users = {}
        
    def update_presence(self, user_id, status, ws_server_id=None):
        self.users[user_id] = v2_mod.UserPresence(
            user_id=user_id,
            status=status,
            ws_server_id=ws_server_id
        )
        
    def get_presence(self, user_id):
        return self.users.get(user_id, v2_mod.UserPresence(user_id=user_id))
        
    def get_group_presence(self, group_id):
        return {}
        
    def set_online(self, user_id: str, device_id: str, ws_server_id: str) -> None:
        self.update_presence(user_id, v2_mod.PresenceStatus.ONLINE, ws_server_id)
        
    def set_offline(self, user_id: str, device_id: str = None) -> None:
        if user_id in self.users:
            self.users[user_id].status = v2_mod.PresenceStatus.OFFLINE
            
    def get_presence_bulk(self, user_ids):
        return {uid: self.get_presence(uid) for uid in user_ids}
        
    def heartbeat(self, user_id, device_id):
        pass

class MockConnectionRegistry(v2_mod.ConnectionRegistry):
    def register(self, user_id, device_id, ws_server_id):
        pass
    def unregister(self, user_id, device_id):
        pass
    def get_ws_server(self, user_id):
        return "srv1"
    def push_to_user(self, ws_server_id, user_id, message):
        return True # success

class TestAsyncMessageService(unittest.TestCase):
    def setUp(self):
        self.queue = MockMessageQueue()
        self.presence = MockPresenceService()
        self.cache = MockCache()
        
        self.service = v2_mod.AsyncMessageService(
            message_queue=self.queue,
            presence_service=self.presence,
            cache=self.cache
        )
        
    def test_send_message_async(self):
        async def run_test():
            msg_id = await self.service.send_message("u1", "conv1", "Hello Async", ["u2"])
            self.assertIsNotNone(msg_id)
            
            # Check published to queue
            self.assertEqual(len(self.queue.published), 1)
            topic, data = self.queue.published[0]
            self.assertEqual(topic, self.service.DELIVERY_TOPIC)
            
            # Check status updated
            status = self.cache.get(f"msg:{msg_id}:status")
            self.assertEqual(status, v2_mod.MessageStatusEnum.SENT.value)
            
        asyncio.run(run_test())
        
    def test_send_group_message_small(self):
        async def run_test():
            msg_id = await self.service.send_group_message("u1", "group1", "Hi all", ["u1", "u2", "u3"])
            self.assertIsNotNone(msg_id)
            
            # 2 messages because sender is skipped
            self.assertEqual(len(self.queue.published), 2)
            self.assertTrue(all(t == self.service.DELIVERY_TOPIC for t, _ in self.queue.published))
            
        asyncio.run(run_test())
        
    def test_send_group_message_fanout(self):
        async def run_test():
            members = [f"u{i}" for i in range(100)]
            msg_id = await self.service.send_group_message("u1", "group_big", "Announcement", members)
            
            self.assertEqual(len(self.queue.published), 1)
            topic, data = self.queue.published[0]
            self.assertEqual(topic, self.service.FANOUT_TOPIC)
            
        asyncio.run(run_test())
        
    def test_mark_delivered(self):
        self.service.mark_delivered("msg1", "u2")
        
        # Verify cache status
        self.assertEqual(self.cache.get("msg:msg1:status:u2"), v2_mod.MessageStatusEnum.DELIVERED.value)
        
        # Verify sender notified
        self.assertEqual(len(self.cache.published), 1)
        channel, data = self.cache.published[0]
        self.assertEqual(channel, "status_updates")
        self.assertEqual(data, "msg1:delivered:u2")
        
    def test_mark_read(self):
        self.service.mark_read("msg2", "u3")
        
        self.assertEqual(self.cache.get("msg:msg2:status:u3"), v2_mod.MessageStatusEnum.READ.value)
        self.assertEqual(self.cache.published[0][1], "msg2:read:u3")


class TestDeliveryWorker(unittest.TestCase):
    def setUp(self):
        self.queue = MockMessageQueue()
        self.presence = MockPresenceService()
        self.cache = MockCache()
        self.registry = MockConnectionRegistry()
        
        self.worker = v2_mod.DeliveryWorker(
            presence_service=self.presence,
            connection_registry=self.registry,
            message_queue=self.queue,
            cache=self.cache
        )
        
    def test_worker_offline_user(self):
        # Override deserialize for testing
        def mock_deserialize(data):
            return v2_mod.DeliveryTask(
                message_id="msg123",
                conversation_id="c1",
                sender_id="u1",
                recipient_ids=["u2"],
                content="test"
            )
        self.worker._deserialize = mock_deserialize
        
        self.presence.update_presence("u2", v2_mod.PresenceStatus.OFFLINE)
        
        self.worker.process_message(b"dummy")
        
        # Should queue for offline
        self.assertEqual(self.cache.get("offline_queue:u2"), "msg123")

if __name__ == '__main__':
    unittest.main()
