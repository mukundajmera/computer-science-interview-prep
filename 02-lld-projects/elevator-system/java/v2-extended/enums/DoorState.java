package enums;

/**
 * DoorState.java - Physical door state.
 * 
 * Used for safety checks and timing.
 * Elevator cannot move unless doors are CLOSED.
 */
public enum DoorState {
    OPEN, // Doors fully open
    CLOSED // Doors fully closed
}
