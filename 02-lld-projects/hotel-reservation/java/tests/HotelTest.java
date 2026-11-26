/**
 * Hotel Reservation System Tests - JUnit 5
 * 
 * Tests for all versions of the Hotel Reservation system
 */

import org.junit.jupiter.api.*;
import static org.junit.jupiter.api.Assertions.*;

import java.time.*;
import java.util.*;

// ==================== Test Enums ====================

enum RoomType {
    SINGLE(1, 100.0), DOUBLE(2, 150.0), DELUXE(3, 200.0), SUITE(4, 350.0);
    private final int maxOccupancy;
    private final double basePrice;
    RoomType(int maxOccupancy, double basePrice) {
        this.maxOccupancy = maxOccupancy;
        this.basePrice = basePrice;
    }
    public int getMaxOccupancy() { return maxOccupancy; }
    public double getBasePrice() { return basePrice; }
}

enum RoomStatus { AVAILABLE, OCCUPIED, MAINTENANCE, CLEANING }
enum ReservationStatus { PENDING, CONFIRMED, CHECKED_IN, CHECKED_OUT, CANCELLED }

// ==================== Minimal Classes for Testing ====================

class Guest {
    private final String guestId;
    private final String name;
    private final String email;
    private final List<Reservation> reservations = new ArrayList<>();
    
    public Guest(String guestId, String name, String email) {
        this.guestId = guestId;
        this.name = name;
        this.email = email;
    }
    
    public String getGuestId() { return guestId; }
    public String getName() { return name; }
    public String getEmail() { return email; }
    public void addReservation(Reservation res) { reservations.add(res); }
    public List<Reservation> getReservations() { return new ArrayList<>(reservations); }
}

class Room {
    private final String roomNumber;
    private final RoomType roomType;
    private RoomStatus status = RoomStatus.AVAILABLE;
    
    public Room(String roomNumber, RoomType roomType) {
        this.roomNumber = roomNumber;
        this.roomType = roomType;
    }
    
    public String getRoomNumber() { return roomNumber; }
    public RoomType getRoomType() { return roomType; }
    public double getBasePrice() { return roomType.getBasePrice(); }
    public RoomStatus getStatus() { return status; }
    public void setStatus(RoomStatus status) { this.status = status; }
}

class Reservation {
    private final String reservationId;
    private final Guest guest;
    private final Room room;
    private final LocalDate checkIn;
    private final LocalDate checkOut;
    private ReservationStatus status = ReservationStatus.PENDING;
    private final double totalAmount;
    
    public Reservation(String id, Guest guest, Room room, LocalDate checkIn, LocalDate checkOut) {
        this.reservationId = id;
        this.guest = guest;
        this.room = room;
        this.checkIn = checkIn;
        this.checkOut = checkOut;
        this.totalAmount = java.time.temporal.ChronoUnit.DAYS.between(checkIn, checkOut) * room.getBasePrice();
    }
    
    public String getReservationId() { return reservationId; }
    public Guest getGuest() { return guest; }
    public Room getRoom() { return room; }
    public LocalDate getCheckIn() { return checkIn; }
    public LocalDate getCheckOut() { return checkOut; }
    public ReservationStatus getStatus() { return status; }
    public double getTotalAmount() { return totalAmount; }
    
    public void confirm() {
        if (status == ReservationStatus.PENDING) status = ReservationStatus.CONFIRMED;
    }
    
    public void checkIn() {
        if (status == ReservationStatus.CONFIRMED) {
            status = ReservationStatus.CHECKED_IN;
            room.setStatus(RoomStatus.OCCUPIED);
        }
    }
    
    public void checkOut() {
        if (status == ReservationStatus.CHECKED_IN) {
            status = ReservationStatus.CHECKED_OUT;
            room.setStatus(RoomStatus.CLEANING);
        }
    }
    
    public void cancel() {
        if (status == ReservationStatus.PENDING || status == ReservationStatus.CONFIRMED) {
            status = ReservationStatus.CANCELLED;
        }
    }
}

// ==================== Tests ====================

public class HotelTest {
    
    private Guest testGuest;
    private Room testRoom;
    private LocalDate checkIn;
    private LocalDate checkOut;
    
    @BeforeEach
    void setUp() {
        testGuest = new Guest("G001", "John Doe", "john@email.com");
        testRoom = new Room("201", RoomType.DOUBLE);
        checkIn = LocalDate.now().plusDays(5);
        checkOut = LocalDate.now().plusDays(8);
    }
    
    // ==================== Room Tests ====================
    
    @Nested
    @DisplayName("Room Tests")
    class RoomTests {
        
