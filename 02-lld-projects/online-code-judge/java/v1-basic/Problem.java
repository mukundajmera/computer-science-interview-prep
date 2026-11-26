
import java.util.List;

public class Problem {
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
