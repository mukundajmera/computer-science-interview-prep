import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.Set;
import java.util.HashSet;

class PacelcSimulatorTest {

    @Test
    void testPcEcRejectsMinority() {
        PacelcSimulator simulator = new PacelcSimulator("PC_EC");
        simulator.injectPartition(Set.of(2, 3));
        
        PacelcSimulator.Result res = simulator.write("k1", "v1");
        assertEquals("error", res.status);
        assertTrue(res.message.contains("Minority partition"));
    }

    @Test
    void testPcElNormalFastButRejectsMinority() {
        PacelcSimulator simulator = new PacelcSimulator("PC_EL");
        
        PacelcSimulator.Result res1 = simulator.write("k1", "v1");
        assertEquals("success", res1.status);
        assertTrue(res1.latencyMs < 50);

        simulator.injectPartition(Set.of(2, 3));
        PacelcSimulator.Result res2 = simulator.write("k1", "v2");
        assertEquals("error", res2.status);
        assertTrue(res2.message.contains("Minority partition"));
    }

    @Test
    void testPaElAcceptsFastWritesAndConverges() {
        PacelcSimulator simulator = new PacelcSimulator("PA_EL");
        
        PacelcSimulator.Result res1 = simulator.write("k1", "v1");
        assertEquals("success", res1.status);
        assertTrue(res1.latencyMs < 50);

        simulator.injectPartition(Set.of(2, 3));
        PacelcSimulator.Result res2 = simulator.write("k1", "v2");
        assertEquals("success", res2.status);

        assertEquals("v1", simulator.getNodes().get(2));
        assertEquals("v1", simulator.getNodes().get(3));

        simulator.healPartition();
        assertEquals(simulator.getNodes().get(1), simulator.getNodes().get(2));
        assertEquals(simulator.getNodes().get(2), simulator.getNodes().get(3));
    }

    @Test
    void testInvalidPolicyRejection() {
        assertThrows(IllegalArgumentException.class, () -> {
            new PacelcSimulator("INVALID_POLICY");
        });
    }
}
