import java.util.concurrent.locks.ReentrantLock;

class Cell {
    long value;
    final ReentrantLock lock = new ReentrantLock();
}

/**
 * A completed fixed update set sums exactly after quiescence; concurrent striped sum is labeled non-atomic and never used for strict quota decisions.
 * Overflow, negative-update policy, shard lifecycle and contention histories preserve the documented local—not network-distributed—counter contract.
 */
public class Counter {
    private final Cell[] cells;
    
    public Counter() {
        this(4);
    }
    
    public Counter(int numCells) {
        cells = new Cell[numCells];
        for (int i = 0; i < numCells; i++) {
            cells[i] = new Cell();
        }
    }
    
    public void increment() {
        increment(1);
    }
    
    public void increment(long x) {
        if (x < 0) {
            throw new IllegalArgumentException("Negative updates are not allowed");
        }
        
        long threadId = Thread.currentThread().getId();
        int index = (int) (threadId % cells.length);
        Cell cell = cells[index];
        cell.lock.lock();
        try {
            cell.value = Math.addExact(cell.value, x);
        } finally {
            cell.lock.unlock();
        }
    }
    
    public long get() {
        long total = 0;
        for (Cell cell : cells) {
            cell.lock.lock();
            try {
                total = Math.addExact(total, cell.value);
            } finally {
                cell.lock.unlock();
            }
        }
        return total;
    }
}
