package models;

import enums.Direction;
import enums.ElevatorState;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class ElevatorModelTest {
    @Test
    void stopsAndClearsDestinationOnTheArrivalTick() {
        Elevator elevator = new Elevator(1, 1, 10);
        elevator.addDestination(3);

        elevator.move();
        assertEquals(2, elevator.getCurrentFloor());
        assertTrue(elevator.hasDestinations());

        elevator.move();

        assertEquals(3, elevator.getCurrentFloor());
        assertFalse(elevator.hasDestinations());
        assertEquals(ElevatorState.IDLE, elevator.getState());
        assertEquals(Direction.NONE, elevator.getDirection());
    }
}
