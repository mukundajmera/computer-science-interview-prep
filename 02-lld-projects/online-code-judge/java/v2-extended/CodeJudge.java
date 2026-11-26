
import java.util.HashMap;
import java.util.Map;

public class CodeJudge {
    private Map<String, Problem> problems;
    private Map<String, Submission> submissions;

    public CodeJudge() {
        this.problems = new HashMap<>();
        this.submissions = new HashMap<>();
    }

    public void addProblem(Problem problem) {
        problems.put(problem.getId(), problem);
    }

    public void submit(Submission submission) {
        submissions.put(submission.getId(), submission);
        process(submission);
    }

    public Verdict getVerdict(String submissionId) {
        Submission sub = submissions.get(submissionId);
        return sub != null ? sub.getVerdict() : null;
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

        LanguageRunner runner = RunnerFactory.getRunner(submission.getLanguage());

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
}
