import unittest
import sys
import os

# Add repo root to path to allow importing _testutil
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.insert(0, root_dir)
from _testutil import load_module

v1_mod = load_module(os.path.abspath(os.path.join(os.path.dirname(__file__), "../v1-basic/chat_service.py")), "chat_service")

class MockWebSocketSession(v1_mod.WebSocketSession):
    def __init__(self, session_id, user_id):
        self.session_id = session_id
        self.user_id = user_id
        self.messages = []
        self.open = True
        
    def send_message(self, payload):
        self.messages.append(payload)
        
    def is_open(self):
        return self.open

class TestBasicChatService(unittest.TestCase):
    def setUp(self):
        self.msg_repo = v1_mod.InMemoryMessageRepository()
        self.conv_repo = v1_mod.InMemoryConversationRepository()
        self.user_sessions = {}
        
        self.msg_service = v1_mod.BasicMessageService(
            message_repository=self.msg_repo,
            conversation_repository=self.conv_repo,
            user_sessions=self.user_sessions
        )
        self.conv_service = v1_mod.BasicConversationService(
            conversation_repository=self.conv_repo
        )
        
    def test_create_conversation(self):
        conv = self.conv_service.create_direct_conversation("u1", "u2")
        self.assertIsNotNone(conv.conversation_id)
        self.assertEqual(conv.type, "direct")
        self.assertIn("u1", conv.participant_ids)
        self.assertIn("u2", conv.participant_ids)
        
    def test_get_conversations(self):
        conv = self.conv_service.create_direct_conversation("u1", "u2")
        self.conv_service.create_direct_conversation("u1", "u3")
        
        convs = self.conv_service.get_conversations("u1")
        self.assertEqual(len(convs), 2)
        
    def test_send_message_happy_path(self):
        conv = self.conv_service.create_direct_conversation("u1", "u2")
        
        req = v1_mod.SendMessageRequest(
            conversation_id=conv.conversation_id,
            content="Hello u2!"
        )
        resp = self.msg_service.send_message("u1", req)
        
        self.assertEqual(resp.status, "sent")
        
        msgs = self.msg_repo.find_by_conversation_id(conv.conversation_id)
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0].content, "Hello u2!")
        
    def test_send_message_not_participant(self):
        conv = self.conv_service.create_direct_conversation("u1", "u2")
        
        req = v1_mod.SendMessageRequest(
            conversation_id=conv.conversation_id,
            content="Spying!"
        )
        with self.assertRaises(ValueError):
            self.msg_service.send_message("u3", req)
            
    def test_message_delivery(self):
        conv = self.conv_service.create_direct_conversation("u1", "u2")
        
        # Setup session for u2
        ws_session = MockWebSocketSession("sess2", "u2")
        self.user_sessions["u2"] = ws_session
        
        req = v1_mod.SendMessageRequest(
            conversation_id=conv.conversation_id,
            content="Are you there?"
        )
        self.msg_service.send_message("u1", req)
        
        self.assertEqual(len(ws_session.messages), 1)
        self.assertIn("Are you there?", ws_session.messages[0])
        
    def test_get_messages(self):
        conv = self.conv_service.create_direct_conversation("u1", "u2")
        
        for i in range(5):
            req = v1_mod.SendMessageRequest(
                conversation_id=conv.conversation_id,
                content=f"msg {i}"
            )
            self.msg_service.send_message("u1", req)
            
        msgs = self.msg_service.get_messages("u2", conv.conversation_id, limit=3)
        self.assertEqual(len(msgs), 3)

if __name__ == '__main__':
    unittest.main()
