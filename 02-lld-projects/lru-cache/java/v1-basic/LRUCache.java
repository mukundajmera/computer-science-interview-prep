package v1_basic;

import java.util.HashMap;
import java.util.Map;

/**
 * LRU Cache - V1 Basic
 * 
 * Least Recently Used (LRU) cache implementation.
 * Uses HashMap for O(1) lookup and Doubly Linked List for O(1) order maintenance.
 * 
 * @param <K> Key type
 * @param <V> Value type
 */
public class LRUCache<K, V> {
    private final int capacity;
    private final Map<K, CacheNode<K, V>> cache;
    private final DoublyLinkedList<K, V> list;

    /**
     * Create an LRU cache with specified capacity.
     * 
     * @param capacity Maximum number of entries (must be >= 1)
     */
    public LRUCache(int capacity) {
        if (capacity < 1) {
            throw new IllegalArgumentException("Capacity must be at least 1");
        }
        this.capacity = capacity;
        this.cache = new HashMap<>();
        this.list = new DoublyLinkedList<>();
    }

    /**
     * Get value by key. Returns null if key doesn't exist.
     * Marks the entry as recently used.
     * 
     * Time: O(1)
     */
    public V get(K key) {
        CacheNode<K, V> node = cache.get(key);
        if (node == null) {
            return null;
        }
        // Move to front (most recently used)
        list.moveToFront(node);
        return node.getValue();
    }

    /**
     * Insert or update a key-value pair.
     * If cache is full and inserting new key, evicts least recently used entry.
     * 
     * Time: O(1)
     */
    public void put(K key, V value) {
        if (key == null) {
            throw new IllegalArgumentException("Key cannot be null");
        }

        CacheNode<K, V> existingNode = cache.get(key);

        if (existingNode != null) {
            // Update existing entry
            existingNode.setValue(value);
            list.moveToFront(existingNode);
        } else {
            // Insert new entry
            if (cache.size() >= capacity) {
                evict();
            }

            CacheNode<K, V> newNode = new CacheNode<>(key, value);
            cache.put(key, newNode);
            list.addToFront(newNode);
        }
    }

    /**
     * Remove an entry by key.
     * 
     * @return The removed value, or null if key didn't exist
     */
    public V remove(K key) {
        CacheNode<K, V> node = cache.remove(key);
        if (node == null) {
            return null;
        }
        list.remove(node);
        return node.getValue();
    }

    /**
     * Check if key exists in cache.
     * Does NOT update access order.
     */
    public boolean containsKey(K key) {
        return cache.containsKey(key);
    }

    /**
     * Get current number of entries.
     */
    public int size() {
        return cache.size();
    }

    /**
     * Get maximum capacity.
     */
    public int getCapacity() {
        return capacity;
    }

    /**
     * Remove all entries.
     */
    public void clear() {
        cache.clear();
        while (!list.isEmpty()) {
            list.removeLast();
        }
    }

    /**
     * Evict the least recently used entry.
     */
    private void evict() {
        CacheNode<K, V> lru = list.removeLast();
        if (lru != null) {
            cache.remove(lru.getKey());
        }
    }

    @Override
    public String toString() {
        return String.format("LRUCache{capacity=%d, size=%d, order=%s}",
                capacity, size(), list);
    }
}
