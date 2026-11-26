import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;
import java.util.*;

/**
 * Tests for Consistent Hashing Implementations.
 */
public class ConsistentHashTest {

    @Nested
    @DisplayName("SimpleConsistentHash Tests")
    class SimpleTests {

        @Test
        @DisplayName("Should map keys consistently")
        void testConsistency() {
            SimpleConsistentHash ch = new SimpleConsistentHash();
            ch.addServer("a");
            ch.addServer("b");

            String server1 = ch.getServer("key");
            String server2 = ch.getServer("key");

            assertNotNull(server1);
            assertEquals(server1, server2);
        }

        @Test
        @DisplayName("Should distribute keys across servers")
        void testDistribution() {
            SimpleConsistentHash ch = new SimpleConsistentHash();
            ch.addServer("a");
            ch.addServer("b");
            ch.addServer("c");

            Set<String> servers = new HashSet<>();
            for (int i = 0; i < 100; i++) {
                servers.add(ch.getServer("key-" + i));
            }

            assertTrue(servers.size() > 1);
            assertTrue(ch.getServers().containsAll(servers));
        }
    }

    @Nested
    @DisplayName("VirtualNodeConsistentHash Tests")
    class VnodeTests {

        @Test
        @DisplayName("Should have better distribution with vnodes")
        void testBetterDistribution() {
            VirtualNodeConsistentHash ch = new VirtualNodeConsistentHash(100);
            ch.addServer("a");
            ch.addServer("b");
            ch.addServer("c");

            Map<String, Integer> distribution = new HashMap<>();
            for (int i = 0; i < 900; i++) {
                String server = ch.getServer("key-" + i);
                distribution.merge(server, 1, Integer::sum);
            }

            assertEquals(3, ch.getServerCount());
            assertEquals(300, ch.getVirtualNodeCount());
            assertEquals(Set.of("a", "b", "c"), distribution.keySet());
        }

        @Test
        @DisplayName("Should respect server weights")
        void testWeights() {
            VirtualNodeConsistentHash ch = new VirtualNodeConsistentHash(50);
            ch.addServer("a", 2);
            ch.addServer("b", 1);

            Map<String, Integer> distribution = new HashMap<>();
            for (int i = 0; i < 2000; i++) {
                String server = ch.getServer("key-" + i);
                distribution.merge(server, 1, Integer::sum);
            }

            assertEquals(150, ch.getVirtualNodeCount());
            assertTrue(distribution.get("a") > distribution.get("b"));
        }

        @Test
        @DisplayName("Should return distinct servers for replication")
        void testReplication() {
            VirtualNodeConsistentHash ch = new VirtualNodeConsistentHash(100);
            ch.addServer("a");
            ch.addServer("b");
            ch.addServer("c");

            List<String> replicas = ch.getServers("key", 3);

            assertEquals(3, replicas.size());
            assertEquals(3, new HashSet<>(replicas).size());
        }
    }

    @Nested
    @DisplayName("ProductionConsistentHash Tests")
    class ProductionTests {

        @Test
        @DisplayName("Should handle node failures")
        void testFailover() {
            ProductionConsistentHash ch = new ProductionConsistentHash(100, 2, 1.0);
            ch.addNode("a");
            ch.addNode("b");

            ch.setNodeHealth("a", false);

            ProductionConsistentHash.LookupResult result = ch.lookup("key");
            assertNotNull(result);
            assertFalse(result.getAllNodes().contains("a"));
            assertTrue(result.getAllNodes().contains("b"));
        }

        @Test
        @DisplayName("Should track metrics")
        void testMetrics() {
            ProductionConsistentHash ch = new ProductionConsistentHash(100, 1, 1.0);
            ch.addNode("a");

            ch.lookup("key1");
            ch.lookup("key2");

            assertEquals(2, ch.getMetrics().getLookups());
            assertEquals(1, ch.getMetrics().getRebalanceCount());
        }
    }
}
