import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;
import java.util.Map;
import java.util.List;
import java.util.ArrayList;

public class OnlineCodeJudge {

    public enum Verdict {
        PENDING, RUNNING, AC, WA, TLE, MLE, CE, RE
    }

    public static class TestCase {
        private String input;
        private String expectedOutput;
        public TestCase(String input, String expectedOutput) {
            this.input = input;
            this.expectedOutput = expectedOutput;
        }
        public String getInput() { return input; }
        public String getExpectedOutput() { return expectedOutput; }
    }

    public static class Problem {
        private String id;
        private List<TestCase> testCases;
        private int timeLimitMs;
        private int memoryLimitKb;

        public Problem(String id, List<TestCase> testCases, int timeLimitMs, int memoryLimitKb) {
            this.id = id;
            this.testCases = testCases;
            this.timeLimitMs = timeLimitMs;
            this.memoryLimitKb = memoryLimitKb;
        }
        public String getId() { return id; }
        public List<TestCase> getTestCases() { return testCases; }
        public int getTimeLimitMs() { return timeLimitMs; }
        public int getMemoryLimitKb() { return memoryLimitKb; }
    }

    public static class Submission {
        private String id;
        private String userId;
        private String problemId;
        private String language;
        private String code;
        private AtomicReference<Verdict> verdict = new AtomicReference<>(Verdict.PENDING);

        public Submission(String id, String userId, String problemId, String language, String code) {
            this.id = id;
            this.userId = userId;
            this.problemId = problemId;
            this.language = language;
            this.code = code;
        }

        public String getId() { return id; }
        public String getProblemId() { return problemId; }
        public String getLanguage() { return language; }
        public String getCode() { return code; }
        public Verdict getVerdict() { return verdict.get(); }

        public boolean updateVerdict(Verdict newVerdict) {
            while (true) {
                Verdict current = verdict.get();
                if (isTerminal(current)) {
                    return false;
                }
                if (verdict.compareAndSet(current, newVerdict)) {
                    return true;
                }
            }
        }

        private boolean isTerminal(Verdict v) {
            return v != Verdict.PENDING && v != Verdict.RUNNING;
        }
    }

    public static class ExecutionResult {
        private String output;
        private int timeTakenMs;
        private int memoryUsedKb;
        private boolean error;

        public ExecutionResult(String output, int timeTakenMs, int memoryUsedKb, boolean error) {
            this.output = output;
            this.timeTakenMs = timeTakenMs;
            this.memoryUsedKb = memoryUsedKb;
            this.error = error;
        }

        public String getOutput() { return output; }
        public int getTimeTakenMs() { return timeTakenMs; }
        public int getMemoryUsedKb() { return memoryUsedKb; }
        public boolean isError() { return error; }
    }

    /**
     * Trusted fake execution-adapter simulation.
     * 
     * SECURITY NOTICE:
     * Do not execute user-supplied code, shell commands, compilers, or arbitrary files on the host.
     * stdlib timeouts/resource labels are not a security sandbox.
     * Actual execution must occur in a separately approved VM/container boundary 
     * with strict filesystem, network, CPU, memory, output, and process controls.
     * MLE/TLE are adapter-reported simulations, not unproven isolation.
     */
    public interface LanguageRunner {
        ExecutionResult execute(String code, String input);
    }

    public static class FakeRunner implements LanguageRunner {
        @Override
        public ExecutionResult execute(String code, String input) {
            if (code.contains("TLE")) return new ExecutionResult("", 2000, 1000, false);
            if (code.contains("MLE")) return new ExecutionResult("", 100, 1000000, false);
            if (code.contains("RE")) return new ExecutionResult("", 10, 10, true);
            if (code.contains("WA")) return new ExecutionResult("wrong", 10, 10, false);
            return new ExecutionResult(input, 10, 10, false);
        }
    }

    private Map<String, Problem> problems;
    private Map<String, Submission> submissions;
    private BlockingQueue<Submission> queue;
    private List<Thread> workers;
    private volatile boolean active;

    public OnlineCodeJudge(int numWorkers) {
        this.problems = new ConcurrentHashMap<>();
        this.submissions = new ConcurrentHashMap<>();
        this.queue = new LinkedBlockingQueue<>();
        this.workers = new ArrayList<>();
        this.active = true;

        for (int i = 0; i < numWorkers; i++) {
            Thread t = new Thread(this::workerLoop);
            t.setDaemon(false);
            t.start();
            workers.add(t);
        }
    }

    public void addProblem(Problem problem) {
        problems.put(problem.getId(), problem);
    }

    public void submit(Submission submission) {
        submissions.put(submission.getId(), submission);
        queue.offer(submission);
    }

    public Verdict getVerdict(String submissionId) {
        Submission sub = submissions.get(submissionId);
        return sub != null ? sub.getVerdict() : null;
    }

    private void workerLoop() {
        while (active || !queue.isEmpty()) {
            try {
                Submission submission = queue.poll(100, TimeUnit.MILLISECONDS);
                if (submission != null) {
                    process(submission);
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            } catch (Exception e) {
                // ignore
            }
        }
    }

    private void process(Submission submission) {
        if (!submission.updateVerdict(Verdict.RUNNING)) {
            return; 
        }

        Problem problem = problems.get(submission.getProblemId());
        if (problem == null) {
            submission.updateVerdict(Verdict.CE);
            return;
        }

        LanguageRunner runner = new FakeRunner();

        for (TestCase tc : problem.getTestCases()) {
            ExecutionResult res = runner.execute(submission.getCode(), tc.getInput());
            if (res.isError()) {
                submission.updateVerdict(Verdict.RE);
                return;
            }
            if (res.getTimeTakenMs() > problem.getTimeLimitMs()) {
                submission.updateVerdict(Verdict.TLE);
                return;
            }
            if (res.getMemoryUsedKb() > problem.getMemoryLimitKb()) {
                submission.updateVerdict(Verdict.MLE);
                return;
            }
            if (!res.getOutput().equals(tc.getExpectedOutput())) {
                submission.updateVerdict(Verdict.WA);
                return;
            }
        }
        submission.updateVerdict(Verdict.AC);
    }

    public void stop() {
        active = false;
        for (Thread w : workers) {
            try {
                w.join(2000);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
    }
}
