import java.util.*;

enum NodeState {
    FOLLOWER,
    CANDIDATE,
    LEADER
}

class LogEntry {
    int term;
    String command;

    public LogEntry(int term, String command) {
        this.term = term;
        this.command = command;
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (!(obj instanceof LogEntry)) return false;
        LogEntry other = (LogEntry) obj;
        return this.term == other.term && Objects.equals(this.command, other.command);
    }
}

class VoteResponse {
    int term;
    boolean granted;

    public VoteResponse(int term, boolean granted) {
        this.term = term;
        this.granted = granted;
    }
}

class AppendResponse {
    int term;
    boolean success;

    public AppendResponse(int term, boolean success) {
        this.term = term;
        this.success = success;
    }
}

class RaftNode {
    int nodeId;
    List<Integer> clusterNodes;
    NodeState state;
    
    // Persistent state
    int currentTerm;
    Integer votedFor;
    List<LogEntry> log;
    
    // Volatile state
    int commitIndex;
    int lastApplied;
    
    // Volatile state on leaders
    Map<Integer, Integer> nextIndex;
    Map<Integer, Integer> matchIndex;
    
    // Simulator state
    boolean isPartitioned;
    Set<Integer> votesReceived;

    public RaftNode(int nodeId, List<Integer> clusterNodes) {
        this.nodeId = nodeId;
        this.clusterNodes = clusterNodes;
        this.state = NodeState.FOLLOWER;
        this.currentTerm = 0;
        this.votedFor = null;
        this.log = new ArrayList<>();
        this.commitIndex = -1;
        this.lastApplied = -1;
        this.nextIndex = new HashMap<>();
        this.matchIndex = new HashMap<>();
        this.isPartitioned = false;
        this.votesReceived = new HashSet<>();
    }
    
    public void initializeLeaderState() {
        for (int n : clusterNodes) {
            if (n != nodeId) {
                nextIndex.put(n, log.size());
                matchIndex.put(n, -1);
            }
        }
    }
    
    public VoteResponse requestVote(int candidateTerm, int candidateId, int lastLogIndex, int lastLogTerm) {
        if (isPartitioned) {
            return new VoteResponse(currentTerm, false);
        }
        
        if (candidateTerm < currentTerm) {
            return new VoteResponse(currentTerm, false);
        }
        
        if (candidateTerm > currentTerm) {
            currentTerm = candidateTerm;
            state = NodeState.FOLLOWER;
            votedFor = null;
        }
        
        int myLastLogIndex = log.size() - 1;
        int myLastLogTerm = log.isEmpty() ? -1 : log.get(log.size() - 1).term;
        
        boolean logOk = (lastLogTerm > myLastLogTerm) || 
                        (lastLogTerm == myLastLogTerm && lastLogIndex >= myLastLogIndex);
                        
        if ((votedFor == null || votedFor == candidateId) && logOk) {
            votedFor = candidateId;
            return new VoteResponse(currentTerm, true);
        }
        
        return new VoteResponse(currentTerm, false);
    }
    
    public AppendResponse appendEntries(int leaderTerm, int leaderId, int prevLogIndex, int prevLogTerm, 
                                        List<LogEntry> entries, int leaderCommit) {
        if (isPartitioned) {
            return new AppendResponse(currentTerm, false);
        }
        
        if (leaderTerm < currentTerm) {
            return new AppendResponse(currentTerm, false);
        }
        
        if (leaderTerm > currentTerm) {
            currentTerm = leaderTerm;
            votedFor = null;
        }
        
        state = NodeState.FOLLOWER;
        
        if (prevLogIndex >= 0) {
            if (log.size() <= prevLogIndex || log.get(prevLogIndex).term != prevLogTerm) {
                return new AppendResponse(currentTerm, false);
            }
        }
        
        if (entries != null && !entries.isEmpty()) {
            int idx = prevLogIndex + 1;
            for (LogEntry entry : entries) {
                if (log.size() > idx) {
                    if (log.get(idx).term != entry.term) {
                        log = new ArrayList<>(log.subList(0, idx));
                        log.add(entry);
                    }
                } else {
                    log.add(entry);
                }
                idx++;
            }
        }
        
        if (leaderCommit > commitIndex) {
            commitIndex = Math.min(leaderCommit, log.size() - 1);
        }
        
        return new AppendResponse(currentTerm, true);
    }
}

