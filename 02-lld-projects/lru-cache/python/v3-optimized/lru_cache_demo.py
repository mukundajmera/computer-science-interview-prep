"""
LRU Cache - V1 Basic Demo

Demonstrates the LRU cache in action.
"""
from lru_cache import LRUCache


def main():
    print("=== LRU Cache Demo ===\n")

    # Create cache with capacity 3
    cache: LRUCache[str, int] = LRUCache(3)
    print("Created cache with capacity 3\n")

    # Test 1: Basic operations
    print("Test 1: Basic put and get operations")
    cache.put("a", 1)
    print(f"put(a, 1): {cache}")

    cache.put("b", 2)
    print(f"put(b, 2): {cache}")

    cache.put("c", 3)
    print(f"put(c, 3): {cache}")

    print(f"get(a) = {cache.get('a')}")
    print(f"After get(a): {cache}")

    # Test 2: Eviction
    print("\nTest 2: Eviction on capacity overflow")
    cache.put("d", 4)
    print(f"put(d, 4): {cache}")
    print(f"get(b) = {cache.get('b')} (should be None - evicted)")

    # Test 3: Update existing key
    print("\nTest 3: Update existing key")
    cache.put("a", 100)
    print(f"put(a, 100): {cache}")
    print(f"get(a) = {cache.get('a')} (should be 100)")

    # Test 4: Remove
    print("\nTest 4: Remove operation")
    removed = cache.remove("c")
    print(f"remove(c) = {removed}")
    print(f"After remove: {cache}")

    # Test 5: Size and capacity
    print("\nTest 5: Size and capacity")
    print(f"size() = {cache.size()}")
    print(f"capacity = {cache.capacity}")
    print(f"contains_key(a) = {cache.contains_key('a')}")
    print(f"contains_key(c) = {cache.contains_key('c')}")

    # Test 6: Clear
    print("\nTest 6: Clear cache")
    cache.clear()
    print(f"After clear(): {cache}")

    # Test 7: Edge case - single capacity
    print("\nTest 7: Single capacity cache")
    single_cache: LRUCache[str, str] = LRUCache(1)
    single_cache.put("only", "one")
    print(f"After put(only, one): {single_cache}")
    single_cache.put("new", "entry")
    print(f"After put(new, entry): {single_cache}")
    print(f"get(only) = {single_cache.get('only')} (evicted)")
    print(f"get(new) = {single_cache.get('new')}")

    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    main()