        @Test
        @DisplayName("Room creation with correct values")
        void testRoomCreation() {
            assertEquals("201", testRoom.getRoomNumber());
            assertEquals(RoomType.DOUBLE, testRoom.getRoomType());
            assertEquals(150.0, testRoom.getBasePrice());
            assertEquals(RoomStatus.AVAILABLE, testRoom.getStatus());
        }
        
        @Test
        @DisplayName("Room status changes")
        void testRoomStatusChange() {
            testRoom.setStatus(RoomStatus.OCCUPIED);
            assertEquals(RoomStatus.OCCUPIED, testRoom.getStatus());
            
            testRoom.setStatus(RoomStatus.CLEANING);
            assertEquals(RoomStatus.CLEANING, testRoom.getStatus());
        }
        
        @Test
        @DisplayName("Different room types have correct prices")
        void testRoomTypePrices() {
            Room single = new Room("101", RoomType.SINGLE);
            Room suite = new Room("401", RoomType.SUITE);
            
            assertEquals(100.0, single.getBasePrice());
            assertEquals(350.0, suite.getBasePrice());
        }
    }
    
    // ==================== Guest Tests ====================
    
    @Nested
    @DisplayName("Guest Tests")
    class GuestTests {
        
        @Test
        @DisplayName("Guest creation with correct values")
        void testGuestCreation() {
            assertEquals("G001", testGuest.getGuestId());
            assertEquals("John Doe", testGuest.getName());
            assertEquals("john@email.com", testGuest.getEmail());
        }
        
        @Test
        @DisplayName("Guest reservation history")
        void testGuestReservationHistory() {
            Reservation res = new Reservation("RES001", testGuest, testRoom, checkIn, checkOut);
            testGuest.addReservation(res);
            
            assertEquals(1, testGuest.getReservations().size());
            assertEquals("RES001", testGuest.getReservations().get(0).getReservationId());
        }
    }
    
    // ==================== Reservation Tests ====================
    
    @Nested
    @DisplayName("Reservation Tests")
    class ReservationTests {
        
        @Test
        @DisplayName("Reservation creation with correct values")
        void testReservationCreation() {
            Reservation res = new Reservation("RES001", testGuest, testRoom, checkIn, checkOut);
            
            assertEquals("RES001", res.getReservationId());
            assertEquals(testGuest, res.getGuest());
            assertEquals(testRoom, res.getRoom());
            assertEquals(checkIn, res.getCheckIn());
            assertEquals(checkOut, res.getCheckOut());
            assertEquals(ReservationStatus.PENDING, res.getStatus());
        }
        
        @Test
        @DisplayName("Reservation total amount calculation")
        void testReservationTotalAmount() {
            Reservation res = new Reservation("RES001", testGuest, testRoom, checkIn, checkOut);
            // 3 nights at $150/night = $450
            assertEquals(450.0, res.getTotalAmount());
        }
        
        @Test
        @DisplayName("Reservation confirm flow")
        void testReservationConfirm() {
            Reservation res = new Reservation("RES001", testGuest, testRoom, checkIn, checkOut);
            assertEquals(ReservationStatus.PENDING, res.getStatus());
            
            res.confirm();
            assertEquals(ReservationStatus.CONFIRMED, res.getStatus());
        }
        
        @Test
        @DisplayName("Reservation check-in flow")
        void testReservationCheckIn() {
            Reservation res = new Reservation("RES001", testGuest, testRoom, checkIn, checkOut);
            res.confirm();
            res.checkIn();
            
            assertEquals(ReservationStatus.CHECKED_IN, res.getStatus());
            assertEquals(RoomStatus.OCCUPIED, testRoom.getStatus());
        }
        
        @Test
        @DisplayName("Reservation check-out flow")
        void testReservationCheckOut() {
            Reservation res = new Reservation("RES001", testGuest, testRoom, checkIn, checkOut);
            res.confirm();
            res.checkIn();
            res.checkOut();
            
            assertEquals(ReservationStatus.CHECKED_OUT, res.getStatus());
            assertEquals(RoomStatus.CLEANING, testRoom.getStatus());
        }
        
        @Test
        @DisplayName("Reservation cancellation")
        void testReservationCancel() {
            Reservation res = new Reservation("RES001", testGuest, testRoom, checkIn, checkOut);
            res.confirm();
            res.cancel();
            
            assertEquals(ReservationStatus.CANCELLED, res.getStatus());
        }
        
        @Test
        @DisplayName("Cannot check in without confirmation")
        void testCannotCheckInWithoutConfirmation() {
            Reservation res = new Reservation("RES001", testGuest, testRoom, checkIn, checkOut);
            res.checkIn(); // Should not change status
            
            assertEquals(ReservationStatus.PENDING, res.getStatus());
        }
        
