import java.util.*;
import java.util.concurrent.locks.*;

class Partition {
    int id;
    List<String> log = new ArrayList<>();
    Lock lock = new ReentrantLock();

    Partition(int id) { this.id = id; }

    int append(String message) {
        lock.lock();
        try {
            int offset = log.size();
            log.add(message);
            return offset;
        } finally {
            lock.unlock();
        }
    }

    String read(int offset) {
        lock.lock();
        try {
            if (offset < log.size()) return log.get(offset);
            return null;
        } finally {
            lock.unlock();
        }
    }
}

class Topic {
    String name;
    List<Partition> partitions = new ArrayList<>();

    Topic(String name, int numPartitions) {
        this.name = name;
        for (int i = 0; i < numPartitions; i++) {
            partitions.add(new Partition(i));
        }
    }

    int produce(int partitionId, String message) {
        return partitions.get(partitionId).append(message);
    }
}

class ConsumerGroup {
    Topic topic;
    String groupId;
    Map<Integer, Integer> offsets = new HashMap<>();
    Lock lock = new ReentrantLock();

    ConsumerGroup(Topic topic, String groupId) {
        this.topic = topic;
        this.groupId = groupId;
        for (int i = 0; i < topic.partitions.size(); i++) {
            offsets.put(i, 0);
        }
    }

    String poll(int partitionId) {
        lock.lock();
        try {
            int offset = offsets.get(partitionId);
            String msg = topic.partitions.get(partitionId).read(offset);
            if (msg != null) {
                offsets.put(partitionId, offset + 1);
            }
            return msg;
        } finally {
            lock.unlock();
        }
    }
}
