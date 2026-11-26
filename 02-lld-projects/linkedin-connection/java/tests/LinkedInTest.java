package v2_extended;
import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;


/**
 * Unit tests for LinkedIn Connection System
 */
class LinkedInTest {

    @BeforeEach
    void setUp() {
        NetworkService.resetInstance();
    }

    @AfterEach
    void tearDown() {
        NetworkService.resetInstance();
    }

    @Test
    @DisplayName("User creation with valid data")
    void testUserCreation() {
        User user = new User("U001", "Alice", "alice@email.com");
        assertEquals("U001", user.getUserId());
        assertEquals("Alice", user.getName());
        assertEquals(0, user.getConnectionCount());
    }

    @Test
    @DisplayName("Connection between two users")
    void testAddConnection() {
        User alice = new User("U001", "Alice", "alice@email.com");
        User bob = new User("U002", "Bob", "bob@email.com");
        
        alice.addConnection(bob);
        bob.addConnection(alice);
        
        assertTrue(alice.isConnectedTo(bob));
        assertTrue(bob.isConnectedTo(alice));
    }

    @Test
    @DisplayName("Mutual connections calculation")
    void testMutualConnections() {
        User alice = new User("U001", "Alice", "alice@email.com");
        User bob = new User("U002", "Bob", "bob@email.com");
        User charlie = new User("U003", "Charlie", "charlie@email.com");
        
        alice.addConnection(bob);
        alice.addConnection(charlie);
        bob.addConnection(alice);
        bob.addConnection(charlie);
        charlie.addConnection(alice);
        charlie.addConnection(bob);
        
        var mutual = alice.getMutualConnections(bob);
        assertEquals(1, mutual.size());
        assertTrue(mutual.contains(charlie));
    }

    @Test
    @DisplayName("NetworkService singleton returns same instance")
    void testSingletonInstance() {
        NetworkService ns1 = NetworkService.getInstance();
        NetworkService ns2 = NetworkService.getInstance();
        assertSame(ns1, ns2);
    }

    @Test
    @DisplayName("Register user successfully")
    void testRegisterUser() {
        NetworkService network = NetworkService.getInstance();
        User alice = new User("U001", "Alice", "alice@email.com");
        
        assertTrue(network.registerUser(alice));
        assertEquals(alice, network.getUser("U001"));
    }

    @Test
    @DisplayName("Prevent duplicate user registration")
    void testDuplicateUserRegistration() {
        NetworkService network = NetworkService.getInstance();
        User alice1 = new User("U001", "Alice", "alice@email.com");
        User alice2 = new User("U001", "Alice Copy", "alice2@email.com");
        
        assertTrue(network.registerUser(alice1));
        assertFalse(network.registerUser(alice2));
    }

    @Test
    @DisplayName("Connection request workflow")
    void testConnectionRequest() {
        NetworkService network = NetworkService.getInstance();
        User alice = new User("U001", "Alice", "alice@email.com");
        User bob = new User("U002", "Bob", "bob@email.com");
        
        network.registerUser(alice);
        network.registerUser(bob);
        
        ConnectionRequest request = network.sendConnectionRequest("U001", "U002", "Hi!");
        
        assertNotNull(request);
        assertTrue(request.isPending());
        
        network.acceptRequest(request.getRequestId());
        
        assertTrue(network.areConnected("U001", "U002"));
    }

    @Test
    @DisplayName("Reject connection request")
    void testRejectRequest() {
        NetworkService network = NetworkService.getInstance();
        User alice = new User("U001", "Alice", "alice@email.com");
        User bob = new User("U002", "Bob", "bob@email.com");
        
        network.registerUser(alice);
        network.registerUser(bob);
        
        ConnectionRequest request = network.sendConnectionRequest("U001", "U002", null);
        network.rejectRequest(request.getRequestId());
        
        assertFalse(network.areConnected("U001", "U002"));
        assertEquals(RequestStatus.REJECTED, request.getStatus());
    }

