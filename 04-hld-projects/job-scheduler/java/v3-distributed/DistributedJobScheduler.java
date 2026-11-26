package v3_distributed;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

public class DistributedJobScheduler {

    public enum JobState {
        SCHEDULED, RUNNING, COMPLETED, FAILED, DEAD_LETTER
    }

    public static class JobRun {
        public String jobId;
        public long scheduledAt;
        public String leaseOwner;
        public long leaseUntil;
        public int attempt;
        public JobState state;
        public String idempotencyToken;

        public JobRun(String jobId, long scheduledAt) {
            this.jobId = jobId;
            this.scheduledAt = scheduledAt;
            this.state = JobState.SCHEDULED;
            this.attempt = 0;
            this.idempotencyToken = jobId + "-" + scheduledAt;
        }
    }

    public static class Datastore {
        public String leaderId = null;
        public long leaderLeaseUntil = 0;
        public final Map<String, Long> heartbeats = new ConcurrentHashMap<>();
        public final Map<String, JobRun> jobs = new ConcurrentHashMap<>();
        public final Set<String> completedTokens = ConcurrentHashMap.newKeySet();

        public synchronized boolean tryAcquireLeader(String nodeId, long currentTime, long leaseDuration) {
            if (leaderId == null || currentTime >= leaderLeaseUntil) {
                leaderId = nodeId;
                leaderLeaseUntil = currentTime + leaseDuration;
                return true;
            }
            if (nodeId.equals(leaderId)) {
                leaderLeaseUntil = currentTime + leaseDuration;
                return true;
            }
            return false;
        }

        public synchronized void heartbeat(String nodeId, long currentTime) {
            heartbeats.put(nodeId, currentTime);
        }

        public synchronized List<String> getActiveNodes(long currentTime, long timeout) {
            return heartbeats.entrySet().stream()
                    .filter(e -> (currentTime - e.getValue()) <= timeout)
                    .map(Map.Entry::getKey)
                    .sorted()
                    .collect(Collectors.toList());
        }

        public synchronized void submitJob(String jobId, long scheduledAt) {
            jobs.putIfAbsent(jobId, new JobRun(jobId, scheduledAt));
        }

        public synchronized JobRun getJob(String jobId) {
            return jobs.get(jobId);
        }
    }

    public static class ConsistentHashRing {
        private final TreeMap<Integer, String> ring = new TreeMap<>();
        private final int VIRTUAL_NODES = 5;

        public void updateRing(List<String> nodes) {
            ring.clear();
            for (String node : nodes) {
                for (int i = 0; i < VIRTUAL_NODES; i++) {
                    ring.put(hash(node + "-vn-" + i), node);
                }
            }
        }

        public String getNode(String key) {
            if (ring.isEmpty()) return null;
            int hash = hash(key);
            Map.Entry<Integer, String> entry = ring.ceilingEntry(hash);
            if (entry == null) {
                return ring.firstEntry().getValue();
            }
            return entry.getValue();
        }

        private int hash(String key) {
            try {
                MessageDigest md = MessageDigest.getInstance("MD5");
                byte[] digest = md.digest(key.getBytes(StandardCharsets.UTF_8));
                return ((digest[0] & 0xFF) << 24) |
                        ((digest[1] & 0xFF) << 16) |
                        ((digest[2] & 0xFF) << 8) |
                        (digest[3] & 0xFF);
            } catch (Exception e) {
                return key.hashCode();
            }
        }
    }

    public interface JobHandler {
        boolean execute(String jobId, String idempotencyToken);
    }

    private final String nodeId;
    private final Datastore datastore;
    private final JobHandler handler;
    private final ConsistentHashRing ring = new ConsistentHashRing();

    private boolean isLeader = false;

    public DistributedJobScheduler(String nodeId, Datastore datastore, JobHandler handler) {
        this.nodeId = nodeId;
        this.datastore = datastore;
        this.handler = handler;
    }

    public String getNodeId() {
        return nodeId;
    }

    public boolean isLeader() {
        return isLeader;
    }

    public void tick(long now) {
        datastore.heartbeat(nodeId, now);
        isLeader = datastore.tryAcquireLeader(nodeId, now, 5000);

        if (isLeader) {
            manageCluster(now);
        }

        processJobs(now);
    }

    private void manageCluster(long now) {
        List<String> activeNodes = datastore.getActiveNodes(now, 5000);
        ring.updateRing(activeNodes);

        synchronized (datastore) {
            for (JobRun run : datastore.jobs.values()) {
                if (run.state == JobState.SCHEDULED && run.scheduledAt <= now) {
                    assignJob(run, now);
                } else if (run.state == JobState.RUNNING && now >= run.leaseUntil) {
                    assignJob(run, now);
                } else if (run.state == JobState.FAILED) {
                    assignJob(run, now);
                }
            }
        }
    }

    private void assignJob(JobRun run, long now) {
        String targetNode = ring.getNode(run.jobId);
        if (targetNode != null) {
            run.attempt++;
            if (run.attempt > 3) {
                run.state = JobState.DEAD_LETTER;
            } else {
                run.leaseOwner = targetNode;
                run.leaseUntil = now + 10000;
                run.state = JobState.RUNNING;
            }
        }
    }

    private void processJobs(long now) {
        List<JobRun> myJobs = new ArrayList<>();
        synchronized (datastore) {
            for (JobRun run : datastore.jobs.values()) {
                if (run.state == JobState.RUNNING && nodeId.equals(run.leaseOwner) && now < run.leaseUntil) {
                    myJobs.add(run);
                }
            }
        }

        for (JobRun run : myJobs) {
            if (datastore.completedTokens.contains(run.idempotencyToken)) {
                synchronized (datastore) {
                    run.state = JobState.COMPLETED;
                }
                continue;
            }

            try {
                boolean success = handler.execute(run.jobId, run.idempotencyToken);
                synchronized (datastore) {
                    if (success) {
                        run.state = JobState.COMPLETED;
                        datastore.completedTokens.add(run.idempotencyToken);
                    } else {
                        run.state = JobState.FAILED;
                        run.leaseUntil = 0;
                    }
                }
            } catch (Exception e) {
                synchronized (datastore) {
                    run.state = JobState.FAILED;
                    run.leaseUntil = 0;
                }
            }
        }
    }
}
