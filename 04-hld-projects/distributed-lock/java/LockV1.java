public class LockV1 {
    private boolean locked = false;
    public synchronized boolean acquire() {
        if (!locked) {
            locked = true;
            return true;
        }
        return false;
    }
    public synchronized void release() {
        locked = false;
    }
    public static void main(String[] args) {
        LockV1 l = new LockV1();
        // Test 1
        assert l.acquire();
        // Test 2
        assert !l.acquire();
        // Test 3
        l.release();
        assert l.acquire();
        // Test 4
        l.release();
        assert l.acquire();
        // Test 5
        l.release();
        assert l.acquire();
        // Test 6
        l.release();
        assert l.acquire();
    }
}
