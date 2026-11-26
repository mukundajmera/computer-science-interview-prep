import enums.ReservationStatus;
import models.Reservation;
import models.Customer;
import enums.VehicleType;
import models.Vehicle;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.*;

/**
 * Car Rental System - V2 Extended
 * 
 * Enhanced with pricing strategies, insurance, damage tracking, and payments.
 */

enum VehicleType {
    CAR(1.0), SUV(1.3), TRUCK(1.4), VAN(1.2), LUXURY(2.0);
    
    private final double priceMultiplier;
    VehicleType(double multiplier) { this.priceMultiplier = multiplier; }
    public double getMultiplier() { return priceMultiplier; }
}

enum VehicleStatus {
    AVAILABLE, RESERVED, RENTED, MAINTENANCE, OUT_OF_SERVICE
}

enum ReservationStatus {
    PENDING, CONFIRMED, ACTIVE, COMPLETED, CANCELLED
}

enum DamageSeverity {
    MINOR(100), MODERATE(500), SEVERE(2000);
    
    private final double baseCost;
    DamageSeverity(double cost) { this.baseCost = cost; }
    public double getBaseCost() { return baseCost; }
}

enum InsuranceType {
    NONE(0, 0), BASIC(15, 0.5), PREMIUM(30, 1.0);
    
    private final double dailyCost;
    private final double damageCoverage;
    InsuranceType(double cost, double coverage) { 
        this.dailyCost = cost; 
        this.damageCoverage = coverage;
    }
    public double getDailyCost() { return dailyCost; }
    public double getCoverage() { return damageCoverage; }
}

enum PaymentStatus {
    PENDING, COMPLETED, REFUNDED, FAILED
}

// Pricing Strategy Pattern
interface PricingStrategy {
    double calculatePrice(Vehicle vehicle, long durationHours);
}

class HourlyPricing implements PricingStrategy {
    private static final double HOURLY_RATE_FACTOR = 0.1; // 10% of daily rate
    
    @Override
    public double calculatePrice(Vehicle vehicle, long durationHours) {
        return vehicle.getBasePrice() * HOURLY_RATE_FACTOR * durationHours;
    }
}

class DailyPricing implements PricingStrategy {
    @Override
    public double calculatePrice(Vehicle vehicle, long durationHours) {
        long days = Math.max(1, durationHours / 24);
        return vehicle.getBasePrice() * days;
    }
}

class WeeklyPricing implements PricingStrategy {
    private static final double WEEKLY_DISCOUNT = 0.85; // 15% discount
    
    @Override
    public double calculatePrice(Vehicle vehicle, long durationHours) {
        long weeks = durationHours / (24 * 7);
        long remainingDays = (durationHours % (24 * 7)) / 24;
        
        double weeklyPrice = vehicle.getBasePrice() * 7 * WEEKLY_DISCOUNT * weeks;
        double dailyPrice = vehicle.getBasePrice() * remainingDays;
        
        return weeklyPrice + dailyPrice;
    }
}

class Vehicle {
    private final String vehicleId;
    private final String licensePlate;
    private final String make;
    private final String model;
    private final VehicleType type;
    private VehicleStatus status;
    private double basePrice;
    private int mileage;
    private final List<DamageReport> damageReports;

    public Vehicle(String vehicleId, String licensePlate, String make, 
                   String model, VehicleType type, double basePrice) {
        this.vehicleId = vehicleId;
        this.licensePlate = licensePlate;
        this.make = make;
        this.model = model;
        this.type = type;
        this.basePrice = basePrice * type.getMultiplier();
        this.status = VehicleStatus.AVAILABLE;
        this.mileage = 0;
        this.damageReports = new ArrayList<>();
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

    public void setMaintenance() {
        status = VehicleStatus.MAINTENANCE;
    }

    public void addDamageReport(DamageReport report) {
        damageReports.add(report);
        if (report.getSeverity() == DamageSeverity.SEVERE) {
            status = VehicleStatus.MAINTENANCE;
        }
    }

    public void updateMileage(int miles) {
        this.mileage += miles;
    }

    // Getters
    public String getVehicleId() { return vehicleId; }
    public String getLicensePlate() { return licensePlate; }
    public String getMake() { return make; }
    public String getModel() { return model; }
    public VehicleType getType() { return type; }
    public VehicleStatus getStatus() { return status; }
    public double getBasePrice() { return basePrice; }
    public int getMileage() { return mileage; }
    public List<DamageReport> getDamageReports() { return new ArrayList<>(damageReports); }

    @Override
    public String toString() {
        return String.format("%s %s (%s) - $%.2f/day", make, model, type, basePrice);
    }
}

class DamageReport {
    private static int counter = 0;
    
    private final String reportId;
    private final Vehicle vehicle;
    private final String description;
    private final DamageSeverity severity;
    private final double estimatedCost;
    private final LocalDateTime reportDate;

    public DamageReport(Vehicle vehicle, String description, DamageSeverity severity) {
        this.reportId = "DMG-" + (++counter);
        this.vehicle = vehicle;
        this.description = description;
        this.severity = severity;
        this.estimatedCost = severity.getBaseCost();
        this.reportDate = LocalDateTime.now();
    }

