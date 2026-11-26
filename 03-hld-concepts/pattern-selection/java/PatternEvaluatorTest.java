import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.assertEquals;
import java.util.List;

public class PatternEvaluatorTest {

    @Test
    public void testCacheAsidePattern() {
        PatternEvaluator evaluator = new PatternEvaluator();
        SystemRequirements req = new SystemRequirements(5000, 10.0, 40, ConsistencyLevel.EVENTUAL);
        List<String> patterns = evaluator.evaluate(req);
        assertTrue(patterns.contains("Cache-Aside"));
    }

    @Test
    public void testWriteBehindPattern() {
        PatternEvaluator evaluator = new PatternEvaluator();
        SystemRequirements req = new SystemRequirements(15000, 0.1, 200, ConsistencyLevel.EVENTUAL);
        List<String> patterns = evaluator.evaluate(req);
        assertTrue(patterns.contains("Write-Behind"));
        assertTrue(patterns.contains("Message Queue / Worker Pool"));
    }

    @Test
    public void testEventSourcingPattern() {
        PatternEvaluator evaluator = new PatternEvaluator();
        SystemRequirements req = new SystemRequirements(15000, 0.1, 200, ConsistencyLevel.STRONG);
        List<String> patterns = evaluator.evaluate(req);
        assertTrue(patterns.contains("Event Sourcing"));
        assertTrue(patterns.contains("Message Queue / Worker Pool"));
    }

    @Test
    public void testTwoPhaseCommitPattern() {
        PatternEvaluator evaluator = new PatternEvaluator();
        SystemRequirements req = new SystemRequirements(1000, 1.0, 500, ConsistencyLevel.STRONG);
        List<String> patterns = evaluator.evaluate(req);
        assertTrue(patterns.contains("2PC (Two-Phase Commit)"));
    }

    @Test
    public void testCqrsPattern() {
        PatternEvaluator evaluator = new PatternEvaluator();
        SystemRequirements req = new SystemRequirements(60000, 2.0, 200, ConsistencyLevel.EVENTUAL);
        List<String> patterns = evaluator.evaluate(req);
        assertTrue(patterns.contains("CQRS"));
        assertTrue(patterns.contains("Message Queue / Worker Pool"));
    }

    @Test
    public void testCdnPattern() {
        PatternEvaluator evaluator = new PatternEvaluator();
        SystemRequirements req = new SystemRequirements(5000, 200.0, 10, ConsistencyLevel.EVENTUAL);
        List<String> patterns = evaluator.evaluate(req);
        assertTrue(patterns.contains("CDN"));
        assertTrue(patterns.contains("Cache-Aside"));
    }

    @Test
    public void testStandardArchitectureFallback() {
        PatternEvaluator evaluator = new PatternEvaluator();
        SystemRequirements req = new SystemRequirements(100, 1.0, 500, ConsistencyLevel.EVENTUAL);
        List<String> patterns = evaluator.evaluate(req);
        assertEquals(1, patterns.size());
        assertEquals("Standard 3-Tier Architecture", patterns.get(0));
    }
}
