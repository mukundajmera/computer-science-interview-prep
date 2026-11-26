import org.junit.jupiter.api.Test;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

public class StreamJobSkeletonTest {

    @Test
    public void testJobConfigCreation() {
        StreamJobSkeleton.JobConfig config = new StreamJobSkeleton.JobConfig("TestJob", 1000L, 500L);
        assertEquals("TestJob", config.jobName());
        assertEquals(1000L, config.checkpointIntervalMs());
        assertEquals(500L, config.allowedLatenessMs());
    }

    @Test
    public void testJobConfigCreationNullJobNameThrowsException() {
        assertThrows(NullPointerException.class, () -> new StreamJobSkeleton.JobConfig(null, 1000L, 500L));
    }

    @Test
    public void testStreamJobProcessing() {
        StreamJobSkeleton job = new StreamJobSkeleton();

        List<String> results = new ArrayList<>();

        StreamJobSkeleton.Source<Integer> source = new StreamJobSkeleton.Source<Integer>() {
            private int count = 0;
            @Override
            public Integer readNext() {
                if (count == 0) {
                    count++;
                    return 42;
                }
                return null;
            }
        };

        StreamJobSkeleton.Operator<Integer, String> operator = (input, eventTime) -> "Processed: " + input;

        StreamJobSkeleton.Sink<String> sink = results::add;

        job.run(source, operator, sink);

        assertEquals(1, results.size());
        assertEquals("Processed: 42", results.get(0));
    }

    @Test
    public void testStreamJobEmptySource() {
        StreamJobSkeleton job = new StreamJobSkeleton();

        List<String> results = new ArrayList<>();

        StreamJobSkeleton.Source<Integer> source = () -> null;

        StreamJobSkeleton.Operator<Integer, String> operator = (input, eventTime) -> "Processed: " + input;

        StreamJobSkeleton.Sink<String> sink = results::add;

        job.run(source, operator, sink);

        assertEquals(0, results.size());
    }
}
