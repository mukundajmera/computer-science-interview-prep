import pytest
import sys
import os

# Dynamic sys.path insert for v1-basic implementation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v1-basic')))
from chat_assistant import MultiTenantChatAssistant, TenantConfig

def test_multi_tenant_isolation_and_encryption():
    assistant = MultiTenantChatAssistant()
    tenant_1 = TenantConfig("t1", "Basic", "You are T1 bot.", max_tokens_per_minute=1000)
    tenant_2 = TenantConfig("t2", "Pro", "You are T2 bot.", max_tokens_per_minute=2000)

    assistant.register_tenant(tenant_1)
    assistant.register_tenant(tenant_2)

    # Send a message to t1
    list(assistant.chat_stream("t1", "session_1", "Hello T1"))

    # Send a message to t2
    list(assistant.chat_stream("t2", "session_1", "Hello T2"))

    # Verify separate sessions memory buffers
    assert len(assistant.sessions["t1"]["session_1"].history) == 2 # 1 user, 1 assistant
    assert len(assistant.sessions["t2"]["session_1"].history) == 2 # 1 user, 1 assistant

    # Verify encryption simulated format
    t1_msg = assistant.sessions["t1"]["session_1"].history[0]["content"]
    assert t1_msg != "Hello T1" # It should be encrypted

    # Decrypt using assistant's helper
    decrypted_t1_msg = assistant._decrypt(t1_msg, tenant_1.encryption_key)
    assert decrypted_t1_msg == "Hello T1"

def test_token_rate_limiter():
    assistant = MultiTenantChatAssistant()
    # Very small rate limit to trigger easily
    tenant_1 = TenantConfig("t1", "Basic", "You are T1 bot.", max_tokens_per_minute=10)
    assistant.register_tenant(tenant_1)

    # First message: input 2 tokens, output approx 10+ tokens
    # Input is okay, output might exceed. Let's make message long enough
    response_gen = assistant.chat_stream("t1", "session_1", "One two three four five six seven eight nine ten eleven")
    responses = list(response_gen)

    assert responses == ["Error: Rate limit exceeded"]

def test_streaming_response_chunking():
    assistant = MultiTenantChatAssistant()
    tenant_1 = TenantConfig("t1", "Pro", "You are a fast bot.", max_tokens_per_minute=1000)
    assistant.register_tenant(tenant_1)

    response_gen = assistant.chat_stream("t1", "session_1", "Hello")
    chunks = list(response_gen)

    assert len(chunks) > 1 # It should chunk the string into words
    assert "Assistant " in chunks
    assert "response " in chunks
    assert "Hello'. " in "".join(chunks)

def test_session_state_persistence_and_eviction():
    # Only allow 2 active sessions
    assistant = MultiTenantChatAssistant(max_active_sessions=2)
    tenant_1 = TenantConfig("t1", "Enterprise", "Bot", max_tokens_per_minute=1000)
    assistant.register_tenant(tenant_1)

    list(assistant.chat_stream("t1", "session_1", "Msg 1"))
    list(assistant.chat_stream("t1", "session_2", "Msg 2"))

    assert "session_1" in assistant.sessions["t1"]
    assert "session_2" in assistant.sessions["t1"]

    # Make session_1 older
    import time
    time.sleep(0.01)
    # Access session_2 to update its last_accessed
    list(assistant.chat_stream("t1", "session_2", "Msg 3"))

    # Adding a 3rd session should evict the oldest one (session_1)
    list(assistant.chat_stream("t1", "session_3", "Msg 4"))

    assert "session_1" not in assistant.sessions["t1"]
    assert "session_2" in assistant.sessions["t1"]
    assert "session_3" in assistant.sessions["t1"]
