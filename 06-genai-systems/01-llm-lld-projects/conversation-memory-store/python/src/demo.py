"""
Runnable demo for the Conversation Memory Store.

Shows each memory strategy in action with the same conversation,
illustrating how different strategies shape the context sent to an LLM.
"""

from message import Conversation, Message, Role
from memory import (
    BufferMemory,
    MemoryStore,
    SummaryMemory,
    TokenLimitedMemory,
    WindowMemory,
)
from summarizer import SimpleSummarizer


def _build_sample_messages():
    """Create a realistic multi-turn conversation."""
    return [
        Message(role=Role.SYSTEM, content="You are a helpful assistant."),
        Message(role=Role.USER, content="What is caching?"),
        Message(
            role=Role.ASSISTANT,
            content="Caching stores copies of data in a fast-access layer. It reduces latency and load on the primary data store.",
        ),
        Message(role=Role.USER, content="How does Redis work?"),
        Message(
            role=Role.ASSISTANT,
            content="Redis is an in-memory key-value store. It supports strings, hashes, lists, sets, and sorted sets.",
        ),
        Message(role=Role.USER, content="What about cache invalidation?"),
        Message(
            role=Role.ASSISTANT,
            content="Cache invalidation removes stale data. Common strategies are TTL-based expiry, write-through, and write-behind.",
        ),
        Message(role=Role.USER, content="Can you compare Redis vs Memcached?"),
        Message(
            role=Role.ASSISTANT,
            content="Redis supports richer data types and persistence. Memcached is simpler and focused on pure key-value caching with multi-threaded performance.",
        ),
    ]


def demo_buffer_memory():
    """BufferMemory keeps every message."""
    print("=" * 60)
    print("BUFFER MEMORY — keeps all messages")
    print("=" * 60)
    mem = BufferMemory()
    for msg in _build_sample_messages():
        mem.add_message(msg)
    print(f"Messages stored: {len(mem.get_messages())}")
    print(mem.get_context())
    print()


def demo_window_memory():
    """WindowMemory keeps only the last N messages."""
    print("=" * 60)
    print("WINDOW MEMORY (window_size=4) — last 4 messages")
    print("=" * 60)
    mem = WindowMemory(window_size=4)
    for msg in _build_sample_messages():
        mem.add_message(msg)
    print(f"Messages in context: {len(mem.get_messages())}")
    print(mem.get_context())
    print()


def demo_summary_memory():
    """SummaryMemory summarizes older messages, keeps recent ones."""
    print("=" * 60)
    print("SUMMARY MEMORY (max_recent=3) — summarize + recent")
    print("=" * 60)
    mem = SummaryMemory(summarizer=SimpleSummarizer(), max_recent=3)
    for msg in _build_sample_messages():
        mem.add_message(msg)
    msgs = mem.get_messages()
    print(f"Messages in context: {len(msgs)}")
    print(f"Running summary: {mem.running_summary[:80]}...")
    print()
    print(mem.get_context())
    print()


def demo_token_limited_memory():
    """TokenLimitedMemory keeps messages within a token budget."""
    print("=" * 60)
    print("TOKEN-LIMITED MEMORY (max_tokens=30) — fit within budget")
    print("=" * 60)
    mem = TokenLimitedMemory(max_tokens=30)
    for msg in _build_sample_messages():
        mem.add_message(msg)
    msgs = mem.get_messages()
    total_tokens = sum(m.token_count() for m in msgs)
    print(f"Messages in context: {len(msgs)} (≈{total_tokens} tokens)")
    print(mem.get_context())
    print()


def demo_memory_store():
    """MemoryStore manages multiple independent conversations."""
    print("=" * 60)
    print("MEMORY STORE — multi-conversation management")
    print("=" * 60)
    store = MemoryStore()

    conv1 = store.create_conversation("conv-1", BufferMemory())
    conv1.add_message(Message(role=Role.USER, content="Hello from conversation 1"))

    conv2 = store.create_conversation("conv-2", WindowMemory(window_size=3))
    conv2.add_message(Message(role=Role.USER, content="Hello from conversation 2"))

    print(f"Active conversations: {store.list_conversations()}")

    for cid in store.list_conversations():
        conv = store.get_conversation(cid)
        print(f"\n--- {cid} ---")
        print(conv.get_context())

    store.delete_conversation("conv-1")
    print(f"\nAfter deleting conv-1: {store.list_conversations()}")
    print()


if __name__ == "__main__":
    demo_buffer_memory()
    demo_window_memory()
    demo_summary_memory()
    demo_token_limited_memory()
    demo_memory_store()
    print("Demo complete.")
