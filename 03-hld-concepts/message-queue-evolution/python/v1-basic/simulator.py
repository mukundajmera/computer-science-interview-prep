import time
import collections

class MessageQueueEvolutionSimulator:
    """
    Models the evolution of message queue architectures:
    - Gen 1: AMQP Smart Broker (Exchange Routing with ACKs)
    - Gen 2: Kafka Partitioned Commit Log (Consumer Offsets, Replay)
    - Gen 3: Pulsar Segmented/Tiered Storage (Segment rolling and cold data retrieval)
    """
    def __init__(self):
        # Gen 1 State
        self.exchanges = {}
        self.queues = {}
        self.bindings = collections.defaultdict(list)

        # Gen 2 State
        self.topics = collections.defaultdict(list) # topic -> list of partition logs (each partition is a list of messages)
        self.consumer_offsets = collections.defaultdict(int) # consumer_id_partition -> offset

        # Gen 3 State
        self.active_ledgers = collections.defaultdict(list) # topic_partition -> current segment list
        self.tiered_storage = collections.defaultdict(list) # topic_partition -> list of archived segments
        self.SEGMENT_SIZE = 3 # roll segment after 3 messages

    # --- Gen 1: Smart Broker / Dumb Consumer (AMQP / RabbitMQ) ---
    def create_exchange(self, name, type="topic"):
        self.exchanges[name] = type

    def create_queue(self, name):
        self.queues[name] = collections.deque()

    def bind_queue(self, exchange, queue, routing_key):
        self.bindings[exchange].append((queue, routing_key))

    def publish_amqp(self, exchange, routing_key, message):
        if exchange not in self.exchanges:
            raise ValueError(f"Exchange {exchange} not found")
        
        for queue, bind_key in self.bindings.get(exchange, []):
            if self._matches_routing_key(bind_key, routing_key):
                self.queues[queue].append({"msg": message, "acked": False})

    def consume_amqp(self, queue):
        if queue in self.queues and self.queues[queue]:
            return self.queues[queue][0] # peek
        return None

    def ack_amqp(self, queue):
        if queue in self.queues and self.queues[queue]:
            msg = self.queues[queue].popleft() # Remove from memory upon ACK
            return msg
        return None

    def _matches_routing_key(self, bind_key, routing_key):
        # Extremely basic topic matching (just handles exact match or '#' wildcard for simplicity)
        if bind_key == "#": return True
        if bind_key == routing_key: return True
        
        # simple prefix matching for test cases
        if bind_key.endswith(".*"):
            prefix = bind_key[:-2]
            return routing_key.startswith(prefix)
            
        return False

    # --- Gen 2: Dumb Broker / Smart Consumer (Kafka) ---
    def create_topic_partitions(self, topic, num_partitions):
        if topic not in self.topics:
            self.topics[topic] = [[] for _ in range(num_partitions)]

    def publish_kafka(self, topic, partition, message):
        if topic not in self.topics or partition >= len(self.topics[topic]):
            raise ValueError("Topic/Partition not found")
        
        offset = len(self.topics[topic][partition])
        self.topics[topic][partition].append({"offset": offset, "msg": message})
        return offset

    def consume_kafka(self, topic, partition, consumer_group):
        if topic not in self.topics or partition >= len(self.topics[topic]):
            raise ValueError("Topic/Partition not found")
            
        offset_key = f"{consumer_group}_{topic}_{partition}"
        current_offset = self.consumer_offsets[offset_key]
        
        log = self.topics[topic][partition]
        if current_offset < len(log):
            return log[current_offset]
        return None

    def commit_offset_kafka(self, topic, partition, consumer_group, offset):
        offset_key = f"{consumer_group}_{topic}_{partition}"
        self.consumer_offsets[offset_key] = offset + 1

    def replay_kafka(self, topic, partition, consumer_group, target_offset):
        """Allows 'time travel' by resetting the consumer offset"""
        offset_key = f"{consumer_group}_{topic}_{partition}"
        self.consumer_offsets[offset_key] = target_offset

    # --- Gen 3: Decoupled / Tiered Storage (Pulsar) ---
    def publish_pulsar(self, topic_partition, message):
        ledger = self.active_ledgers[topic_partition]
        ledger.append(message)
        
        if len(ledger) >= self.SEGMENT_SIZE:
            # Segment full, roll to tiered storage (simulate S3 offload)
            self.tiered_storage[topic_partition].append(list(ledger))
            self.active_ledgers[topic_partition] = [] # open new ledger

    def consume_pulsar(self, topic_partition, message_index):
        """
        Abstracts the consumer fetching.
        If the index is in active ledger, get it from broker/active bookie.
        If it's older, fetch transparently from tiered storage.
        """
        num_tiered_segments = len(self.tiered_storage[topic_partition])
        total_tiered_msgs = num_tiered_segments * self.SEGMENT_SIZE
        
        if message_index < total_tiered_msgs:
            # Cold data retrieval
            segment_idx = message_index // self.SEGMENT_SIZE
            msg_idx_in_seg = message_index % self.SEGMENT_SIZE
            return {"source": "S3_TIERED", "msg": self.tiered_storage[topic_partition][segment_idx][msg_idx_in_seg]}
        else:
            # Active ledger retrieval
            active_idx = message_index - total_tiered_msgs
            if active_idx < len(self.active_ledgers[topic_partition]):
                return {"source": "ACTIVE_BOOKIE", "msg": self.active_ledgers[topic_partition][active_idx]}
        
        return None
