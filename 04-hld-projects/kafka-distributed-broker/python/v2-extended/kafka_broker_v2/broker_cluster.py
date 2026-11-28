"""v2-extended Kafka broker cluster.

Improvements over v1-basic (each has dedicated tests):

1. Retention policies and disk monitoring (FOLLOW-UPS.md #2): see
   partition_log.py.

2. Idempotent producers with sequence numbers (FOLLOW-UPS.md #3):
   produce_idempotent() deduplicates retried produce calls per
   (partition, producer_id) so a producer retry never appends a
   duplicate, and rejects out-of-order sequences loudly.

3. Injectable-clock consumer coordination and lag metrics: see
   consumer_group_coordinator.py.
"""
import threading
from typing import Dict, List, Optional, Set
from .partition_log import PartitionLogV2
import time

class Replica:
    def __init__(self, broker_id: str, is_leader: bool):
        self.broker_id = broker_id
        self.is_leader = is_leader
        self.log = PartitionLogV2()
        self.leo = 0  # Log End Offset
        self.hw = 0   # High Watermark

class PartitionInfo:
    def __init__(self, partition_id: str, leader_id: str, replicas: List[str]):
        self.partition_id = partition_id
        self.leader_id = leader_id
        self.replicas = replicas
        self.isr: Set[str] = set(replicas)
        self.hw = 0
        self.min_isr = 2
        self.lock = threading.RLock()

class Broker:
    def __init__(self, broker_id: str):
        self.broker_id = broker_id
        self.replicas: Dict[str, Replica] = {} # partition_id -> Replica
        self.lock = threading.RLock()

    def add_replica(self, partition_id: str, is_leader: bool):
        with self.lock:
            self.replicas[partition_id] = Replica(self.broker_id, is_leader)

