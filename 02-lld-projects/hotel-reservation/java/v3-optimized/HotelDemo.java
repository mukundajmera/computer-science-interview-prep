import enums.RoomType;
import models.Guest;
import models.Reservation;
import models.Room;
import java.time.*;
import java.time.temporal.ChronoUnit;
import java.util.*;

public class HotelDemo {
    public static void main(String[] args) {
        System.out.println("=== Hotel Reservation System v2 - Extended Demo ===\n");
        
        // Create hotel
        Hotel hotel = new Hotel("H001", "Grand Hotel");
        
        // Add observers
        hotel.addObserver(new EmailNotifier());
        hotel.addObserver(new HousekeepingNotifier());
        
        // Set pricing strategy
        hotel.setPricingStrategy(new WeekendPricingStrategy());
        
        // Add rooms using factory
        System.out.println("--- Creating Rooms with Factory ---");
        hotel.addRoom(RoomFactory.createRoom("101", RoomType.SINGLE, 1));
        hotel.addRoom(RoomFactory.createRoom("201", RoomType.DOUBLE, 2));
        hotel.addRoom(RoomFactory.createRoom("301", RoomType.DELUXE, 3));
        hotel.addRoom(RoomFactory.createRoom("401", RoomType.SUITE, 4));
        
        // Create guest with profile
        Guest guest = new Guest("G001", "John Smith", "john@email.com", "555-0101");
        guest.setAddress("123 Main St, City");
        
        // Search and book
        System.out.println("\n--- Search and Booking ---");
        LocalDate checkIn = LocalDate.now().plusDays(5);
        LocalDate checkOut = LocalDate.now().plusDays(8);
        
        List<Room> available = hotel.searchAvailableRooms(checkIn, checkOut, RoomType.DELUXE);
        System.out.println("Available deluxe rooms: " + available.size());
        
        Room selectedRoom = available.get(0);
        System.out.println("Selected: " + selectedRoom);
        
        Reservation res = hotel.makeReservation(guest, selectedRoom, checkIn, checkOut);
        System.out.println("\n" + res);
        System.out.println("Deposit paid: $" + String.format("%.2f", res.getTotalPaid()));
        System.out.println("Balance due: $" + String.format("%.2f", res.getBalanceDue()));
        
        // Check-in
        System.out.println("\n--- Check-In ---");
        hotel.checkIn(res.getReservationId());
        
        // Check-out
        System.out.println("\n--- Check-Out ---");
        Payment finalPayment = hotel.checkOut(res.getReservationId());
        System.out.println("Final payment: " + finalPayment);
        System.out.println("Guest loyalty points: " + guest.getLoyaltyPoints());
        
        // Demonstrate cancellation with refund
        System.out.println("\n--- Cancellation with Refund ---");
        Room room201 = hotel.getRoom("201");
        Reservation res2 = hotel.makeReservation(guest, room201, 
            LocalDate.now().plusDays(30), LocalDate.now().plusDays(32));
        System.out.println("Created: " + res2);
        double refund = hotel.cancelReservation(res2.getReservationId());
        System.out.println("Refund amount: $" + String.format("%.2f", refund));
        
        System.out.println("\n=== Demo Complete ===");
    }
}
