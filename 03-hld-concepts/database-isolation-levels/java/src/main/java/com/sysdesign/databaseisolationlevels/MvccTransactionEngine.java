package com.sysdesign.databaseisolationlevels;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.locks.ReentrantReadWriteLock;
import java.util.stream.Collectors;

public class MvccTransactionEngine {
    
    public enum IsolationLevel {
        READ_COMMITTED,
        SNAPSHOT_ISOLATION
    }

    private static class RecordVersion {
        final int txId;
        final String value;
        final boolean isDeleted;

        RecordVersion(int txId, String value, boolean isDeleted) {
            this.txId = txId;
            this.value = value;
            this.isDeleted = isDeleted;
        }
    }

    private static class ReadView {
        final int minTrxId;
        final int maxTrxId;
        final Set<Integer> activeTrxIds;

        ReadView(int minTrxId, int maxTrxId, Set<Integer> activeTrxIds) {
            this.minTrxId = minTrxId;
            this.maxTrxId = maxTrxId;
            this.activeTrxIds = activeTrxIds;
        }

        boolean isVisible(int txId) {
            if (txId < minTrxId) return true;
            if (txId >= maxTrxId) return false;
            return !activeTrxIds.contains(txId);
        }
    }

    private static class Transaction {
        final int txId;
        final IsolationLevel isolationLevel;
        ReadView readView;
        final Map<String, RecordVersion> writes = new HashMap<>();

        Transaction(int txId, IsolationLevel isolationLevel, ReadView readView) {
            this.txId = txId;
            this.isolationLevel = isolationLevel;
            this.readView = readView;
        }
    }

    private final Map<String, List<RecordVersion>> store = new ConcurrentHashMap<>();
    private final Map<Integer, Transaction> activeTransactions = new ConcurrentHashMap<>();
    private final AtomicInteger nextTxId = new AtomicInteger(1);
    private final ReentrantReadWriteLock lock = new ReentrantReadWriteLock();

    private ReadView createReadView() {
        Set<Integer> activeIds = activeTransactions.keySet().stream().collect(Collectors.toSet());
        int minTrx = activeIds.isEmpty() ? nextTxId.get() : Collections.min(activeIds);
        return new ReadView(minTrx, nextTxId.get(), activeIds);
    }

    public int begin() {
        return begin(IsolationLevel.SNAPSHOT_ISOLATION);
    }

    public int begin(IsolationLevel isolationLevel) {
        lock.writeLock().lock();
        try {
            int txId = nextTxId.getAndIncrement();
            ReadView readView = createReadView();
            Transaction tx = new Transaction(txId, isolationLevel, readView);
            activeTransactions.put(txId, tx);
            return txId;
        } finally {
            lock.writeLock().unlock();
        }
    }

    public String read(int txId, String key) {
        lock.writeLock().lock();
        try {
            Transaction tx = activeTransactions.get(txId);
            if (tx == null) {
                throw new IllegalArgumentException("Transaction " + txId + " is not active");
            }

            if (tx.writes.containsKey(key)) {
                RecordVersion version = tx.writes.get(key);
                return version.isDeleted ? null : version.value;
            }

            if (tx.isolationLevel == IsolationLevel.READ_COMMITTED) {
                tx.readView = createReadView();
            }

            List<RecordVersion> versions = store.get(key);
            if (versions == null || versions.isEmpty()) {
                return null;
            }

            for (int i = versions.size() - 1; i >= 0; i--) {
                RecordVersion version = versions.get(i);
                if (tx.readView.isVisible(version.txId)) {
                    return version.isDeleted ? null : version.value;
                }
            }

            return null;
        } finally {
            lock.writeLock().unlock();
        }
    }

    public void write(int txId, String key, String value) {
        lock.writeLock().lock();
        try {
            Transaction tx = activeTransactions.get(txId);
            if (tx == null) {
                throw new IllegalArgumentException("Transaction " + txId + " is not active");
            }
            tx.writes.put(key, new RecordVersion(txId, value, false));
        } finally {
            lock.writeLock().unlock();
        }
    }

    public void delete(int txId, String key) {
        lock.writeLock().lock();
        try {
            Transaction tx = activeTransactions.get(txId);
            if (tx == null) {
                throw new IllegalArgumentException("Transaction " + txId + " is not active");
            }
            tx.writes.put(key, new RecordVersion(txId, null, true));
        } finally {
            lock.writeLock().unlock();
        }
    }

    public boolean commit(int txId) {
        lock.writeLock().lock();
        try {
            Transaction tx = activeTransactions.get(txId);
            if (tx == null) {
                return false;
            }

            for (String key : tx.writes.keySet()) {
                List<RecordVersion> versions = store.get(key);
                if (versions != null && !versions.isEmpty()) {
                    RecordVersion latestVersion = versions.get(versions.size() - 1);
                    if (!tx.readView.isVisible(latestVersion.txId)) {
                        rollback(txId);
                        return false;
                    }
                }
            }

            for (Map.Entry<String, RecordVersion> entry : tx.writes.entrySet()) {
                store.computeIfAbsent(entry.getKey(), k -> new ArrayList<>()).add(entry.getValue());
            }

            activeTransactions.remove(txId);
            return true;
        } finally {
            lock.writeLock().unlock();
        }
    }

    public void rollback(int txId) {
        lock.writeLock().lock();
        try {
            activeTransactions.remove(txId);
        } finally {
            lock.writeLock().unlock();
        }
    }
}
