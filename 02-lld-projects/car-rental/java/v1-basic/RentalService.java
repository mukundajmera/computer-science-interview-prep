import models.Customer;
import models.Reservation;
import models.Vehicle;
import enums.VehicleType;
import models.*;
import java.time.LocalDate;
import java.util.*;

/**
 * RentalService.java - Singleton car rental service.
 */
public class RentalService {
    private static RentalService instance;
    private final Map<String, Vehicle> vehicles;
    private final Map<String, Customer> customers;
    private final Map<String, Reservation> reservations;
    private int resCounter;

    private RentalService() {
        vehicles = new HashMap<>();
        customers = new HashMap<>();
        reservations = new HashMap<>();
        resCounter = 0;
    }

    public static synchronized RentalService getInstance() {
        if (instance == null)
            instance = new RentalService();
        return instance;
    }

    public void addVehicle(Vehicle v) {
        vehicles.put(v.getId(), v);
    }

    public void registerCustomer(Customer c) {
        customers.put(c.getId(), c);
    }

    public List<Vehicle> searchAvailable(VehicleType type) {
        List<Vehicle> available = new ArrayList<>();
        for (Vehicle v : vehicles.values()) {
            if (v.isAvailable() && (type == null || v.getType() == type)) {
                available.add(v);
            }
        }
        return available;
    }

    public Reservation makeReservation(String customerId, String vehicleId, LocalDate start, LocalDate end) {
        Customer customer = customers.get(customerId);
        Vehicle vehicle = vehicles.get(vehicleId);

        if (customer == null || vehicle == null || !vehicle.isAvailable()) {
            System.out.println("Invalid reservation");
            return null;
        }

        String id = "RES-" + (++resCounter);
        Reservation res = new Reservation(id, customer, vehicle, start, end);
        reservations.put(id, res);
        res.confirm();
        System.out.println("Reservation created: " + res);
        return res;
    }

    public void pickUp(String resId) {
        Reservation res = reservations.get(resId);
        if (res != null) {
            res.pickUp();
            System.out.println("Vehicle picked up: " + res.getVehicle());
        }
    }

    public void returnVehicle(String resId) {
        Reservation res = reservations.get(resId);
        if (res != null) {
            res.returnVehicle();
            System.out.printf("Vehicle returned. Total: $%.2f%n", res.getTotalCost());
        }
    }
}
