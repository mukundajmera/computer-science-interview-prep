package models;

import enums.Direction;
import enums.ElevatorState;
import enums.DoorState;
import java.util.Set;
import java.util.TreeSet;

/**
 * Elevator.java - Core elevator entity with state machine behavior.
 * 
 * DESIGN PATTERNS USED:
 * 1. STATE PATTERN: ElevatorState enum controls behavior
 * 2. STRATEGY (implicit): Movement logic varies by state
 * 
 * KEY DATA STRUCTURE:
 * - TreeSet<Integer> for destinations
 * - WHY TreeSet?
 * -> O(log n) add/remove
 * -> Automatically sorted (efficient floor traversal)
 * -> No duplicates (same floor can't be added twice)
 * 
 * INTERVIEW TIP: Be ready to explain:
 * - Why TreeSet over ArrayList? (Sorted + O(log n))
 * - Why TreeSet over HashSet? (Need sorted order for SCAN algorithm)
 * - Thread safety? (Not safe - use ConcurrentSkipListSet in v3)
 * 
 * COMPLEXITY:
 * - addDestination(): O(log n)
 * - move(): O(log n) for higher()/lower() calls
 * - Space: O(n) where n = max pending destinations
 */
public class Elevator {
    private final int id;
    private int currentFloor;
    private ElevatorState state;
    private Direction direction;
    private final TreeSet<Integer> destinations; // Sorted destinations
    private DoorState doorState;
    private final int minFloor;
    private final int maxFloor;

    /**
     * Create elevator at ground floor (minFloor).
     * 
     * @param id       Unique elevator identifier
     * @param minFloor Lowest floor (typically 1 or 0)
     * @param maxFloor Highest floor in building
     */
    public Elevator(int id, int minFloor, int maxFloor) {
        this.id = id;
        this.currentFloor = minFloor;
        this.state = ElevatorState.IDLE;
        this.direction = Direction.NONE;
        this.destinations = new TreeSet<>();
        this.doorState = DoorState.CLOSED;
        this.minFloor = minFloor;
        this.maxFloor = maxFloor;
    }

    /**
     * Add a floor to visit.
     * 
     * VALIDATION:
     * - Floor must be within building bounds
     * - Can't add current floor (already there)
     * 
     * SIDE EFFECT: Updates direction if idle.
     * 
     * @param floor Target floor to add
     */
    public void addDestination(int floor) {
        if (floor >= minFloor && floor <= maxFloor && floor != currentFloor) {
            destinations.add(floor);
            updateDirection();
        }
    }

    /**
     * Update elevator direction based on pending destinations.
     * 
     * ALGORITHM:
     * - If no destinations -> IDLE, direction NONE
     * - If currently idle -> pick direction toward first destination
     * - Otherwise -> keep current direction
     */
    private void updateDirection() {
        if (destinations.isEmpty()) {
            direction = Direction.NONE;
            state = ElevatorState.IDLE;
        } else if (direction == Direction.NONE || state == ElevatorState.IDLE) {
            Integer next = destinations.first();
            direction = next > currentFloor ? Direction.UP : Direction.DOWN;
            state = direction == Direction.UP ? ElevatorState.MOVING_UP : ElevatorState.MOVING_DOWN;
        }
    }

    /**
     * Move elevator one step (one floor or stop).
     * 
     * ALGORITHM: SCAN (Elevator Algorithm)
     * 1. If current floor is a destination -> stop and open doors
     * 2. Else move one floor in current direction
     * 3. If no more floors in direction -> reverse
     * 
     * INTERVIEW TIP: Compare SCAN vs FCFS vs LOOK
     * - SCAN: Go all the way to end before reversing
     * - LOOK: Reverse at last request, not building end
     * - FCFS: First come first serve (inefficient)
     */
    public void move() {
        if (destinations.isEmpty()) {
            state = ElevatorState.IDLE;
            direction = Direction.NONE;
            return;
        }

        // Check if we should stop at current floor
        if (destinations.contains(currentFloor)) {
            stopAtCurrentFloor();
            return;
        }

        // Move one floor in current direction
        if (direction == Direction.UP) {
            moveUp();
        } else if (direction == Direction.DOWN) {
            moveDown();
        }

        if (destinations.contains(currentFloor)) {
            stopAtCurrentFloor();
        }
    }

    /**
     * Stop at current floor, open doors, remove from destinations.
     */
    private void stopAtCurrentFloor() {
        openDoor();
        destinations.remove(currentFloor);
        closeDoor();

        if (destinations.isEmpty()) {
            state = ElevatorState.IDLE;
            direction = Direction.NONE;
        }
    }

    /**
     * Move up one floor if possible.
     * Changes direction if no more floors above.
     */
    private void moveUp() {
        Integer higher = destinations.higher(currentFloor);
        if (higher != null) {
            currentFloor++;
            System.out.println("Elevator " + id + " moving UP to floor " + currentFloor);
        } else {
            // No higher floors, reverse direction
            direction = Direction.DOWN;
            state = ElevatorState.MOVING_DOWN;
        }
    }

    /**
     * Move down one floor if possible.
     * Changes direction if no more floors below.
     */
    private void moveDown() {
        Integer lower = destinations.lower(currentFloor);
        if (lower != null) {
            currentFloor--;
            System.out.println("Elevator " + id + " moving DOWN to floor " + currentFloor);
        } else {
            // No lower floors, reverse direction
            direction = Direction.UP;
            state = ElevatorState.MOVING_UP;
        }
    }

    /**
     * Open elevator doors.
     */
    public void openDoor() {
        doorState = DoorState.OPEN;
        state = ElevatorState.DOOR_OPEN;
        System.out.println("Elevator " + id + " doors OPEN at floor " + currentFloor);
    }

    /**
     * Close elevator doors.
     */
    public void closeDoor() {
        doorState = DoorState.CLOSED;
        updateDirection();
        System.out.println("Elevator " + id + " doors CLOSED");
    }

    // ============ State Queries ============

    public boolean isIdle() {
        return state == ElevatorState.IDLE;
    }

    public boolean hasDestinations() {
        return !destinations.isEmpty();
    }

    /**
     * Calculate distance to a floor.
     * Used by dispatcher to select optimal elevator.
     */
    public int distanceTo(int floor) {
        return Math.abs(currentFloor - floor);
    }

    // ============ Getters ============

    public int getId() {
        return id;
    }

    public int getCurrentFloor() {
        return currentFloor;
    }

    public ElevatorState getState() {
        return state;
    }

    public Direction getDirection() {
        return direction;
    }

    public Set<Integer> getDestinations() {
        return new TreeSet<>(destinations); // Return copy for encapsulation
    }

    @Override
    public String toString() {
        return "Elevator[" + id + ", Floor:" + currentFloor + ", State:" + state +
                ", Dir:" + direction + ", Dest:" + destinations + "]";
    }
}
