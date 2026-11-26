import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class SimpleMetricsTest {
    
    private SimpleMetrics metrics;
    
    @BeforeEach
    public void setUp() {
        metrics = new SimpleMetrics();
    }
    
    @Test
    public void testRecordAndGetSum() {
        metrics.record("request_latency", 10.5);
        metrics.record("request_latency", 20.0);
        
        assertEquals(30.5, metrics.getSum("request_latency"), 0.001, "Sum of recorded metrics should be correct");
        assertEquals(0.0, metrics.getSum("non_existent_metric"), 0.001, "Sum of non-existent metric should be 0");
    }
    
    @Test
    public void testIncrementAndCount() {
        metrics.increment("request_count");
        metrics.increment("request_count");
        metrics.increment("request_count");
        
        assertEquals(3.0, metrics.getSum("request_count"), 0.001, "Sum should equal the number of increments");
        assertEquals(1.0, metrics.getAverage("request_count"), 0.001, "Average of increments (1s) should be 1");
    }
    
    @Test
    public void testGetAverage() {
        metrics.record("cpu_usage", 50.0);
        metrics.record("cpu_usage", 70.0);
        metrics.record("cpu_usage", 90.0);
        
        assertEquals(70.0, metrics.getAverage("cpu_usage"), 0.001, "Average should be calculated correctly");
        assertEquals(0.0, metrics.getAverage("non_existent_metric"), 0.001, "Average of non-existent metric should be 0");
    }
}
