import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.Map;

public class CausalClockEngineTest {

    @Test
    public void testLamportMonotonicityAndOrdering() {
        CausalClockEngine.LamportClock nodeA = new CausalClockEngine.LamportClock("A");
        CausalClockEngine.LamportClock nodeB = new CausalClockEngine.LamportClock("B");

        int timeA1 = nodeA.tick();
        assertEquals(1, timeA1);

        int timeB1 = nodeB.tick();
        assertEquals(1, timeB1);

        int timeA2 = nodeA.sendEvent();
        int timeB2 = nodeB.receiveEvent(timeA2);
        
        assertEquals(3, timeB2);
        assertEquals(CausalClockEngine.Causality.BEFORE, CausalClockEngine.LamportClock.compareCausality(timeA2, "A", timeB2, "B"));

        // Tiebreaker
        assertEquals(CausalClockEngine.Causality.BEFORE, CausalClockEngine.LamportClock.compareCausality(3, "A", 3, "B"));
        assertEquals(CausalClockEngine.Causality.AFTER, CausalClockEngine.LamportClock.compareCausality(3, "B", 3, "A"));
    }

    @Test
    public void testVectorClockCausalOrdering() {
        CausalClockEngine.VectorClock nodeA = new CausalClockEngine.VectorClock("A");
        CausalClockEngine.VectorClock nodeB = new CausalClockEngine.VectorClock("B");

        Map<String, Integer> va1 = nodeA.tick();
        assertEquals(1, (int) va1.get("A"));

        Map<String, Integer> va2 = nodeA.sendEvent();
        Map<String, Integer> vb1 = nodeB.receiveEvent(va2);

        assertEquals(2, (int) vb1.get("A"));
        assertEquals(1, (int) vb1.get("B"));

        assertEquals(CausalClockEngine.Causality.BEFORE, CausalClockEngine.VectorClock.compareCausality(va2, vb1));
    }

    @Test
    public void testVectorClockConcurrentConflict() {
        CausalClockEngine.VectorClock nodeA = new CausalClockEngine.VectorClock("A");
        CausalClockEngine.VectorClock nodeB = new CausalClockEngine.VectorClock("B");

        Map<String, Integer> va1 = nodeA.tick();
        Map<String, Integer> vb1 = nodeB.tick();

        assertEquals(CausalClockEngine.Causality.CONCURRENT, CausalClockEngine.VectorClock.compareCausality(va1, vb1));

        Map<String, Integer> va2 = nodeA.sendEvent();
        nodeB.receiveEvent(va2);
        Map<String, Integer> vb3 = nodeB.tick();

        CausalClockEngine.VectorClock nodeC = new CausalClockEngine.VectorClock("C");
        Map<String, Integer> vc1 = nodeC.receiveEvent(va1);

        CausalClockEngine.VectorClock nodeD = new CausalClockEngine.VectorClock("D");
        Map<String, Integer> vd1 = nodeD.receiveEvent(vb3);

        assertEquals(CausalClockEngine.Causality.CONCURRENT, CausalClockEngine.VectorClock.compareCausality(vc1, vd1));
    }

    @Test
    public void testTrueTimeCommitWait() {
        CausalClockEngine.TrueTimeSimulator tt = new CausalClockEngine.TrueTimeSimulator(5);

        long t1CommitTs = tt.commitTransaction();
        long[] nowAfterT1 = tt.now();

        assertTrue(nowAfterT1[0] > t1CommitTs, "Earliest TrueTime should be strictly greater than commit timestamp");

        long t2CommitTs = tt.commitTransaction();
        assertTrue(t2CommitTs > t1CommitTs, "Second transaction commit timestamp should be greater than first");
    }
}