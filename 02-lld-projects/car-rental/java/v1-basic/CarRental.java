import enums.ReservationStatus;
import models.Reservation;
import models.Customer;
import enums.VehicleType;
import models.Vehicle;
import java.time.LocalDate;
import java.time.temporal.ChronoUnit;
import java.util.*;

/**
 * Car Rental System - V1 Basic
 * 
 * Core implementation with vehicles, customers, and reservations.
 */

enum VehicleType {
    CAR, SUV, TRUCK, VAN, LUXURY
}

enum VehicleStatus {
    AVAILABLE, RESERVED, RENTED, MAINTENANCE
}

enum ReservationStatus {
    PENDING, CONFIRMED, ACTIVE, COMPLETED, CANCELLED
}

class Vehicle {
    private final String vehicleId;
    private final String licensePlate;
    private final String make;
    private final String model;
    private final VehicleType type;
    private VehicleStatus status;
    private double pricePerDay;

    public Vehicle(String vehicleId, String licensePlate, String make, 
                   String model, VehicleType type, double pricePerDay) {
        this.vehicleId = vehicleId;
        this.licensePlate = licensePlate;
        this.make = make;
        this.model = model;
        this.type = type;
        this.status = VehicleStatus.AVAILABLE;
        this.pricePerDay = pricePerDay;
    }

    public boolean isAvailable() {
        return status == VehicleStatus.AVAILABLE;
    }

    public void reserve() {
        if (status == VehicleStatus.AVAILABLE) {
            status = VehicleStatus.RESERVED;
        }
    }

    public void startRental() {
        if (status == VehicleStatus.RESERVED) {
            status = VehicleStatus.RENTED;
        }
    }

    public void completeRental() {
        status = VehicleStatus.AVAILABLE;
    }

    public void release() {
        status = VehicleStatus.AVAILABLE;
    }

    // Getters
    public String getVehicleId() { return vehicleId; }
    public String getLicensePlate() { return licensePlate; }
    public String getMake() { return make; }
    public String getModel() { return model; }
    public VehicleType getType() { return type; }
    public VehicleStatus getStatus() { return status; }
    public double getPricePerDay() { return pricePerDay; }

    @Override
    public String toString() {
        return String.format("%s %s (%s) - $%.2f/day", make, model, type, pricePerDay);
    }
}

class Customer {
    private final String customerId;
    private String name;
    private String email;
    private String drivingLicense;
    private final List<Reservation> reservations;

    public Customer(String customerId, String name, String email, String drivingLicense) {
        this.customerId = customerId;
        this.name = name;
        this.email = email;
        this.drivingLicense = drivingLicense;
        this.reservations = new ArrayList<>();
    }

    public void addReservation(Reservation reservation) {
        reservations.add(reservation);
    }

    public List<Reservation> getActiveReservations() {
        List<Reservation> active = new ArrayList<>();
        for (Reservation r : reservations) {
            if (r.getStatus() == ReservationStatus.CONFIRMED || 
                r.getStatus() == ReservationStatus.ACTIVE) {
                active.add(r);
            }
        }
        return active;
    }

    // Getters
    public String getCustomerId() { return customerId; }
    public String getName() { return name; }
    public String getEmail() { return email; }
    public String getDrivingLicense() { return drivingLicense; }
    public List<Reservation> getReservations() { return new ArrayList<>(reservations); }
}

class Reservation {
    private static int counter = 0;
    
    private final String reservationId;
    private final Customer customer;
    private final Vehicle vehicle;
    private final LocalDate startDate;
    private final LocalDate endDate;
    private ReservationStatus status;
    private double totalCost;

    public Reservation(Customer customer, Vehicle vehicle, 
                       LocalDate startDate, LocalDate endDate) {
        this.reservationId = "RES-" + (++counter);
        this.customer = customer;
        this.vehicle = vehicle;
        this.startDate = startDate;
        this.endDate = endDate;
        this.status = ReservationStatus.PENDING;
        this.totalCost = calculateCost();
    }

    private double calculateCost() {
        long days = ChronoUnit.DAYS.between(startDate, endDate);
        if (days < 1) days = 1;
        return days * vehicle.getPricePerDay();
    }

    public void confirm() {
        if (status == ReservationStatus.PENDING) {
            status = ReservationStatus.CONFIRMED;
            vehicle.reserve();
        }
    }

    public void cancel() {
        if (status == ReservationStatus.PENDING || status == ReservationStatus.CONFIRMED) {
            status = ReservationStatus.CANCELLED;
            vehicle.release();
        }
    }

    public void startRental() {
        if (status == ReservationStatus.CONFIRMED) {
            status = ReservationStatus.ACTIVE;
            vehicle.startRental();
        }
    }

    public void complete() {
        if (status == ReservationStatus.ACTIVE) {
            status = ReservationStatus.COMPLETED;
            vehicle.completeRental();
        }
    }

    // Getters
    public String getReservationId() { return reservationId; }
    public Customer getCustomer() { return customer; }
    public Vehicle getVehicle() { return vehicle; }
    public LocalDate getStartDate() { return startDate; }
    public LocalDate getEndDate() { return endDate; }
    public ReservationStatus getStatus() { return status; }
    public double getTotalCost() { return totalCost; }
}

class RentalService {
    private static RentalService instance;
    
    private final Map<String, Vehicle> vehicles;
    private final Map<String, Customer> customers;
    private final Map<String, Reservation> reservations;

    private RentalService() {
        vehicles = new HashMap<>();
        customers = new HashMap<>();
        reservations = new HashMap<>();
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

    public void addVehicle(Vehicle vehicle) {
        vehicles.put(vehicle.getVehicleId(), vehicle);
    }

    public Customer registerCustomer(String customerId, String name, 
                                     String email, String drivingLicense) {
        Customer customer = new Customer(customerId, name, email, drivingLicense);
        customers.put(customerId, customer);
        return customer;
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

    public Reservation makeReservation(Customer customer, Vehicle vehicle,
                                       LocalDate startDate, LocalDate endDate) {
        if (!vehicle.isAvailable()) {
            throw new IllegalStateException("Vehicle is not available");
        }

        Reservation reservation = new Reservation(customer, vehicle, startDate, endDate);
        reservation.confirm();
        customer.addReservation(reservation);
        reservations.put(reservation.getReservationId(), reservation);
        return reservation;
    }

    public void pickupVehicle(Reservation reservation) {
        reservation.startRental();
    }

    public void returnVehicle(Reservation reservation) {
        reservation.complete();
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
}
