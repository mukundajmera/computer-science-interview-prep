import models.Customer;
import enums.VehicleType;
import models.Reservation;
import models.Vehicle;
import java.time.LocalDate;

public class CarRentalDemo {
    public static void main(String[] args) {
        System.out.println("=== Car Rental V1 (Basic) Demo ===\n");
        
        RentalService.resetInstance();
        RentalService service = RentalService.getInstance();
        
        // Add vehicles
        service.addVehicle(new Vehicle("V1", "ABC-123", "Toyota", "Camry", VehicleType.CAR, 50.0));
        service.addVehicle(new Vehicle("V2", "DEF-456", "Honda", "CR-V", VehicleType.SUV, 75.0));
        service.addVehicle(new Vehicle("V3", "GHI-789", "Ford", "F-150", VehicleType.TRUCK, 85.0));
        service.addVehicle(new Vehicle("V4", "JKL-012", "BMW", "X5", VehicleType.LUXURY, 150.0));
        
        System.out.println("Vehicles added to inventory");
        
        // Register customer
        Customer john = service.registerCustomer("C1", "John Doe", "john@email.com", "DL123456");
        System.out.println("Customer registered: " + john.getName());
        
        // Search for available SUVs
        System.out.println("\n--- Searching for SUVs ---");
        var availableSUVs = service.searchAvailable(VehicleType.SUV);
        for (Vehicle v : availableSUVs) {
            System.out.println("  Available: " + v);
        }
        
        // Make reservation
        Vehicle suv = availableSUVs.get(0);
        LocalDate start = LocalDate.now();
        LocalDate end = start.plusDays(5);
        
        Reservation reservation = service.makeReservation(john, suv, start, end);
        System.out.println("\n--- Reservation Created ---");
        System.out.println("Reservation ID: " + reservation.getReservationId());
        System.out.println("Vehicle: " + reservation.getVehicle());
        System.out.println("Duration: " + start + " to " + end);
        System.out.println("Total Cost: $" + reservation.getTotalCost());
        System.out.println("Status: " + reservation.getStatus());
        
        // Check vehicle is no longer available
        System.out.println("\n--- After Reservation ---");
        System.out.println("Vehicle status: " + suv.getStatus());
        System.out.println("Available SUVs: " + service.searchAvailable(VehicleType.SUV).size());
        
        // Pickup vehicle
        service.pickupVehicle(reservation);
        System.out.println("\n--- After Pickup ---");
        System.out.println("Reservation status: " + reservation.getStatus());
        System.out.println("Vehicle status: " + suv.getStatus());
        
        // Return vehicle
        service.returnVehicle(reservation);
        System.out.println("\n--- After Return ---");
        System.out.println("Reservation status: " + reservation.getStatus());
        System.out.println("Vehicle status: " + suv.getStatus());
        System.out.println("Available SUVs: " + service.searchAvailable(VehicleType.SUV).size());
        
        System.out.println("\n=== Demo Complete ===");
    }
}
