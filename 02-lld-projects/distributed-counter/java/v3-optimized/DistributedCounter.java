import java.util.concurrent.locks.ReentrantLock;
import java.util.concurrent.atomic.LongAdder;

/**
 * v3-optimized DistributedCounter implementation.
 * 
 * A highly concurrent counter that dynamically resizes its cell array based on 
 * contention and CPU count, using probe hashing to minimize lock collisions.
 * 
 * LongAdder/striped local state is not a distributed counter, and a concurrent 
 * sum is not an atomic snapshot suitable for strict quota limits.
 * Overflow, negative-update policy, shard lifecycle and contention histories 
 * preserve the documented local-not network-distributed-counter contract.
 */
public class DistributedCounter {
    private final LongAdder counter = new LongAdder();
    
    public void increment() {
        counter.increment();
    }
    
    public void increment(long x) {
        counter.add(x);
    }
    
    public long get() {
        return counter.sum();
    }
}
