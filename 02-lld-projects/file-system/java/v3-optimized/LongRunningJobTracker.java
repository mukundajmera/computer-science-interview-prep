import java.time.Instant;
import java.util.ArrayDeque;
import java.util.HashMap;
import java.util.Map;
import java.util.Queue;
import java.util.UUID;

/**
 * Tracks async jobs with idempotency and retry/DLQ primitives.
 * This is an illustrative skeleton for interview-oriented design discussion.
 */
class LongRunningJobTracker {
    private final Map<String, JobRecord> jobsById = new HashMap<>();
    private final Map<String, String> jobsByIdempotencyKey = new HashMap<>();
    private final Map<String, Queue<String>> queues = new HashMap<>();
    private final Queue<String> deadLetter = new ArrayDeque<>();

    public String submitJob(String idempotencyKey, JobType jobType, String payloadRef) {
        JobRecord existing = getByIdempotencyKey(idempotencyKey);
        if (existing != null) {
            return existing.jobId;
        }

        String jobId = UUID.randomUUID().toString();
        JobRecord record = new JobRecord(jobId, idempotencyKey, jobType, payloadRef);
        jobsById.put(jobId, record);
        jobsByIdempotencyKey.put(idempotencyKey, jobId);
        queues.computeIfAbsent(jobType.queueName, ignored -> new ArrayDeque<>()).offer(jobId);
        return jobId;
    }

    public JobRecord getJob(String jobId) {
        return jobsById.get(jobId);
    }

    public JobRecord getByIdempotencyKey(String idempotencyKey) {
        String jobId = jobsByIdempotencyKey.get(idempotencyKey);
        return jobId == null ? null : jobsById.get(jobId);
    }

    public JobRecord claimNext(String workerId, String queueName, int visibilityTimeoutSec) {
        Queue<String> queue = queues.get(queueName);
        if (queue == null || queue.isEmpty()) {
            return null;
        }

        String jobId = queue.poll();
        JobRecord record = jobsById.get(jobId);
        if (record == null) {
            return null;
        }

        record.status = JobStatus.RUNNING;
        record.claimedBy = workerId;
        record.nextVisibleAt = Instant.now().plusSeconds(visibilityTimeoutSec);
        record.lastHeartbeatAt = Instant.now();
        return record;
    }

    public void heartbeat(String jobId, String workerId) {
        JobRecord record = requireJob(jobId);
        if (!workerId.equals(record.claimedBy)) {
            throw new IllegalStateException("Worker does not own this job");
        }
        record.lastHeartbeatAt = Instant.now();
    }

    public void markSucceeded(String jobId, String resultRef) {
        JobRecord record = requireJob(jobId);
        record.status = JobStatus.SUCCEEDED;
        record.resultRef = resultRef;
        record.finishedAt = Instant.now();
    }

    public void markFailed(String jobId, String errorCode, boolean retryable) {
        JobRecord record = requireJob(jobId);
        record.lastErrorCode = errorCode;
        record.attempt += 1;

        if (!retryable || record.attempt >= record.maxAttempts) {
            moveToDeadLetter(jobId, "retry-limit-or-non-retryable");
            return;
        }

        record.status = JobStatus.QUEUED;
        record.nextVisibleAt = Instant.now().plusSeconds(5L * record.attempt);
        queues.computeIfAbsent(record.jobType.queueName, ignored -> new ArrayDeque<>()).offer(jobId);
    }

    public int retryTimedOutClaims(Instant now) {
        int requeued = 0;
        for (JobRecord record : jobsById.values()) {
            if (record.status == JobStatus.RUNNING && record.nextVisibleAt != null && record.nextVisibleAt.isBefore(now)) {
                record.status = JobStatus.QUEUED;
                record.claimedBy = null;
                queues.computeIfAbsent(record.jobType.queueName, ignored -> new ArrayDeque<>()).offer(record.jobId);
                requeued++;
            }
        }
        return requeued;
    }

    public void moveToDeadLetter(String jobId, String reason) {
        JobRecord record = requireJob(jobId);
        record.status = JobStatus.DEAD_LETTER;
        record.deadLetterReason = reason;
        deadLetter.offer(jobId);
    }

    public int queueDepth(String queueName) {
        Queue<String> queue = queues.get(queueName);
        return queue == null ? 0 : queue.size();
    }

    private JobRecord requireJob(String jobId) {
        JobRecord record = jobsById.get(jobId);
        if (record == null) {
            throw new IllegalArgumentException("Unknown job: " + jobId);
        }
        return record;
    }

    enum JobStatus {
        QUEUED,
        RUNNING,
        SUCCEEDED,
        FAILED,
        DEAD_LETTER
    }

    enum JobType {
        VIRUS_SCAN("file-fast"),
        THUMBNAIL_GEN("file-slow"),
        METADATA_EXTRACT("file-fast");

        final String queueName;

        JobType(String queueName) {
            this.queueName = queueName;
        }
    }

    static class JobRecord {
        final String jobId;
        final String idempotencyKey;
        final JobType jobType;
        final String payloadRef;
        int attempt;
        int maxAttempts;
        JobStatus status;
        String claimedBy;
        Instant nextVisibleAt;
        Instant lastHeartbeatAt;
        Instant finishedAt;
        String resultRef;
        String lastErrorCode;
        String deadLetterReason;

        JobRecord(String jobId, String idempotencyKey, JobType jobType, String payloadRef) {
            this.jobId = jobId;
            this.idempotencyKey = idempotencyKey;
            this.jobType = jobType;
            this.payloadRef = payloadRef;
            this.attempt = 0;
            this.maxAttempts = 5;
            this.status = JobStatus.QUEUED;
        }
    }
}
