package v3_optimized;

public class BackpressureController {
    private final int maxConcurrent;
    private int current = 0;

    public BackpressureController(int maxConcurrent) {
        this.maxConcurrent = maxConcurrent;
    }

    public synchronized boolean acquire() {
        if (current < maxConcurrent) {
            current++;
            return true;
        }
        return false;
    }

    public synchronized void release() {
        if (current > 0) {
            current--;
        }
    }
}
