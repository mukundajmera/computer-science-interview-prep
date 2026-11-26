import java.time.Instant;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Minimal orchestration skeleton for coding submissions.
 *
 * This file intentionally focuses on responsibilities and signatures,
 * not production-ready implementation details.
 */
public class JudgeOrchestrator {
    private final ExecutionSandbox executionSandbox;
    private final LeaderboardProjection leaderboardProjection;
    private final SubmissionRepository submissionRepository;

    public JudgeOrchestrator(
            ExecutionSandbox executionSandbox,
            LeaderboardProjection leaderboardProjection,
            SubmissionRepository submissionRepository) {
        this.executionSandbox = executionSandbox;
        this.leaderboardProjection = leaderboardProjection;
        this.submissionRepository = submissionRepository;
    }

    public Submission submitForJudging(SubmissionRequest request) {
        Submission submission = Submission.queued(request);
        submissionRepository.save(submission);

        // In a full design this call is async via queue + workers.
        SandboxJobHandle handle = executionSandbox.submit(
                submission.id,
                request.language,
                request.sourceCode,
                request.testBundleRef,
                request.runtimeLimitMs,
                request.memoryLimitMb);
        submissionRepository.bindHandle(submission.id, handle.jobId());
        return submission;
    }

    public SubmissionStatus pollSubmissionStatus(UUID submissionId) {
        Submission submission = submissionRepository.get(submissionId)
                .orElseThrow(() -> new IllegalArgumentException("Unknown submission"));

        if (submission.status.isTerminal()) {
            return submission.status;
        }

        SandboxExecutionResult latest = executionSandbox.getStatus(submission.sandboxJobId)
                .orElse(SandboxExecutionResult.running());

        if (latest.isTerminal()) {
            SubmissionStatus terminal = SubmissionStatus.fromSandboxResult(latest);
            submissionRepository.markCompleted(submissionId, terminal, latest);
            if (terminal == SubmissionStatus.ACCEPTED && submission.contestId != null) {
                leaderboardProjection.recordResult(submission.contestId, submission.userId, latest.score);
            }
            return terminal;
        }

        return SubmissionStatus.RUNNING;
    }

    public List<LeaderboardEntry> getContestTopK(UUID contestId, int k) {
        return leaderboardProjection.topK(contestId, k);
    }

    public Optional<LeaderboardSnapshot> getContestSnapshot(UUID contestId) {
        return leaderboardProjection.snapshot(contestId);
    }
}

interface ExecutionSandbox {
    SandboxJobHandle submit(UUID submissionId, String language, String sourceCode,
                            String testBundleRef, long runtimeLimitMs, long memoryLimitMb);

    boolean cancel(String sandboxJobId);

    Optional<SandboxExecutionResult> getStatus(String sandboxJobId);
}

interface LeaderboardProjection {
    void recordResult(UUID contestId, UUID userId, double score);

    List<LeaderboardEntry> topK(UUID contestId, int k);

    Optional<LeaderboardSnapshot> snapshot(UUID contestId);
}

interface SubmissionRepository {
    void save(Submission submission);

    Optional<Submission> get(UUID submissionId);

    void bindHandle(UUID submissionId, String sandboxJobId);

    void markCompleted(UUID submissionId, SubmissionStatus status, SandboxExecutionResult result);
}

enum SubmissionStatus {
    QUEUED,
    RUNNING,
    ACCEPTED,
    WRONG_ANSWER,
    TIME_LIMIT_EXCEEDED,
    MEMORY_LIMIT_EXCEEDED,
    RUNTIME_ERROR,
    COMPILE_ERROR,
    SYSTEM_ERROR;

    boolean isTerminal() {
        return this != QUEUED && this != RUNNING;
    }

    static SubmissionStatus fromSandboxResult(SandboxExecutionResult result) {
        if (result.verdict == null) {
            return SYSTEM_ERROR;
        }
        return switch (result.verdict) {
            case "AC" -> ACCEPTED;
            case "WA" -> WRONG_ANSWER;
            case "TLE" -> TIME_LIMIT_EXCEEDED;
            case "MLE" -> MEMORY_LIMIT_EXCEEDED;
            case "RE" -> RUNTIME_ERROR;
            case "CE" -> COMPILE_ERROR;
            default -> SYSTEM_ERROR;
        };
    }
}

final class SubmissionRequest {
    final UUID userId;
    final UUID contestId;
    final String language;
    final String sourceCode;
    final String testBundleRef;
    final long runtimeLimitMs;
    final long memoryLimitMb;

    SubmissionRequest(UUID userId, UUID contestId, String language, String sourceCode,
                      String testBundleRef, long runtimeLimitMs, long memoryLimitMb) {
        this.userId = userId;
        this.contestId = contestId;
        this.language = language;
        this.sourceCode = sourceCode;
        this.testBundleRef = testBundleRef;
        this.runtimeLimitMs = runtimeLimitMs;
        this.memoryLimitMb = memoryLimitMb;
    }
}

final class Submission {
    final UUID id;
    final UUID userId;
    final UUID contestId;
    SubmissionStatus status;
    String sandboxJobId;
    final Instant createdAt;

    private Submission(UUID id, UUID userId, UUID contestId, SubmissionStatus status, Instant createdAt) {
        this.id = id;
        this.userId = userId;
        this.contestId = contestId;
        this.status = status;
        this.createdAt = createdAt;
    }

    static Submission queued(SubmissionRequest request) {
        return new Submission(UUID.randomUUID(), request.userId, request.contestId, SubmissionStatus.QUEUED, Instant.now());
    }
}

record SandboxJobHandle(String jobId) {
}

final class SandboxExecutionResult {
    final String verdict;
    final double score;
    final boolean terminal;

    SandboxExecutionResult(String verdict, double score, boolean terminal) {
        this.verdict = verdict;
        this.score = score;
        this.terminal = terminal;
    }

    static SandboxExecutionResult running() {
        return new SandboxExecutionResult(null, 0.0, false);
    }

    boolean isTerminal() {
        return terminal;
    }
}

record LeaderboardEntry(UUID userId, double score, long rank) {
}

record LeaderboardSnapshot(UUID contestId, Instant generatedAt, List<LeaderboardEntry> topEntries) {
}

/**
 * Tiny in-memory helper for local experimentation of projection semantics.
 */
class InMemoryLeaderboardProjection implements LeaderboardProjection {
    private final Map<UUID, Map<UUID, Double>> scoresByContest = new ConcurrentHashMap<>();

    @Override
    public void recordResult(UUID contestId, UUID userId, double score) {
        scoresByContest.computeIfAbsent(contestId, ignored -> new ConcurrentHashMap<>())
                .merge(userId, score, Math::max);
    }

    @Override
    public List<LeaderboardEntry> topK(UUID contestId, int k) {
        Map<UUID, Double> scores = scoresByContest.getOrDefault(contestId, Map.of());
        return scores.entrySet().stream()
                .sorted(Map.Entry.<UUID, Double>comparingByValue(Comparator.reverseOrder()))
                .limit(k)
                .map(e -> new LeaderboardEntry(e.getKey(), e.getValue(), 0))
                .toList();
    }

    @Override
    public Optional<LeaderboardSnapshot> snapshot(UUID contestId) {
        return Optional.of(new LeaderboardSnapshot(contestId, Instant.now(), topK(contestId, 100)));
    }
}
