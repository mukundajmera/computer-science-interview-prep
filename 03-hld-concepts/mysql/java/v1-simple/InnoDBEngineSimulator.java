import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.ReentrantLock;
import java.time.Instant;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

public class InnoDBEngineSimulator {

    public static class Row {
        int primaryKey;
        Map<String, Object> data;
        int transactionId;
        boolean deleted;

        public Row(int primaryKey, Map<String, Object> data) {
            this.primaryKey = primaryKey;
            this.data = new HashMap<>(data);
            this.transactionId = 0;
            this.deleted = false;
        }

        public Row(Row other) {
            this.primaryKey = other.primaryKey;
            this.data = new HashMap<>(other.data);
            this.transactionId = other.transactionId;
            this.deleted = other.deleted;
        }
    }

    public static class BufferPool {
        int capacity;
        // Using LinkedHashMap for LRU cache
        LinkedHashMap<Integer, Row> pages;
        Set<Integer> dirtyPages;
        ReentrantLock lock;

        public BufferPool(int capacity) {
            this.capacity = capacity;
            this.pages = new LinkedHashMap<>(capacity, 0.75f, true) {
                @Override
                protected boolean removeEldestEntry(Map.Entry<Integer, Row> eldest) {
                    if (size() > BufferPool.this.capacity) {
                        dirtyPages.remove(eldest.getKey());
                        return true;
                    }
                    return false;
                }
            };
            this.dirtyPages = new HashSet<>();
            this.lock = new ReentrantLock();
        }

        public Row get(int primaryKey) {
            lock.lock();
            try {
                return pages.get(primaryKey);
            } finally {
                lock.unlock();
            }
        }

        public void put(int primaryKey, Row row, boolean isDirty) {
            lock.lock();
            try {
                pages.put(primaryKey, row);
                if (isDirty) {
                    dirtyPages.add(primaryKey);
                }
            } finally {
                lock.unlock();
            }
        }
    }

    public static class RedoLog {
        List<Map<String, Object>> logEntries;
        ReentrantLock lock;

        public RedoLog() {
            this.logEntries = new ArrayList<>();
            this.lock = new ReentrantLock();
        }

        public void append(int txId, String operation, int primaryKey, Map<String, Object> data) {
            lock.lock();
            try {
                Map<String, Object> entry = new HashMap<>();
                entry.put("tx_id", txId);
                entry.put("operation", operation);
                entry.put("primary_key", primaryKey);
                entry.put("data", new HashMap<>(data));
                entry.put("timestamp", Instant.now().toEpochMilli());
                logEntries.add(entry);
            } finally {
                lock.unlock();
            }
        }
    }

    public static class UndoLog {
        Map<Integer, List<Row>> logs;
        ReentrantLock lock;

        public UndoLog() {
            this.logs = new HashMap<>();
            this.lock = new ReentrantLock();
        }

        public void add(int txId, Row previousRow) {
            lock.lock();
            try {
                logs.putIfAbsent(txId, new ArrayList<>());
                if (previousRow != null) {
                    logs.get(txId).add(new Row(previousRow));
                }
            } finally {
                lock.unlock();
            }
        }

        public List<Row> getOldVersions(int txId) {
            lock.lock();
            try {
                return logs.getOrDefault(txId, new ArrayList<>());
            } finally {
                lock.unlock();
            }
        }
    }

    BufferPool bufferPool;
    RedoLog redoLog;
    UndoLog undoLog;

    Map<Integer, Row> diskStorage;

    AtomicInteger nextTxId;
    Set<Integer> activeTransactions;

    Map<Integer, Integer> locks;
    ReentrantLock lockMutex;

    public InnoDBEngineSimulator() {
        this.bufferPool = new BufferPool(100);
        this.redoLog = new RedoLog();
        this.undoLog = new UndoLog();

        this.diskStorage = new ConcurrentHashMap<>();

        this.nextTxId = new AtomicInteger(1);
        this.activeTransactions = ConcurrentHashMap.newKeySet();

        this.locks = new HashMap<>();
        this.lockMutex = new ReentrantLock();
    }