public class RaftClusterSimulator {
    Map<Integer, RaftNode> nodes;
    List<Integer> clusterNodes;
    
    public RaftClusterSimulator(int numNodes) {
        nodes = new HashMap<>();
        clusterNodes = new ArrayList<>();
        for (int i = 0; i < numNodes; i++) {
            clusterNodes.add(i);
        }
        for (int i = 0; i < numNodes; i++) {
            nodes.put(i, new RaftNode(i, clusterNodes));
        }
    }
    
    public boolean startElection(int candidateId) {
        RaftNode candidate = nodes.get(candidateId);
        if (candidate.isPartitioned) {
            return false;
        }
        
        candidate.state = NodeState.CANDIDATE;
        candidate.currentTerm++;
        candidate.votedFor = candidateId;
        candidate.votesReceived.clear();
        candidate.votesReceived.add(candidateId);
        
        int lastLogIndex = candidate.log.size() - 1;
        int lastLogTerm = candidate.log.isEmpty() ? -1 : candidate.log.get(candidate.log.size() - 1).term;
        
        for (int peerId : clusterNodes) {
            if (peerId == candidateId) continue;
            
            VoteResponse res = nodes.get(peerId).requestVote(candidate.currentTerm, candidateId, lastLogIndex, lastLogTerm);
            
            if (res.term > candidate.currentTerm) {
                candidate.currentTerm = res.term;
                candidate.state = NodeState.FOLLOWER;
                candidate.votedFor = null;
                return false;
            }
            
            if (res.granted) {
                candidate.votesReceived.add(peerId);
            }
        }
        
        if (candidate.votesReceived.size() > clusterNodes.size() / 2) {
            candidate.state = NodeState.LEADER;
            candidate.initializeLeaderState();
            sendHeartbeats(candidateId);
            return true;
        }
        
        return false;
    }
    
    private void sendHeartbeats(int leaderId) {
        RaftNode leader = nodes.get(leaderId);
        for (int peerId : clusterNodes) {
            if (peerId == leaderId) continue;
            
            int prevLogIndex = leader.nextIndex.get(peerId) - 1;
            int prevLogTerm = prevLogIndex >= 0 ? leader.log.get(prevLogIndex).term : -1;
            
            nodes.get(peerId).appendEntries(leader.currentTerm, leaderId, prevLogIndex, prevLogTerm, Collections.emptyList(), leader.commitIndex);
        }
    }
    
    public boolean appendCommand(int leaderId, String command) {
        RaftNode leader = nodes.get(leaderId);
        if (leader.state != NodeState.LEADER || leader.isPartitioned) {
            return false;
        }
        
        LogEntry entry = new LogEntry(leader.currentTerm, command);
        leader.log.add(entry);
        
        int replicas = 1;
        
        for (int peerId : clusterNodes) {
            if (peerId == leaderId) continue;
            
            int nextIdx = leader.nextIndex.get(peerId);
            int prevLogIndex = nextIdx - 1;
            int prevLogTerm = prevLogIndex >= 0 ? leader.log.get(prevLogIndex).term : -1;
            List<LogEntry> entries = leader.log.subList(nextIdx, leader.log.size());
            
            AppendResponse res = nodes.get(peerId).appendEntries(leader.currentTerm, leaderId, prevLogIndex, prevLogTerm, entries, leader.commitIndex);
            
            if (res.term > leader.currentTerm) {
                leader.currentTerm = res.term;
                leader.state = NodeState.FOLLOWER;
                leader.votedFor = null;
                return false;
            }
            
            if (res.success) {
                leader.matchIndex.put(peerId, leader.log.size() - 1);
                leader.nextIndex.put(peerId, leader.matchIndex.get(peerId) + 1);
                replicas++;
            } else {
                leader.nextIndex.put(peerId, Math.max(0, leader.nextIndex.get(peerId) - 1));
            }
        }
        
        if (replicas > clusterNodes.size() / 2) {
            leader.commitIndex = leader.log.size() - 1;
            sendHeartbeats(leaderId);
            return true;
        }
        
        return false;
    }
    
    public void partitionNode(int nodeId) {
        nodes.get(nodeId).isPartitioned = true;
    }
    
    public void healPartition(int nodeId) {
        nodes.get(nodeId).isPartitioned = false;
    }
    
    public RaftNode getNode(int nodeId) {
        return nodes.get(nodeId);
    }
}