import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import pytest
from message import Message, Role, Conversation
from memory import BufferMemory, WindowMemory, SummaryMemory, TokenLimitedMemory, MemoryStore
from summarizer import SimpleSummarizer, NullSummarizer
from entity_memory import EntityMemory

def test_message_token_count():
    msg = Message(role=Role.USER, content="one two three four five")
    assert msg.token_count() == 5

def test_conversation_add_and_get_messages():
    conv = Conversation()
    msg1 = Message(role=Role.USER, content="1")
    msg2 = Message(role=Role.ASSISTANT, content="2")
    conv.add_message(msg1)
    conv.add_message(msg2)
    
    msgs = conv.get_messages()
    assert len(msgs) == 2
    assert msgs[0] == msg1
    assert msgs[1] == msg2

def test_buffer_memory_stores_all():
    mem = BufferMemory()
    for i in range(5):
        mem.add_message(Message(role=Role.USER, content=f"msg-{i}"))
    assert len(mem.get_messages()) == 5

def test_window_memory_keeps_last_n():
    mem = WindowMemory(window_size=3)
    for i in range(5):
        mem.add_message(Message(role=Role.USER, content=f"msg-{i}"))
    msgs = mem.get_messages()
    assert len(msgs) == 3
    assert msgs[0].content == "msg-2"
    assert msgs[-1].content == "msg-4"

def test_summary_memory_summarizes_older_messages():
    mem = SummaryMemory(summarizer=SimpleSummarizer(), max_recent=2)
    mem.add_message(Message(role=Role.USER, content="Hello there."))
    mem.add_message(Message(role=Role.ASSISTANT, content="Hi."))
    mem.add_message(Message(role=Role.USER, content="How are you?"))
    
    msgs = mem.get_messages()
    # 1 summary + 2 recent = 3 messages
    assert len(msgs) == 3
    assert msgs[0].role == Role.SYSTEM
    assert "Hello there." in msgs[0].content

def test_token_limited_memory_fits_within_budget():
    mem = TokenLimitedMemory(max_tokens=4)
    mem.add_message(Message(role=Role.USER, content="one two")) # 2 tokens
    mem.add_message(Message(role=Role.ASSISTANT, content="three four five")) # 3 tokens
    
    # Budget is 4, recent is 3 tokens. 
    # Previous is 2 tokens (total 5). So only recent should be kept.
    msgs = mem.get_messages()
    assert len(msgs) == 1
    assert msgs[0].content == "three four five"

def test_memory_store_create_and_retrieve():
    store = MemoryStore()
    store.create_conversation("c1", BufferMemory())
    conv = store.get_conversation("c1")
    assert isinstance(conv, BufferMemory)

def test_entity_memory_extraction():
    base = BufferMemory()
    mem = EntityMemory(base)
    mem.add_message(Message(role=Role.USER, content="My name is Dave."))
    mem.add_message(Message(role=Role.USER, content="I like pizza."))
    
    ctx = mem.get_context()
    assert "Dave" in ctx
    assert "pizza" in ctx
    
    messages = mem.get_messages()
    assert messages[0].role == Role.SYSTEM
    assert "[Extracted Entities]" in messages[0].content
