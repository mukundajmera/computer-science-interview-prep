import models.Elevator;
import system.ElevatorSystem;
import enums.Direction;
import java.util.*;

public class ElevatorDemo {
    public static void main(String[] args) {
        System.out.println("=== Elevator System Demo ===\n");

        ElevatorSystem.resetInstance();
        ElevatorSystem system = ElevatorSystem.getInstance(10, 2);

        system.displayStatus();

        // Simulate requests
        System.out.println("\n--- Requesting Elevators ---");
        system.requestElevator(5, Direction.UP);
        system.requestElevator(3, Direction.DOWN);

        // Run simulation steps
        for (int i = 0; i < 10; i++) {
            system.step();
        }

        // Select destination inside elevator
        System.out.println("\n--- Selecting Destinations ---");
        system.selectDestination(1, 8);
        system.selectDestination(2, 1);

        // More steps
        for (int i = 0; i < 10; i++) {
            system.step();
        }

        system.displayStatus();

        System.out.println("\n=== Demo Complete ===");
    }
}
