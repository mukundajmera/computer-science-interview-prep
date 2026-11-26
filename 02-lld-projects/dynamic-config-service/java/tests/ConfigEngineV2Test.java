import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import java.util.Arrays;
import java.util.Collections;
import static org.junit.jupiter.api.Assertions.*;

public class ConfigEngineV2Test {
    private ConfigEngine engine;

    @BeforeEach
    public void setUp() {
        engine = new ConfigEngine();
    }

    @Test
    public void testEvaluateDefault() {
        FeatureFlag flag = new FeatureFlag("color", new Variant("blue"), Collections.emptyList());
        engine.updateFlag(flag);
        
        UserContext ctx = new UserContext("u1");
        Variant result = engine.evaluate("color", ctx);
        assertEquals("blue", result.getValue());
    }

    @Test
    public void testEvaluateRuleMatches() {
        Rule rule = new Rule("country", Operator.EQUALS, "US", new Variant("red"));
        FeatureFlag flag = new FeatureFlag("color", new Variant("blue"), Arrays.asList(rule));
        engine.updateFlag(flag);
        
        UserContext ctx = new UserContext("u1");
        ctx.setAttribute("country", "US");
        
        Variant result = engine.evaluate("color", ctx);
        assertEquals("red", result.getValue());
    }

    @Test
    public void testEvaluateRuleDoesNotMatch() {
        Rule rule = new Rule("country", Operator.EQUALS, "US", new Variant("red"));
        FeatureFlag flag = new FeatureFlag("color", new Variant("blue"), Arrays.asList(rule));
        engine.updateFlag(flag);
        
        UserContext ctx = new UserContext("u1");
        ctx.setAttribute("country", "UK");
        
        Variant result = engine.evaluate("color", ctx);
        assertEquals("blue", result.getValue());
    }
}
