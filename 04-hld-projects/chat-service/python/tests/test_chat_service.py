import sys
import os
import uuid
from typing import Dict, Callable

# Dynamic sys.path for v1, v2, v3
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v2-scaled')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v3-distributed')))

import chat_service
import scaled_chat_service
import distributed_chat_service

class MockCache(scaled_chat_service.Cache):
    def __init__(self):
        self.data = {}
        self.published = []

    def get(self, key: str) -> str:
        return self.data.get(key)

    def set(self, key: str, value: str, ttl_seconds: int) -> None:
        self.data[key] = value

    def delete(self, key: str) -> None:
        if key in self.data:
            del self.data[key]

    def publish(self, channel: str, message: str) -> None:
        self.published.append((channel, message))

    def subscribe(self, channel: str, callback: Callable[[str, str], None]) -> None:
        pass


def test_basic_conversation_service_create():
    """Test v1-basic: BasicConversationService creates a direct conversation."""
    repo = chat_service.InMemoryConversationRepository()
    service = chat_service.BasicConversationService(repo)
    
    user1 = str(uuid.uuid4())
    user2 = str(uuid.uuid4())
    
    conv = service.create_direct_conversation(user1, user2)
    
    assert conv.type == "direct"
    assert len(conv.participant_ids) == 2
    assert user1 in conv.participant_ids
    assert user2 in conv.participant_ids
    
    # Check repository
    convs = service.get_conversations(user1)
    assert len(convs) == 1
    assert convs[0].conversation_id == conv.conversation_id


def test_typing_indicator_service():
    """Test v2-scaled: TypingIndicatorService sets typing status and broadcasts."""
    cache = MockCache()
    service = scaled_chat_service.TypingIndicatorService(cache)
    
    user_id = str(uuid.uuid4())
    conv_id = str(uuid.uuid4())
    
    # Set typing
    service.set_typing(user_id, conv_id, True)
    
    key = f"typing:{conv_id}:{user_id}"
    assert cache.data[key] == "1"
    assert len(cache.published) == 1
    assert cache.published[0] == (f"typing:{conv_id}", f"{user_id}:1")
    
    # Unset typing
    service.set_typing(user_id, conv_id, False)
    assert key not in cache.data
    assert len(cache.published) == 2
    assert cache.published[1] == (f"typing:{conv_id}", f"{user_id}:0")


def test_conflict_resolver_first_write_wins():
    """Test v3-distributed: ConflictResolver with first write wins."""
    resolver = distributed_chat_service.ConflictResolver(
        distributed_chat_service.ConflictResolutionStrategy.FIRST_WRITE_WINS
    )
    
    m1 = distributed_chat_service.DistributedMessage(
        message_id=100,
        conversation_id=str(uuid.uuid4()),
        sender_id=str(uuid.uuid4()),
        content="first",
        vector_clock=distributed_chat_service.VectorClock(),
        origin_region="us-east"
    )
    
    m2 = distributed_chat_service.DistributedMessage(
        message_id=200,
        conversation_id=str(uuid.uuid4()),
        sender_id=str(uuid.uuid4()),
        content="second",
        vector_clock=distributed_chat_service.VectorClock(),
        origin_region="us-west"
    )
    
    m3 = distributed_chat_service.DistributedMessage(
        message_id=50,
        conversation_id=str(uuid.uuid4()),
        sender_id=str(uuid.uuid4()),
        content="third",
        vector_clock=distributed_chat_service.VectorClock(),
        origin_region="eu-west"
    )
    
    # FIRST_WRITE_WINS should sort descending by message_id
    resolved = resolver.resolve([m1, m2, m3])
    
    assert [m.message_id for m in resolved] == [200, 100, 50]
