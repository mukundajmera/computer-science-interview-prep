public class LockV3 {
    private int token = 0;
    private boolean locked = false;
    public synchronized int acquire() {
        if (!locked) {
            locked = true;
            return ++token;
        }
        return 0;
    }
    public synchronized void release() {
        locked = false;
    }

    static class Resource {
        int lastToken = 0;
        public boolean write(int t, String val) {
            if (t < lastToken) return false;
            lastToken = t;
            return true;
        }
    }

    public static void main(String[] args) {
        LockV3 l = new LockV3();
        Resource r = new Resource();
        
        // Test 1
        int t1 = l.acquire();
        assert t1 > 0;
        
        // Test 2
        l.release();
        int t2 = l.acquire();
        assert t2 > t1;
        
        // Test 3 (stale holder)
        assert r.write(t2, "val2");
        assert !r.write(t1, "val1"); // stale holder rejected
        
        // Test 4
        l.release();
        assert l.acquire() > 0;
        // Test 5
        l.release();
        assert l.acquire() > 0;
        // Test 6
        l.release();
        assert l.acquire() > 0;
    }
}
