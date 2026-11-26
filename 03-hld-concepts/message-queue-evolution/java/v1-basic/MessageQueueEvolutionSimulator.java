import java.util.*;

public class MessageQueueEvolutionSimulator {

    // --- Gen 1 State ---
    private final Map<String, String> exchanges = new HashMap<>();
    private final Map<String, Deque<Message>> queues = new HashMap<>();
    private final Map<String, List<Binding>> bindings = new HashMap<>();

    // --- Gen 2 State ---
    private final Map<String, List<List<KafkaMessage>>> topics = new HashMap<>();
    private final Map<String, Integer> consumerOffsets = new HashMap<>();

    // --- Gen 3 State ---
    private final Map<String, List<String>> activeLedgers = new HashMap<>();
    private final Map<String, List<List<String>>> tieredStorage = new HashMap<>();
    private static final int SEGMENT_SIZE = 3;

    public static class Message {
        public String msg;
        public boolean acked;

        public Message(String msg) {
            this.msg = msg;
            this.acked = false;
        }
    }

    public static class Binding {
        public String queue;
        public String routingKey;

        public Binding(String queue, String routingKey) {
            this.queue = queue;
            this.routingKey = routingKey;
        }
    }

    public static class KafkaMessage {
        public int offset;
        public String msg;

        public KafkaMessage(int offset, String msg) {
            this.offset = offset;
            this.msg = msg;
        }
    }

    public static class PulsarFetchResult {
        public String source;
        public String msg;

        public PulsarFetchResult(String source, String msg) {
            this.source = source;
            this.msg = msg;
        }
    }

    // --- Gen 1: AMQP Smart Broker ---
    public void createExchange(String name, String type) {
        exchanges.put(name, type);
    }

    public void createQueue(String name) {
        queues.put(name, new LinkedList<>());
    }

    public void bindQueue(String exchange, String queue, String routingKey) {
        bindings.computeIfAbsent(exchange, k -> new ArrayList<>()).add(new Binding(queue, routingKey));
    }

    public void publishAmqp(String exchange, String routingKey, String message) {
        if (!exchanges.containsKey(exchange)) {
            throw new IllegalArgumentException("Exchange not found: " + exchange);
        }

        List<Binding> exchangeBindings = bindings.getOrDefault(exchange, Collections.emptyList());
        for (Binding binding : exchangeBindings) {
            if (matchesRoutingKey(binding.routingKey, routingKey)) {
                queues.get(binding.queue).add(new Message(message));
            }
        }
    }

    public Message consumeAmqp(String queue) {
        Deque<Message> q = queues.get(queue);
        if (q != null && !q.isEmpty()) {
            return q.peekFirst();
        }
        return null;
    }

    public Message ackAmqp(String queue) {
        Deque<Message> q = queues.get(queue);
        if (q != null && !q.isEmpty()) {
            return q.pollFirst(); // Removes from queue
        }
        return null;
    }

    private boolean matchesRoutingKey(String bindKey, String routingKey) {
        if (bindKey.equals("#")) return true;
        if (bindKey.equals(routingKey)) return true;
        if (bindKey.endsWith(".*")) {
            String prefix = bindKey.substring(0, bindKey.length() - 2);
            return routingKey.startsWith(prefix);
        }
        return false;
    }

    // --- Gen 2: Kafka Dumb Broker / Append Log ---
    public void createTopicPartitions(String topic, int numPartitions) {
        if (!topics.containsKey(topic)) {
            List<List<KafkaMessage>> partitions = new ArrayList<>();
            for (int i = 0; i < numPartitions; i++) {
                partitions.add(new ArrayList<>());
            }
            topics.put(topic, partitions);
        }
    }

    public int publishKafka(String topic, int partition, String message) {
        if (!topics.containsKey(topic) || partition >= topics.get(topic).size()) {
            throw new IllegalArgumentException("Topic/Partition not found");
        }
        
        List<KafkaMessage> log = topics.get(topic).get(partition);
        int offset = log.size();
        log.add(new KafkaMessage(offset, message));
        return offset;
    }

    public KafkaMessage consumeKafka(String topic, int partition, String consumerGroup) {
        if (!topics.containsKey(topic) || partition >= topics.get(topic).size()) {
            throw new IllegalArgumentException("Topic/Partition not found");
        }

        String offsetKey = consumerGroup + "_" + topic + "_" + partition;
        int currentOffset = consumerOffsets.getOrDefault(offsetKey, 0);

        List<KafkaMessage> log = topics.get(topic).get(partition);
        if (currentOffset < log.size()) {
            return log.get(currentOffset);
        }
        return null;
    }

    public void commitOffsetKafka(String topic, int partition, String consumerGroup, int offset) {
        String offsetKey = consumerGroup + "_" + topic + "_" + partition;
        consumerOffsets.put(offsetKey, offset + 1);
    }

    public void replayKafka(String topic, int partition, String consumerGroup, int targetOffset) {
        String offsetKey = consumerGroup + "_" + topic + "_" + partition;
        consumerOffsets.put(offsetKey, targetOffset);
    }

    // --- Gen 3: Pulsar Decoupled Tiered Storage ---
    public void publishPulsar(String topicPartition, String message) {
        activeLedgers.putIfAbsent(topicPartition, new ArrayList<>());
        tieredStorage.putIfAbsent(topicPartition, new ArrayList<>());

        List<String> ledger = activeLedgers.get(topicPartition);
        ledger.add(message);

        if (ledger.size() >= SEGMENT_SIZE) {
            tieredStorage.get(topicPartition).add(new ArrayList<>(ledger));
            ledger.clear(); // roll segment
        }
    }

    public PulsarFetchResult consumePulsar(String topicPartition, int messageIndex) {
        List<List<String>> tiers = tieredStorage.getOrDefault(topicPartition, Collections.emptyList());
        int numTieredSegments = tiers.size();
        int totalTieredMsgs = numTieredSegments * SEGMENT_SIZE;

        if (messageIndex < totalTieredMsgs) {
            // Fetch from S3/GCS
            int segmentIdx = messageIndex / SEGMENT_SIZE;
            int msgIdxInSeg = messageIndex % SEGMENT_SIZE;
            return new PulsarFetchResult("S3_TIERED", tiers.get(segmentIdx).get(msgIdxInSeg));
        } else {
            // Fetch from active Bookie
            int activeIdx = messageIndex - totalTieredMsgs;
            List<String> ledger = activeLedgers.getOrDefault(topicPartition, Collections.emptyList());
            if (activeIdx < ledger.size()) {
                return new PulsarFetchResult("ACTIVE_BOOKIE", ledger.get(activeIdx));
            }
        }
        return null;
    }

    public int getQueueSize(String queue) {
        return queues.getOrDefault(queue, new LinkedList<>()).size();
    }
    
    public int getTieredStorageSize(String topicPartition) {
        return tieredStorage.getOrDefault(topicPartition, Collections.emptyList()).size();
    }
    
    public int getActiveLedgerSize(String topicPartition) {
        return activeLedgers.getOrDefault(topicPartition, Collections.emptyList()).size();
    }
}
