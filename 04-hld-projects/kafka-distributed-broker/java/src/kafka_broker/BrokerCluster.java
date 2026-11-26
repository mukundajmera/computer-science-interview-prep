package kafka_broker;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.ReentrantLock;
import java.util.stream.Collectors;

public class BrokerCluster {

    public static class Replica {
        public final String brokerId;
        public boolean isLeader;
        public final PartitionLog log;
        public int leo;
        public int hw;

        public Replica(String brokerId, boolean isLeader) {
            this.brokerId = brokerId;
            this.isLeader = isLeader;
            this.log = new PartitionLog(1024);
            this.leo = 0;
            this.hw = 0;
        }
    }

    public static class PartitionInfo {
        public final String partitionId;
        public String leaderId;
        public final List<String> replicas;
        public final Set<String> isr;
        public int hw;
        public final ReentrantLock lock = new ReentrantLock();

        public PartitionInfo(String partitionId, String leaderId, List<String> replicas) {
            this.partitionId = partitionId;
            this.leaderId = leaderId;
            this.replicas = new ArrayList<>(replicas);
            this.isr = new HashSet<>(replicas);
            this.hw = 0;
        }
    }

    public static class Broker {
        public final String brokerId;
        public final Map<String, Replica> replicas = new ConcurrentHashMap<>();
        public final ReentrantLock lock = new ReentrantLock();

        public Broker(String brokerId) {
            this.brokerId = brokerId;
        }

        public void addReplica(String partitionId, boolean isLeader) {
            lock.lock();
            try {
                replicas.put(partitionId, new Replica(brokerId, isLeader));
            } finally {
                lock.unlock();
            }
        }
    }

    private final Map<String, Broker> brokers = new ConcurrentHashMap<>();
    private final Map<String, PartitionInfo> partitions = new ConcurrentHashMap<>();
    private final ReentrantLock lock = new ReentrantLock();

    public BrokerCluster(List<String> brokerIds) {
        for (String bid : brokerIds) {
            brokers.put(bid, new Broker(bid));
        }
    }

    public void createPartition(String partitionId, List<String> replicaIds, String leaderId) {
        lock.lock();
        try {
            PartitionInfo pInfo = new PartitionInfo(partitionId, leaderId, replicaIds);
            partitions.put(partitionId, pInfo);
            for (String bid : replicaIds) {
                if (brokers.containsKey(bid)) {
                    brokers.get(bid).addReplica(partitionId, bid.equals(leaderId));
                }
            }
        } finally {
            lock.unlock();
        }
    }

    public int produce(String partitionId, byte[] data, int acks) {
        lock.lock();
        try {
            if (!partitions.containsKey(partitionId)) {
                throw new IllegalArgumentException("Partition not found");
            }
            PartitionInfo pInfo = partitions.get(partitionId);
            String leaderId = pInfo.leaderId;
            if (leaderId == null || leaderId.isEmpty()) {
                throw new RuntimeException("No leader available");
            }

            Broker leaderBroker = brokers.get(leaderId);
            int offset;
            leaderBroker.lock.lock();
            try {
                Replica replica = leaderBroker.replicas.get(partitionId);
                offset = replica.log.append(data);
                replica.leo = replica.log.getLogEndOffset();
            } finally {
                leaderBroker.lock.unlock();
            }

            if (acks == 0) {
                return offset;
            }

            if (acks == 1) {
                updateHw(partitionId);
                return offset;
            }

            if (acks == -1) {
                simulateFollowersFetch(partitionId);
                updateHw(partitionId);
                pInfo.lock.lock();
                try {
                    if (pInfo.hw >= offset + 1) {
                        return offset;
                    } else {
                        throw new RuntimeException("Failed to replicate to all ISRs");
                    }
                } finally {
                    pInfo.lock.unlock();
                }
            }
            return offset;
        } finally {
            lock.unlock();
        }
    }

