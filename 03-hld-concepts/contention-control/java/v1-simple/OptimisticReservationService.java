import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * v1-simple: optimistic reservation with version check.
 */
public final class OptimisticReservationService {
    public static final class Resource {
        public int available;
        public int version;

        public Resource(int available, int version) {
            this.available = available;
            this.version = version;
        }
    }

    private final Map<String, Resource> resources = new ConcurrentHashMap<>();

    public void upsert(String resourceKey, int available) {
        resources.put(resourceKey, new Resource(available, 0));
    }

    public boolean reserve(String resourceKey, int quantity, int expectedVersion) {
        Resource current = resources.get(resourceKey);
        if (current == null || current.available < quantity || current.version != expectedVersion) {
            return false;
        }
        current.available -= quantity;
        current.version += 1;
        return true;
    }
}
