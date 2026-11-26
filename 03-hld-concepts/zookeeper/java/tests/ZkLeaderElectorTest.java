package v1_simple;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.ArrayList;
import java.util.List;

public class ZkLeaderElectorTest {

    @Test
    public void testSingleNodeElection() {
        ZkLeaderElector.ZkSimulator zk = new ZkLeaderElector.ZkSimulator();
        ZkLeaderElector elector = new ZkLeaderElector(zk, "/election", "session_1");

        List<Boolean> events = new ArrayList<>();
        elector.setOnLeadershipChange(events::add);

        elector.joinElection();

        assertTrue(elector.isLeader());
        assertEquals(1, events.size());
        assertTrue(events.get(0));
    }

    @Test
    public void testMultipleNodesElection() {
        ZkLeaderElector.ZkSimulator zk = new ZkLeaderElector.ZkSimulator();
        ZkLeaderElector elector1 = new ZkLeaderElector(zk, "/election", "session_1");
        ZkLeaderElector elector2 = new ZkLeaderElector(zk, "/election", "session_2");
        ZkLeaderElector elector3 = new ZkLeaderElector(zk, "/election", "session_3");

        elector1.joinElection();
        elector2.joinElection();
        elector3.joinElection();

        assertTrue(elector1.isLeader());
        assertFalse(elector2.isLeader());
        assertFalse(elector3.isLeader());

        // Node2 watches Node1, Node3 watches Node2
        assertEquals(1, zk.getWatchCount(elector1.getNodePath()));
        assertEquals(1, zk.getWatchCount(elector2.getNodePath()));
    }

    @Test
    public void testLeaderFailover() {
        ZkLeaderElector.ZkSimulator zk = new ZkLeaderElector.ZkSimulator();
        ZkLeaderElector elector1 = new ZkLeaderElector(zk, "/election", "session_1");
        ZkLeaderElector elector2 = new ZkLeaderElector(zk, "/election", "session_2");

        elector1.joinElection();
        elector2.joinElection();

        assertTrue(elector1.isLeader());
        assertFalse(elector2.isLeader());

        zk.expireSession("session_1");

        assertTrue(elector2.isLeader());
    }

    @Test
    public void testThunderingHerdPrevention() {
        ZkLeaderElector.ZkSimulator zk = new ZkLeaderElector.ZkSimulator();
        List<ZkLeaderElector> electors = new ArrayList<>();

        for (int i = 0; i < 5; i++) {
            ZkLeaderElector elector = new ZkLeaderElector(zk, "/election", "session_" + i);
            electors.add(elector);
            elector.joinElection();
        }

        assertTrue(electors.get(0).isLeader());
        for (int i = 1; i < 5; i++) {
            assertFalse(electors.get(i).isLeader());
        }

        for (int i = 1; i < 5; i++) {
            String watchedPath = electors.get(i - 1).getNodePath();
            assertEquals(1, zk.getWatchCount(watchedPath));
        }

        zk.expireSession("session_0");

        assertTrue(electors.get(1).isLeader());
        for (int i = 2; i < 5; i++) {
            assertFalse(electors.get(i).isLeader());
        }
    }
}