    public String getReportId() { return reportId; }
    public Vehicle getVehicle() { return vehicle; }
    public String getDescription() { return description; }
    public DamageSeverity getSeverity() { return severity; }
    public double getEstimatedCost() { return estimatedCost; }
    public LocalDateTime getReportDate() { return reportDate; }
}

class Customer {
    private final String customerId;
    private String name;
    private String email;
    private String phone;
    private String drivingLicense;
    private final List<Reservation> reservations;

    public Customer(String customerId, String name, String email, 
                    String phone, String drivingLicense) {
        this.customerId = customerId;
        this.name = name;
        this.email = email;
        this.phone = phone;
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

    public String getCustomerId() { return customerId; }
    public String getName() { return name; }
    public String getEmail() { return email; }
    public String getDrivingLicense() { return drivingLicense; }
    public List<Reservation> getReservations() { return new ArrayList<>(reservations); }
}

class Payment {
    private static int counter = 0;
    
    private final String paymentId;
    private final double amount;
    private PaymentStatus status;
    private final String paymentMethod;
    private final LocalDateTime transactionDate;

    public Payment(double amount, String paymentMethod) {
        this.paymentId = "PAY-" + (++counter);
        this.amount = amount;
        this.paymentMethod = paymentMethod;
        this.status = PaymentStatus.PENDING;
        this.transactionDate = LocalDateTime.now();
    }

    public void process() {
        // Simulate payment processing
        this.status = PaymentStatus.COMPLETED;
    }

    public void refund() {
        if (status == PaymentStatus.COMPLETED) {
            status = PaymentStatus.REFUNDED;
        }
    }

    public String getPaymentId() { return paymentId; }
    public double getAmount() { return amount; }
    public PaymentStatus getStatus() { return status; }
    public String getPaymentMethod() { return paymentMethod; }
}

class Reservation {
    private static int counter = 0;
    
    private final String reservationId;
    private final Customer customer;
    private final Vehicle vehicle;
    private final LocalDate startDate;
    private final LocalDate endDate;
    private ReservationStatus status;
    private InsuranceType insurance;
    private double rentalCost;
    private double insuranceCost;
    private double damageCost;
    private double totalCost;
    private Payment payment;
    private final PricingStrategy pricingStrategy;

    public Reservation(Customer customer, Vehicle vehicle, 
                       LocalDate startDate, LocalDate endDate,
                       InsuranceType insurance, PricingStrategy pricingStrategy) {
        this.reservationId = "RES-" + (++counter);
        this.customer = customer;
        this.vehicle = vehicle;
        this.startDate = startDate;
        this.endDate = endDate;
        this.status = ReservationStatus.PENDING;
        this.insurance = insurance;
        this.pricingStrategy = pricingStrategy;
        this.damageCost = 0;
        calculateCosts();
    }

    private void calculateCosts() {
        long hours = ChronoUnit.HOURS.between(startDate.atStartOfDay(), endDate.atStartOfDay());
        if (hours < 24) hours = 24;
        
        this.rentalCost = pricingStrategy.calculatePrice(vehicle, hours);
        this.insuranceCost = insurance.getDailyCost() * (hours / 24);
        this.totalCost = rentalCost + insuranceCost;
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

    public void complete(int milesDriven, DamageReport damageReport) {
        if (status != ReservationStatus.ACTIVE) return;
        
        vehicle.updateMileage(milesDriven);
        
        if (damageReport != null) {
            vehicle.addDamageReport(damageReport);
            double covered = damageReport.getEstimatedCost() * insurance.getCoverage();
            this.damageCost = damageReport.getEstimatedCost() - covered;
            this.totalCost += damageCost;
        }
        
        status = ReservationStatus.COMPLETED;
        vehicle.completeRental();
    }

    public void processPayment(String paymentMethod) {
        payment = new Payment(totalCost, paymentMethod);
        payment.process();
    }

    // Getters
    public String getReservationId() { return reservationId; }
    public Customer getCustomer() { return customer; }
    public Vehicle getVehicle() { return vehicle; }
    public LocalDate getStartDate() { return startDate; }
    public LocalDate getEndDate() { return endDate; }
    public ReservationStatus getStatus() { return status; }
    public InsuranceType getInsurance() { return insurance; }
    public double getRentalCost() { return rentalCost; }
    public double getInsuranceCost() { return insuranceCost; }
    public double getDamageCost() { return damageCost; }
    public double getTotalCost() { return totalCost; }
    public Payment getPayment() { return payment; }
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
                                     String email, String phone, String drivingLicense) {
        Customer customer = new Customer(customerId, name, email, phone, drivingLicense);
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

    public Reservation makeReservation(Customer customer, Vehicle vehicle,
                                       LocalDate startDate, LocalDate endDate,
                                       InsuranceType insurance) {
        if (!vehicle.isAvailable()) {
            throw new IllegalStateException("Vehicle is not available");
        }

        PricingStrategy strategy = selectPricingStrategy(startDate, endDate);
        Reservation reservation = new Reservation(customer, vehicle, startDate, endDate, 
                                                   insurance, strategy);
        reservation.confirm();
        customer.addReservation(reservation);
        reservations.put(reservation.getReservationId(), reservation);
        return reservation;
    }

    public void pickupVehicle(Reservation reservation) {
        reservation.startRental();
    }

    public void returnVehicle(Reservation reservation, int milesDriven, DamageReport damage) {
        reservation.complete(milesDriven, damage);
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
