package enums;

/**
 * Direction.java - Movement direction for elevators.
 * 
 * DESIGN PATTERN: Enumeration
 * Simple enum representing elevator movement state.
 * 
 * INTERVIEW TIP: Keep enums simple and focused.
 * Use NONE to represent idle state clearly.
 */
public enum Direction {
    UP, // Moving toward higher floors
    DOWN, // Moving toward lower floors
    NONE // Elevator is idle, not moving
}
