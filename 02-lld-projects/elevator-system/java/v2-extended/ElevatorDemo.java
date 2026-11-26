import models.Elevator;
import system.ElevatorSystem;
import enums.Direction;
import java.util.*;

public class ElevatorDemo {
    public static void main(String[] args) {
        System.out.println("=== Elevator System V2 Demo ===\n");

        ElevatorSystem.resetInstance();
        ElevatorSystem system = ElevatorSystem.getInstance(15, 3);

        // Add observer
        system.addObserverToAll(new DisplayPanel("Lobby"));

        // Set SCAN dispatcher
        system.setDispatcher(new SCANDispatcher());

        system.displayStatus();

        // Requests from different floors
        System.out.println("\n--- Multiple Requests ---");
        system.requestElevator(5, Direction.UP);
        system.requestElevator(10, Direction.DOWN);
        system.requestElevator(3, Direction.UP);

        // Run simulation
        for (int i = 0; i < 15; i++) {
            system.step();
        }

        // Internal destination selections
        system.selectDestination(1, 12);
        system.selectDestination(2, 1);

        for (int i = 0; i < 15; i++) {
            system.step();
        }

        system.displayStatus();

        System.out.println("\n=== Demo Complete ===");
    }
}
