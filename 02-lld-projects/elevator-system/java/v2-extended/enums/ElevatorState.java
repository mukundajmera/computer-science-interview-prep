package enums;

/**
 * ElevatorState.java - State machine states for elevator.
 * 
 * DESIGN PATTERN: State Pattern
 * Each elevator transitions between these states during operation.
 * 
 * STATE TRANSITIONS:
 * IDLE --> MOVING_UP/DOWN --> DOOR_OPEN --> IDLE
 * | |
 * |---- MAINTENANCE <------------|
 * 
 * INTERVIEW TIP: State Pattern is commonly asked.
 * Explain how this replaces complex if-else chains.
 */
public enum ElevatorState {
    IDLE, // Elevator not moving, waiting for requests
    MOVING_UP, // Traveling to higher floor
    MOVING_DOWN, // Traveling to lower floor
    DOOR_OPEN // Stopped at floor, doors open for passengers
}
