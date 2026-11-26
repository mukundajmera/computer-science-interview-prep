from enum import Enum
import time

class Causality(Enum):
    BEFORE = -1
    AFTER = 1
    CONCURRENT = 0
    EQUAL = 2

class LamportClock:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.counter = 0

    def tick(self) -> int:
        self.counter += 1
        return self.counter

    def send_event(self) -> int:
        return self.tick()

    def receive_event(self, received_time: int) -> int:
        self.counter = max(self.counter, received_time) + 1
        return self.counter
    
    @staticmethod
    def compare_causality(time_a: int, node_a: str, time_b: int, node_b: str) -> Causality:
        if time_a < time_b:
            return Causality.BEFORE
        elif time_a > time_b:
            return Causality.AFTER
        else:
            if node_a < node_b:
                return Causality.BEFORE
            elif node_a > node_b:
                return Causality.AFTER
            else:
                return Causality.EQUAL

class VectorClock:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.vector = {node_id: 0}

    def tick(self) -> dict:
        self.vector[self.node_id] = self.vector.get(self.node_id, 0) + 1
        return self.vector.copy()

    def send_event(self) -> dict:
        return self.tick()

    def receive_event(self, received_vector: dict) -> dict:
        for node, count in received_vector.items():
            self.vector[node] = max(self.vector.get(node, 0), count)
        self.vector[self.node_id] = self.vector.get(self.node_id, 0) + 1
        return self.vector.copy()

    @staticmethod
    def compare_causality(vector_a: dict, vector_b: dict) -> Causality:
        all_nodes = set(vector_a.keys()).union(set(vector_b.keys()))
        a_is_smaller = False
        b_is_smaller = False

        for node in all_nodes:
            val_a = vector_a.get(node, 0)
            val_b = vector_b.get(node, 0)

            if val_a < val_b:
                a_is_smaller = True
            elif val_a > val_b:
                b_is_smaller = True

        if a_is_smaller and not b_is_smaller:
            return Causality.BEFORE
        elif b_is_smaller and not a_is_smaller:
            return Causality.AFTER
        elif not a_is_smaller and not b_is_smaller:
            return Causality.EQUAL
        else:
            return Causality.CONCURRENT


class TrueTimeSimulator:
    def __init__(self, epsilon_ms: int = 5):
        self.epsilon_ms = epsilon_ms
        self.current_time_ms = int(time.time() * 1000)

    def _advance_time(self, ms: int):
        self.current_time_ms += ms

    def now(self) -> tuple:
        # Returns [earliest, latest]
        # To simulate uncertainty, the actual current time is somewhere in the middle
        # For simulation, we return [current_time, current_time + epsilon_ms]
        # and advance the simulated time slightly.
        earliest = self.current_time_ms
        latest = earliest + self.epsilon_ms
        self._advance_time(1) # Time moves forward
        return (earliest, latest)

    def wait_until(self, target_time: int):
        # Simulates waiting until earliest time > target_time
        while self.now()[0] <= target_time:
            self._advance_time(1)

    def commit_transaction(self) -> int:
        # 1. Get current TrueTime interval
        earliest, latest = self.now()
        
        # 2. Commit timestamp is latest
        commit_timestamp = latest
        
        # 3. Commit wait
        self.wait_until(commit_timestamp)
        
        return commit_timestamp
