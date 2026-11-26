public class LockV2 {
    private boolean locked = false;
    private long expires = 0;
    public synchronized boolean acquire() {
        long now = System.currentTimeMillis();
        if (!locked || now > expires) {
            locked = true;
            expires = now + 1000;
            return true;
        }
        return false;
    }
    public synchronized void release() {
        locked = false;
    }
    public static void main(String[] args) {
        LockV2 l = new LockV2();
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
