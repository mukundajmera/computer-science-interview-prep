package v3_optimized;

/**
 * Parking Lot System - V1 Basic Demo
 * 
 * Demonstrates the basic functionality of the parking lot system.
 */
public class ParkingDemo {
    public static void main(String[] args) {
        System.out.println("=== Parking Lot System Demo ===\n");

        // Reset and get parking lot instance
        ParkingLot.resetInstance();
        ParkingLot parkingLot = ParkingLot.getInstance("Downtown Parking");

        // Add floors with different spot configurations
        // Floor 1: 10 motorcycle, 20 compact, 5 large spots
        parkingLot.addFloor(10, 20, 5);
        // Floor 2: 10 motorcycle, 20 compact, 5 large spots
        parkingLot.addFloor(10, 20, 5);

        // Display initial status
        parkingLot.displayStatus();

        // Create some vehicles
        Vehicle car1 = VehicleFactory.createVehicle(VehicleType.CAR, "CAR-001");
        Vehicle car2 = VehicleFactory.createVehicle(VehicleType.CAR, "CAR-002");
        Vehicle motorcycle1 = VehicleFactory.createVehicle(VehicleType.MOTORCYCLE, "MOTO-001");
        Vehicle truck1 = VehicleFactory.createVehicle(VehicleType.TRUCK, "TRUCK-001");

        System.out.println("\n--- Parking Vehicles ---\n");

        // Park vehicles
        Ticket ticket1 = parkingLot.parkVehicle(car1);
        Ticket ticket2 = parkingLot.parkVehicle(car2);
        Ticket ticket3 = parkingLot.parkVehicle(motorcycle1);
        Ticket ticket4 = parkingLot.parkVehicle(truck1);

        // Display tickets
        System.out.println("\n--- Issued Tickets ---");
        System.out.println(ticket1);
        System.out.println(ticket2);
        System.out.println(ticket3);
        System.out.println(ticket4);

        // Find a vehicle
        System.out.println("\n--- Finding Vehicle ---");
        ParkingSpot foundSpot = parkingLot.findVehicle("CAR-001");
        if (foundSpot != null) {
            System.out.println("Found CAR-001 at: " + foundSpot.getSpotId());
        }

        // Display status after parking
        parkingLot.displayStatus();

        // Try to park the same vehicle again
        System.out.println("\n--- Attempting Double Park ---");
        Ticket duplicateTicket = parkingLot.parkVehicle(car1);
        System.out.println("Duplicate ticket: " + duplicateTicket);

        // Unpark a vehicle
        System.out.println("\n--- Unparking Vehicle ---");
        double fee = parkingLot.unparkVehicle(ticket1);
        System.out.println("Paid fee: $" + String.format("%.2f", fee));

        // Display final status
        parkingLot.displayStatus();

        // Unpark remaining vehicles
        System.out.println("\n--- Unparking Remaining Vehicles ---");
        parkingLot.unparkVehicle(ticket2);
        parkingLot.unparkVehicle(ticket3);
        parkingLot.unparkVehicle(ticket4);

        // Final status
        parkingLot.displayStatus();

        System.out.println("\n=== Demo Complete ===");
    }
}
