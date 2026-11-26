import models.Reservation;
import enums.InsuranceType;
import models.Customer;
import enums.VehicleType;
import models.Branch;
import models.MaintenanceWindow;
import models.Vehicle;
import java.time.LocalDate;

public class CarRentalDemo {
    public static void main(String[] args) {
        System.out.println("=== Car Rental V3 (Optimized) Demo ===\n");
        
        RentalService.resetInstance();
        RentalService service = RentalService.getInstance();
        
        // Setup Branches
        Branch downtown = new Branch("B1", "Downtown Branch", "123 Main St");
        Branch airport = new Branch("B2", "Airport Branch", "Terminal 1");
        service.addBranch(downtown);
        service.addBranch(airport);
        
        // Add vehicles and assign to branches
        Vehicle v1 = new Vehicle("V1", "ABC-123", "Toyota", "Camry", VehicleType.CAR, 50.0);
        Vehicle v2 = new Vehicle("V2", "DEF-456", "Honda", "CR-V", VehicleType.SUV, 60.0);
        Vehicle v3 = new Vehicle("V3", "GHI-789", "Honda", "CR-V", VehicleType.SUV, 60.0);
        Vehicle v4 = new Vehicle("V4", "JKL-012", "BMW", "X5", VehicleType.LUXURY, 80.0);
        
        service.addVehicle(v1);
        service.addVehicle(v2);
        service.addVehicle(v3);
        service.addVehicle(v4);
        
        service.transferVehicle(v1, downtown);
        service.transferVehicle(v2, downtown);
        service.transferVehicle(v3, downtown);
        service.transferVehicle(v4, airport);
        
        System.out.println("Vehicles assigned to branches:");
        for (Vehicle v : service.getAllVehicles()) {
            System.out.println("  " + v + " -> " + v.getCurrentBranch().getName());
        }
        
        // Register customers
        Customer john = service.registerCustomer("C1", "John Doe", "john@email.com", 
                                                  "555-1234", "DL123456");
        Customer jane = service.registerCustomer("C2", "Jane Smith", "jane@email.com", 
                                                  "555-5678", "DL654321");
                                                  
        System.out.println("\n--- 1. Inter-Branch Transfer ---");
        System.out.println("Transferring V4 (BMW X5) from Airport to Downtown...");
        service.transferVehicle(v4, downtown);
        System.out.println("V4 is now at: " + v4.getCurrentBranch().getName());
        
        System.out.println("\n--- 2. Scheduled Maintenance Window ---");
        LocalDate today = LocalDate.now();
        MaintenanceWindow window = new MaintenanceWindow(today.plusDays(10), today.plusDays(12), "Routine Oil Change");
        v1.scheduleMaintenance(window);
        System.out.println("Scheduled maintenance for V1 from " + window.getStartDate() + " to " + window.getEndDate());
        
        System.out.println("Attempting to reserve V1 during maintenance...");
        try {
            service.makeReservation(john, v1, today.plusDays(10), today.plusDays(11), InsuranceType.BASIC);
        } catch (IllegalStateException e) {
            System.out.println("Reservation failed correctly: " + e.getMessage());
        }
        
        System.out.println("\n--- 3. Dynamic Surge Pricing ---");
        // We have two SUVs at Downtown branch.
        System.out.println("Reserving first SUV (V2)...");
        Reservation res1 = service.makeReservation(john, v2, today, today.plusDays(2), InsuranceType.NONE);
        System.out.println("First SUV Base Rental Cost: $" + String.format("%.2f", res1.getRentalCost()));
        service.pickupVehicle(res1); // Now v2 is RENTED
        
        System.out.println("Only 1 out of 2 SUVs remaining at Downtown branch (50% availability).");
        System.out.println("Reserving second SUV (V3) - Surge pricing should apply...");
        Reservation res2 = service.makeReservation(jane, v3, today, today.plusDays(2), InsuranceType.NONE);
        System.out.println("Second SUV Base Rental Cost (Surge Applied): $" + String.format("%.2f", res2.getRentalCost()));
        
        System.out.println("\n=== Demo Complete ===");
    }
}
