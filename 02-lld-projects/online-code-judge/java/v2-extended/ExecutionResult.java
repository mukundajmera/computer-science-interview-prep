
public class ExecutionResult {
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
