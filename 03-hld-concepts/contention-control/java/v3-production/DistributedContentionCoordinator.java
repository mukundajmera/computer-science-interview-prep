import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.Supplier;

/**
 * v3-production: contention execution with idempotency guard.
 */
public final class DistributedContentionCoordinator {
    public interface IdempotencyStore<T> {
        T get(String key);
        boolean putIfAbsent(String key, T value);
    }

    public static final class InMemoryIdempotencyStore<T> implements IdempotencyStore<T> {
        private final Map<String, T> cache = new ConcurrentHashMap<>();

        @Override
        public T get(String key) {
            return cache.get(key);
        }

        @Override
        public boolean putIfAbsent(String key, T value) {
            return cache.putIfAbsent(key, value) == null;
        }
    }

    public <T> T executeOnce(String idempotencyKey, Supplier<T> action, IdempotencyStore<T> store) {
        T existing = store.get(idempotencyKey);
        if (existing != null) {
            return existing;
        }
        T result = action.get();
        store.putIfAbsent(idempotencyKey, result);
        return store.get(idempotencyKey);
    }
}
