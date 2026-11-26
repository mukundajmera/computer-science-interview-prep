import models.Customer;
import enums.VehicleType;
import models.Reservation;
import models.Vehicle;
import java.time.LocalDate;

public class CarRentalDemo {
    public static void main(String[] args) {
        System.out.println("=== Car Rental V2 (Extended) Demo ===\n");
        
        RentalService.resetInstance();
        RentalService service = RentalService.getInstance();
        
        // Add vehicles with type-based pricing
        service.addVehicle(new Vehicle("V1", "ABC-123", "Toyota", "Camry", VehicleType.CAR, 50.0));
        service.addVehicle(new Vehicle("V2", "DEF-456", "Honda", "CR-V", VehicleType.SUV, 60.0));
        service.addVehicle(new Vehicle("V3", "GHI-789", "Ford", "F-150", VehicleType.TRUCK, 55.0));
        service.addVehicle(new Vehicle("V4", "JKL-012", "BMW", "X5", VehicleType.LUXURY, 80.0));
        
        System.out.println("Vehicles added:");
        for (Vehicle v : service.getAllVehicles()) {
            System.out.println("  " + v);
        }
        
        // Register customer
        Customer john = service.registerCustomer("C1", "John Doe", "john@email.com", 
                                                  "555-1234", "DL123456");
        System.out.println("\nCustomer registered: " + john.getName());
        
        // Search for luxury vehicles
        System.out.println("\n--- Available Luxury Vehicles ---");
        var luxuryVehicles = service.searchAvailable(VehicleType.LUXURY);
        for (Vehicle v : luxuryVehicles) {
            System.out.println("  " + v);
        }
        
        // Make reservation with premium insurance
        Vehicle bmw = luxuryVehicles.get(0);
        LocalDate start = LocalDate.now();
        LocalDate end = start.plusDays(7); // Weekly rental
        
        Reservation reservation = service.makeReservation(john, bmw, start, end, 
                                                           InsuranceType.PREMIUM);
        
        System.out.println("\n--- Reservation Details ---");
        System.out.println("ID: " + reservation.getReservationId());
        System.out.println("Vehicle: " + bmw);
        System.out.println("Insurance: " + reservation.getInsurance());
        System.out.println("Rental Cost: $" + String.format("%.2f", reservation.getRentalCost()));
        System.out.println("Insurance Cost: $" + String.format("%.2f", reservation.getInsuranceCost()));
        System.out.println("Total Cost: $" + String.format("%.2f", reservation.getTotalCost()));
        
        // Pickup
        service.pickupVehicle(reservation);
        System.out.println("\n--- Vehicle Picked Up ---");
        System.out.println("Status: " + reservation.getStatus());
        
        // Return with damage
        DamageReport damage = service.reportDamage(bmw, "Minor scratch on rear bumper", 
                                                    DamageSeverity.MINOR);
        service.returnVehicle(reservation, 500, damage);
        
        System.out.println("\n--- Vehicle Returned ---");
        System.out.println("Status: " + reservation.getStatus());
        System.out.println("Miles driven: 500");
        System.out.println("Damage: " + damage.getDescription());
        System.out.println("Damage severity: " + damage.getSeverity());
        System.out.println("Damage cost (before insurance): $" + damage.getEstimatedCost());
        System.out.println("Damage cost (customer pays): $" + reservation.getDamageCost());
        System.out.println("Final Total: $" + String.format("%.2f", reservation.getTotalCost()));
        
        // Process payment
        reservation.processPayment("Credit Card");
        System.out.println("\n--- Payment Processed ---");
        System.out.println("Payment ID: " + reservation.getPayment().getPaymentId());
        System.out.println("Amount: $" + reservation.getPayment().getAmount());
        System.out.println("Status: " + reservation.getPayment().getStatus());
        
        System.out.println("\n=== Demo Complete ===");
    }
}