class BrokerClusterV2:
    def __init__(self, broker_ids: List[str]):
        self.brokers: Dict[str, Broker] = {bid: Broker(bid) for bid in broker_ids}
        self.partitions: Dict[str, PartitionInfo] = {}
        self.lock = threading.RLock()
        # Improvement #2: per (partition, producer_id) idempotence state:
        # last contiguous sequence and the offsets of recent sequences.
        self._producer_state: Dict[str, Dict[str, dict]] = {}

    def create_partition(self, partition_id: str, replica_ids: List[str], leader_id: str):
        with self.lock:
            p_info = PartitionInfo(partition_id, leader_id, replica_ids)
            self.partitions[partition_id] = p_info
            for bid in replica_ids:
                if bid in self.brokers:
                    self.brokers[bid].add_replica(partition_id, is_leader=(bid == leader_id))

    def produce(self, partition_id: str, data: bytes, acks: int) -> Optional[int]:
        """
        acks=0: no wait
        acks=1: wait for leader
        acks=-1 (all): wait for all ISR
        """
        with self.lock:
            if partition_id not in self.partitions:
                raise ValueError("Partition not found")
            p_info = self.partitions[partition_id]
            leader_id = p_info.leader_id
            if not leader_id:
                raise RuntimeError("No leader available")

        leader_broker = self.brokers[leader_id]
        with leader_broker.lock:
            replica = leader_broker.replicas[partition_id]
            offset = replica.log.append(data)
            replica.leo = replica.log.get_log_end_offset()
            
        if acks == 0:
            return offset
            
        if acks == 1:
            # We already appended to leader
            self._update_hw(partition_id)
            return offset
            
        if acks == -1:
            with self.partitions[partition_id].lock:
                if len(self.partitions[partition_id].isr) < self.partitions[partition_id].min_isr:
                    raise RuntimeError("NotEnoughReplicasException: Insufficient ISR")
            # For acks=all in this simulation, we simulate the followers fetching immediately.
            # In real Kafka, followers fetch periodically.
            self._simulate_followers_fetch(partition_id)
            self._update_hw(partition_id)
            # Check if HW reached the offset
            with self.partitions[partition_id].lock:
                if self.partitions[partition_id].hw >= offset + 1:
                    return offset
                else:
                    raise RuntimeError("Failed to replicate to all ISRs")
        return offset

    def _simulate_followers_fetch(self, partition_id: str):
        with self.lock:
            p_info = self.partitions[partition_id]
            leader_id = p_info.leader_id
            leader_replica = self.brokers[leader_id].replicas[partition_id]
            
            for follower_id in p_info.isr:
                if follower_id == leader_id:
                    continue
                follower_replica = self.brokers[follower_id].replicas[partition_id]
                # follower fetches from follower_replica.leo
                messages = leader_replica.log.read(follower_replica.leo, 100)
                for _, msg_data in messages:
                    follower_replica.log.append(msg_data)
                follower_replica.leo = follower_replica.log.get_log_end_offset()

    def fetch(self, partition_id: str, offset: int, max_messages: int = 10) -> List[bytes]:
        with self.lock:
            p_info = self.partitions[partition_id]
            leader_id = p_info.leader_id
            hw = p_info.hw
            
        leader_broker = self.brokers[leader_id]
        with leader_broker.lock:
            replica = leader_broker.replicas[partition_id]
            msgs = replica.log.read(offset, max_messages)
            # Only return messages up to HW
            return [m[1] for m in msgs if m[0] < hw]

    def _update_hw(self, partition_id: str):
        with self.lock:
            p_info = self.partitions[partition_id]
            leos = []
            for bid in p_info.isr:
                leos.append(self.brokers[bid].replicas[partition_id].leo)
            if leos:
                new_hw = min(leos)
                p_info.hw = new_hw
                # update leader's hw
                leader_replica = self.brokers[p_info.leader_id].replicas[partition_id]
                leader_replica.hw = new_hw

    def fail_broker(self, broker_id: str):
        with self.lock:
            for p_id, p_info in self.partitions.items():
                with p_info.lock:
                    if broker_id in p_info.isr:
                        p_info.isr.remove(broker_id)
                    if p_info.leader_id == broker_id:
                        # Elect new leader
                        if p_info.isr:
                            # Pick the one with highest LEO (simplification)
                            # Simplified election protocol: the controller is omitted, 
                            # we directly select the replica with the highest LEO from the ISR.
                            best_replica = max(p_info.isr, key=lambda bid: self.brokers[bid].replicas[p_id].leo)
                            p_info.leader_id = best_replica
                            for bid in p_info.replicas:
                                if bid in self.brokers and p_id in self.brokers[bid].replicas:
                                    self.brokers[bid].replicas[p_id].is_leader = (bid == best_replica)
                        else:
                            p_info.leader_id = "" # No leader available

    def recover_broker(self, broker_id: str):
        with self.lock:
            for p_id, p_info in self.partitions.items():
                with p_info.lock:
                    if broker_id in p_info.replicas:
                        follower_replica = self.brokers[broker_id].replicas[p_id]
                        
                        # Deterministic recovery: truncate to HW before fetching
                        follower_replica.log.truncate_to(follower_replica.hw)
                        follower_replica.leo = follower_replica.log.get_log_end_offset()
                        # hw will be updated below if it catches up
                        
                        if p_info.leader_id and p_info.leader_id != broker_id:
                            leader_replica = self.brokers[p_info.leader_id].replicas[p_id]
                            try:
                                messages = leader_replica.log.read(follower_replica.leo, 100)
                                for _, msg_data in messages:
                                    follower_replica.log.append(msg_data)
                                follower_replica.leo = follower_replica.log.get_log_end_offset()
                            except ValueError:
                                pass # handle retention gap if necessary
                        
                        if follower_replica.leo >= p_info.hw:
                            p_info.isr.add(broker_id)
                            self._update_hw(p_id)



    def produce_idempotent(self, partition_id: str, data: bytes, acks: int,
                           producer_id: str, sequence: int) -> int:
        """Improvement #2 (FOLLOW-UPS.md #3): idempotent produce. A retried
        call with an already-seen (producer_id, sequence) returns the
        original offset without appending a duplicate; a sequence gap
        raises loudly instead of silently reordering the log."""
        with self.lock:
            state = self._producer_state.setdefault(partition_id, {})
            producer = state.setdefault(producer_id, {"last_sequence": -1, "offsets": {}})
            if sequence <= producer["last_sequence"]:
                if sequence in producer["offsets"]:
                    return producer["offsets"][sequence]
                raise ValueError(
                    f"OutOfOrderSequence: sequence {sequence} already acknowledged for producer {producer_id}")
            if sequence != producer["last_sequence"] + 1:
                raise ValueError(
                    f"OutOfOrderSequence: expected sequence {producer['last_sequence'] + 1} "
                    f"from producer {producer_id}, got {sequence}")

        offset = self.produce(partition_id, data, acks)

        with self.lock:
            producer = self._producer_state[partition_id][producer_id]
            producer["last_sequence"] = sequence
            producer["offsets"][sequence] = offset
            # Keep only the most recent sequences for dedup lookup.
            while len(producer["offsets"]) > 5:
                oldest = min(producer["offsets"])
                del producer["offsets"][oldest]
        return offset
