import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;
import java.util.*;

/**
 * Unit tests for Elevator System
 */
class ElevatorTest {

    @BeforeEach
    void setUp() {
        ElevatorSystem.resetInstance();
    }

    @AfterEach
    void tearDown() {
        ElevatorSystem.resetInstance();
    }

    @Test
    @DisplayName("Elevator starts idle at floor 1")
    void testElevatorInitialState() {
        Elevator elevator = new Elevator(1, 1, 10);
        
        assertEquals(1, elevator.getCurrentFloor());
        assertEquals(ElevatorState.IDLE, elevator.getState());
        assertEquals(Direction.NONE, elevator.getDirection());
        assertTrue(elevator.isIdle());
    }

    @Test
    @DisplayName("Elevator adds destination and starts moving")
    void testAddDestination() {
        Elevator elevator = new Elevator(1, 1, 10);
        
        elevator.addDestination(5);
        
        assertFalse(elevator.isIdle());
        assertEquals(Direction.UP, elevator.getDirection());
    }

    @Test
    @DisplayName("Elevator moves toward destination")
    void testElevatorMove() {
        Elevator elevator = new Elevator(1, 1, 10);
        elevator.addDestination(5);
        
        int initialFloor = elevator.getCurrentFloor();
        elevator.move();
        
        assertEquals(initialFloor + 1, elevator.getCurrentFloor());
    }

    @Test
    @DisplayName("Elevator stops at destination floor")
    void testElevatorStopsAtDestination() {
        Elevator elevator = new Elevator(1, 1, 10);
        elevator.addDestination(3);
        
        // Move to floor 3
        while (elevator.getCurrentFloor() != 3) {
            elevator.move();
        }
        
        // Elevator should have stopped and removed destination
        assertFalse(elevator.hasDestinations());
    }

    @Test
    @DisplayName("ElevatorSystem singleton returns same instance")
    void testSingleton() {
        ElevatorSystem sys1 = ElevatorSystem.getInstance(10, 2);
        ElevatorSystem sys2 = ElevatorSystem.getInstance(10, 2);
        
        assertSame(sys1, sys2);
    }

    @Test
    @DisplayName("System handles external request")
    void testExternalRequest() {
        ElevatorSystem system = ElevatorSystem.getInstance(10, 2);
        
        system.requestElevator(5, Direction.UP);
        
        // At least one elevator should have a destination
        boolean hasDestination = false;
        for (Elevator e : system.getElevators()) {
            if (e.hasDestinations()) {
                hasDestination = true;
                break;
            }
        }
        assertTrue(hasDestination);
    }

    @Test
    @DisplayName("System handles internal destination selection")
    void testInternalDestination() {
        ElevatorSystem system = ElevatorSystem.getInstance(10, 2);
        
        system.selectDestination(1, 8);
        
        Elevator elevator1 = system.getElevators().get(0);
        assertTrue(elevator1.hasDestinations());
    }

    @Test
    @DisplayName("Elevator distance calculation is correct")
    void testDistanceCalculation() {
        Elevator elevator = new Elevator(1, 1, 10);
        
        assertEquals(4, elevator.distanceTo(5));
        assertEquals(0, elevator.distanceTo(1));
    }

    @Test
    @DisplayName("Elevator changes direction when needed")
    void testDirectionChange() {
        Elevator elevator = new Elevator(1, 1, 10);
        
        // Start going up
        elevator.addDestination(5);
        assertEquals(Direction.UP, elevator.getDirection());
        
        // Move to floor 5
        for (int i = 0; i < 10; i++) {
            elevator.move();
            if (!elevator.hasDestinations()) break;
        }
        
        // Should be idle now
        assertTrue(elevator.isIdle());
        
        // Add down destination
        elevator.addDestination(2);
        assertEquals(Direction.DOWN, elevator.getDirection());
    }

    @Test
    @DisplayName("Invalid floor requests are ignored")
    void testInvalidFloorRequest() {
        ElevatorSystem system = ElevatorSystem.getInstance(10, 2);
        
        // Should not throw
        system.requestElevator(0, Direction.UP);
        system.requestElevator(11, Direction.UP);
        system.selectDestination(1, 0);
        system.selectDestination(1, 11);
        
        // All elevators should still be idle
        for (Elevator e : system.getElevators()) {
            assertTrue(e.isIdle());
        }
    }

    @Test
    @DisplayName("Step advances elevator simulation")
    void testStep() {
        ElevatorSystem system = ElevatorSystem.getInstance(10, 1);
        
        system.requestElevator(5, Direction.UP);
        Elevator elevator = system.getElevators().get(0);
        
        int initialFloor = elevator.getCurrentFloor();
        system.step();
        
        // Elevator should have moved
        assertNotEquals(initialFloor, elevator.getCurrentFloor());
    }
}
