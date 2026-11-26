package system;

import enums.Direction;
import models.Elevator;
import models.Request;
import java.util.*;

/**
 * ElevatorSystem.java - Central controller managing all elevators.
 * 
 * DESIGN PATTERN: SINGLETON
 * - One system per building
 * - Global access via getInstance()
 * - Centralized request handling
 * 
 * WHY SINGLETON?
 * - Single source of truth for elevator state
 * - Prevents conflicting dispatches
 * - Easy access from floor panels and elevator buttons
 * 
 * INTERVIEW TIP: Discuss Singleton alternatives:
 * - Dependency Injection (preferred in modern apps)
 * - But Singleton is fine for this bounded context
 * 
 * THREAD SAFETY (v1):
 * - synchronized getInstance() for lazy init
 * - NOT thread-safe for operations (see v3 for concurrent version)
 * 
 * DISPATCHING ALGORITHM:
 * v1 uses simple "nearest elevator" strategy.
 * See v2/v3 for Strategy pattern with pluggable dispatchers.
 */
public class ElevatorSystem {
    private static ElevatorSystem instance;

    private final int numFloors;
    private final List<Elevator> elevators;
    private final Queue<Request> pendingRequests;

    /**
     * Private constructor - enforces Singleton.
     * 
     * @param numFloors    Total floors in building
     * @param numElevators Number of elevators to create
     */
    private ElevatorSystem(int numFloors, int numElevators) {
        this.numFloors = numFloors;
        this.elevators = new ArrayList<>();
        this.pendingRequests = new LinkedList<>();

        // Create elevators starting at ground floor
        for (int i = 0; i < numElevators; i++) {
            elevators.add(new Elevator(i + 1, 1, numFloors));
        }
    }

    /**
     * Get singleton instance.
     * THREAD SAFETY: synchronized for lazy initialization.
     */
    public static synchronized ElevatorSystem getInstance(int numFloors, int numElevators) {
        if (instance == null) {
            instance = new ElevatorSystem(numFloors, numElevators);
        }
        return instance;
    }

    /**
     * Reset for testing - allows creating fresh instance.
     */
    public static synchronized void resetInstance() {
        instance = null;
    }

    // ============ Public API ============

    /**
     * External request - user pressed UP/DOWN button on floor.
     * 
     * FLOW:
     * 1. Validate floor
     * 2. Create Request object
     * 3. Select best elevator
     * 4. Assign or queue request
     * 
     * @param floor     The floor where button was pressed
     * @param direction UP or DOWN
     */
    public void requestElevator(int floor, Direction direction) {
        if (!isValidFloor(floor)) {
            System.out.println("Invalid floor: " + floor);
            return;
        }

        Request request = new Request(floor, direction);
        System.out.println("Request received: " + request);

        Elevator selectedElevator = selectElevator(floor, direction);
        if (selectedElevator != null) {
            selectedElevator.addDestination(floor);
            System.out.println("Assigned to Elevator " + selectedElevator.getId());
        } else {
            pendingRequests.offer(request);
            System.out.println("Request queued - all elevators busy");
        }
    }

    /**
     * Internal request - user selected floor inside elevator.
     * 
     * @param elevatorId Which elevator
     * @param floor      Destination floor
     */
    public void selectDestination(int elevatorId, int floor) {
        if (!isValidFloor(floor)) {
            System.out.println("Invalid floor: " + floor);
            return;
        }

        for (Elevator elevator : elevators) {
            if (elevator.getId() == elevatorId) {
                elevator.addDestination(floor);
                System.out.println("Elevator " + elevatorId + " destination added: floor " + floor);
                return;
            }
        }
        System.out.println("Elevator not found: " + elevatorId);
    }

    // ============ Dispatching Logic ============

    /**
     * Select best elevator for a request.
     * 
     * ALGORITHM (v1 - Simple Nearest):
     * 1. Prefer IDLE elevators (pick nearest)
     * 2. Consider elevators moving TOWARD the floor in same direction
     * 3. If none suitable, return null (request will be queued)
     * 
     * INTERVIEW TIP: Discuss trade-offs:
     * - Nearest: Simple but may not be optimal
     * - SCAN: Better for high traffic
     * - LOOK: Optimized SCAN
     * 
     * COMPLEXITY: O(E) where E = number of elevators
     */
    private Elevator selectElevator(int floor, Direction direction) {
        Elevator best = null;
        int minDistance = Integer.MAX_VALUE;

        // First pass: find suitable elevator
        for (Elevator elevator : elevators) {
            int distance = elevator.distanceTo(floor);

            // Prefer idle elevators
            if (elevator.isIdle() && distance < minDistance) {
                best = elevator;
                minDistance = distance;
            }
            // Or elevators moving toward the floor in same direction
            else if (elevator.getDirection() == direction) {
                boolean isApproaching = (direction == Direction.UP && elevator.getCurrentFloor() <= floor) ||
                        (direction == Direction.DOWN && elevator.getCurrentFloor() >= floor);

                if (isApproaching && distance < minDistance) {
                    best = elevator;
                    minDistance = distance;
                }
            }
        }

        // Fallback: any idle elevator
        if (best == null) {
            for (Elevator elevator : elevators) {
                if (elevator.isIdle()) {
                    int distance = elevator.distanceTo(floor);
                    if (distance < minDistance) {
                        best = elevator;
                        minDistance = distance;
                    }
                }
            }
        }

        return best;
    }

    // ============ Simulation ============

    /**
     * Advance simulation by one time step.
     * 
     * FLOW:
     * 1. Try to assign pending requests
     * 2. Move each elevator one floor
     * 
     * INTERVIEW TIP: Discuss real vs simulated time
     * - Real system: event-driven with actual delays
     * - Simulation: discrete time steps for testing
     */
    public void step() {
        System.out.println("\n--- Step ---");

        // Process pending requests
        processPendingRequests();

        // Move each elevator
        for (Elevator elevator : elevators) {
            elevator.move();
        }
    }

    /**
     * Try to assign queued requests to available elevators.
     */
    private void processPendingRequests() {
        while (!pendingRequests.isEmpty()) {
            Request request = pendingRequests.peek();
            Elevator elevator = selectElevator(request.getSourceFloor(), request.getDirection());

            if (elevator != null) {
                elevator.addDestination(request.getSourceFloor());
                pendingRequests.poll();
            } else {
                break; // No available elevator, keep in queue
            }
        }
    }

    // ============ Utility ============

    private boolean isValidFloor(int floor) {
        return floor >= 1 && floor <= numFloors;
    }

    public void displayStatus() {
        System.out.println("\n=== Elevator System Status ===");
        System.out.println("Floors: " + numFloors);
        System.out.println("Pending Requests: " + pendingRequests.size());
        for (Elevator elevator : elevators) {
            System.out.println(elevator);
        }
    }

    // ============ Getters ============

    public int getNumFloors() {
        return numFloors;
    }

    public int getNumElevators() {
        return elevators.size();
    }

    public List<Elevator> getElevators() {
        return new ArrayList<>(elevators); // Return copy
    }
}
