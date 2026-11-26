package models;

import enums.Direction;

/**
 * Request.java - Represents an elevator call request.
 * 
 * DESIGN CONCEPTS:
 * - Immutable object (all fields final)
 * - Two types: External (floor button) vs Internal (inside elevator)
 * 
 * EXTERNAL REQUEST: User presses UP/DOWN button on floor
 * - sourceFloor: Where the user is
 * - direction: Which way they want to go
 * - destinationFloor: -1 (unknown until they enter elevator)
 * 
 * INTERNAL REQUEST: User selects floor inside elevator
 * - sourceFloor: Current floor when pressed
 * - destinationFloor: Where they want to go
 * - direction: Computed from source -> destination
 * 
 * INTERVIEW TIP: Discuss why requests are immutable.
 * Answer: Thread safety, easier debugging, predictable state.
 */
public class Request {
    private final int sourceFloor;
    private final int destinationFloor;
    private final Direction direction;
    private final long timestamp;

    /**
     * External request - user pressed button on a floor.
     * 
     * @param sourceFloor Floor where button was pressed
     * @param direction   UP or DOWN (which button)
     */
    public Request(int sourceFloor, Direction direction) {
        this.sourceFloor = sourceFloor;
        this.destinationFloor = -1; // Unknown for external requests
        this.direction = direction;
        this.timestamp = System.currentTimeMillis();
    }

    /**
     * Internal request - user selected destination inside elevator.
     * 
     * @param sourceFloor      Current elevator floor
     * @param destinationFloor Target floor selected
     */
    public Request(int sourceFloor, int destinationFloor) {
        this.sourceFloor = sourceFloor;
        this.destinationFloor = destinationFloor;
        this.direction = destinationFloor > sourceFloor ? Direction.UP : Direction.DOWN;
        this.timestamp = System.currentTimeMillis();
    }

    // ============ Getters (no setters - immutable) ============

    public int getSourceFloor() {
        return sourceFloor;
    }

    public int getDestinationFloor() {
        return destinationFloor;
    }

    public Direction getDirection() {
        return direction;
    }

    public long getTimestamp() {
        return timestamp;
    }

    /**
     * Check if this is an external request (button on floor).
     */
    public boolean isExternalRequest() {
        return destinationFloor == -1;
    }

    @Override
    public String toString() {
        return "Request[Floor:" + sourceFloor + ", Dir:" + direction + "]";
    }
}
