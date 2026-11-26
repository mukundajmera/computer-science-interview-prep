import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.locks.ReentrantLock;

class Cell {
    volatile long value;
    final ReentrantLock lock = new ReentrantLock();
    Cell(long x) { value = x; }
}

public class Counter {
    transient volatile Cell[] cells;
    transient volatile long base;
    final ReentrantLock baseLock = new ReentrantLock();
    final ReentrantLock cellsBusy = new ReentrantLock();
    
    static final int NCPU = Runtime.getRuntime().availableProcessors();
    
    public void increment() {
        increment(1);
    }
    
    public void increment(long x) {
        Cell[] as; long b; Cell a; int n;
        if ((as = cells) != null || !casBase(x)) {
            boolean uncontended = true;
            long threadId = Thread.currentThread().getId();
            int probe = getProbe(threadId);
            
            if (as == null || (n = as.length) == 0 ||
                (a = as[(n - 1) & probe]) == null ||
                !(uncontended = casCell(a, x))) {
                longAccumulate(x, probe, uncontended);
            }
        }
    }
    
    private boolean casBase(long x) {
        if (baseLock.tryLock()) {
            try {
                base += x;
                return true;
            } finally {
                baseLock.unlock();
            }
        }
        return false;
    }
    
    private boolean casCell(Cell a, long x) {
        if (a.lock.tryLock()) {
            try {
                a.value += x;
                return true;
            } finally {
                a.lock.unlock();
            }
        }
        return false;
    }
    
    private int getProbe(long threadId) {
        int hash = (int)(threadId ^ (threadId >>> 32));
        hash ^= (hash << 13);
        hash ^= (hash >>> 17);
        hash ^= (hash << 5);
        return hash;
    }
    
    private void longAccumulate(long x, int probe, boolean wasUncontended) {
        int h = probe;
        if (h == 0) {
            h = (int)Thread.currentThread().getId();
            wasUncontended = true;
        }
        boolean collide = false;
        for (;;) {
            Cell[] as; Cell a; int n; long v;
            if ((as = cells) != null && (n = as.length) > 0) {
                if ((a = as[(n - 1) & h]) == null) {
                    if (!cellsBusy.isLocked()) {
                        Cell r = new Cell(x);
                        if (cellsBusy.tryLock()) {
                            boolean created = false;
                            try {
                                Cell[] rs; int m, j;
                                if ((rs = cells) != null && (m = rs.length) > 0 &&
                                    rs[j = (m - 1) & h] == null) {
                                    rs[j] = r;
                                    created = true;
                                }
                            } finally {
                                cellsBusy.unlock();
                            }
                            if (created) break;
                            continue;
                        }
                    }
                    collide = false;
                }
                else if (!wasUncontended) {
                    wasUncontended = true;
                }
                else if (casCell(a, x)) {
                    break;
                }
                else if (n >= Math.max(2, NCPU) || cells != as) {
                    collide = false;
                }
                else if (!collide) {
                    collide = true;
                }
                else if (!cellsBusy.isLocked() && cellsBusy.tryLock()) {
                    try {
                        if (cells == as) {
                            Cell[] rs = new Cell[n << 1];
                            for (int i = 0; i < n; ++i) rs[i] = as[i];
                            cells = rs;
                        }
                    } finally {
                        cellsBusy.unlock();
                    }
                    collide = false;
                    continue;
                }
                h ^= h << 13;
                h ^= h >>> 17;
                h ^= h << 5;
            }
            else if (!cellsBusy.isLocked() && cells == as && cellsBusy.tryLock()) {
                boolean init = false;
                try {
                    if (cells == as) {
                        Cell[] rs = new Cell[2];
                        rs[h & 1] = new Cell(x);
                        cells = rs;
                        init = true;
                    }
                } finally {
                    cellsBusy.unlock();
                }
                if (init) break;
            }
            else if (casBase(x)) {
                break;
            }
        }
    }
    
    public long get() {
        long sum = base;
        Cell[] as = cells;
        if (as != null) {
            for (int i = 0; i < as.length; ++i) {
                Cell a = as[i];
                if (a != null) {
                    a.lock.lock();
                    try {
                        sum += a.value;
                    } finally {
                        a.lock.unlock();
                    }
                }
            }
        }
        return sum;
    }
}
