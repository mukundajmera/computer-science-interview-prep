import java.time.Instant;
import java.util.Objects;

/**
 * Minimal stream-job abstraction for interview-level Flink discussions.
 */
public class StreamJobSkeleton {

    public interface Source<T> {
        T readNext();
    }

    public interface Operator<I, O> {
        O process(I input, Instant eventTime);
    }

    public interface Sink<T> {
        void write(T record);
    }

    public static final class JobConfig {
        private final String jobName;
        private final long checkpointIntervalMs;
        private final long allowedLatenessMs;

        public JobConfig(String jobName, long checkpointIntervalMs, long allowedLatenessMs) {
            this.jobName = Objects.requireNonNull(jobName, "jobName");
            this.checkpointIntervalMs = checkpointIntervalMs;
            this.allowedLatenessMs = allowedLatenessMs;
        }

        public String jobName() {
            return jobName;
        }

        public long checkpointIntervalMs() {
            return checkpointIntervalMs;
        }

        public long allowedLatenessMs() {
            return allowedLatenessMs;
        }
    }

    public <I, O> void run(Source<I> source, Operator<I, O> operator, Sink<O> sink) {
        I next = source.readNext();
        if (next == null) {
            return;
        }
        O output = operator.process(next, Instant.now());
        sink.write(output);
    }
}
