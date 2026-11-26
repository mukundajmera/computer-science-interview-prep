import java.util.concurrent.locks.ReentrantLock;

/**
 * A completed fixed update set sums exactly after quiescence; concurrent striped sum is labeled non-atomic and never used for strict quota decisions.
 * Overflow, negative-update policy, shard lifecycle and contention histories preserve the documented local—not network-distributed—counter contract.
 */
public class DistributedCounter {
    private final Counter counter;
    
    public DistributedCounter() {
        this(4);
    }
    
    public DistributedCounter(int numCells) {
        counter = new Counter(numCells);
    }
    
    public void increment() {
        counter.increment();
    }
    
    public void increment(long x) {
        counter.increment(x);
    }
    
    public long get() {
        return counter.get();
    }
}