    private void simulateFollowersFetch(String partitionId) {
        lock.lock();
        try {
            PartitionInfo pInfo = partitions.get(partitionId);
            String leaderId = pInfo.leaderId;
            Replica leaderReplica = brokers.get(leaderId).replicas.get(partitionId);

            for (String followerId : pInfo.isr) {
                if (followerId.equals(leaderId)) {
                    continue;
                }
                Replica followerReplica = brokers.get(followerId).replicas.get(partitionId);
                List<PartitionLog.Message> messages = leaderReplica.log.read(followerReplica.leo, 100);
                for (PartitionLog.Message msg : messages) {
                    followerReplica.log.append(msg.data);
                }
                followerReplica.leo = followerReplica.log.getLogEndOffset();
            }
        } finally {
            lock.unlock();
        }
    }

    public List<byte[]> fetch(String partitionId, int offset, int maxMessages) {
        lock.lock();
        try {
            PartitionInfo pInfo = partitions.get(partitionId);
            String leaderId = pInfo.leaderId;
            int hw = pInfo.hw;

            Broker leaderBroker = brokers.get(leaderId);
            List<PartitionLog.Message> msgs;
            leaderBroker.lock.lock();
            try {
                Replica replica = leaderBroker.replicas.get(partitionId);
                msgs = replica.log.read(offset, maxMessages);
            } finally {
                leaderBroker.lock.unlock();
            }

            List<byte[]> result = new ArrayList<>();
            for (PartitionLog.Message m : msgs) {
                if (m.offset < hw) {
                    result.add(m.data);
                }
            }
            return result;
        } finally {
            lock.unlock();
        }
    }

    private void updateHw(String partitionId) {
        lock.lock();
        try {
            PartitionInfo pInfo = partitions.get(partitionId);
            List<Integer> leos = new ArrayList<>();
            for (String bid : pInfo.isr) {
                leos.add(brokers.get(bid).replicas.get(partitionId).leo);
            }
            if (!leos.isEmpty()) {
                int newHw = Collections.min(leos);
                pInfo.hw = newHw;
                Replica leaderReplica = brokers.get(pInfo.leaderId).replicas.get(partitionId);
                leaderReplica.hw = newHw;
            }
        } finally {
            lock.unlock();
        }
    }

    public void failBroker(String brokerId) {
        lock.lock();
        try {
            for (Map.Entry<String, PartitionInfo> entry : partitions.entrySet()) {
                String pId = entry.getKey();
                PartitionInfo pInfo = entry.getValue();
                pInfo.lock.lock();
                try {
                    pInfo.isr.remove(brokerId);
                    if (brokerId.equals(pInfo.leaderId)) {
                        if (!pInfo.isr.isEmpty()) {
                            String bestReplica = null;
                            int maxLeo = -1;
                            for (String bid : pInfo.isr) {
                                int leo = brokers.get(bid).replicas.get(pId).leo;
                                if (leo > maxLeo) {
                                    maxLeo = leo;
                                    bestReplica = bid;
                                }
                            }
                            pInfo.leaderId = bestReplica;
                            for (String bid : pInfo.replicas) {
                                if (brokers.containsKey(bid) && brokers.get(bid).replicas.containsKey(pId)) {
                                    brokers.get(bid).replicas.get(pId).isLeader = bid.equals(bestReplica);
                                }
                            }
                        } else {
                            pInfo.leaderId = "";
                        }
                    }
                } finally {
                    pInfo.lock.unlock();
                }
            }
        } finally {
            lock.unlock();
        }
    }

    public void recoverBroker(String brokerId) {
        lock.lock();
        try {
            for (Map.Entry<String, PartitionInfo> entry : partitions.entrySet()) {
                String pId = entry.getKey();
                PartitionInfo pInfo = entry.getValue();
                pInfo.lock.lock();
                try {
                    if (pInfo.replicas.contains(brokerId)) {
                        simulateFollowersFetch(pId);
                        Replica followerReplica = brokers.get(brokerId).replicas.get(pId);
                        if (followerReplica.leo >= pInfo.hw) {
                            pInfo.isr.add(brokerId);
                            updateHw(pId);
                        }
                    }
                } finally {
                    pInfo.lock.unlock();
                }
            }
        } finally {
            lock.unlock();
        }
    }
}
