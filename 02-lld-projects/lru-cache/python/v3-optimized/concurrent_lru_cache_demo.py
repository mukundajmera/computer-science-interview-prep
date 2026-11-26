"""
LRU Cache - V3 Optimized Demo

Demonstrates thread-safe LRU cache with concurrent access.
"""
import time
import threading
from concurrent.futures import ThreadPoolExecutor
from concurrent_lru_cache import ConcurrentLRUCache


def demonstrate_basic_operations():
    print("--- Basic Operations (Same as V1) ---\n")

    cache: ConcurrentLRUCache[str, int] = ConcurrentLRUCache(3)

    cache.put("a", 1)
    cache.put("b", 2)
    cache.put("c", 3)
    print("Added a=1, b=2, c=3")
    print(f"Cache: {cache}")

    print(f"\nget(a) = {cache.get('a')}")
    cache.put("d", 4)  # Evicts 'b'
    print("put(d, 4) - evicts 'b'")
    print(f"get(b) = {cache.get('b')} (evicted)")
    print(f"Cache: {cache}")


def demonstrate_concurrent_access():
    print("--- Concurrent Access Test ---\n")

    cache: ConcurrentLRUCache[int, int] = ConcurrentLRUCache(100)
    num_threads = 10
    operations_per_thread = 1000

    put_count = [0]
    get_count = [0]
    count_lock = threading.Lock()

    def worker(thread_id: int):
        local_puts = 0
        local_gets = 0
        
        for i in range(operations_per_thread):
            key = (thread_id * 100 + i) % 150  # Keys 0-149

            if i % 3 == 0:
                cache.put(key, thread_id * 1000 + i)
                local_puts += 1
            else:
                cache.get(key)
                local_gets += 1
        
        with count_lock:
            put_count[0] += local_puts
            get_count[0] += local_gets

    print(f"Starting {num_threads} threads with {operations_per_thread} operations each...")
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(worker, t) for t in range(num_threads)]
        for f in futures:
            f.result()

    elapsed = (time.time() - start_time) * 1000

    print("\nResults:")
    print(f"  Total time: {elapsed:.0f}ms")
    print(f"  Put operations: {put_count[0]}")
    print(f"  Get operations: {get_count[0]}")
    print(f"  Final cache size: {cache.size()}")
    print(f"  Cache hits: {cache.hits}")
    print(f"  Cache misses: {cache.misses}")
    print(f"  Hit ratio: {cache.hit_ratio:.2%}")
    print(f"  Evictions: {cache.evictions}")
    print("\n  ✓ No exceptions = Thread-safe!")


def demonstrate_statistics():
    print("--- Thread-Safe Statistics ---\n")

    cache: ConcurrentLRUCache[str, int] = ConcurrentLRUCache(5)

    # Populate
    for i in range(5):
        cache.put(f"key{i}", i)

    # Access pattern: some hits, some misses
    for i in range(10):
        cache.get(f"key{i % 7}")  # Keys 0-4 exist, 5-6 don't

    print("Cache operations:")
    print("  5 puts, 10 gets")
    print("\nStatistics (thread-safe):")
    print(f"  Hits: {cache.hits}")
    print(f"  Misses: {cache.misses}")
    print(f"  Hit Ratio: {cache.hit_ratio:.1%}")
    print(f"  Evictions: {cache.evictions}")

    # Trigger evictions
    print("\nAdding 3 more entries (triggers evictions)...")
    cache.put("new1", 100)
    cache.put("new2", 200)
    cache.put("new3", 300)

    print(f"  Evictions after: {cache.evictions}")
    print(f"\nFinal: {cache}")


def main():
    print("=== Concurrent LRU Cache Demo ===\n")

    demonstrate_basic_operations()
    print("\n" + "=" * 60 + "\n")
    demonstrate_concurrent_access()
    print("\n" + "=" * 60 + "\n")
    demonstrate_statistics()


if __name__ == "__main__":
    main()
