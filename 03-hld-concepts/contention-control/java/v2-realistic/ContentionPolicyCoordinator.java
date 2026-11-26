import java.util.ArrayDeque;
import java.util.Deque;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.Supplier;

/**
 * v2-realistic: switch policy per resource key.
 */
public final class ContentionPolicyCoordinator {
    public enum ContentionPolicy {
        OPTIMISTIC,
        PESSIMISTIC,
        SERIAL_QUEUE,
        DISTRIBUTED_LOCK
    }

    private final Map<String, ContentionPolicy> policyByResource = new ConcurrentHashMap<>();
    private final Map<String, Deque<Runnable>> queueByResource = new ConcurrentHashMap<>();

    public void setPolicy(String resourceKey, ContentionPolicy policy) {
        policyByResource.put(resourceKey, policy);
    }

    public <T> T execute(String resourceKey, Supplier<T> action) {
        ContentionPolicy policy = policyByResource.getOrDefault(resourceKey, ContentionPolicy.OPTIMISTIC);
        if (policy == ContentionPolicy.SERIAL_QUEUE) {
            Deque<Runnable> queue = queueByResource.computeIfAbsent(resourceKey, k -> new ArrayDeque<>());
            final Holder<T> holder = new Holder<>();
            synchronized (queue) {
                queue.addLast(() -> holder.value = action.get());
                Runnable next = queue.removeFirst();
                next.run();
            }
            return holder.value;
        }
        return action.get();
    }

    private static final class Holder<T> {
        private T value;
    }
}