    @Test
    @DisplayName("Cannot send duplicate request")
    void testDuplicateRequest() {
        NetworkService network = NetworkService.getInstance();
        User alice = new User("U001", "Alice", "alice@email.com");
        User bob = new User("U002", "Bob", "bob@email.com");
        
        network.registerUser(alice);
        network.registerUser(bob);
        
        ConnectionRequest req1 = network.sendConnectionRequest("U001", "U002", null);
        ConnectionRequest req2 = network.sendConnectionRequest("U001", "U002", null);
        
        assertNotNull(req1);
        assertNull(req2);
    }

    @Test
    @DisplayName("Cannot connect to self")
    void testSelfConnection() {
        NetworkService network = NetworkService.getInstance();
        User alice = new User("U001", "Alice", "alice@email.com");
        
        network.registerUser(alice);
        
        ConnectionRequest request = network.sendConnectionRequest("U001", "U001", null);
        assertNull(request);
    }

    @Test
    @DisplayName("Remove connection")
    void testRemoveConnection() {
        NetworkService network = NetworkService.getInstance();
        User alice = new User("U001", "Alice", "alice@email.com");
        User bob = new User("U002", "Bob", "bob@email.com");
        
        network.registerUser(alice);
        network.registerUser(bob);
        
        var req = network.sendConnectionRequest("U001", "U002", null);
        network.acceptRequest(req.getRequestId());
        
        assertTrue(network.areConnected("U001", "U002"));
        
        network.removeConnection("U001", "U002");
        
        assertFalse(network.areConnected("U001", "U002"));
    }

    @Test
    @DisplayName("Connection degree calculation")
    void testConnectionDegree() {
        NetworkService network = NetworkService.getInstance();
        User a = new User("A", "A", "a@email.com");
        User b = new User("B", "B", "b@email.com");
        User c = new User("C", "C", "c@email.com");
        User d = new User("D", "D", "d@email.com");
        
        network.registerUser(a);
        network.registerUser(b);
        network.registerUser(c);
        network.registerUser(d);
        
        // A - B - C - D
        var r1 = network.sendConnectionRequest("A", "B", null);
        var r2 = network.sendConnectionRequest("B", "C", null);
        var r3 = network.sendConnectionRequest("C", "D", null);
        
        network.acceptRequest(r1.getRequestId());
        network.acceptRequest(r2.getRequestId());
        network.acceptRequest(r3.getRequestId());
        
        assertEquals(1, network.getConnectionDegree("A", "B"));
        assertEquals(2, network.getConnectionDegree("A", "C"));
        assertEquals(3, network.getConnectionDegree("A", "D"));
    }

    @Test
    @DisplayName("Skill endorsement")
    void testSkillEndorsement() {
        NetworkService network = NetworkService.getInstance();
        User alice = new User("U001", "Alice", "alice@email.com");
        User bob = new User("U002", "Bob", "bob@email.com");
        
        alice.addSkill("Java");
        
        network.registerUser(alice);
        network.registerUser(bob);
        
        var req = network.sendConnectionRequest("U001", "U002", null);
        network.acceptRequest(req.getRequestId());
        
        assertTrue(network.endorseSkill("U002", "U001", "Java"));
        
        Skill javaSkill = alice.getSkill("Java");
        assertEquals(1, javaSkill.getEndorsementCount());
        assertTrue(javaSkill.isEndorsedBy(bob));
    }

    @Test
    @DisplayName("Cannot endorse non-connection")
    void testCannotEndorseNonConnection() {
        NetworkService network = NetworkService.getInstance();
        User alice = new User("U001", "Alice", "alice@email.com");
        User bob = new User("U002", "Bob", "bob@email.com");
        
        alice.addSkill("Java");
        
        network.registerUser(alice);
        network.registerUser(bob);
        
        assertFalse(network.endorseSkill("U002", "U001", "Java"));
    }
}