    public int startTransaction() {
        lockMutex.lock();
        try {
            int txId = nextTxId.getAndIncrement();
            activeTransactions.add(txId);
            return txId;
        } finally {
            lockMutex.unlock();
        }
    }

    private boolean acquireLock(int txId, int primaryKey, long timeoutMillis) {
        long startTime = System.currentTimeMillis();
        while (true) {
            lockMutex.lock();
            try {
                Integer owner = locks.get(primaryKey);
                if (owner == null || owner == txId) {
                    locks.put(primaryKey, txId);
                    return true;
                }
            } finally {
                lockMutex.unlock();
            }

            if (System.currentTimeMillis() - startTime > timeoutMillis) {
                return false;
            }
            try {
                Thread.sleep(10);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return false;
            }
        }
    }

    private void releaseLocks(int txId) {
        lockMutex.lock();
        try {
            locks.entrySet().removeIf(entry -> entry.getValue() == txId);
        } finally {
            lockMutex.unlock();
        }
    }

    public Map<String, Object> read(int txId, int primaryKey) {
        Row row = bufferPool.get(primaryKey);
        if (row == null) {
            row = diskStorage.get(primaryKey);
            if (row != null) {
                bufferPool.put(primaryKey, row, false);
            } else {
                return null;
            }
        }

        if (row.deleted) {
            return null;
        }

        if (row.transactionId > txId || (activeTransactions.contains(row.transactionId) && row.transactionId != txId)) {
            List<Row> oldVersions = undoLog.getOldVersions(row.transactionId);
            for (int i = oldVersions.size() - 1; i >= 0; i--) {
                Row oldRow = oldVersions.get(i);
                if (oldRow.primaryKey == primaryKey) {
                    if (oldRow.transactionId <= txId && !activeTransactions.contains(oldRow.transactionId)) {
                        if (oldRow.deleted) {
                            return null;
                        }
                        return new HashMap<>(oldRow.data);
                    }
                }
            }
            return null;
        }

        return new HashMap<>(row.data);
    }

    public boolean write(int txId, int primaryKey, Map<String, Object> data) {
        if (!acquireLock(txId, primaryKey, 1000)) {
            throw new RuntimeException("Deadlock detected or lock timeout");
        }

        Row oldRow = bufferPool.get(primaryKey);
        if (oldRow == null && diskStorage.containsKey(primaryKey)) {
            oldRow = diskStorage.get(primaryKey);
        }

        if (oldRow != null) {
            undoLog.add(txId, oldRow);
        }

        Row newRow = new Row(primaryKey, data);
        newRow.transactionId = txId;

        redoLog.append(txId, "WRITE", primaryKey, data);
        bufferPool.put(primaryKey, newRow, true);
        return true;
    }

    public void commit(int txId) {
        lockMutex.lock();
        try {
            activeTransactions.remove(txId);
        } finally {
            lockMutex.unlock();
        }
        releaseLocks(txId);
    }

    public void rollback(int txId) {
        List<Row> oldVersions = undoLog.getOldVersions(txId);
        for (Row oldRow : oldVersions) {
            bufferPool.put(oldRow.primaryKey, oldRow, true);
            redoLog.append(txId, "ROLLBACK_RESTORE", oldRow.primaryKey, oldRow.data);
        }

        lockMutex.lock();
        try {
            activeTransactions.remove(txId);
        } finally {
            lockMutex.unlock();
        }
        releaseLocks(txId);
    }

    public void flushDirtyPages() {
        bufferPool.lock.lock();
        try {
            for (Integer key : new ArrayList<>(bufferPool.dirtyPages)) {
                if (bufferPool.pages.containsKey(key)) {
                    diskStorage.put(key, bufferPool.pages.get(key));
                }
            }
            bufferPool.dirtyPages.clear();
        } finally {
            bufferPool.lock.unlock();
        }
    }
}
