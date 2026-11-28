import threading
import time
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'v2-extended')))

from base62_v2 import encode, decode
from pastebin_service_v2 import PastebinService, PasteMetadata, TokenBucket, KeyBlockAllocator

# ---------------------------------------------------------------------------
# v1 parity tests: same scenarios as tests/test_pastebin_service.py, run
# against v2.
# ---------------------------------------------------------------------------

def test_base62_encoding_integrity():
    assert encode(0) == '0'
    assert encode(1) == '1'
    assert encode(10) == 'a'
    assert encode(36) == 'A'
    assert encode(61) == 'Z'
    assert encode(62) == '10'

    # Bijective check
    test_nums = [0, 1, 62, 1000, 1000000000]
    for num in test_nums:
        assert decode(encode(num)) == num

def test_create_and_get_paste():
    service = PastebinService()
    content = "Hello, Pastebin!"
    ip = "127.0.0.1"

    short_link = service.create_paste(content, ip)
    assert short_link is not None
    assert len(short_link) >= 7

    retrieved = service.get_paste(short_link)
    assert retrieved == content

def test_expiration_ttl_handling():
    service = PastebinService()
    content = "Ephemeral content"
    ip = "127.0.0.2"

    short_link = service.create_paste(content, ip, ttl_seconds=1)
    assert short_link is not None

    # Immediately accessible
    assert service.get_paste(short_link) == content

    # Wait for expiration
    time.sleep(1.1)

    # Passive expiration on read
    assert service.get_paste(short_link) is None

def test_rate_limiter_exceeded():
    # Capacity 2, fill rate 0.5/sec
    service = PastebinService(capacity=2, fill_rate=0.5)
    ip = "127.0.0.3"

    link1 = service.create_paste("1", ip)
    link2 = service.create_paste("2", ip)
    link3 = service.create_paste("3", ip)

    assert link1 is not None
    assert link2 is not None
    assert link3 is None  # Should be rate limited

def test_batch_ttl_cleanup_sweep():
    service = PastebinService()
    ip = "127.0.0.4"

    link1 = service.create_paste("Persist", ip)
    link2 = service.create_paste("Die1", ip, ttl_seconds=1)
    link3 = service.create_paste("Die2", ip, ttl_seconds=1)

    assert link1 is not None
    assert link2 is not None
    assert link3 is not None

    # Before expiration
    assert service.sweep_expired_pastes() == 0

    time.sleep(1.1)

    # Sweeper should clean up expired pastes
    assert service.sweep_expired_pastes() == 2

    # Links should be gone
    assert service.get_paste(link2) is None
    assert service.get_paste(link3) is None
    # Persistent link remains
    assert service.get_paste(link1) == "Persist"

# ---------------------------------------------------------------------------
# v2-only tests: one or more per improvement.
# ---------------------------------------------------------------------------

# Improvement #1: burn-after-reading (FOLLOW-UPS.md #2).

def test_burn_after_reading_single_read():
    service = PastebinService()
    link = service.create_paste("secret", "127.0.0.10", burn_after_reading=True)
    assert link is not None

    assert service.get_paste(link) == "secret", "first reader receives the content"
    assert service.get_paste(link) is None, "paste is gone after one read"

def test_burn_after_reading_concurrent_single_winner():
    service = PastebinService()
    link = service.create_paste("one-time", "127.0.0.11", burn_after_reading=True)

    barrier = threading.Barrier(8)
    results = []

    def reader():
        barrier.wait()
        results.append(service.get_paste(link))

    threads = [threading.Thread(target=reader) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert results.count("one-time") == 1, "exactly one concurrent reader wins"
    assert results.count(None) == 7

def test_burn_after_reading_never_cached():
    service = PastebinService()
    link = service.create_paste("no-cache", "127.0.0.12", burn_after_reading=True)
    service.get_paste(link)

    assert link not in service.read_cache, "burned pastes must not linger in the cache"

# Improvement #2: hot-key read cache with metrics (FOLLOW-UPS.md #1).

def test_read_cache_absorbs_repeat_reads():
    service = PastebinService()
    link = service.create_paste("viral", "127.0.0.13")

    assert service.get_paste(link) == "viral"   # miss, fills cache
    assert service.get_paste(link) == "viral"   # hit
    assert service.get_paste(link) == "viral"   # hit

    assert service.read_cache_misses == 1
    assert service.read_cache_hits == 2

def test_read_cache_entries_expire():
    service = PastebinService(read_cache_ttl_seconds=0.1)
    link = service.create_paste("brief", "127.0.0.14")

    service.get_paste(link)  # miss
    time.sleep(0.15)
    service.get_paste(link)  # stale cache entry -> miss again

    assert service.read_cache_misses == 2
    assert service.read_cache_hits == 0

def test_sweep_purges_read_cache():
    service = PastebinService()
    link = service.create_paste("cached-die", "127.0.0.15", ttl_seconds=1)
    service.get_paste(link)  # fills cache
    assert link in service.read_cache

    time.sleep(1.1)
    assert service.sweep_expired_pastes() == 1
    assert link not in service.read_cache, "swept pastes leave no cache residue"

# Improvement #3: KGS-style key block allocation (FOLLOW-UPS.md #3).

def test_key_block_allocator_hands_out_unique_ids():
    allocator = KeyBlockAllocator(start_id=1000, block_size=4)
    ids = [allocator.next_id() for _ in range(9)]

    assert len(set(ids)) == 9, "every id is unique across blocks"
    assert allocator.blocks_allocated == 3, "4+4+1 ids span three blocks"
    assert min(ids) >= 1000

def test_key_block_allocator_exhaustion_is_loud():
    allocator = KeyBlockAllocator(start_id=5000, block_size=2, max_blocks=1)
    service = PastebinService(key_allocator=allocator)

    link1 = service.create_paste("a", "127.0.0.16")
    link2 = service.create_paste("b", "127.0.0.16")
    assert link1 is not None and link2 is not None
    assert link1 != link2

    try:
        service.create_paste("c", "127.0.0.16")
        raised = False
    except RuntimeError as e:
        raised = "KeyPoolExhausted" in str(e)
    assert raised, "exhausted key pool must raise, never silently collide"
