
public class PythonRunner implements LanguageRunner {
    @Override
    public ExecutionResult execute(String code, String input) {
        if (code.contains("TLE")) return new ExecutionResult("", 2000, 1000, false);
        if (code.contains("MLE")) return new ExecutionResult("", 10, 1000000, false);
        if (code.contains("RE")) return new ExecutionResult("", 10, 10, true);
        if (code.contains("WA")) return new ExecutionResult("wrong", 10, 10, false);
        return new ExecutionResult(input, 10, 10, false);
    }
}
