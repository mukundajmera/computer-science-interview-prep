package v1_basic;

/**
 * LRU Cache - V1 Basic
 * 
 * Cache node for doubly linked list.
 */
public class CacheNode<K, V> {
    private K key;
    private V value;
    CacheNode<K, V> prev;
    CacheNode<K, V> next;

    public CacheNode(K key, V value) {
        this.key = key;
        this.value = value;
    }

    public K getKey() {
        return key;
    }

    public V getValue() {
        return value;
    }

    public void setValue(V value) {
        this.value = value;
    }

    @Override
    public String toString() {
        return String.format("(%s=%s)", key, value);
    }
}

/**
 * Doubly linked list for maintaining access order.
 * Uses sentinel nodes (dummy head and tail) to simplify operations.
 */
class DoublyLinkedList<K, V> {
    private final CacheNode<K, V> head;  // Dummy head
    private final CacheNode<K, V> tail;  // Dummy tail
    private int size;

    public DoublyLinkedList() {
        head = new CacheNode<>(null, null);
        tail = new CacheNode<>(null, null);
        head.next = tail;
        tail.prev = head;
        size = 0;
    }

    /**
     * Add node right after head (most recently used position).
     */
    public void addToFront(CacheNode<K, V> node) {
        node.prev = head;
        node.next = head.next;
        head.next.prev = node;
        head.next = node;
        size++;
    }

    /**
     * Remove a node from its current position.
     */
    public void remove(CacheNode<K, V> node) {
        node.prev.next = node.next;
        node.next.prev = node.prev;
        size--;
    }

    /**
     * Move an existing node to the front.
     */
    public void moveToFront(CacheNode<K, V> node) {
        remove(node);
        addToFront(node);
    }

    /**
     * Remove and return the last node (least recently used).
     */
    public CacheNode<K, V> removeLast() {
        if (isEmpty()) {
            return null;
        }
        CacheNode<K, V> last = tail.prev;
        remove(last);
        return last;
    }

    public boolean isEmpty() {
        return size == 0;
    }

    public int size() {
        return size;
    }

    /**
     * Get string representation showing order from MRU to LRU.
     */
    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder("[");
        CacheNode<K, V> current = head.next;
        while (current != tail) {
            sb.append(current);
            if (current.next != tail) {
                sb.append(" -> ");
            }
            current = current.next;
        }
        sb.append("]");
        return sb.toString();
    }
}
