import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;

public class DurableQueue {

    public static class DurableMessage implements Serializable {
        public final String key;
        public final String payload;
        public long offset;
        public final long timestamp;

        public DurableMessage(String key, String payload, long offset) {
            this.key = key;
            this.payload = payload;
            this.offset = offset;
            this.timestamp = System.currentTimeMillis();
        }
    }

    public static class Partition {
        private final int partitionId;
        private final File logFile;
        private final List<DurableMessage> messages = new ArrayList<>();
        private long nextOffset = 0;

        public Partition(int partitionId, String logDir) throws IOException {
            this.partitionId = partitionId;
            this.logFile = new File(logDir, "part_" + partitionId + ".log");
            load();
        }

        private void load() {
            if (!logFile.exists()) return;
            try (ObjectInputStream ois = new ObjectInputStream(new FileInputStream(logFile))) {
                while (true) {
                    try {
                        DurableMessage msg = (DurableMessage) ois.readObject();
                        messages.add(msg);
                        nextOffset = Math.max(nextOffset, msg.offset + 1);
                    } catch (EOFException e) {
                        break;
                    }
                }
            } catch (Exception e) {
                // Initial creation or corrupt file, start fresh
            }
        }

        public synchronized long append(DurableMessage message) throws IOException {
            message.offset = nextOffset++;
            messages.add(message);

            boolean appendMode = logFile.exists();
            try (FileOutputStream fos = new FileOutputStream(logFile, true)) {
                if (!appendMode) {
                    try (ObjectOutputStream oos = new ObjectOutputStream(fos)) {
                        oos.writeObject(message);
                        oos.flush();
                    }
                } else {
                    // Custom appending ObjectOutputStream to avoid writing header again
                    try (ObjectOutputStream oos = new ObjectOutputStream(fos) {
                        @Override
                        protected void writeStreamHeader() throws IOException {
                            reset();
                        }
                    }) {
                        oos.writeObject(message);
                        oos.flush();
                    }
                }
                fos.flush();
                try {
                    fos.getFD().sync(); // Ensure durable
                } catch (SyncFailedException e) {
                    // Ignore in certain virtualized environments where sync is unsupported
                }
            }
            return message.offset;
        }

        public synchronized DurableMessage read(long offset) {
            // In a real system, we'd search or maintain an index. 
            // For simple in-memory + sequential offsets, array indexing works.
            if (offset >= 0 && offset < messages.size()) {
                return messages.get((int) offset);
            }
            return null;
        }

        public int getPartitionId() {
            return partitionId;
        }
    }

    private final String logDir;
    private final int numPartitions;
    private final Partition[] partitions;
    
    // GroupID -> (PartitionID -> Offset)
    private final Map<String, Map<Integer, Long>> consumerOffsets = new HashMap<>();
    private final File offsetsFile;
    private final Object offsetLock = new Object();

    public DurableQueue(String logDir, int numPartitions) throws IOException {
        this.logDir = logDir;
        this.numPartitions = numPartitions;
        
        File dir = new File(logDir);
        if (!dir.exists()) {
            dir.mkdirs();
        }

        this.partitions = new Partition[numPartitions];
        for (int i = 0; i < numPartitions; i++) {
            this.partitions[i] = new Partition(i, logDir);
        }

        this.offsetsFile = new File(logDir, "offsets.dat");
        loadOffsets();
    }

    @SuppressWarnings("unchecked")
    private void loadOffsets() {
        if (!offsetsFile.exists()) return;
        try (ObjectInputStream ois = new ObjectInputStream(new FileInputStream(offsetsFile))) {
            Map<String, Map<Integer, Long>> loaded = (Map<String, Map<Integer, Long>>) ois.readObject();
            consumerOffsets.putAll(loaded);
        } catch (Exception e) {
            // Ignore
        }
    }

    private void saveOffsets() throws IOException {
        try (FileOutputStream fos = new FileOutputStream(offsetsFile);
             ObjectOutputStream oos = new ObjectOutputStream(fos)) {
            oos.writeObject(consumerOffsets);
            oos.flush();
            fos.flush();
            try {
                fos.getFD().sync();
            } catch (SyncFailedException e) {
                // Ignore
            }
        }
    }

    private Partition getPartition(String key) {
        // Bitwise AND to safely guarantee positive integer
        int hash = key.hashCode() & Integer.MAX_VALUE;
        return partitions[hash % numPartitions];
    }

    public long[] produce(String key, String payload) throws IOException {
        Partition part = getPartition(key);
        DurableMessage msg = new DurableMessage(key, payload, -1);
        long offset = part.append(msg);
        return new long[] { part.getPartitionId(), offset };
    }

    public DurableMessage consume(String groupId, int partitionId) {
        long offset = 0;
        synchronized (offsetLock) {
            consumerOffsets.putIfAbsent(groupId, new HashMap<>());
            offset = consumerOffsets.get(groupId).getOrDefault(partitionId, 0L);
        }
        Partition part = partitions[partitionId];
        return part.read(offset);
    }

    public void commitOffset(String groupId, int partitionId, long offset) throws IOException {
        synchronized (offsetLock) {
            consumerOffsets.putIfAbsent(groupId, new HashMap<>());
            long current = consumerOffsets.get(groupId).getOrDefault(partitionId, 0L);
            if (offset > current) {
                consumerOffsets.get(groupId).put(partitionId, offset);
                saveOffsets();
            }
        }
    }
    
    public static class IdempotentConsumer {
        private final DurableQueue queue;
        private final String groupId;
        private final Set<String> processedMessages = ConcurrentHashMap.newKeySet();
        private final Map<String, Integer> retryCounts = new ConcurrentHashMap<>();
        private final List<DurableMessage> dlq = new CopyOnWriteArrayList<>();
        private final int maxRetries;

        public IdempotentConsumer(DurableQueue queue, String groupId, int maxRetries) {
            this.queue = queue;
            this.groupId = groupId;
            this.maxRetries = maxRetries;
        }

        public interface Processor {
            void process(String payload) throws Exception;
        }

        public boolean consumeAndProcess(int partitionId, Processor processor) throws IOException {
            DurableMessage msg = queue.consume(groupId, partitionId);
            if (msg == null) return false;

            String msgId = partitionId + ":" + msg.offset;

            if (processedMessages.contains(msgId)) {
                queue.commitOffset(groupId, partitionId, msg.offset + 1);
                return true;
            }

            boolean success = false;
            try {
                processor.process(msg.payload);
                success = true;
            } catch (Exception e) {
                int count = retryCounts.getOrDefault(msgId, 0) + 1;
                retryCounts.put(msgId, count);
                if (count >= maxRetries) {
                    dlq.add(msg);
                    // Move past poison pill
                    queue.commitOffset(groupId, partitionId, msg.offset + 1);
                }
            }

            if (success) {
                processedMessages.add(msgId);
                queue.commitOffset(groupId, partitionId, msg.offset + 1);
            }
            
            return success;
        }
        
        public List<DurableMessage> getDlq() {
            return new ArrayList<>(dlq);
        }
    }
}