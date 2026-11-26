import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.util.Arrays;
import java.util.Collections;
import java.util.concurrent.atomic.AtomicBoolean;
import static org.junit.jupiter.api.Assertions.*;

public class ConfigEngineV3Test {
    private ConfigEngine engine;

    @BeforeEach
    public void setUp() {
        engine = new ConfigEngine();
    }

    @Test
    public void testEvaluateRollout() {
        RolloutBucket bucket1 = new RolloutBucket(50, new Variant("A"));
        RolloutBucket bucket2 = new RolloutBucket(50, new Variant("B"));
        Rollout rollout = new Rollout(Arrays.asList(bucket1, bucket2));
        
        Rule rule = new Rule("country", Operator.EQUALS, "US", rollout);
        FeatureFlag flag = new FeatureFlag("experiment", new Variant("C"), Arrays.asList(rule));
        engine.updateFlag(flag);
        
        UserContext ctx1 = new UserContext("u1");
        ctx1.setAttribute("country", "US");
        
        Variant result1 = engine.evaluate("experiment", ctx1);
        
        // Determinism test: evaluate multiple times
        Variant result2 = engine.evaluate("experiment", ctx1);
        assertEquals(result1.getValue(), result2.getValue());
    }

    @Test
    public void testListener() {
        AtomicBoolean notified = new AtomicBoolean(false);
        engine.registerListener("featureX", flag -> notified.set(true));
        
        FeatureFlag flag = new FeatureFlag("featureX", new Variant(true), Collections.emptyList());
        engine.updateFlag(flag);
        
        assertTrue(notified.get());
    }
}
