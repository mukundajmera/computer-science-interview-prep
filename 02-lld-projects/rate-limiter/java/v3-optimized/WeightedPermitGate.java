import java.util.concurrent.TimeUnit;
import java.util.concurrent.locks.Condition;
import java.util.concurrent.locks.ReentrantLock;

/**
 * Weighted permit gate for bounded scarcity handling.
 */
public class WeightedPermitGate {
    private final int maxPermits;
    private final ReentrantLock lock;
    private final Condition permitsAvailable;
    private int usedPermits;

    public WeightedPermitGate(int maxPermits) {
        if (maxPermits <= 0) {
            throw new IllegalArgumentException("maxPermits must be > 0");
        }
        this.maxPermits = maxPermits;
        this.lock = new ReentrantLock();
        this.permitsAvailable = lock.newCondition();
        this.usedPermits = 0;
    }

    public boolean tryAcquire(int permits, long timeoutMs) throws InterruptedException {
        validateWeight(permits);

        long nanos = TimeUnit.MILLISECONDS.toNanos(Math.max(0L, timeoutMs));
        lock.lockInterruptibly();
        try {
            while (!canAcquire(permits)) {
                if (nanos <= 0L) {
                    return false;
                }
                nanos = permitsAvailable.awaitNanos(nanos);
            }
            usedPermits += permits;
            return true;
        } finally {
            lock.unlock();
        }
    }

    public void release(int permits) {
        validateWeight(permits);

        lock.lock();
        try {
            usedPermits = Math.max(0, usedPermits - permits);
            permitsAvailable.signalAll();
        } finally {
            lock.unlock();
        }
    }

    public int availablePermits() {
        lock.lock();
        try {
            return maxPermits - usedPermits;
        } finally {
            lock.unlock();
        }
    }

    public int maxPermits() {
        return maxPermits;
    }

    private boolean canAcquire(int permits) {
        return usedPermits + permits <= maxPermits;
    }

    private void validateWeight(int permits) {
        if (permits <= 0 || permits > maxPermits) {
            throw new IllegalArgumentException("permits must be in range [1, maxPermits]");
        }
    }
}
