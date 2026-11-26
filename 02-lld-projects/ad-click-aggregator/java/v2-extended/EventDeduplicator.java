package v2_extended;
import java.util.BitSet;
import java.util.HashSet;
import java.util.Set;

public class EventDeduplicator {
    private final BitSet bitSet;
    private final int size;
    private final Set<String> exactStore;

    public EventDeduplicator(int size) {
        this.size = size;
        this.bitSet = new BitSet(size);
        this.exactStore = new HashSet<>();
    }

    public EventDeduplicator() {
        this(1000000);
    }

    private int hash(String eventId) {
        return (eventId.hashCode() & 0x7fffffff) % size;
    }

    public boolean isDuplicate(String eventId) {
        int idx = hash(eventId);
        if (bitSet.get(idx)) {
            if (exactStore.contains(eventId)) {
                return true;
            }
        }
        bitSet.set(idx);
        exactStore.add(eventId);
        return false;
    }
}
