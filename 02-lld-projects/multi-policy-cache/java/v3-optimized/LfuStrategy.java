package v3_optimized;
import java.util.Map;
import java.util.HashMap;

public class LfuStrategy<K, V> implements EvictionStrategy<K, V> {
    class FreqNode {
        int freq;
        FreqNode prev, next;
        CacheEntry<K, V> head, tail;

        public FreqNode(int freq) {
            this.freq = freq;
            head = new CacheEntry<>(null, null, -1);
            tail = new CacheEntry<>(null, null, -1);
            head.next = tail;
            tail.prev = head;
        }

        void addEntry(CacheEntry<K, V> entry) {
            entry.next = head.next;
            entry.prev = head;
            head.next.prev = entry;
            head.next = entry;
            entry.freqNode = this;
        }

        void removeEntry(CacheEntry<K, V> entry) {
            entry.prev.next = entry.next;
            entry.next.prev = entry.prev;
        }

        boolean isEmpty() {
            return head.next == tail;
        }
    }

    private final FreqNode freqHead, freqTail;
    private final Map<Integer, FreqNode> freqMap;

    public LfuStrategy() {
        freqHead = new FreqNode(0);
        freqTail = new FreqNode(Integer.MAX_VALUE);
        freqHead.next = freqTail;
        freqTail.prev = freqHead;
        freqMap = new HashMap<>();
    }

    private FreqNode addFreqNodeAfter(int freq, FreqNode prevNode) {
        FreqNode newNode = new FreqNode(freq);
        newNode.prev = prevNode;
        newNode.next = prevNode.next;
        prevNode.next.prev = newNode;
        prevNode.next = newNode;
        freqMap.put(freq, newNode);
        return newNode;
    }

    private void removeFreqNode(FreqNode node) {
        node.prev.next = node.next;
        node.next.prev = node.prev;
        freqMap.remove(node.freq);
    }

    @Override
    public void onAccess(CacheEntry<K, V> entry) {
        FreqNode currentFreqNode = (FreqNode) entry.freqNode;
        int nextFreq = currentFreqNode.freq + 1;
        
        currentFreqNode.removeEntry(entry);
        
        FreqNode nextFreqNode = currentFreqNode.next;
        if (nextFreqNode.freq != nextFreq) {
            nextFreqNode = addFreqNodeAfter(nextFreq, currentFreqNode);
        }
        nextFreqNode.addEntry(entry);
        entry.frequency = nextFreq;
        
        if (currentFreqNode.isEmpty() && currentFreqNode.freq != 0) {
            removeFreqNode(currentFreqNode);
        }
    }

    @Override
    public void onInsert(CacheEntry<K, V> entry) {
        if (entry.frequency <= 0) entry.frequency = 1;
        int freq = entry.frequency;
        
        FreqNode node = freqMap.get(freq);
        if (node == null) {
            FreqNode prevNode = freqHead;
            while (prevNode.next != freqTail && prevNode.next.freq < freq) {
                prevNode = prevNode.next;
            }
            node = addFreqNodeAfter(freq, prevNode);
        }
        node.addEntry(entry);
    }

    @Override
    public void onRemove(CacheEntry<K, V> entry) {
        FreqNode node = (FreqNode) entry.freqNode;
        if (node != null) {
            node.removeEntry(entry);
            if (node.isEmpty() && node.freq != 0) {
                removeFreqNode(node);
            }
        }
    }

    @Override
    public CacheEntry<K, V> evict() {
        FreqNode leastFreqNode = freqHead.next;
        if (leastFreqNode == freqTail) return null;
        
        CacheEntry<K, V> toEvict = leastFreqNode.tail.prev;
        leastFreqNode.removeEntry(toEvict);
        
        if (leastFreqNode.isEmpty()) {
            removeFreqNode(leastFreqNode);
        }
        return toEvict;
    }

    @Override
    public void clear() {
        freqHead.next = freqTail;
        freqTail.prev = freqHead;
        freqMap.clear();
    }
}
