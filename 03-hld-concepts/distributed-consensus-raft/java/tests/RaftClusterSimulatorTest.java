import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class RaftClusterSimulatorTest {

    @Test
    public void testLeaderElection() {
        RaftClusterSimulator simulator = new RaftClusterSimulator(5);
        
        boolean success = simulator.startElection(0);
        assertTrue(success);
        
        assertEquals(NodeState.LEADER, simulator.getNode(0).state);
        assertEquals(1, simulator.getNode(0).currentTerm);
        
        for (int i = 1; i < 5; i++) {
            assertEquals(NodeState.FOLLOWER, simulator.getNode(i).state);
            assertEquals(1, simulator.getNode(i).currentTerm);
        }
    }

    @Test
    public void testLogReplicationQuorum() {
        RaftClusterSimulator simulator = new RaftClusterSimulator(5);
        simulator.startElection(0);
        
        boolean success = simulator.appendCommand(0, "SET x 10");
        assertTrue(success);
        
        assertEquals(0, simulator.getNode(0).commitIndex);
        assertEquals(1, simulator.getNode(0).log.size());
        assertEquals("SET x 10", simulator.getNode(0).log.get(0).command);
        
        for (int i = 1; i < 5; i++) {
            assertEquals(0, simulator.getNode(i).commitIndex);
            assertEquals(1, simulator.getNode(i).log.size());
            assertEquals("SET x 10", simulator.getNode(i).log.get(0).command);
        }
    }

    @Test
    public void testRejectionWhenPartitioned() {
        RaftClusterSimulator simulator = new RaftClusterSimulator(5);
        simulator.startElection(0);
        
        simulator.partitionNode(2);
        simulator.partitionNode(3);
        simulator.partitionNode(4);
        
        boolean success = simulator.appendCommand(0, "SET y 20");
        assertFalse(success);
        
        assertEquals(-1, simulator.getNode(0).commitIndex);
        
        simulator.healPartition(2);
        simulator.healPartition(3);
        simulator.healPartition(4);
        
        success = simulator.appendCommand(0, "SET y 20");
        assertTrue(success);
        assertEquals(1, simulator.getNode(0).commitIndex); // Since the uncommitted one is index 0
    }

    @Test
    public void testLogReconciliation() {
        RaftClusterSimulator simulator = new RaftClusterSimulator(5);
        simulator.startElection(0);
        
        simulator.partitionNode(4);
        
        simulator.appendCommand(0, "cmd1");
        simulator.appendCommand(0, "cmd2");
        
        assertEquals(1, simulator.getNode(0).commitIndex);
        assertEquals(1, simulator.getNode(1).commitIndex);
        assertEquals(-1, simulator.getNode(4).commitIndex);
        assertEquals(0, simulator.getNode(4).log.size());
        
        simulator.healPartition(4);
        
        simulator.appendCommand(0, "cmd3");
        
        assertEquals(2, simulator.getNode(4).commitIndex);
        assertEquals(3, simulator.getNode(4).log.size());
        assertEquals("cmd1", simulator.getNode(4).log.get(0).command);
        assertEquals("cmd2", simulator.getNode(4).log.get(1).command);
        assertEquals("cmd3", simulator.getNode(4).log.get(2).command);
    }
}