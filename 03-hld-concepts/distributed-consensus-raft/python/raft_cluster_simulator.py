import random
from enum import Enum
from typing import List, Dict, Optional, Tuple

class NodeState(Enum):
    FOLLOWER = "FOLLOWER"
    CANDIDATE = "CANDIDATE"
    LEADER = "LEADER"

class LogEntry:
    def __init__(self, term: int, command: str):
        self.term = term
        self.command = command
        
    def __eq__(self, other):
        if not isinstance(other, LogEntry):
            return False
        return self.term == other.term and self.command == other.command
        
    def __repr__(self):
        return f"LogEntry(term={self.term}, cmd='{self.command}')"

class RaftNode:
    def __init__(self, node_id: int, cluster_nodes: List[int]):
        self.node_id = node_id
        self.cluster_nodes = cluster_nodes
        self.state = NodeState.FOLLOWER
        
        # Persistent state
        self.current_term = 0
        self.voted_for = None
        self.log: List[LogEntry] = []  # 1-indexed conceptually, but we'll use 0-indexed list and offset
        
        # Volatile state on all servers
        self.commit_index = -1
        self.last_applied = -1
        
        # Volatile state on leaders
        self.next_index: Dict[int, int] = {}
        self.match_index: Dict[int, int] = {}
        
        # Simulator state
        self.is_partitioned = False
        self.votes_received = set()
        
    def initialize_leader_state(self):
        self.next_index = {n: len(self.log) for n in self.cluster_nodes if n != self.node_id}
        self.match_index = {n: -1 for n in self.cluster_nodes if n != self.node_id}
        
    def request_vote(self, candidate_term: int, candidate_id: int, last_log_index: int, last_log_term: int) -> Tuple[int, bool]:
        if self.is_partitioned:
            return self.current_term, False
            
        if candidate_term < self.current_term:
            return self.current_term, False
            
        if candidate_term > self.current_term:
            self.current_term = candidate_term
            self.state = NodeState.FOLLOWER
            self.voted_for = None
            
        # Determine if candidate's log is at least as up-to-date
        my_last_log_index = len(self.log) - 1
        my_last_log_term = self.log[-1].term if self.log else -1
        
        log_ok = (last_log_term > my_last_log_term) or \
                 (last_log_term == my_last_log_term and last_log_index >= my_last_log_index)
                 
        if (self.voted_for is None or self.voted_for == candidate_id) and log_ok:
            self.voted_for = candidate_id
            return self.current_term, True
            
        return self.current_term, False
        
    def append_entries(self, leader_term: int, leader_id: int, prev_log_index: int, prev_log_term: int, 
                       entries: List[LogEntry], leader_commit: int) -> Tuple[int, bool]:
        if self.is_partitioned:
            return self.current_term, False
            
        if leader_term < self.current_term:
            return self.current_term, False
            
        if leader_term > self.current_term:
            self.current_term = leader_term
            self.voted_for = None
            
        self.state = NodeState.FOLLOWER
        
        # Log consistency check
        if prev_log_index >= 0:
            if len(self.log) <= prev_log_index or self.log[prev_log_index].term != prev_log_term:
                return self.current_term, False
                
        # Append any new entries not already in the log
        # Delete conflicting entries
        if entries:
            # We start replacing from prev_log_index + 1
            idx = prev_log_index + 1
            for entry in entries:
                if len(self.log) > idx:
                    if self.log[idx].term != entry.term:
                        # Conflict! truncate the log
                        self.log = self.log[:idx]
                        self.log.append(entry)
                else:
                    self.log.append(entry)
                idx += 1
                
        if leader_commit > self.commit_index:
            self.commit_index = min(leader_commit, len(self.log) - 1)
            
        return self.current_term, True

class RaftClusterSimulator:
    def __init__(self, num_nodes: int = 5):
        self.nodes = {i: RaftNode(i, list(range(num_nodes))) for i in range(num_nodes)}
        self.cluster_nodes = list(range(num_nodes))
        
    def start_election(self, candidate_id: int) -> bool:
        candidate = self.nodes[candidate_id]
        if candidate.is_partitioned:
            return False
            
        candidate.state = NodeState.CANDIDATE
        candidate.current_term += 1
        candidate.voted_for = candidate_id
        candidate.votes_received = {candidate_id}
        
        last_log_index = len(candidate.log) - 1
        last_log_term = candidate.log[-1].term if candidate.log else -1
        
        for peer_id in self.cluster_nodes:
            if peer_id == candidate_id:
                continue
                
            term, granted = self.nodes[peer_id].request_vote(
                candidate.current_term, candidate_id, last_log_index, last_log_term
            )
            
            if term > candidate.current_term:
                candidate.current_term = term
                candidate.state = NodeState.FOLLOWER
                candidate.voted_for = None
                return False
                
            if granted:
                candidate.votes_received.add(peer_id)
                
        if len(candidate.votes_received) > len(self.cluster_nodes) // 2:
            candidate.state = NodeState.LEADER
            candidate.initialize_leader_state()
            # Send initial heartbeats
            self._send_heartbeats(candidate_id)
            return True
            
        return False
        
    def _send_heartbeats(self, leader_id: int):
        leader = self.nodes[leader_id]
        for peer_id in self.cluster_nodes:
            if peer_id == leader_id:
                continue
            prev_log_index = leader.next_index[peer_id] - 1
            prev_log_term = leader.log[prev_log_index].term if prev_log_index >= 0 else -1
            self.nodes[peer_id].append_entries(
                leader.current_term, leader_id, prev_log_index, prev_log_term, [], leader.commit_index
            )
            
    def append_command(self, leader_id: int, command: str) -> bool:
        leader = self.nodes[leader_id]
        if leader.state != NodeState.LEADER or leader.is_partitioned:
            return False
            
        entry = LogEntry(leader.current_term, command)
        leader.log.append(entry)
        
        # Try to replicate
        replicas = 1  # leader itself
        for peer_id in self.cluster_nodes:
            if peer_id == leader_id:
                continue
                
            # Replicate entries starting from next_index
            prev_log_index = leader.next_index[peer_id] - 1
            prev_log_term = leader.log[prev_log_index].term if prev_log_index >= 0 else -1
            entries = leader.log[leader.next_index[peer_id]:]
            
            term, success = self.nodes[peer_id].append_entries(
                leader.current_term, leader_id, prev_log_index, prev_log_term, entries, leader.commit_index
            )
            
            if term > leader.current_term:
                leader.current_term = term
                leader.state = NodeState.FOLLOWER
                leader.voted_for = None
                return False
                
            if success:
                leader.match_index[peer_id] = len(leader.log) - 1
                leader.next_index[peer_id] = leader.match_index[peer_id] + 1
                replicas += 1
            else:
                # Decrement next_index and we'll retry next time
                leader.next_index[peer_id] = max(0, leader.next_index[peer_id] - 1)
                
        if replicas > len(self.cluster_nodes) // 2:
            # Commit the entry
            # In real Raft, we also check if the entry's term is current_term (Figure 8)
            leader.commit_index = len(leader.log) - 1
            self._send_heartbeats(leader_id) # Send commit index
            return True
            
        return False
        
    def partition_node(self, node_id: int):
        self.nodes[node_id].is_partitioned = True
        
    def heal_partition(self, node_id: int):
        self.nodes[node_id].is_partitioned = False
