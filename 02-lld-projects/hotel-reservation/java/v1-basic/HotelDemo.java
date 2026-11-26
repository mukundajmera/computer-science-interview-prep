import enums.RoomType;
import models.Guest;
import models.Reservation;
import models.Room;
import java.time.*;
import java.time.temporal.ChronoUnit;
import java.util.*;

public class HotelDemo {
    public static void main(String[] args) {
        System.out.println("=== Hotel Reservation System v1 - Basic Demo ===\n");
        
        // Create hotel
        Hotel hotel = new Hotel("H001", "Grand Hotel");
        
        // Add rooms
        System.out.println("--- Adding Rooms ---");
        hotel.addRoom(new Room("101", RoomType.SINGLE, 1));
        hotel.addRoom(new Room("102", RoomType.SINGLE, 1));
        hotel.addRoom(new Room("201", RoomType.DOUBLE, 2));
        hotel.addRoom(new Room("202", RoomType.DOUBLE, 2));
        hotel.addRoom(new Room("301", RoomType.DELUXE, 3));
        hotel.addRoom(new Room("401", RoomType.SUITE, 4));
        
        // Create guests
        Guest guest1 = new Guest("G001", "John Smith", "john@email.com", "555-0101");
        Guest guest2 = new Guest("G002", "Jane Doe", "jane@email.com", "555-0102");
        
        // Search for available rooms
        System.out.println("\n--- Search Available Rooms ---");
        LocalDate checkIn = LocalDate.now().plusDays(1);
        LocalDate checkOut = LocalDate.now().plusDays(4);
        
        System.out.println("Searching for DOUBLE rooms from " + checkIn + " to " + checkOut);
        List<Room> available = hotel.searchAvailableRooms(checkIn, checkOut, RoomType.DOUBLE);
        System.out.println("Found " + available.size() + " available rooms:");
        for (Room room : available) {
            System.out.println("  " + room);
        }
        
        // Make reservation
        System.out.println("\n--- Make Reservation ---");
        Room selectedRoom = available.get(0);
        Reservation res1 = hotel.makeReservation(guest1, selectedRoom, checkIn, checkOut);
        System.out.println(res1);
        
        // Try to book same room (should fail)
        System.out.println("\n--- Attempt Double Booking ---");
        Reservation res2 = hotel.makeReservation(guest2, selectedRoom, checkIn, checkOut);
        if (res2 == null) {
            System.out.println("Double booking prevented!");
        }
        
        // Check-in
        System.out.println("\n--- Check-In ---");
        hotel.checkIn(res1.getReservationId());
        System.out.println("Room status: " + selectedRoom.getStatus());
        
        // Check-out
        System.out.println("\n--- Check-Out ---");
        hotel.checkOut(res1.getReservationId());
        System.out.println("Room status: " + selectedRoom.getStatus());
        System.out.println("Reservation status: " + res1.getStatus());
        
        // New booking and cancellation
        System.out.println("\n--- Cancellation Demo ---");
        Room room301 = hotel.searchAvailableRooms(checkIn, checkOut, RoomType.DELUXE).get(0);
        Reservation res3 = hotel.makeReservation(guest2, room301, checkIn, checkOut);
        System.out.println("Created: " + res3);
        hotel.cancelReservation(res3.getReservationId());
        System.out.println("After cancellation: " + res3.getStatus());
        
        // List all reservations
        System.out.println("\n--- All Reservations ---");
        for (Reservation res : hotel.getAllReservations()) {
            System.out.println(res);
        }
        
        System.out.println("\n=== Demo Complete ===");
    }
}
