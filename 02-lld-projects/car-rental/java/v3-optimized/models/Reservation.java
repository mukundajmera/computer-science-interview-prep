package models;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.*;

public class Reservation {
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
    private double lateFeeCost;
    private double totalCost;
    private Payment payment;
    private final PricingStrategy pricingStrategy;

    public Reservation(Customer customer, Vehicle vehicle, 
                       LocalDate startDate, LocalDate endDate,
                       InsuranceType insurance, PricingStrategy pricingStrategy, double surgeMultiplier) {
        this.reservationId = "RES-" + (++counter);
        this.customer = customer;
        this.vehicle = vehicle;
        this.startDate = startDate;
        this.endDate = endDate;
        this.status = ReservationStatus.PENDING;
        this.insurance = insurance;
        this.pricingStrategy = pricingStrategy;
        this.damageCost = 0;
        calculateCosts(surgeMultiplier);
    }

    private void calculateCosts(double surgeMultiplier) {
        long hours = ChronoUnit.HOURS.between(startDate.atStartOfDay(), endDate.atStartOfDay());
        if (hours < 24) hours = 24;
        
        this.rentalCost = pricingStrategy.calculatePrice(vehicle, hours, surgeMultiplier);
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

    public void complete(int milesDriven, DamageReport damageReport, LocalDate actualReturnDate) {
        if (status != ReservationStatus.ACTIVE) return;
        
        vehicle.updateMileage(milesDriven);
        
        if (actualReturnDate != null && actualReturnDate.isAfter(endDate)) {
            long lateDays = java.time.temporal.ChronoUnit.DAYS.between(endDate, actualReturnDate);
            this.lateFeeCost = lateDays * vehicle.getBasePrice() * 2; // Late fee is 2x base price
            this.totalCost += lateFeeCost;
        }
        
        if (damageReport != null) {
            vehicle.addDamageReport(damageReport);
            double covered = damageReport.getEstimatedCost() * insurance.getCoverage();
            this.damageCost = damageReport.getEstimatedCost() - covered;
            this.totalCost += damageCost;
        }
        
        status = ReservationStatus.COMPLETED;
        vehicle.completeRental();
        customer.addLoyaltyPoints((int) (totalCost / 10)); // 1 point per $10 spent

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
    public double getLateFeeCost() { return lateFeeCost; }
    public double getTotalCost() { return totalCost; }
    public Payment getPayment() { return payment; }
}
