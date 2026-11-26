# Testing

## Running Tests

You can run all Python tests using the provided script:

```bash
bash 01-design-patterns/run_tests.sh
```

If the environment variable `JUNIT_JAR` is set, this script will also run the Java tests using JUnit5 Console Launcher.

Example:

```bash
JUNIT_JAR=/path/to/junit-platform-console-standalone.jar bash 01-design-patterns/run_tests.sh
```