        @Test
        @DisplayName("Cannot cancel after check-in")
        void testCannotCancelAfterCheckIn() {
            Reservation res = new Reservation("RES001", testGuest, testRoom, checkIn, checkOut);
            res.confirm();
            res.checkIn();
            res.cancel(); // Should not change status
            
            assertEquals(ReservationStatus.CHECKED_IN, res.getStatus());
        }
    }
    
    // ==================== Integration Tests ====================
    
    @Nested
    @DisplayName("Integration Tests")
    class IntegrationTests {
        
        @Test
        @DisplayName("Complete booking flow")
        void testCompleteBookingFlow() {
            // Create reservation
            Reservation res = new Reservation("RES001", testGuest, testRoom, checkIn, checkOut);
            testGuest.addReservation(res);
            
            // Confirm
            res.confirm();
            assertEquals(ReservationStatus.CONFIRMED, res.getStatus());
            
            // Check in
            res.checkIn();
            assertEquals(ReservationStatus.CHECKED_IN, res.getStatus());
            assertEquals(RoomStatus.OCCUPIED, testRoom.getStatus());
            
            // Check out
            res.checkOut();
            assertEquals(ReservationStatus.CHECKED_OUT, res.getStatus());
            assertEquals(RoomStatus.CLEANING, testRoom.getStatus());
            
            // Verify guest history
            assertEquals(1, testGuest.getReservations().size());
        }
        
        @Test
        @DisplayName("Multiple reservations for same guest")
        void testMultipleReservationsForGuest() {
            Room room1 = new Room("201", RoomType.DOUBLE);
            Room room2 = new Room("301", RoomType.DELUXE);
            
            Reservation res1 = new Reservation("RES001", testGuest, room1, 
                LocalDate.now().plusDays(5), LocalDate.now().plusDays(7));
            Reservation res2 = new Reservation("RES002", testGuest, room2, 
                LocalDate.now().plusDays(10), LocalDate.now().plusDays(12));
            
            testGuest.addReservation(res1);
            testGuest.addReservation(res2);
            
            assertEquals(2, testGuest.getReservations().size());
        }
    }
    
    // ==================== Main method ====================
    
    public static void main(String[] args) {
        System.out.println("Running Hotel Reservation System Tests...\n");
        
        HotelTest test = new HotelTest();
        int passed = 0;
        int failed = 0;
        
        // Room Tests
        try {
            test.setUp();
            test.new RoomTests().testRoomCreation();
            System.out.println("✓ Room creation test passed");
            passed++;
        } catch (Exception e) {
            System.out.println("✗ Room creation test failed: " + e.getMessage());
            failed++;
        }
        
        try {
            test.setUp();
            test.new RoomTests().testRoomTypePrices();
            System.out.println("✓ Room type prices test passed");
            passed++;
        } catch (Exception e) {
            System.out.println("✗ Room type prices test failed: " + e.getMessage());
            failed++;
        }
        
        // Reservation Tests
        try {
            test.setUp();
            test.new ReservationTests().testReservationCreation();
            System.out.println("✓ Reservation creation test passed");
            passed++;
        } catch (Exception e) {
            System.out.println("✗ Reservation creation test failed: " + e.getMessage());
            failed++;
        }
        
        try {
            test.setUp();
            test.new ReservationTests().testReservationTotalAmount();
            System.out.println("✓ Reservation total amount test passed");
            passed++;
        } catch (Exception e) {
            System.out.println("✗ Reservation total amount test failed: " + e.getMessage());
            failed++;
        }
        
        try {
            test.setUp();
            test.new ReservationTests().testReservationCheckIn();
            System.out.println("✓ Reservation check-in test passed");
            passed++;
        } catch (Exception e) {
            System.out.println("✗ Reservation check-in test failed: " + e.getMessage());
            failed++;
        }
        
        try {
            test.setUp();
            test.new ReservationTests().testReservationCheckOut();
            System.out.println("✓ Reservation check-out test passed");
            passed++;
        } catch (Exception e) {
            System.out.println("✗ Reservation check-out test failed: " + e.getMessage());
            failed++;
        }
        
        // Integration Tests
        try {
            test.setUp();
            test.new IntegrationTests().testCompleteBookingFlow();
            System.out.println("✓ Complete booking flow test passed");
            passed++;
        } catch (Exception e) {
            System.out.println("✗ Complete booking flow test failed: " + e.getMessage());
            failed++;
        }
        
        System.out.println("\n=== Test Results ===");
        System.out.println("Passed: " + passed);
        System.out.println("Failed: " + failed);
        System.out.println("Total: " + (passed + failed));
    }
}
