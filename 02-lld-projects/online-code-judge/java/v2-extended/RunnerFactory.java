
public class RunnerFactory {
    public static LanguageRunner getRunner(String language) {
        if (language.equals("PYTHON")) {
            return new PythonRunner();
        }
        return new PythonRunner();
    }
}
