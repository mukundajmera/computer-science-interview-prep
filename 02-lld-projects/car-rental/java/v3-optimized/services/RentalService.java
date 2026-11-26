import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.*;

public class RentalService {
    private static RentalService instance;
    
    private final Map<String, Vehicle> vehicles;
    private final Map<String, Customer> customers;
    private final Map<String, Reservation> reservations;
    private final Map<String, Branch> branches;

    private final Map<VehicleType, Double> demandMultipliers = new HashMap<>();

    public void updateDemand(VehicleType type, double multiplier) {
        demandMultipliers.put(type, multiplier);
    }


    private RentalService() {
        vehicles = new HashMap<>();
        customers = new HashMap<>();
        reservations = new HashMap<>();
        branches = new HashMap<>();
    }

    public static RentalService getInstance() {
        if (instance == null) {
            instance = new RentalService();
        }
        return instance;
    }

    public static void resetInstance() {
        instance = null;
    }

    
    public void addBranch(Branch branch) {
        branches.put(branch.getBranchId(), branch);
    }

    public Branch getBranch(String branchId) {
        return branches.get(branchId);
    }

    public void transferVehicle(Vehicle vehicle, Branch targetBranch) {
        if (!vehicle.isAvailable()) {
            throw new IllegalStateException("Cannot transfer a vehicle that is not available");
        }
        vehicle.setCurrentBranch(targetBranch);
    }
    
    public double calculateSurgeMultiplier(Branch branch, VehicleType type, LocalDate startDate, LocalDate endDate) {
        if (branch == null) return 1.0;
        
        long totalInBranch = 0;
        long availableInBranch = 0;
        
        for (Vehicle v : vehicles.values()) {
            if (v.getType() == type && branch.equals(v.getCurrentBranch())) {
                totalInBranch++;
                if (v.isAvailableForDates(startDate, endDate)) {
                    availableInBranch++;
                }
            }
        }
        
        if (totalInBranch == 0) return 1.0;
        
        double manualDemand = demandMultipliers.getOrDefault(type, 1.0);
        double availabilityRatio = (double) availableInBranch / totalInBranch;
        
        double inventorySurge = 1.0;
        if (availabilityRatio <= 0.20) {
            inventorySurge = 1.5;
        } else if (availabilityRatio <= 0.50) {
            inventorySurge = 1.2;
        }
        return Math.max(inventorySurge, manualDemand);
    }

    public void addVehicle(Vehicle vehicle) {
        vehicles.put(vehicle.getVehicleId(), vehicle);
    }

    public Customer registerCustomer(String customerId, String name, 
                                     String email, String phone, String drivingLicense) {
        Customer customer = new Customer(customerId, name, email, phone, drivingLicense);
        customers.put(customerId, customer);
        return customer;
    }

    public List<Vehicle> searchAvailable(VehicleType type, LocalDate startDate, LocalDate endDate) {
        List<Vehicle> available = new ArrayList<>();
        for (Vehicle v : vehicles.values()) {
            if (v.isAvailableForDates(startDate, endDate) && v.getType() == type) {
                available.add(v);
            }
        }
        return available;
    }

    public List<Vehicle> searchAvailable(VehicleType type) {
        List<Vehicle> available = new ArrayList<>();
        for (Vehicle v : vehicles.values()) {
            if (v.isAvailable() && v.getType() == type) {
                available.add(v);
            }
        }
        return available;
    }

    public List<Vehicle> searchAvailableByPriceRange(double minPrice, double maxPrice) {
        List<Vehicle> available = new ArrayList<>();
        for (Vehicle v : vehicles.values()) {
            if (v.isAvailable() && v.getBasePrice() >= minPrice && v.getBasePrice() <= maxPrice) {
                available.add(v);
            }
        }
        return available;
    }

    public PricingStrategy selectPricingStrategy(LocalDate startDate, LocalDate endDate) {
        long days = ChronoUnit.DAYS.between(startDate, endDate);
        if (days < 1) return new HourlyPricing();
        if (days >= 7) return new WeeklyPricing();
        return new DailyPricing();
    }

    public synchronized Reservation makeReservation(Customer customer, Vehicle vehicle,
                                       LocalDate startDate, LocalDate endDate,
                                       InsuranceType insurance) {
        if (!vehicle.isAvailableForDates(startDate, endDate)) {
            throw new IllegalStateException("Vehicle is not available for the requested dates");
        }

        double surgeMultiplier = calculateSurgeMultiplier(vehicle.getCurrentBranch(), vehicle.getType(), startDate, endDate);
        PricingStrategy strategy = selectPricingStrategy(startDate, endDate);
        Reservation reservation = new Reservation(customer, vehicle, startDate, endDate, 
                                                   insurance, strategy, surgeMultiplier);
        reservation.confirm();
        customer.addReservation(reservation);
        reservations.put(reservation.getReservationId(), reservation);
        return reservation;
    }

    public void pickupVehicle(Reservation reservation) {
        reservation.startRental();
    }

    public void returnVehicle(Reservation reservation, int milesDriven, DamageReport damage, LocalDate actualReturnDate) {
        reservation.complete(milesDriven, damage, actualReturnDate);
    }
    
    public void returnVehicle(Reservation reservation, int milesDriven, DamageReport damage) {
        reservation.complete(milesDriven, damage, reservation.getEndDate());
    }

    public DamageReport reportDamage(Vehicle vehicle, String description, DamageSeverity severity) {
        return new DamageReport(vehicle, description, severity);
    }

    public void cancelReservation(Reservation reservation) {
        reservation.cancel();
    }

    public Vehicle getVehicle(String vehicleId) {
        return vehicles.get(vehicleId);
    }

    public Customer getCustomer(String customerId) {
        return customers.get(customerId);
    }

    public Reservation getReservation(String reservationId) {
        return reservations.get(reservationId);
    }

    public Collection<Vehicle> getAllVehicles() {
        return new ArrayList<>(vehicles.values());
    }
}
