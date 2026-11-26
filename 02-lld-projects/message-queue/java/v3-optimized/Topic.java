
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;

public class Topic {
    private final String name;
    private final List<Partition> partitions;
    private final AtomicInteger roundRobinCounter;

    public Topic(String name, int numPartitions) {
        this.name = name;
        this.partitions = new ArrayList<>();
        for (int i = 0; i < numPartitions; i++) {
            this.partitions.add(new Partition(i));
        }
        this.roundRobinCounter = new AtomicInteger(0);
    }

    public String getName() { return name; }

    public List<Partition> getPartitions() { return partitions; }

    public void publish(Message message) {
        int val = roundRobinCounter.getAndIncrement();
        if (val < 0) val = val & Integer.MAX_VALUE;
        int partitionIndex = val % partitions.size();
        partitions.get(partitionIndex).append(message);
    }

    public void publishToPartition(int partitionIndex, Message message) {
        if (partitionIndex >= 0 && partitionIndex < partitions.size()) {
            partitions.get(partitionIndex).append(message);
        } else {
            throw new IllegalArgumentException("Invalid partition index");
        }
    }
}
