/**
 * A completed fixed update set sums exactly after quiescence; concurrent striped sum is labeled non-atomic and never used for strict quota decisions.
 * Overflow, negative-update policy, shard lifecycle and contention histories preserve the documented local—not network-distributed—counter contract.
 */
public class Counter {
    private long value = 0;
    
    public synchronized void increment() {
        this.value++;
    }
    
    public synchronized void increment(long x) {
        this.value += x;
    }
    
    public synchronized long get() {
        return this.value;
    }
}
