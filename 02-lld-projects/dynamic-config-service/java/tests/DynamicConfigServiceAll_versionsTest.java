import org.junit.jupiter.api.Test;
import java.util.HashMap;
import java.util.Map;
import static org.junit.jupiter.api.Assertions.*;

public class DynamicConfigServiceAll_versionsTest {

    @Test
    public void testCrossLanguageHashDeterminism() {
        FeatureFlag flag = new FeatureFlag("experiment", new Variant("A"), 50, null);
        Map<String, FeatureFlag> flags = new HashMap<>();
        flags.put("experiment", flag);
        DynamicConfigService service = new DynamicConfigService(new ConfigSnapshot(1, flags));
        
        UserContext ctx1 = new UserContext("u1"); // MD5 % 100 = 20
        Variant result1 = service.evaluate("experiment", ctx1, new Variant("Fallback"));
        assertEquals("A", result1.getValue());
        
        UserContext ctx2 = new UserContext("u3"); // MD5 % 100 = 65
        Variant result2 = service.evaluate("experiment", ctx2, new Variant("Fallback"));
        assertEquals("Fallback", result2.getValue()); 
    }

    @Test
    public void testAtomicSnapshotsAndRollbackAndStale() {
        Map<String, FeatureFlag> flagsV1 = new HashMap<>();
        flagsV1.put("f1", new FeatureFlag("f1", new Variant("V1"), 100, null));
        ConfigSnapshot snap1 = new ConfigSnapshot(1, flagsV1);
        DynamicConfigService service = new DynamicConfigService(snap1);
        
        UserContext ctx = new UserContext("u1");
        assertEquals("V1", service.evaluate("f1", ctx, new Variant(null)).getValue());
        
        Map<String, FeatureFlag> flagsV2 = new HashMap<>();
        flagsV2.put("f1", new FeatureFlag("f1", new Variant("V2"), 100, null));
        ConfigSnapshot snap2 = new ConfigSnapshot(2, flagsV2);
        
        assertTrue(service.applySnapshot(snap2));
        assertEquals("V2", service.evaluate("f1", ctx, new Variant(null)).getValue());
        
        ConfigSnapshot snapStale = new ConfigSnapshot(1, flagsV1);
        assertFalse(service.applySnapshot(snapStale));
        assertEquals("V2", service.evaluate("f1", ctx, new Variant(null)).getValue());
        
        assertTrue(service.rollback(1));
        assertEquals("V1", service.evaluate("f1", ctx, new Variant(null)).getValue());
        assertFalse(service.rollback(999));
    }
    
    @Test
    public void testMissingFlag() {
        DynamicConfigService service = new DynamicConfigService(new ConfigSnapshot(1, new HashMap<>()));
        Variant fallback = new Variant("fallback_val");
        assertEquals("fallback_val", service.evaluate("missing", new UserContext("u1"), fallback).getValue());
    }
    
    @Test
    public void testInvalidPercentage() {
        FeatureFlag flag = new FeatureFlag("f1", new Variant("default"), 150, null);
        Map<String, FeatureFlag> flags = new HashMap<>();
        flags.put("f1", flag);
        DynamicConfigService service = new DynamicConfigService(new ConfigSnapshot(1, flags));
        
        UserContext ctx = new UserContext("u1");
        Variant result = service.evaluate("f1", ctx, new Variant("fb"));
        assertEquals("fb", result.getValue());
    }

    @Test
    public void testTenantOverridePrecedence() {
        Map<String, Variant> overrides = new HashMap<>();
        overrides.put("tenantA", new Variant("override_val"));
        
        FeatureFlag flag = new FeatureFlag("f1", new Variant("def"), 100, overrides);
        Map<String, FeatureFlag> flags = new HashMap<>();
        flags.put("f1", flag);
        DynamicConfigService service = new DynamicConfigService(new ConfigSnapshot(1, flags));
        
        UserContext ctx = new UserContext("u1");
        ctx.setAttribute("tenant", "tenantA");
        
        assertEquals("override_val", service.evaluate("f1", ctx, new Variant("fb")).getValue());
    }
}
